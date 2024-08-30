from .serializers import ChatSerializer, ChatMessageSerializer, ChatOptionSerializer
from .models import Chat, ChatMessage, ChatOption

from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.contrib.auth import get_user_model

UserModel = get_user_model()

def save_chat(userId, chat_list):
    chat = Chat.objects.filter(user__id=userId)
    if not chat.exists():
        chat_serializer = ChatSerializer(data={"user": userId})
        if chat_serializer.is_valid():
            chat = chat_serializer.save()
    else:
        chat = chat.last()

    for chat_data in chat_list:
        chat_data["chat"] = chat.id

    save_chat_list = ChatMessageSerializer(data=chat_list, many=True)
    if save_chat_list.is_valid():
        save_chat_list.save()


def get_chats_by_user(user_id):
    chat = Chat.objects.filter(user__id=user_id)
    if chat.exists():
        chat = chat.last()
        chat_messages = ChatMessage.objects.filter(chat__id=chat.id).order_by("datetime")
    else:
        return []
    return list(chat_messages)


def create_new_chat(user, data):
    chat_id = Chat.objects.filter(user=user).last().id
    if len(ChatMessage.objects.filter(chat__id=chat_id)) > 2 or data['isCustomPrompt'] == True:
        chat_message = create_chat_util(user)
        return ChatMessageSerializer(chat_message)
    else:
        return None
        # return list(ChatMessage.objects.filter(chat__id=chat_id))

def create_chat_util(user):
    chat = Chat.objects.create(user=user)
    chat_message = ChatMessage.objects.create(chat=chat, is_user_message=False, message=f"Hello {user.first_name} {user.last_name}! How can I assist you today?")
    return chat_message

def create_new_custom_chat(data, user):
    prompt = data['prompt']
    chat = Chat.objects.create(user=user)
    chat_message = ChatMessage.objects.create(chat=chat, is_user_message=False, message=f"Hello {user.first_name} {user.last_name}! {prompt}")


def fetch_buttons(user):
    buttons_with_prompts = ChatOption.objects.all().order_by("id")
    buttons_with_prompts_data = ChatOptionSerializer(buttons_with_prompts, many=True).data
    return buttons_with_prompts_data


class ActiveUsersAPIView(APIView):
    # This ensures that only admin users can access this view
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    
    def get(self, request, *args, **kwargs):
        
        if not request.user.is_superuser:
            # If not, return an HTTP 403 Forbidden response
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
            
        users_count = UserModel.objects.all().count()
        
        # Calculate the datetime for 24 hours and 28 days ago
        one_day_ago = timezone.now() - timedelta(days=1)
        
        # minutes_ago = timezone.now() - timedelta(minutes=5)
        
        twenty_eight_days_ago = timezone.now() - timedelta(days=28)

        # Get the count of unique users who sent messages in the last 24 hours
        daily_active_users = ChatMessage.objects.filter(
            datetime__gte=one_day_ago,
            is_user_message = True
        ).values('chat__user').distinct().count()

        # Get the count of unique users who sent messages in the last 28 days
        monthly_active_users = ChatMessage.objects.filter(
            datetime__gte=twenty_eight_days_ago
        ).values('chat__user').distinct().count()

        # Return the count in the response
        return Response({
            'daily_active_users': daily_active_users,
            'monthly_active_users': monthly_active_users,
            "user_count": users_count
        })