import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

# Crea un nuevo UserManager para tu modelo de usuario personalizado
class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None):
        if not email:
            raise ValueError('El usuario debe tener un correo UCM')
        if not nombre:
            raise ValueError('El usuario debe tener un nombre')

        user = self.model(
            email=self.normalize_email(email),
            nombre=nombre,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None):
        user = self.create_user(
            email,
            password=password,
            nombre=nombre,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Modelo de Usuario
class Usuario(AbstractBaseUser):
    nombre = models.CharField(max_length=50)
    email = models.EmailField(verbose_name='correo UCM', max_length=255, unique=True)
    email_verificado = models.BooleanField(default=False)
    codigo_verificacion = models.UUIDField(default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email

    # Para determinar los permisos. to consider.
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin



class Chat(models.Model):
    nombre = models.CharField(max_length=100)
    modulo = models.TextField(default='')
    titulo_modulo = models.CharField(max_length=255, default='Sin título')  # Nuevo campo
    usuario = models.ForeignKey('Proyecto1.Usuario', on_delete=models.CASCADE, related_name='chats')

class Mensaje(models.Model):
    class EstadoChoices(models.TextChoices):
        NINGUNO = 'ninguno', 'Ninguno'
        BIEN = 'bien', 'Bien'
        MAL = 'mal', 'Mal'

    chat = models.ForeignKey(Chat, related_name='mensajes', on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    comando = models.TextField()
    respuesta = models.TextField()
    titulo_modulo = models.CharField(max_length=255,default="Desconocido")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=7,
        choices=EstadoChoices.choices,
        default=EstadoChoices.NINGUNO
    )

    

class Modulo(models.Model):
    nombre = models.CharField(max_length=255, unique=True, verbose_name="Nombre del Módulo")
    descripcion = models.TextField(verbose_name="Descripción")
    codigo_maude = models.TextField(verbose_name="Código Maude")
    imagen = models.ImageField(upload_to="modulos_maude", verbose_name="Imagen del Módulo", blank=True, null=True)
    creador = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="modulos_creados", verbose_name="Usuario Creador")
    activo = models.BooleanField(default=False, verbose_name="Activo para No Administradores")
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")

    def __str__(self):
        return f"{self.nombre} - Creado por {self.creador.email}"

    def save(self, *args, **kwargs):
        # Borrar la imagen anterior si se está actualizando con una nueva
        try:
            old_instance = Modulo.objects.get(pk=self.pk)
            if old_instance.imagen and old_instance.imagen != self.imagen:
                if os.path.isfile(old_instance.imagen.path):
                    os.remove(old_instance.imagen.path)
        except Modulo.DoesNotExist:
            pass  # No hay imagen anterior que borrar

        super().save(*args, **kwargs)

# Señal para borrar la imagen del sistema de archivos cuando se elimina el objeto
@receiver(post_delete, sender=Modulo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Borra el archivo asociado cuando se elimina un objeto `Modulo`.
    """
    if instance.imagen and os.path.isfile(instance.imagen.path):
        os.remove(instance.imagen.path)
    
class ModuloVersion(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='versiones')
    titulo = models.CharField(max_length=100)
    codigo = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.fecha_creacion}"

class Entrega(models.Model):
    administrador = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'is_admin': True})
    mensajes = models.ManyToManyField(Mensaje)  # Cambiamos a ManyToManyField para relacionar varios mensajes
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=255, verbose_name="Título de la Entrega", default="Nombre título default")
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='entregas_enviadas', default=0)
    corregido = models.BooleanField(default=False)
    nota = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Entrega: {self.titulo} por {self.remitente.nombre} para {self.administrador.nombre} el {self.fecha}"



