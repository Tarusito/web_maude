import json
from pyexpat.errors import messages
import re
from django.core.mail import send_mail
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import PasswordResetRequestForm, RegistrationForm, SetPasswordForm, UserLoginForm
from django.contrib.auth import login as auth_login
from .forms import RegistrationForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Chat, Mensaje, Modulo, Usuario,Entrega
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
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Modulo, ModuloVersion, Chat
import difflib

#Cada funcion que hay aquí es una vista
@login_required
def blank(request):
    return redirect('home', chat_id=None)

@login_required
def home(request, chat_id=None):
    chats = Chat.objects.filter(usuario=request.user).order_by('-id')
    return render(request, 'home.html', {'chats': chats})

# Mejoras en la vista para asegurar retroalimentación adecuada y redirección
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = get_user_model().objects.filter(email=email)
            if users.exists():
                for user in users:
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
                    subject = 'Restablecimiento de contraseña'
                    message = f'Haz clic en el enlace para restablecer tu contraseña: {link}'
                    email_from = settings.EMAIL_HOST_USER
                    send_mail(subject, message, email_from, [user.email])
                return HttpResponse('Te hemos enviado un correo para restablecer tu contraseña.')
            else:
                form.add_error('email', 'No hay usuarios registrados con ese correo.')
    else:
        form = PasswordResetRequestForm()
    return render(request, "password_reset_form.html", {"form": form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (ValueError, OverflowError, get_user_model().DoesNotExist):
        return HttpResponse('Enlace inválido o caducado')

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                return redirect('login')  # Asegúrate de redirigir a una página de confirmación o login
        else:
            form = SetPasswordForm()
        return render(request, 'password_reset_confirm.html', {'form': form, 'uidb64': uidb64, 'token': token})
    else:
        return HttpResponse('Enlace inválido o caducado')

@login_required
def chat_view(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    if request.method == 'POST':
        comando = request.POST.get('maude_execution')
        estado = request.POST.get('estado', Mensaje.EstadoChoices.NINGUNO)  # Por defecto 'Ninguno'
        respuesta = interpret_command(comando)  # Procesa el comando con Maude
        Mensaje.objects.create(chat=chat, comando=comando, respuesta=respuesta, estado=estado)
        return redirect('chat', chat_id=chat.id)

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
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    mensajes = Mensaje.objects.filter(chat=chat).order_by('fecha_creacion')
    mensajes_data = [{
        'comando': mensaje.comando,
        'respuesta': mensaje.respuesta,
        'titulo_modulo': mensaje.titulo_modulo,
        'mensaje_id':mensaje.id,
        'estado':mensaje.estado
    } for mensaje in mensajes]
    chat_data = {
        'nombre': chat.nombre,
        'modulo': chat.modulo,
        'mensajes': mensajes_data,
    }
    return JsonResponse(chat_data)

@login_required
@csrf_protect
def new_chat(request):
        data = json.loads(request.body)
        chat_name = data.get('nombre')
        titulo_modulo = data.get('titulo_modulo', 'Sin título')
        Chat.objects.create(nombre=chat_name, titulo_modulo=titulo_modulo, usuario=request.user)
        # Devuelve todos los chats
        chats = Chat.objects.filter(usuario=request.user)
        chats_data = [{'id': chat.id, 'nombre': chat.nombre} for chat in chats]
        return JsonResponse({'status': 'success', 'chats': chats_data})

@login_required
def saveModule(request, chat_id):
    chat = Chat.objects.get(id=chat_id, usuario=request.user)
    data = json.loads(request.body)
    modulo = data.get('codigo', '')
    titulo_modulo = data.get('titulo', 'Sin título')  # Obtener el nuevo título del módulo

    chat.modulo = modulo
    chat.titulo_modulo = titulo_modulo  # Actualizar el título del módulo
    chat.save()

    return JsonResponse({'status': 'success', 'message': 'Módulo guardado correctamente.'})


@login_required
def get_mensajes_bien(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    mensajes = Mensaje.objects.filter(chat=chat, estado=Mensaje.EstadoChoices.BIEN)
    mensajes_data = [{'comando': m.comando, 'respuesta': m.respuesta, 'titulo_modulo': m.titulo_modulo} for m in mensajes]
    administradores = Usuario.objects.filter(is_admin=True).values('id', 'nombre')
    return JsonResponse({'mensajes': mensajes_data, 'administradores': list(administradores)})


@login_required
@require_http_methods(["POST"])
def enviar_mensajes_bien(request, chat_id):
    data = json.loads(request.body)
    admin_id = data.get('administrador_id')
    administrador = get_object_or_404(Usuario, id=admin_id, is_admin=True)
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)

    mensajes = Mensaje.objects.filter(chat=chat, estado=Mensaje.EstadoChoices.BIEN)
    
    if mensajes.exists():
        # Crear una única entrega
        entrega = Entrega.objects.create(
            administrador=administrador,
            remitente=request.user,
            titulo=data.get('titulo'),  # Puedes ajustar esto según sea necesario
        )
        # Asociar los mensajes a la entrega
        entrega.mensajes.set(mensajes)
        entrega.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'No hay mensajes para entregar.'})





def logout_request(request):
    logout(request)
    # Puedes añadir aquí cualquier lógica adicional que necesites.
    return redirect('login')

def get_available_modules(request):
    query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'nombre')
    direction = request.GET.get('direction', 'asc')
    status = request.GET.get('status', 'both')

    modulos_list = Modulo.objects.filter(activo=True)

    if query:
        modulos_list = modulos_list.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    if direction == 'desc':
        order_by = f'-{order_by}'

    modulos_list = modulos_list.order_by(order_by)
    
    paginator = Paginator(modulos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'modulos_modal_list.html', {
        'page_obj': page_obj,
        'query': query,
        'order_by': order_by,
        'direction': direction,
        'status': status
    })
    
