import json
import re
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import PasswordResetRequestForm, RegistrationForm, UserLoginForm
from django.contrib.auth import login as auth_login
from .forms import RegistrationForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Chat, Mensaje, Usuario
import maude
import itertools
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Usuario
from .forms import PasswordResetRequestForm
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .forms import PasswordResetRequestForm
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect

#Cada funcion que hay aquí es una vista
@login_required
def blank(request):
    return redirect('home', chat_id=None)

@login_required
def home(request, chat_id=None):
    chats = Chat.objects.filter(usuario=request.user).order_by('-id')
    return render(request, 'home.html', {'chats': chats})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            Usuario = get_user_model()
            associated_users = Usuario.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    # Crear el token y el uid
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    # Construir el enlace de restablecimiento de contraseña
                    link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
                    # Construir el mensaje de correo
                    subject = 'Restablecimiento de contraseña'
                    message = f'Por favor, haz clic en el siguiente enlace para restablecer tu contraseña: {link}'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    # Enviar el correo
                    send_mail(subject, message, email_from, recipient_list)
                # Podrías redirigir a una página de éxito o renderizar un mensaje en este punto
                return redirect('password_reset_done')
    else:
        form = PasswordResetRequestForm()
    return render(request, "registration/password_reset_form.html", {"form": form})

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
@ensure_csrf_cookie
def delete_chats(request):
    if request.method == 'POST':
        # Asegúrate de parsear el JSON en el body de la solicitud
        chat_ids = json.loads(request.POST.get('chat_ids'))
        # Filtro para asegurarse de que solo se eliminan los chats del usuario
        Chat.objects.filter(id__in=chat_ids, usuario=request.user).delete()
        return JsonResponse({'message': 'Chats eliminados correctamente'}, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

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
@csrf_protect
def new_chat(request):
        data = json.loads(request.body)
        chat_name = data.get('nombre')
        Chat.objects.create(nombre=chat_name, usuario=request.user)
        # Devuelve todos los chats
        chats = Chat.objects.filter(usuario=request.user)
        chats_data = [{'id': chat.id, 'nombre': chat.nombre} for chat in chats]
        return JsonResponse({'status': 'success', 'chats': chats_data})

@login_required
def saveModule(request, chat_id):
    chat = Chat.objects.get(id=chat_id, usuario=request.user)
    modulo = request.body.decode('utf-8')
    print(modulo)
    chat.modulo = modulo
    chat.save()
    return JsonResponse({'status': 'success', 'message': 'Módulo guardado correctamente.'})
    

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
