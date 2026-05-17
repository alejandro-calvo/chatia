from django.shortcuts import render, get_object_or_404, redirect
# render devuelve plantillas HTML
# get_object_or_404 busca un objeto y si no existe devuelve 404
# redirect redirige a otra vista

from django.contrib.auth.decorators import login_required
# login_required protege vistas para que solo entren usuarios autenticados

from django.http import JsonResponse
# JsonResponse sirve para devolver datos en formato JSON

from django.views.decorators.cache import never_cache
# never_cache evita que el navegador muestre versiones antiguas de algunas páginas

from .models import Conversation, Message, UserProfile
# Importamos nuestros modelos

from .llm import obtener_respuesta_ia
# Función que llama al modelo LLM


def datos_footer(request):
    """
    Calcula las métricas que aparecen en el pie de página.
    """

    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()

    if request.user.is_authenticated:
        user_conversations = Conversation.objects.filter(user=request.user).count()
        user_messages = Message.objects.filter(conversation__user=request.user).count()
    else:
        user_conversations = '-'
        user_messages = '-'

    contexto = {
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'user_conversations': user_conversations,
        'user_messages': user_messages,
    }

    return contexto


def index(request):
    """
    Página principal pública.
    """
    contexto = datos_footer(request)
    return render(request, 'index.html', contexto)

@login_required
@never_cache
def conversation_list(request):
    """
    Muestra las conversaciones del usuario autenticado.

    Las ordenamos de más reciente a más antigua para que cuando se cree
    una conversación nueva aparezca arriba en la lista.
    """

    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')

    contexto = datos_footer(request)
    contexto['conversations'] = conversations

    return render(request, 'conversation_list.html', contexto)


@login_required
def conversation_detail(request, conversation_id):
    """
    Muestra una conversación concreta y todos sus mensajes.
    """

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    messages = conversation.message_set.all().order_by('created_at')

    # Cargamos el perfil para aplicar la configuración visual del usuario en los mensajes
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    contexto = datos_footer(request)
    contexto['conversation'] = conversation
    contexto['messages'] = messages
    contexto['profile'] = profile

    return render(request, 'conversation_detail.html', contexto)


@login_required
def new_conversation(request):
    """
    Crea una conversación nueva.

    Después de crearla, redirige directamente al chat recién creado.
    """

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()

        # Si el usuario no pone título, ponemos uno automático
        if title == '':
            total_conversations = Conversation.objects.filter(user=request.user).count()
            title = f'Chat {total_conversations + 1}'

        conversation = Conversation.objects.create(
            user=request.user,
            title=title
        )

        # Redirigimos al chat recién creado
        return redirect('conversation_detail', conversation_id=conversation.id)

    return redirect('conversation_list')


@login_required
def delete_conversation(request, conversation_id):
    """
    Borra una conversación del usuario autenticado.

    Se hace con POST para evitar borrar una conversación simplemente
    entrando a una URL desde el navegador.
    """

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    if request.method == 'POST':
        conversation.delete()

    return redirect('conversation_list')


@login_required
def rename_conversation(request, conversation_id):
    """
    Cambia el título de una conversación del usuario autenticado.

    Se hace por POST porque el cambio viene desde un formulario.
    Además, se comprueba que la conversación pertenece al usuario actual.
    """

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    if request.method == 'POST':
        new_title = request.POST.get('title', '').strip()

        # Solo cambiamos el título si el usuario ha escrito algo
        if new_title:
            conversation.title = new_title
            conversation.save()

    return redirect('conversation_list')


@login_required
def send_message(request, conversation_id):
    """
    Guarda el mensaje del usuario, llama a la IA y guarda la respuesta.
    Esta vista devuelve solo el parcial de mensajes porque se usa con HTMX.
    """

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    # Cargamos el perfil antes de llamar a la IA.
    # Así podemos usar la temperatura configurada por el usuario.
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            # Guardamos el mensaje del usuario
            Message.objects.create(
                conversation=conversation,
                sender='usuario',
                content=content
            )

            # Obtenemos la respuesta de la IA usando la temperatura del perfil
            respuesta_ia = obtener_respuesta_ia(
                content,
                temperature=profile.temperature
            )

            # Guardamos la respuesta de la IA
            Message.objects.create(
                conversation=conversation,
                sender='ia',
                content=respuesta_ia
            )

    messages = conversation.message_set.all().order_by('created_at')

    contexto = datos_footer(request)
    contexto['conversation'] = conversation
    contexto['messages'] = messages
    contexto['profile'] = profile

    return render(request, 'messages_partial.html', contexto)


@login_required
def profile(request):
    """
    Página de perfil del usuario.
    """

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    total_user_conversations = Conversation.objects.filter(user=request.user).count()
    total_user_messages = Message.objects.filter(conversation__user=request.user).count()

    contexto = datos_footer(request)
    contexto['profile'] = profile
    contexto['total_conversations_user_profile'] = total_user_conversations
    contexto['total_messages_user_profile'] = total_user_messages

    return render(request, 'profile.html', contexto)


@login_required
def settings_view(request):
    """
    Página de configuración.
    Permite cambiar alias, modelo por defecto, temperatura
    y el aspecto de los mensajes del chat.
    """

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Alias del usuario
        profile.alias = request.POST.get('alias', '').strip()

        # Modelo preferido
        profile.preferred_model = request.POST.get('preferred_model', '').strip()

        # Temperatura del modelo
        temperature = request.POST.get('temperature', '').strip()
        if temperature != '':
            profile.temperature = temperature

        # Guardamos la configuración visual de los mensajes
        profile.user_message_background = request.POST.get('user_message_background', 'user-bg-orange')
        profile.ai_message_background = request.POST.get('ai_message_background', 'ai-bg-yellow')
        profile.user_message_text_color = request.POST.get('user_message_text_color', 'user-text-black')
        profile.user_message_font = request.POST.get('user_message_font', 'user-font-arial')

        profile.save()

        return redirect('settings')

    contexto = datos_footer(request)
    contexto['profile'] = profile

    return render(request, 'settings.html', contexto)


@login_required
def help_view(request):
    """
    Página de ayuda.
    """

    contexto = datos_footer(request)

    return render(request, 'help.html', contexto)


@login_required
def conversation_json(request, conversation_id):
    """
    Devuelve una conversación completa en formato JSON.
    """

    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    messages = []

    for message in conversation.message_set.all().order_by('created_at'):
        messages.append({
            'sender': message.sender,
            'content': message.content,
            'created_at': message.created_at,
        })

    return JsonResponse({
        'id': conversation.id,
        'title': conversation.title,
        'messages': messages,
    })