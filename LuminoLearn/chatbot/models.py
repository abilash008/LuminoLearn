
# Create your models here.
# chatbot/models.py
from django.db import models
from django.contrib.auth.models import User
from lumino_learn import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    author = models.CharField(max_length=10)  # "user" or "bot"
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
