# chatbot/urls.py


from django.urls import path

from chatbot import views
app_name = 'chatbot'


urlpatterns = [
    path("", views.chatbot_interface, name="chatbot_interface"),
    path("ask/", views.ask_bot, name="ask_bot"),
]
