from django.views.generic import TemplateView
from django.utils.timezone import now
from events.models import Event
from resources.models import Corpus, NLPTool
from projects.models import Project
from django.contrib.auth import get_user_model
from forum.models import Topic

User = get_user_model()

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Événements à venir
        context['events'] = Event.objects.filter(
            start_date__gte=now()
        ).order_by('start_date')[:5]
        
        # Compteurs pour les statistiques
        context['corpus_count'] = Corpus.objects.count()
        context['tools_count'] = NLPTool.objects.count()
        context['projects_count'] = Project.objects.count()
        context['members_count'] = User.objects.count()
        
      

            
        # Utilisez last_updated au lieu de views pour les ressources populaires
        context['popular_resources'] = NLPTool.objects.order_by('-last_updated')[:3]
        
        try:
            context['new_members'] = User.objects.order_by('-date_joined')[:5]
        except:
            context['new_members'] = []
            
        try:
            context['recent_discussions'] = Topic.objects.order_by('-created_at')[:5]
        except:
            context['recent_discussions'] = []
        
        return context