@login_required
def get_module_info(request, module_id):
    modulo = get_object_or_404(Modulo, pk=module_id)
    data = {
        'info': {
            'nombre': modulo.nombre,
            'descripcion': modulo.descripcion,
            'codigo_maude': modulo.codigo_maude,
            # Agrega cualquier otra información relevante del módulo aquí
        }
    }
    return JsonResponse(data)

@login_required
@require_http_methods(["POST"])
def update_message_status(request):
    try:
        data = json.loads(request.body)
        mensaje_id = data.get('mensaje_id')
        nuevo_estado = data.get('estado')

        mensaje = Mensaje.objects.get(id=mensaje_id, chat__usuario=request.user)

        if mensaje and nuevo_estado in Mensaje.EstadoChoices.values:
            mensaje.estado = nuevo_estado
            mensaje.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Estado o mensaje no válido'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def create_version(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        titulo = data.get('titulo')
        codigo = data.get('codigo')

        chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
        
        # Crear y guardar la nueva versión del módulo
        nueva_version = ModuloVersion(chat=chat, titulo=titulo, codigo=codigo)
        nueva_version.save()

        # Actualizar el chat con el nuevo título y código del módulo
        chat.titulo_modulo = titulo
        chat.modulo = codigo
        chat.save()
        
        return JsonResponse({'status': 'success', 'version_id': nueva_version.id})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_versions(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    versiones = chat.versiones.all().values('id', 'titulo', 'fecha_creacion')
    return JsonResponse(list(versiones), safe=False)

@login_required
def select_version(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        version_id = data.get('version_id')
        version = get_object_or_404(ModuloVersion, id=version_id)
        
        chat = version.chat
        chat.modulo = version.codigo
        chat.titulo_modulo = version.titulo  # Actualizar el título del módulo
        chat.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def compare_versions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        version_id_1 = data.get('version_id_1')
        version_id_2 = data.get('version_id_2')

        version_1 = ModuloVersion.objects.get(id=version_id_1)
        version_2 = ModuloVersion.objects.get(id=version_id_2)

        diff = difflib.unified_diff(
            version_1.codigo.splitlines(),
            version_2.codigo.splitlines(),
            fromfile=f'{version_1.titulo} ({version_1.fecha_creacion})',
            tofile=f'{version_2.titulo} ({version_2.fecha_creacion})',
            lineterm=''
        )

        # Genera el HTML para el diff
        diff_html = []
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                diff_html.append(f'<div><strong>{line}</strong></div>')
            elif line.startswith('@'):
                diff_html.append(f'<div style="background-color: #f0f0f0;"><strong>{line}</strong></div>')
            elif line.startswith('-'):
                diff_html.append(f'<div style="background-color: #ffeef0; color: red;">{line}</div>')
            elif line.startswith('+'):
                diff_html.append(f'<div style="background-color: #e6ffed; color: green;">{line}</div>')
            else:
                diff_html.append(f'<div>{line}</div>')

        diff_html = '\n'.join(diff_html)

        return JsonResponse({'status': 'success', 'diff': diff_html})
    return JsonResponse({'status': 'error'}, status=400)

def verify_email(request, uidb64, token):
    try:
        # Decodificar el UID desde base64
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist) as e:
        return HttpResponse(f'Error decodificando UID: {str(e)}')  # Para depuración

    # Verificar que el usuario exista y el token sea válido
    if user is not None and default_token_generator.check_token(user, token):
        # Marcar el correo electrónico como verificado
        user.email_verificado = True
        user.save()
        
        # Redirigir a una página de confirmación o a la página de inicio de sesión
        return redirect('login')
    else:
        return HttpResponse('Enlace de verificación inválido o caducado.')

def enviar_email_verificacion(request, user):
    # Codificar el ID del usuario
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Crear un token seguro
    token = default_token_generator.make_token(user)

    # Construir el enlace de verificación de correo electrónico
    link = request.build_absolute_uri(
        reverse('email_verify', kwargs={'uidb64': uid, 'token': token})
    )

    # Mensaje de correo
    subject = 'Verifica tu correo electrónico'
    message = f'Por favor, usa este enlace para verificar tu cuenta: {link}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    # Enviar el correo
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
            enviar_email_verificacion(request, user)
            return redirect('login')  # Redireccionar a la página que desees después del registro
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def marketModulos(request):
    query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'nombre')  # Valor predeterminado 'nombre'
    direction = request.GET.get('direction', 'asc')
    status = request.GET.get('status', 'both')

    modulos_list = Modulo.objects.all()

    if query:
        modulos_list = modulos_list.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    if status == 'active':
        modulos_list = modulos_list.filter(activo=True)
    elif status == 'inactive':
        modulos_list = modulos_list.filter(activo=False)

    if direction == 'desc':
        order_by = f'-{order_by}'

    modulos_list = modulos_list.order_by(order_by)
    
    paginator = Paginator(modulos_list, 10)  # Mostrar 10 módulos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'modulos_list.html', {'page_obj': page_obj, 'query': query, 'order_by': order_by, 'direction': direction, 'status': status})

    return render(request, 'marketModulos.html', {
        'page_obj': page_obj,
        'query': query,
        'order_by': order_by,
        'direction': direction,
        'status': status
    })


