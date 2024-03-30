import re
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import RegistrationForm, UserLoginForm
from django.contrib.auth import login as auth_login
from .forms import RegistrationForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Chat, Mensaje, Usuario
import maude
import itertools

#Cada funcion que hay aquí es una vista
@login_required
def blank(request):
    return redirect('home', chat_id=None)

@login_required
def home(request, chat_id=None):
    chats = Chat.objects.filter(usuario=request.user).order_by('-id')
    return render(request, 'home.html', {'chats': chats})

def chat_view(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    if request.method == 'POST':
        comando = request.POST.get('maude_execution')
        respuesta = interpret_command(comando)  # Procesa el comando con Maude
        Mensaje.objects.create(chat=chat, comando=comando, respuesta=respuesta)  # Guarda el mensaje y la respuesta en la base de datos
        return redirect('chat', chat_id=chat.id)  # Redirige al mismo chat después de enviar el comando

    mensajes = Mensaje.objects.filter(chat=chat).order_by('-fecha_creacion')
    return render(request, 'chat.html', {'chat': chat, 'mensajes': mensajes})

@login_required
def get_chat_content(request, chat_id):
    # Asegúrate de que solo los usuarios autorizados puedan acceder a sus chats
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    mensajes = Mensaje.objects.filter(chat=chat).order_by('fecha_creacion')
    mensajes_data = [{
        'comando': mensaje.comando,
        'respuesta': mensaje.respuesta,
        # Agrega aquí más datos si necesitas
    } for mensaje in mensajes]
    chat_data = {
        'nombre': chat.nombre,
        'modulo':chat.modulo,
        'mensajes': mensajes_data,
        # Agrega aquí más datos si necesitas
    }
    return JsonResponse(chat_data)

@login_required
def new_chat(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre_chat")
        Chat.objects.create(nombre=nombre, usuario=request.user)
        return redirect('home')
    
    return render(request, 'new_chat.html')

@login_required
def saveModule(request, chat_id):
    print("ha entrado en save module")
    chat = Chat.objects.get(id=chat_id, usuario=request.user)
    modulo = request.POST.get()
    chat.modulo = modulo
    chat.save()
    

def logout_request(request):
    logout(request)
    # Puedes añadir aquí cualquier lógica adicional que necesites.
    return redirect('login')

def verificar_email(request, codigo):
    user = Usuario.objects.get(codigo_verificacion=codigo)
    user.email_verificado = True
    user.save()
    return redirect('login')

def enviar_email_verificacion(user):
    subject = 'Verifica tu correo electrónico'
    message = f'Usa este enlace para verificar tu cuenta: http://127.0.0.1:8000/verificar/{user.codigo_verificacion}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    send_mail(subject, message, email_from, recipient_list)

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)  # Cambia aquí a 'username'
            if user is not None:
                if user.email_verificado:
                    auth_login(request, user)  # Usa el nuevo nombre aquí
                    return redirect('home')
                else:
                    form.add_error(None, 'Por favor, verifica tu correo electrónico antes de iniciar sesión.')
            else:
                form.add_error(None, 'Correo o contraseña incorrectos.')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = Usuario(
                email=form.cleaned_data['correo_ucm'],
                nombre=form.cleaned_data['nombre'],
            )
            user.set_password(form.cleaned_data['contraseña'])
            user.save()
            enviar_email_verificacion(user)
            return redirect('login')  # Redireccionar a la página que desees después del registro
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

@require_http_methods(["POST"])
def run_maude_command(request, chat_id):
    print("Entrando a run_maude_command")
    chat = Chat.objects.get(id=chat_id, usuario=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        maude_execution = request.POST.get('maude_execution')
        user_code = request.POST.get('maude_code')

        maude.init()
        maude.input(user_code)
        module = maude.getCurrentModule()
        operacion = maude_execution.split(" ")
        resto = operacion[1:]
        resto = " ".join(resto)
        comando = operacion[0]

        def reduce():
            
            term = module.parseTerm(resto)
            term.reduce()

            return term
        
        def rewrite():
            match = re.search(r'\[(\d+)\]', resto)
            if match:
                numero = match.group(1)
                numero = int(numero)
                palabra = resto.split(" ")[1]
                term = module.parseTerm(palabra)
                term.rewrite(numero)
            else:
                term = module.parseTerm(resto)
                term.rewrite()

            return term
        
        def frewrite():
            match = re.search(r'\[(\d+)\]', resto)
            if match:
                numero = match.group(1)
                numero = int(numero)
                palabra = resto.split(" ")[1]
                term = module.parseTerm(palabra)
                term.frewrite(numero)
            else:
                term = module.parseTerm(resto)
                term.frewrite()

            return term
        
        def search():
            soluciones = ""

            # La expresión regular para analizar el comando de búsqueda
            pattern_search = re.compile(
                r"\[([^,]*),?([^]]*)\]\s*"  # Argumentos opcionales [n, m]
                r"(\w+)"  # Term-1 (término inicial), permitiendo palabras sin espacios
                r" (=>1|=>\+|=>\*|=>!)"  # SearchArrow
                r" ([^\s]+(?:\s+(?!\s*s\.t\.)[^\s]+)*)"  # Term-2 (patrón a alcanzar), mejorado para múltiples términos y estructuras
                r"(?:\s+s\.t\.\s+(.*))?"  # Condición opcional 's.t. <Condition>', claramente separada
            )

            match = pattern_search.match(resto)
            if match:
                n, m, term1, search_arrow, term2, condition_text = match.groups()
                # Obtener los valores de las variables parseadas
                parsed_values = {
                    'n': n,
                    'm': m,
                    'term1': term1,
                    'search_arrow': search_arrow,
                    'term2': term2,
                    'condition_text': condition_text
                }

                # Imprimir los valores de las variables parseadas
                for variable, value in parsed_values.items():
                    print(f'{variable}: {value}')
                # Convertir a tipos apropiados y preparar la búsqueda
                n = int(n) if n else None
                m = int(m) if m else None

                ini = module.parseTerm(term1)
                fin = module.parseTerm(term2)

                # Procesar la parte de la condición
                conditions = []
                if condition_text:
                    # Verificar si hay múltiples condiciones separadas por 'and'
                    all_conditions = condition_text.split(' and ')
                    for cond_part in all_conditions:
                        # Verificar si la condición contiene una igualdad
                        if "==" in cond_part:
                            lhs, rhs = [module.parseTerm(part.strip()) for part in cond_part.split('==')]
                            conditions.append(maude.EqualityCondition(lhs, rhs))
                        # Aquí puedes añadir más elif para manejar diferentes tipos de condiciones
                        # Por ejemplo:
                        # elif '!=' in cond_part:
                        #    lhs, rhs = [module.parseTerm(part.strip()) for part in cond_part.split('!=')]
                        #    conditions.append(maude.InequalityCondition(lhs, rhs))


                # Determinar el tipo de flecha
                search_arrow_map = {'=>*': maude.ANY_STEPS, '=>+': maude.AT_LEAST_ONE_STEP, '=>!': maude.NORMAL_FORM, '=>1': maude.ONE_STEP}
                flecha = search_arrow_map.get(search_arrow, maude.ANY_STEPS)

                # Realizar la búsqueda
                for sol, subs, path, nrew in itertools.islice(ini.search(flecha, fin, conditions, None, m or -1), n or 1):
                    solucion = str(subs)
                    soluciones += f"{solucion}<br>"  # Usando <br> para HTML, reemplazar por '\n' si es para texto

            return soluciones if soluciones else "No hay soluciones"        
            

        if comando in ["reduce", "red"]:
            resultado = reduce()
        elif comando in ["rew", "rewrite"]:
            resultado = rewrite()
        elif comando in ["search"]:
            resultado = search()
        elif comando in ["frewrite", "frew"]:
            resultado = frewrite()
        # Añadir más condiciones según sea necesario

        response = str(resultado)
        chat.modulo = user_code
        chat.save()
        Mensaje.objects.create(chat=chat, comando=maude_execution, respuesta=response)

        # Devolver la respuesta como JSON
        return JsonResponse({'comando': maude_execution, 'respuesta': response})
    else:
        # Manejar solicitudes no AJAX si es necesario
        return JsonResponse({'error': 'Solicitud incorrecta'}, status=400)
