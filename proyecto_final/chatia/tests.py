from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import Conversation, Message, UserProfile


class ChatIAEndToEndTests(TestCase):
    """
    Tests de extremo a extremo de la aplicación.

    La idea es probar las partes principales como si un usuario
    estuviera usando la web desde el navegador.
    """

    def setUp(self):
        """
        Preparamos datos de prueba antes de cada test.
        """

        # Creamos un usuario normal
        self.user = User.objects.create_user(
            username='alex',
            password='1234'
        )

        # Creamos otro usuario para comprobar que no se mezclan sus chats
        self.other_user = User.objects.create_user(
            username='otro',
            password='1234'
        )

        # Creamos el perfil del usuario principal
        self.profile = UserProfile.objects.create(
            user=self.user,
            alias='Alejandro',
            preferred_model='gemma',
            temperature=0.7
        )

        # Creamos el perfil del otro usuario
        UserProfile.objects.create(
            user=self.other_user,
            alias='Otro usuario',
            preferred_model='gemma',
            temperature=0.7
        )

        # Creamos una conversación para alex
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Chat de prueba'
        )

        # Creamos mensajes dentro de esa conversación
        Message.objects.create(
            conversation=self.conversation,
            sender='usuario',
            content='Hola'
        )

        Message.objects.create(
            conversation=self.conversation,
            sender='ia',
            content='Hola, soy la IA'
        )

        # Creamos una conversación de otro usuario
        self.other_conversation = Conversation.objects.create(
            user=self.other_user,
            title='Chat privado de otro usuario'
        )

    def test_pagina_principal_es_publica(self):
        """
        La página principal se puede ver sin iniciar sesión.
        """

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ChatIA')

    def test_lista_chats_necesita_login(self):
        """
        Si no hay sesión iniciada, la lista de chats redirige al login.
        """

        response = self.client.get(reverse('conversation_list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_login_y_lista_de_chats(self):
        """
        Un usuario puede iniciar sesión y ver su lista de chats.
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

    def test_ver_detalle_de_conversacion(self):
        """
        El usuario puede entrar en una conversación suya y ver sus mensajes.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(
            reverse('conversation_detail', args=[self.conversation.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chat de prueba')
        self.assertContains(response, 'Hola')
        self.assertContains(response, 'Hola, soy la IA')

    def test_no_puedo_ver_chat_de_otro_usuario(self):
        """
        Test extra de seguridad.

        Un usuario no puede entrar en conversaciones que pertenecen a otro usuario.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(
            reverse('conversation_detail', args=[self.other_conversation.id])
        )

        self.assertEqual(response.status_code, 404)

    @patch('chatia.views.obtener_respuesta_ia')
    def test_enviar_mensaje_al_chat(self, mock_ia):
        """
        El usuario puede enviar un mensaje al chat.

        Mockeamos la llamada a la IA para no depender de la API externa
        durante los tests.
        """

        mock_ia.return_value = 'Respuesta de prueba de la IA'

        self.client.login(username='alex', password='1234')

        response = self.client.post(
            reverse('send_message', args=[self.conversation.id]),
            {
                'content': 'Mensaje nuevo'
            }
        )

        self.assertEqual(response.status_code, 200)

        mensaje_usuario = Message.objects.filter(
            conversation=self.conversation,
            sender='usuario',
            content='Mensaje nuevo'
        ).exists()

        mensaje_ia = Message.objects.filter(
            conversation=self.conversation,
            sender='ia',
            content='Respuesta de prueba de la IA'
        ).exists()

        self.assertTrue(mensaje_usuario)
        self.assertTrue(mensaje_ia)

    def test_borrar_conversacion(self):
        """
        El usuario puede borrar una conversación propia.
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
        El usuario puede cambiar el título de una conversación propia.
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

    def test_pagina_perfil(self):
        """
        El usuario autenticado puede ver su perfil.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alejandro')
        self.assertContains(response, 'gemma')

    def test_configuracion_usuario(self):
        """
        El usuario puede cambiar su configuración.
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
        self.assertEqual(self.profile.preferred_model, 'gemma')
        self.assertEqual(str(self.profile.temperature), '0.5')
        self.assertEqual(self.profile.user_message_background, 'user-bg-green')
        self.assertEqual(self.profile.ai_message_background, 'ai-bg-light-red')
        self.assertEqual(self.profile.user_message_text_color, 'user-text-red')
        self.assertEqual(self.profile.user_message_font, 'user-font-courier')

    def test_pagina_ayuda(self):
        """
        El usuario autenticado puede ver la página de ayuda.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(reverse('help'))

        self.assertEqual(response.status_code, 200)

    def test_conversacion_json(self):
        """
        El usuario puede ver una conversación suya en formato JSON.
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

    def test_json_de_otro_usuario_no_se_puede_ver(self):
        """
        Test extra de seguridad.

        Un usuario no puede ver en JSON una conversación de otro usuario.
        """

        self.client.login(username='alex', password='1234')

        response = self.client.get(
            reverse('conversation_json', args=[self.other_conversation.id])
        )

        self.assertEqual(response.status_code, 404)