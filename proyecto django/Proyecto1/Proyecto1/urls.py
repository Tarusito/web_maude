"""
URL configuration for Proyecto1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from Proyecto1 import views  # Importa la vista 'home' desde 'Proyecto1.views'
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),  # Usa 'home' directamente como vistaç
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('verificar/<uidb64>/<token>/', views.verify_email, name='email_verify'),
    path('run_maude_command/', views.run_maude_command, name='run_maude_command'),
    path('logout/', views.logout_request, name='logout'),
    path('new_chat/', views.new_chat, name='new_chat'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat'),
    path('run_maude_command/<int:chat_id>/', views.run_maude_command, name='run_maude_command'),
    path('get_chat_content/<int:chat_id>/', views.get_chat_content, name='get_chat_content'),
    path('saveModule/<int:chat_id>/', views.saveModule, name='saveModule'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_recover/', views.password_reset_request, name='password_recover'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('ruta-para-eliminar-chats/', views.delete_chats, name='delete_chats'),
    path('marketModulos/', views.marketModulos, name='market_modulos'),
    path('toggle_modulo/<str:modulo_nombre>/', views.toggle_modulo, name='toggle_modulo'),
    path('update_modulo/<str:modulo_nombre>/', views.update_modulo, name='update_modulo'),
    path('create_modulo/', views.create_modulo, name='create_modulo'),
    path('get_available_modules/', views.get_available_modules, name='get_available_modules'),
    path('create_version/', views.create_version, name='create_version'),
    path('get_versions/<int:chat_id>/', views.get_versions, name='get_versions'),
    path('select_version/', views.select_version, name='select_version'),
    path('compare_versions/', views.compare_versions, name='compare_versions'),
    path('get_module_info/<int:module_id>/', views.get_module_info, name='get_module_info'),
    path('update_message_status/', views.update_message_status, name='update_message_status'),
    path('get_mensajes_bien/<int:chat_id>/', views.get_mensajes_bien, name='get_mensajes_bien'),
    path('enviar_mensajes_bien/<int:chat_id>/', views.enviar_mensajes_bien, name='enviar_mensajes_bien'),
    path('tareas/', views.tareas, name='tareas'),
    path('entregas_usuario/', views.entregas_usuario, name='entregas_usuario'),
    path('entrega_detalles/<int:entrega_id>/', views.entrega_detalles, name='entrega_detalles'),
    path('entregas_pendientes/', views.vista_entregas_pendientes, name='entregas_pendientes'),
    path('entregas_pendientes_data/', views.entregas_pendientes, name='entregas_pendientes_data'),
    path('corregir_entrega/<int:entrega_id>/', views.corregir_entrega, name='corregir_entrega'),
    path('eliminar_entregas/', views.eliminar_entregas, name='eliminar_entregas'),
    path('historial_entregas_corregidas/', views.historial_entregas_corregidas, name='historial_entregas_corregidas'),
    path('entregas_corregidas_data/', views.entregas_corregidas_data, name='entregas_corregidas_data'),
    path('delete_modulos/', views.delete_modulos, name='delete_modulos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

