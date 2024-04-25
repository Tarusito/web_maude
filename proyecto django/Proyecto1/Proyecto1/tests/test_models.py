# tests.py en tu aplicación Django
from django.test import TestCase, Client
from ..models import Usuario, Chat, Mensaje
from django.urls import reverse
from django.contrib.auth import get_user_model
import json


class UsuarioModelTest(TestCase):
    def test_create_usuario(self):
        # Prueba la creación de un objeto Usuario
        usuario = Usuario.objects.create_user(email='test@ucm.es', nombre='Test User', password='Testpass123')
        self.assertEqual(usuario.email, 'test@ucm.es')
        self.assertEqual(usuario.nombre, 'Test User')
        self.assertTrue(usuario.check_password('Testpass123'))
        self.assertFalse(usuario.email_verificado)  # Verificar que el email no está verificado inicialmente

    def test_create_super_usuario(self):
        # Prueba la creación de un superusuario
        superuser = Usuario.objects.create_superuser(email='admin@ucm.es', nombre='Admin User', password='Adminpass123')
        self.assertEqual(superuser.email, 'admin@ucm.es')
        self.assertTrue(superuser.is_admin)
        self.assertTrue(superuser.is_staff)  # is_staff debe ser True para los superusuarios

class ChatModelTest(TestCase):
    def setUp(self):
        # Crear un usuario para asociar con el chat
        self.usuario = Usuario.objects.create_user(email='user@ucm.es', nombre='User', password='Userpass123')

    def test_create_chat(self):
        # Prueba la creación de un objeto Chat
        chat = Chat.objects.create(nombre='Prueba Chat', usuario=self.usuario, modulo='Módulo inicial')
        self.assertEqual(chat.nombre, 'Prueba Chat')
        self.assertEqual(chat.usuario, self.usuario)
        self.assertEqual(chat.modulo, 'Módulo inicial')

class MensajeModelTest(TestCase):
    def setUp(self):
        # Crear un usuario y un chat para asociar con el mensaje
        self.usuario = Usuario.objects.create_user(email='user2@ucm.es', nombre='User2', password='Userpass456')
        self.chat = Chat.objects.create(nombre='Chat de Pruebas', usuario=self.usuario, modulo='Módulo de prueba')

    def test_create_mensaje(self):
        # Prueba la creación de un objeto Mensaje
        mensaje = Mensaje.objects.create(chat=self.chat, comando='Comando Test', respuesta='Respuesta Test')
        self.assertEqual(mensaje.chat, self.chat)
        self.assertEqual(mensaje.comando, 'Comando Test')
        self.assertEqual(mensaje.respuesta, 'Respuesta Test')
        self.assertTrue(mensaje.fecha_creacion)  # Asegurarse de que la fecha de creación es asignada

