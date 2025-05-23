from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Topic, ChatRoom, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.services import NotificationService

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
        response = super().form_valid(form)
        # NOTIFICATION à tous les utilisateurs actifs via le service
        User = get_user_model()
        for user in User.objects.filter(is_active=True):
            # Évite d'envoyer la notification à l'utilisateur qui vient de créer le topic
            if user != self.request.user:
                NotificationService.create_notification(
                    recipient=user,
                    notification_type='SYSTEM', # Ou un type spécifique si tu en crées un pour le forum
                    title="Nouveau sujet dans le forum",
                    message=f"{self.request.user.username} a créé un nouveau sujet : {form.instance.title}",
                    related_object=form.instance # Optionnel: lie la notification à l'objet Topic créé
                )
        return response

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
    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')  # récupérer l'id du topic depuis l'URL
        return ChatRoom.objects.filter(topic_id=topic_id).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topic_id'] = Topic.objects.get(id=self.kwargs.get('topic_id'))  # pour afficher le nom du topic si besoin
        return context

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'forum/chatroom_detail.html'
    context_object_name = 'chatroom'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(chatroom=self.object).order_by('timestamp')
        return context
    
    def post(self, request, *args, **kwargs):
        # on récupère la salle et on crée le message
        self.object = self.get_object()
        content = request.POST.get('message', '').strip()
        if content:
            message = Message.objects.create(
                chatroom=self.object,
                user=request.user,
                content=content
            )
            # Utiliser NotificationService pour les notifications de nouveau message dans une chatroom
            if self.object.topic: # S'assurer que la chatroom est liée à un topic
                # Notifier le créateur du topic si ce n'est pas l'utilisateur actuel
                if self.object.topic.creator and self.object.topic.creator != request.user:
                    NotificationService.create_notification(
                        recipient=self.object.topic.creator,
                        notification_type='FORUM_REPLY', # Utiliser un type spécifique si possible
                        title=f"Nouvelle réponse dans le sujet « {self.object.topic.title} »",
                        message=f"{request.user.username} a répondu dans la salle de discussion « {self.object.name} » liée à votre sujet.",
                        related_object=self.object.topic,
                        action_url=self.object.get_absolute_url() # Lien vers la chatroom/le message si possible
                    )
                # Tu pourrais aussi vouloir notifier d'autres participants de la chatroom si nécessaire
                # for participant in self.object.participants.exclude(id=request.user.id).exclude(id=self.object.topic.creator.id):
                #     NotificationService.create_notification(...)

        else:
            return HttpResponse(status=204)  # pas de contenu à créer
        
        # si c'est une requête HTMX, on renvoie juste le fragment du nouveau message
        if request.headers.get('HX-Request'):
            html = render_to_string(
                'forum/partials/message_item.html',
                {
                    'message': message,
                    'user': request.user
                },
                request=request
            )
            return HttpResponse(html)
        
        # sinon on redirige normalement
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