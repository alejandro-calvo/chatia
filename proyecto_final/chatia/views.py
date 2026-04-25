from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, UserProfile


def index(request):
    return render(request, 'index.html')


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(user=request.user)

    contexto = {
        'conversations': conversations
    }

    return render(request, 'conversation_list.html', contexto)


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    messages = conversation.message_set.all().order_by('created_at')

    contexto = {
        'conversation': conversation,
        'messages': messages
    }

    return render(request, 'conversation_detail.html', contexto)


@login_required
def new_conversation(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()

        if title == '':
            total_conversations = Conversation.objects.filter(user=request.user).count()
            title = f'Chat {total_conversations + 1}'

        conversation = Conversation.objects.create(
            user=request.user,
            title=title
        )

        return redirect('conversation_detail', conversation_id=conversation.id)

    return redirect('conversation_list')


@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )

    if request.method == 'POST':
        content = request.POST.get('content')

        if content and content.strip():
            Message.objects.create(
                conversation=conversation,
                sender='usuario',
                content=content
            )

            Message.objects.create(
                conversation=conversation,
                sender='ia',
                content='Aquí iría la respuesta de la IA'
            )

    return redirect('conversation_detail', conversation_id=conversation.id)


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    total_conversations = Conversation.objects.filter(user=request.user).count()
    total_messages = Message.objects.filter(conversation__user=request.user).count()

    contexto = {
        'profile': profile,
        'total_conversations': total_conversations,
        'total_messages': total_messages
    }

    return render(request, 'profile.html', contexto)


@login_required
def settings_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.alias = request.POST.get('alias', '').strip()
        profile.preferred_model = request.POST.get('preferred_model', '').strip()

        temperature = request.POST.get('temperature', '').strip()
        if temperature != '':
            profile.temperature = temperature

        profile.save()
        return redirect('settings')

    contexto = {
        'profile': profile
    }

    return render(request, 'settings.html', contexto)


@login_required
def help_view(request):
    return render(request, 'help.html')