from django.urls import path
# path sirve para definir las rutas de la aplicación

from . import views
# Importamos las vistas de nuestra app


urlpatterns = [
    # Página principal
    path('', views.index, name='index'),

    # Conversaciones
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/new/', views.new_conversation, name='new_conversation'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('conversations/<int:conversation_id>/json/', views.conversation_json, name='conversation_json'),

    # Borrar conversación
    path('conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),

    # Renombrar conversación
    path('conversations/<int:conversation_id>/rename/', views.rename_conversation, name='rename_conversation'),

    # Perfil, configuración y ayuda
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
]