from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Conversation, Message, UserProfile


class ChatIAEndToEndTests(TestCase):
    """
    Tests de extremo a extremo básicos de la aplicación ChatIA.

    La idea es probar los recursos principales de la práctica
    como si un usuario estuviera usando la aplicación desde el navegador.
    """

    def setUp(self):
        """
        Preparamos datos de prueba antes de cada test.
        """

        # Creamos un usuario de prueba
        self.user = User.objects.create_user(
            username='alex',
            password='1234'
        )

        # Creamos el perfil del usuario
        self.profile = UserProfile.objects.create(
            user=self.user,
            alias='Alejandro',
            preferred_model='gemma',
            temperature=0.7,
            user_message_background='user-bg-orange',
            ai_message_background='ai-bg-yellow',
            user_message_text_color='user-text-black',
            user_message_font='user-font-arial'
        )

        # Creamos una conversación de prueba
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Chat de prueba'
        )

        # Creamos dos mensajes de prueba
        Message.objects.create(
            conversation=self.conversation,
            sender='usuario',
            content='Hola'
        )

        Message.objects.create(
            conversation=self.conversation,
            sender='ia',
            content='Hola, soy ChatIA'
        )

    def test_pagina_principal(self):
        """
        La página principal se puede ver sin iniciar sesión.
        """

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ChatIA')

    def test_lista_chats_redirige_si_no_hay_login(self):
        """
        Si no hay usuario autenticado, la lista de chats redirige al login.
        """

        response = self.client.get(reverse('conversation_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_lista_conversaciones(self):
        """
        Un usuario autenticado puede ver su lista de conversaciones.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(reverse('conversation_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chat de prueba')

    def test_crear_conversacion(self):
        """
        Un usuario autenticado puede crear una conversación nueva.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('new_conversation'),
            {
                'title': 'Nueva conversación'
            }
        )

        self.assertEqual(response.status_code, 302)

        existe = Conversation.objects.filter(
            user=self.user,
            title='Nueva conversación'
        ).exists()

        self.assertTrue(existe)

    def test_ver_conversacion(self):
        """
        Un usuario puede entrar en una conversación y ver sus mensajes.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(
            reverse('conversation_detail', args=[self.conversation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chat de prueba')
        self.assertContains(response, 'Hola')
        self.assertContains(response, 'Hola, soy ChatIA')

    @patch('chatia.views.obtener_respuesta_ia')
    def test_enviar_mensaje(self, mock_ia):
        """
        Un usuario puede enviar un mensaje al chat.

        Se simula la respuesta de la IA para no depender de la API externa
        durante el test.
        """

        mock_ia.return_value = 'Respuesta de prueba de ChatIA'

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('send_message', args=[self.conversation.id]),
            {
                'content': 'Mensaje nuevo'
            }
        )

        self.assertEqual(response.status_code, 200)

        existe_mensaje_usuario = Message.objects.filter(
            conversation=self.conversation,
            sender='usuario',
            content='Mensaje nuevo'
        ).exists()

        existe_mensaje_ia = Message.objects.filter(
            conversation=self.conversation,
            sender='ia',
            content='Respuesta de prueba de ChatIA'
        ).exists()

        self.assertTrue(existe_mensaje_usuario)
        self.assertTrue(existe_mensaje_ia)

    def test_borrar_conversacion(self):
        """
        Un usuario puede borrar una conversación propia.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('delete_conversation', args=[self.conversation.id])
        )

        self.assertEqual(response.status_code, 302)

        existe = Conversation.objects.filter(
            id=self.conversation.id
        ).exists()

        self.assertFalse(existe)

    def test_renombrar_conversacion(self):
        """
        Un usuario puede cambiar el título de una conversación propia.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('rename_conversation', args=[self.conversation.id]),
            {
                'title': 'Título cambiado'
            }
        )

        self.assertEqual(response.status_code, 302)

        self.conversation.refresh_from_db()

        self.assertEqual(self.conversation.title, 'Título cambiado')

    def test_perfil(self):
        """
        Un usuario autenticado puede ver su perfil.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alejandro')

    def test_configuracion(self):
        """
        Un usuario puede cambiar su configuración.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('settings'),
            {
                'alias': 'Alex cambiado',
                'preferred_model': 'gemma',
                'temperature': '0.5',
                'user_message_background': 'user-bg-green',
                'ai_message_background': 'ai-bg-light-red',
                'user_message_text_color': 'user-text-red',
                'user_message_font': 'user-font-courier',
            }
        )

        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()

        self.assertEqual(self.profile.alias, 'Alex cambiado')
        self.assertEqual(str(self.profile.temperature), '0.5')
        self.assertEqual(self.profile.user_message_background, 'user-bg-green')
        self.assertEqual(self.profile.ai_message_background, 'ai-bg-light-red')
        self.assertEqual(self.profile.user_message_text_color, 'user-text-red')
        self.assertEqual(self.profile.user_message_font, 'user-font-courier')

    def test_ayuda(self):
        """
        Un usuario autenticado puede ver la página de ayuda.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(reverse('help'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ayuda')

    def test_conversacion_json(self):
        """
        Un usuario puede ver una conversación en formato JSON.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(
            reverse('conversation_json', args=[self.conversation.id])
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data['id'], self.conversation.id)
        self.assertEqual(data['title'], 'Chat de prueba')
        self.assertEqual(len(data['messages']), 2)