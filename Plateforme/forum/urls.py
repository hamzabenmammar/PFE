from django.urls import path
from .views import TopicListView, TopicCreateView, TopicUpdateView, TopicDeleteView, ChatRoomDetailView, ChatRoomCreateView, MessageDeleteView, ChatRoomListView 
app_name = 'forum'

urlpatterns = [
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('topics/new/', TopicCreateView.as_view(), name='topic-new'),
    path('topics/<uuid:pk>/edit/', TopicUpdateView.as_view(), name='topic-update'),
    path('topics/<uuid:pk>/delete/', TopicDeleteView.as_view(), name='topic-delete'),
    path('chatroom/<uuid:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    path('topics/<uuid:pk>/chatroom/', ChatRoomListView.as_view(), name='chatroom-list'),
    path('topics/<uuid:topic_id>/chatroom/new/', ChatRoomCreateView.as_view(), name='chatroom-new'),  
    path('message/<uuid:pk>/delete/', MessageDeleteView.as_view(), name='message-delete'),
]