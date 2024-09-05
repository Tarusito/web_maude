import json
from django.test import TestCase
from django.urls import reverse
from ..models import Usuario, Chat, Mensaje
from django.contrib.auth import get_user_model

class MaudeIntegrationTest(TestCase):
    def setUp(self):
        # Crear un usuario
        self.user = get_user_model().objects.create_user(email='user@example.com', password='Password123', nombre='Test User')
        self.client.login(email='user@example.com', password='Password123')

        # Crear un chat
        self.chat = Chat.objects.create(nombre="Test Chat", usuario=self.user, modulo="")

    def test_user_chat_maude_interaction(self):
        # URL para enviar comandos a Maude
        url = reverse('run_maude_command', kwargs={'chat_id': self.chat.id})
        
        # Datos del comando Maude
        maude_command = 'search [1] initial =>* vasija(N:Nat, 4) B:ConjVasija'
        maude_code_formatted = """
            mod DIE-HARD is
            protecting NAT .
            sorts Vasija ConjVasija .
            subsort Vasija < ConjVasija .
            op vasija : Nat Nat -> Vasija [ctor] .

            *** Capacidad / Contenido actual
            op __ : ConjVasija ConjVasija -> ConjVasija [ctor assoc comm] .
            vars M1 N1 M2 N2 : Nat .

            op initial : -> ConjVasija .
            eq initial = vasija(3, 0) vasija(5, 0) vasija(8,0) .

            rl [vacia] : vasija(M1, N1) => vasija(M1, 0) .
            rl [llena] : vasija(M1, N1) => vasija(M1, M1) .

            crl [transfer1] : vasija(M1, N1) vasija(M2, N2) => vasija(M1, 0) vasija(M2, N1 + N2) if N1 + N2 <= M2 .
            crl [transfer2] : vasija(M1, N1) vasija(M2, N2) => vasija(M1, sd(N1 + N2, M2)) vasija(M2, M2) if N1 + N2 > M2 .
            endm
            """

        data = {
            'maude_execution': 'search [1] initial =>* vasija(N:Nat, 4) B:ConjVasija',
            'maude_code': maude_code_formatted
        }
        headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        
        # Simular el envío del comando a Maude
        response = self.client.post(url, data, **headers)
        
        # Verificar que se obtiene una respuesta correcta
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la respuesta de Maude es la esperada
        response_data = json.loads(response.content.decode('utf-8'))
        expected_response = "B:ConjVasija=vasija(3, 3) vasija(8, 3), N:Nat=5<br>"  # Asumiendo que Maude devuelve esto como resultado
        self.assertEqual(response_data.get('respuesta'), expected_response)
        
        # Verificar que el mensaje se guardó correctamente
        mensaje = Mensaje.objects.last()
        self.assertEqual(mensaje.comando, maude_command)
        self.assertEqual(mensaje.respuesta, expected_response)

        # Verificar que el chat contiene el mensaje
        self.assertIn(mensaje, self.chat.mensajes.all())