@login_required
def toggle_modulo(request, modulo_nombre):
    if request.method == 'POST':
        modulo = get_object_or_404(Modulo, nombre=modulo_nombre)
        modulo.activo = not modulo.activo
        modulo.save()
        return JsonResponse({'success': True, 'activo': modulo.activo})
    return JsonResponse({'success': False}, status=400)

@login_required
def update_modulo(request, modulo_nombre):
    if request.method == 'POST':
        modulo = get_object_or_404(Modulo, nombre=modulo_nombre)
        nuevo_codigo = request.POST.get('codigo_maude', '')
        modulo.codigo_maude = nuevo_codigo
        modulo.save()
        return JsonResponse({'success': True, 'codigo_maude': modulo.codigo_maude})
    return JsonResponse({'success': False}, status=400)

@login_required
def create_modulo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        codigo_maude = request.POST.get('codigo_maude')
        imagen = request.FILES.get('imagen')

        if not nombre or not descripcion or not codigo_maude:
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})

        modulo = Modulo(
            nombre=nombre,
            descripcion=descripcion,
            codigo_maude=codigo_maude,
            imagen=imagen,
            creador=request.user
        )
        modulo.save()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)

@login_required
def entregas_usuario(request):
    # Obtener el usuario logueado
    usuario = request.user

    # Obtener los filtros del request GET
    search_query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'fecha')  # Usa 'fecha' aquí
    direction = request.GET.get('direction', 'desc')
    corregido = request.GET.get('corregido', 'both')
    page = request.GET.get('page', 1)  # Obtener el número de página desde la URL

    # Filtro base
    entregas = Entrega.objects.filter(remitente=usuario)

    # Aplicar filtro por nombre de la entrega
    if search_query:
        entregas = entregas.filter(titulo__icontains=search_query)

    # Aplicar filtro por estado corregido/pendiente
    if corregido == 'true':
        entregas = entregas.filter(corregido=True)
    elif corregido == 'false':
        entregas = entregas.filter(corregido=False)

    # Aplicar orden
    if direction == 'asc':
        entregas = entregas.order_by(order_by)
    else:
        entregas = entregas.order_by(f'-{order_by}')

    # Paginación
    paginator = Paginator(entregas, 9)  # 5 entregas por página (puedes ajustar el número)
    try:
        entregas_paginadas = paginator.page(page)
    except PageNotAnInteger:
        entregas_paginadas = paginator.page(1)
    except EmptyPage:
        entregas_paginadas = paginator.page(paginator.num_pages)

    # Convertir las entregas a un diccionario para pasar a JSON
    entregas_data = [{
        'id': entrega.id,
        'titulo': entrega.titulo,
        'fecha': entrega.fecha.strftime('%d/%m/%Y %H:%M'),  # Formatear fecha y hora
        'corregido': entrega.corregido,
        'nota': entrega.nota
    } for entrega in entregas_paginadas]

    response_data = {
        'entregas': entregas_data,
        'has_next': entregas_paginadas.has_next(),
        'has_previous': entregas_paginadas.has_previous(),
        'page': entregas_paginadas.number,
        'num_pages': paginator.num_pages
    }

    return JsonResponse(response_data)

