import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model

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
    usuario = models.ForeignKey('Proyecto1.Usuario', on_delete=models.CASCADE, related_name='chats')

class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, related_name='mensajes', on_delete=models.CASCADE)
    comando = models.TextField()
    respuesta = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
