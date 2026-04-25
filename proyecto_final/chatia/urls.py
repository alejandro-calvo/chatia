from django.urls import path
from . import views

urlpatterns = [
    # name sirve para darle un nombre a la URL y poder usarla luego
    # en plantillas o redirecciones, por ejemplo con {% url 'index' %}
    path('', views.index, name='index'),
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversations/new/', views.new_conversation, name='new_conversation'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_view, name='help'),
]