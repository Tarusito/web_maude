from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Chat, Mensaje, Usuario

class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = ('email', 'nombre', 'email_verificado', 'is_active', 'is_admin')  # Asegúrate de incluir todos los campos deseados aquí
    list_filter = ('is_active', 'is_admin', 'email_verificado')  # Y aquí
    fieldsets = (
        (None, {'fields': ('email', 'nombre', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),  # Asegúrate de que todos los campos necesarios estén aquí, excepto los no editables
        ('Status', {'fields': ('email_verificado',)}),  # Puedes incluir campos adicionales aquí
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'is_active', 'is_admin', 'email_verificado')}  # Y aquí
        ),
    )
    search_fields = ('email', 'nombre')
    ordering = ('email', 'nombre')
    filter_horizontal = ()  # Mantén esto vacío si tu modelo no usa 'groups' ni 'user_permissions'

class ChatAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario']  # Puedes ajustar esta lista para mostrar los campos deseados
    search_fields = ['nombre', 'usuario__email']  # Permite buscar por nombre de chat y email del usuario
    list_filter = ['usuario']  # Permite filtrar por usuario

admin.site.register(Chat, ChatAdmin)

class MensajeAdmin(admin.ModelAdmin):
    list_display = ['chat', 'comando', 'fecha_creacion']  # Ajusta a los campos que quieras mostrar
    search_fields = ['chat__nombre', 'comando']  # Buscar por nombre del chat y comando
    list_filter = ['chat', 'fecha_creacion']  # Filtrar por chat y fecha de creación
    date_hierarchy = 'fecha_creacion'  # Permite navegar rápidamente a través de las fechas

admin.site.register(Mensaje, MensajeAdmin)


admin.site.register(Usuario, UsuarioAdmin)
