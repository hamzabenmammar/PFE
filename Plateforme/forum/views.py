from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Topic, ChatRoom, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'forum/topic_list.html'  # Ajout du préfixe 'forum/'
    context_object_name = 'topics'
    ordering = ['-created_at']  # Tri par date de création décroissante

class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    fields = ['title', 'description']
    template_name = 'forum/topic_new.html'  # Ajout du préfixe 'forum/'
    success_url = reverse_lazy('forum:topic-list')
    context_object_name = 'topic'
      
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

class TopicUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Topic
    fields = ['title', 'description']
    template_name = 'forum/topic_update.html'  # Ajout du préfixe 'forum/'
    success_url = reverse_lazy('forum:topic-list')
    context_object_name = 'topic'
    
    def test_func(self):
        return self.get_object().creator == self.request.user

class TopicDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Topic
    success_url = reverse_lazy('forum:topic-list')
    template_name = 'forum/topic_delete.html'  # Ajout du préfixe 'forum/'
    context_object_name = 'topic'
    
    def test_func(self):
        return self.get_object().creator == self.request.user

class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'forum/chatroom_list.html'  # Ajout du préfixe 'forum/'
    context_object_name = 'chatrooms'
    ordering = ['-created_at']  # Tri par date de création décroissante

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'forum/chatroom_detail.html'  # Ajout du préfixe 'forum/'
    context_object_name = 'chatroom'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(chatroom=self.object).order_by('timestamp')
        context['topic'] = self.object.topic
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        message_content = request.POST.get('message', '').strip()
        if message_content:
            Message.objects.create(
                chatroom=self.object,
                user=request.user,
                content=message_content
            )
        return redirect('forum:chatroom-detail', pk=self.object.pk)

class ChatRoomCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom
    fields = ['name', 'description']
    template_name = 'forum/chatroom_new.html'  # Ajout du préfixe 'forum/'
    context_object_name = 'chatroom'
    
    def form_valid(self, form):
        topic_id = self.kwargs.get('topic_id')
        form.instance.topic = get_object_or_404(Topic, id=topic_id)
        form.instance.creator = self.request.user  # Ajout de l'attribution du créateur
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('forum:chatroom-detail', kwargs={'pk': self.object.pk})

class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    template_name = 'forum/message_delete.html'  # Ajout du template manquant
    context_object_name = 'message'
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('forum:chatroom-detail', kwargs={'pk': self.object.chatroom.pk})

# Supprimer la fonction chatroom inutilisée ou la convertir en vue basée sur classe