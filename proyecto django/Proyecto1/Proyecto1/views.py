import re
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import RegistrationForm
from django.template import loader
from .forms import RegistrationForm
from .models import Usuario
import maude
import itertools

#Cada funcion que hay aquí es una vista

def home(request):
    # Lógica de tu vista aquí
    return render(request, 'home.html')

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
    # Lógica de tu vista aquí
    return render(request, 'login.html')

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
def run_maude_command(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        command_type = request.POST.get('maude_operation')
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
        elif comando in ["example"]:
            example()
        # Añadir más condiciones según sea necesario

        result_str = str(resultado)

        # Devolver la respuesta como JSON
        return JsonResponse({'result': result_str})
    else:
        # Manejar solicitudes no AJAX si es necesario
        return render(request, 'home.html')
