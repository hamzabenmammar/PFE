# consumers.py
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json
from .models import ChatRoom, Message

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.chatroom = get_object_or_404(ChatRoom, id=self.chatroom_id)
        
        # Use the chatroom ID as the channel group name
        self.room_group_name = f'chat_{self.chatroom_id}'
        
        # Join the channel group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, 
            self.channel_name
        )
        
        self.accept()
    
    def disconnect(self, close_code):
        # Leave the channel group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, 
            self.channel_name
        )
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        # Create a new message in the database
        message = Message.objects.create(
            chatroom=self.chatroom,
            user=self.user,
            content=message_content
        )
        
        # Send the message to the channel group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': str(message.id),
                'content': message.content,
                'user_id': str(self.user.id),
                'user_name': str(self.user),  # Using __str__ method instead of username
                'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M'),
                'is_current_user': False
            }
        )
    
    def chat_message(self, event):
        # Send the message to the WebSocket
        self.send(text_data=json.dumps({
            'message_id': event['message_id'],
            'content': event['content'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'timestamp': event['timestamp'],
            'is_current_user': str(self.user.id) == event['user_id']
        }))