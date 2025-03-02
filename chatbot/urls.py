from django.urls import path
from .views import chatbot_ui, chatbot_respond

urlpatterns = [
    path('', chatbot_ui, name='chatbot_ui'),
    path('respond/', chatbot_respond, name='chatbot_respond'),
]