@login_required
def entrega_detalles(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)

    entrega_data = {
        'id': entrega.id,
        'titulo': entrega.titulo,
        'fecha': entrega.fecha.strftime('%d/%m/%Y %H:%M'),  # Formatear fecha y hora
        'corregido': entrega.corregido,
        'nota': entrega.nota if entrega.corregido else None,
        'administrador': entrega.administrador.nombre,
        'mensajes': [{
            'comando': mensaje.comando,
            'respuesta': mensaje.respuesta,
            'codigo_maude': mensaje.chat.modulo
        } for mensaje in entrega.mensajes.all()]
    }

    return JsonResponse(entrega_data)

@login_required
def eliminar_entregas(request):
    if request.method == "POST":
        data = json.loads(request.body)
        ids = data.get('ids')
        entregas = Entrega.objects.filter(id__in=ids, remitente=request.user)
        entregas_deleted, _ = entregas.delete()
        
        if entregas_deleted > 0:
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'No se pudieron eliminar las entregas.'})
        
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def tareas(request):
    return render(request, 'tareas.html')


@login_required
def entregas_pendientes(request):
    # Asegurarse de que el usuario es un administrador
    if not request.user.is_admin:
        return JsonResponse({'error': 'No tienes permisos para ver esta página.'}, status=403)

    # Obtener los filtros del request GET
    search_query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'fecha')
    direction = request.GET.get('direction', 'desc')
    page = request.GET.get('page', 1)  # Obtener el número de página desde la URL

    # Filtro base para las entregas pendientes del administrador logueado
    entregas = Entrega.objects.filter(administrador=request.user, corregido=False)

    # Aplicar filtro por nombre de la entrega
    if search_query:
        entregas = entregas.filter(titulo__icontains=search_query)

    # Aplicar orden
    if direction == 'asc':
        entregas = entregas.order_by(order_by)
    else:
        entregas = entregas.order_by(f'-{order_by}')

    # Paginación
    paginator = Paginator(entregas, 5)  # 5 entregas por página (puedes ajustar el número)
    try:
        entregas_paginadas = paginator.page(page)
    except PageNotAnInteger:
        entregas_paginadas = paginator.page(1)
    except EmptyPage:
        entregas_paginadas = paginator.page(paginator.num_pages)

    # Convertir las entregas a un diccionario para pasar a JSON
    entregas_data = [{
        'id': entrega.id,
        'titulo': entrega.titulo,
        'fecha': entrega.fecha.strftime('%d/%m/%Y %H:%M'),  # Formatear fecha y hora
        'remitente': entrega.remitente.nombre,
    } for entrega in entregas_paginadas]

    response_data = {
        'entregas': entregas_data,
        'has_next': entregas_paginadas.has_next(),
        'has_previous': entregas_paginadas.has_previous(),
        'page': entregas_paginadas.number,
        'num_pages': paginator.num_pages
    }

    return JsonResponse(response_data)

@login_required
def corregir_entrega(request, entrega_id):
    if request.method == "POST":
        entrega = get_object_or_404(Entrega, id=entrega_id, administrador=request.user)
        
        # Cargar datos JSON desde el cuerpo de la solicitud
        try:
            data = json.loads(request.body)
            nota = data.get('nota', '')  # Obtener la nota desde los datos JSON
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)

        entrega.corregido = True
        entrega.nota = nota
        entrega.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def vista_entregas_pendientes(request):
    return render(request, 'entregas_pendientes.html')

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
                    soluciones += f"{solucion}<br>"  

            return soluciones if soluciones else "No hay soluciones"        
            
        try:
            if comando in ["reduce", "red"]:
                resultado = reduce()
            elif comando in ["rew", "rewrite"]:
                resultado = rewrite()
            elif comando in ["search"]:
                resultado = search()
            elif comando in ["frewrite", "frew"]:
                resultado = frewrite()
            else:
                resultado = "[Error]: Comando no reconocido"
            # Añadir más condiciones según sea necesario
        except Exception as e:
            resultado = f"[Error]: {e}"
            
        response = str(resultado)
        chat.modulo = user_code
        chat.save()
        mensaje = Mensaje.objects.create(chat=chat, comando=maude_execution, respuesta=response, titulo_modulo=chat.titulo_modulo)
        print("id mensaje " + str(mensaje.id))
        # Devolver la respuesta como JSON
        return JsonResponse({'comando': maude_execution, 'respuesta': response, 'titulo_modulo': chat.titulo_modulo, 'mensaje_id': mensaje.id})
    else:
        # Manejar solicitudes no AJAX si es necesario
        return JsonResponse({'error': 'Solicitud incorrecta'}, status=400)
