from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Chat, Mensaje, Usuario, Modulo

class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = ('email', 'nombre', 'email_verificado', 'is_active', 'is_admin')
    list_filter = ('is_active', 'is_admin', 'email_verificado')
    fieldsets = (
        (None, {'fields': ('email', 'nombre', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
        ('Status', {'fields': ('email_verificado',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'is_active', 'is_admin', 'email_verificado')}
        ),
    )
    search_fields = ('email', 'nombre')
    ordering = ('email', 'nombre')
    filter_horizontal = ()  # Mantén esto vacío si tu modelo no usa 'groups' ni 'user_permissions'

class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'usuario']  # Agrega 'id' para mostrar el ID del chat
    search_fields = ['nombre', 'usuario__email']
    list_filter = ['usuario']

admin.site.register(Chat, ChatAdmin)

class MensajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat', 'comando', 'fecha_creacion']  # Agrega 'id' para mostrar el ID del mensaje
    search_fields = ['chat__nombre', 'comando']
    list_filter = ['chat', 'fecha_creacion']
    date_hierarchy = 'fecha_creacion'

admin.site.register(Mensaje, MensajeAdmin)

admin.site.register(Usuario, UsuarioAdmin)

class ModuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'codigo_maude', 'creador', 'activo')  # Agrega 'id' para mostrar el ID del módulo
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion', 'codigo_maude')  # Habilita la búsqueda en estos campos

admin.site.register(Modulo, ModuloAdmin)
