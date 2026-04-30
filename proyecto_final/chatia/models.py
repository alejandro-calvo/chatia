from django.db import models
# models permite definir tablas de base de datos en Django

from django.contrib.auth.models import User
# Importamos el modelo User de Django para asociar usuarios a nuestras tablas


class Conversation(models.Model):
    """
    Modelo que representa una conversación o chat.
    Cada conversación pertenece a un usuario.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    """
    Modelo que representa un mensaje dentro de una conversación.
    Puede ser del usuario o de la IA.
    """

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    sender = models.CharField(max_length=10)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:30]}"


class UserProfile(models.Model):
    """
    Modelo para guardar configuración extra del usuario.
    Va unido uno a uno con el User de Django.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    alias = models.CharField(max_length=50, blank=True)

    preferred_model = models.CharField(max_length=50, default='gemma')

    temperature = models.DecimalField(max_digits=2, decimal_places=1, default=0.7)

    def __str__(self):
        return self.user.username