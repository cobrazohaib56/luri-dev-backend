from rest_framework import serializers

class ChatSupportSerializer(serializers.Serializer):
    type = serializers.CharField(allow_blank=False, required=True)
    message = serializers.CharField(allow_blank=False, required=True)

class ChatListSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    chat_list = serializers.ListField(child=ChatSupportSerializer(), required=True)

