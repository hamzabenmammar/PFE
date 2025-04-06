from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
class Topic(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum:topic-list')

class ChatRoom(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='chatrooms')
    name = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='created_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('forum:chatroom-detail', kwargs={'pk': self.pk})

class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='forum_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # Tri par défaut des messages par ordre chronologique

    def __str__(self):
        return f"Message de {self.user.username} à {self.timestamp.strftime('%H:%M:%S')}"