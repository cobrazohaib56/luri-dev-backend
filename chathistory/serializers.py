from rest_framework import serializers
from .models import Chat, ChatMessage, ChatOption

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
    
class ChatOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatOption
        fields = ['title', 'prompt']