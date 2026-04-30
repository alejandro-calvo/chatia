from django.urls import path
# path permite definir rutas de la aplicación

from . import views
# Importamos las vistas del archivo views.py


urlpatterns = [
    # Página principal
    path('', views.index, name='index'),

    # Lista de conversaciones del usuario
    path('conversations/', views.conversation_list, name='conversation_list'),

    # Crear una nueva conversación
    path('conversations/new/', views.new_conversation, name='new_conversation'),

    # Ver una conversación concreta
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),

    # Enviar mensaje dentro de una conversación
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),

    # Ver una conversación en formato JSON
    path('conversations/<int:conversation_id>/json/', views.conversation_json, name='conversation_json'),

    # Perfil del usuario
    path('profile/', views.profile, name='profile'),

    # Configuración del usuario
    path('settings/', views.settings_view, name='settings'),

    # Página de ayuda
    path('help/', views.help_view, name='help'),
]