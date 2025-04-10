from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from .models import Document, OutilTAL, Article, These , Memoire, Cours , Corpus

class ResourceListView(ListView):
    template_name = 'resources/list.html'
    context_object_name = 'resources'
    paginate_by = 10

    def get_queryset(self):
        documents = list(Document.objects.all().select_related('article', 'these', 'memoire'))
        outils = list(OutilTAL.objects.all())
        cours = list(Cours.objects.all())
        lcorpus = list(Corpus.objects.all())

        for doc in documents:
            doc.resource_type = 'document'
            """doc.detail_url = doc.get_absolute_url()"""
        
        for outil in outils:
            outil.resource_type = 'outil'
            """outil.detail_url = outil.get_absolute_url()"""

        for cour in cours:
            cour.resource_type = 'cours'   
            """cour.detail_url = cour.get_absolute_url()   """ 
        
        for corpus in lcorpus:
            corpus.resource_type = 'corpus'
            """corpus.detail_url = corpus.get_absolute_url()"""


        resources = documents + outils + cours + lcorpus
        return sorted(resources, key=lambda x: x.date_creation,reverse=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = ( Document.objects.count() + OutilTAL.objects.count() + Cours.objects.count()  + Corpus.objects.count())
        return context

class OutilListView(ListView):
    model = OutilTAL
    template_name = 'resources/outil_list.html'
    context_object_name = 'outils'       
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = (OutilTAL.objects.count() )
        return context

class CoursListView(ListView):
    model = Cours
    template_name = 'resources/cours_list.html'  
    context_object_name = 'cours'       

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = (Cours.objects.count() )
        return context

class ArticleListView(ListView):
    model = Article
    template_name = 'resources/article_list.html'
    context_object_name = 'articles'

class TheseListView(ListView):
    model = These
    template_name = 'resources/these_list.html'
    context_object_name = 'theses'

class MemoireListView(ListView):
    model = Memoire
    template_name = 'resources/memoire_list.html'
    context_object_name = 'memoires'
    
class CorpusListView(ListView):
    model = Corpus
    template_name = 'resources/corpus_list.html'
    context_object_name = 'lcorpus'
    paginate_by = 10


class ResourceDetailView(DetailView):
    """Detailed view for a generic resource"""
    template_name = 'resources/resource_detail.html'

    TYPE_MODELS = {
    'outil': OutilTAL,
    'cours': Cours,
    'article': Article,
    'these': These,
    'memoire': Memoire,
    'document': Document,
    'corpus': Corpus,
    }

    def get_object(self):
        model = self.TYPE_MODELS.get(self.kwargs['type'])
        if not model:
            raise Http404("Type invalide")
        return get_object_or_404(model, pk=self.kwargs['pk'])

    def get_template_names(self):
        return [
            f"resources/{self.kwargs['type']}_detail.html",
            self.template_name
        ]
   

from django.views.generic.edit import FormView
from .forms import ResourceForm
from django.urls import reverse_lazy

class ResourceCreateView(FormView):
    template_name = 'resources/resource_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resources:list')  # Redirige vers la liste après succès

    def form_valid(self, form):
        form.save()  # Appelle la méthode save() du formulaire
        return super().form_valid(form)