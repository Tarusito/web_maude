import json
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Usuario, Chat, Mensaje
from django.contrib.auth import get_user_model

class ViewAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.login_url = reverse('login')
        self.user = get_user_model().objects.create_user(email='test@example.com', nombre='Test User', password='Testpassword123')

    def test_home_not_logged_in(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.home_url}')

    def test_home_logged_in(self):
        self.client.login(email='test@example.com', password='Testpassword123')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

class MaudeCommandTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.run_maude_command_url = reverse('run_maude_command', kwargs={'chat_id': 1})
        self.user = get_user_model().objects.create_user(email='test@example.com', nombre='Test User', password='Testpassword123')
        self.client.login(email='test@example.com', password='Testpassword123')
        self.chat = Chat.objects.create(nombre="Test Chat", usuario=self.user, modulo="")

    def test_maude_command_execution(self):
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
        response = self.client.post(self.run_maude_command_url, data, **headers)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('respuesta', response_data)
        self.assertEqual(response_data['respuesta'], 'B:ConjVasija=vasija(3, 3) vasija(8, 3), N:Nat=5<br>')

