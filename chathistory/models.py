from django.db import models
from users.models import BaseUser

class Chat(models.Model):
    title = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.title)


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='chat_messages', on_delete=models.CASCADE)
    message = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    is_user_message = models.BooleanField(default=True)

    def __str__(self):
        return str(self.message)
    

class ChatOption(models.Model):
    title = models.CharField(max_length=255)
    prompt = models.TextField()

    def __str__(self):
        return f"{self.title}: {self.prompt[:50]}..."