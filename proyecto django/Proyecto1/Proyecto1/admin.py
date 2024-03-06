from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario

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

admin.site.register(Usuario, UsuarioAdmin)
