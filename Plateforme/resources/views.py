
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView ,UpdateView ,DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .forms import ResourceForm

# Import the correct model names from your models.py
from .models import Document, NLPTool, Article, Thesis, Memoir, Course, Corpus, ResourceBase        

from django.db.models import Q

class ResourceListView(ListView):




    template_name = 'resources/list.html'
    context_object_name = 'resources'
    paginate_by = 9  # 3 cartes par ligne × 3 lignes

    def get_queryset(self):
        search_query = self.request.GET.get('q', '')
        resource_type = self.request.GET.get('type', '')
        
        querysets = []
        
        # Documents
        if resource_type in ['', 'article', 'thesis', 'memoir']:
         docs = Document.objects.all()
         if resource_type in ['article', 'thesis', 'memoir']:
            docs = docs.filter(document_type=resource_type)
         if search_query:
            docs = docs.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
         querysets.append(docs)
        
        # Outils NLP
        if resource_type in ['', 'tool']:
            tools = NLPTool.objects.all()
            if search_query:
                tools = tools.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
            querysets.append(tools)
        
        # Cours
        if resource_type in ['', 'course']:
            courses = Course.objects.all()
            if search_query:
                courses = courses.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
            querysets.append(courses)
        
        # Corpus
        if resource_type in ['', 'corpus']:
            corpora = Corpus.objects.all()
            if search_query:
                corpora = corpora.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query)
                )
            querysets.append(corpora)

        # Combiner et typer les résultats
        combined = []
        for qs in querysets:
            for obj in qs:
                obj.resource_type = self.get_resource_type(obj)
                combined.append(obj)

        # Trier par date de création
        return sorted(combined, key=lambda x: x.creation_date, reverse=True)

    def get_resource_type(self, obj):
        """Détermine dynamiquement le type de ressource"""
        if isinstance(obj, Document):
            return obj.document_type
        elif isinstance(obj, NLPTool):
            return 'tool'
        elif isinstance(obj, Course):
            return 'course'
        elif isinstance(obj, Corpus):
            return 'corpus'
        return 'unknown'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Conserver les paramètres de recherche
        context['current_query'] = self.request.GET.urlencode()
        # Comptage exact avec filtres
        context['total_count'] = len(self.object_list)
        return context

class ToolListView(ListView):
    model = NLPTool  # Corrected model name
    template_name = 'resources/tool_list.html'  # Updated template name
    context_object_name = 'tools'  # Updated context name
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = NLPTool.objects.count()
        return context

class CourseListView(ListView):
    model = Course  # Corrected model name
    template_name = 'resources/course_list.html'  # Updated template name
    context_object_name = 'courses'  # Updated context name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Course.objects.count()
        return context

class ArticleListView(ListView):
    model = Article
    template_name = 'resources/article_list.html'
    context_object_name = 'articles'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Article.objects.count()
        return context

class ThesisListView(ListView):
    model = Thesis  # Corrected model name
    template_name = 'resources/thesis_list.html'  # Updated template name
    context_object_name = 'theses'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Thesis.objects.count()
        return context

class MemoirListView(ListView):
    model = Memoir  # Corrected model name
    template_name = 'resources/memoir_list.html'  # Updated template name
    context_object_name = 'memoirs'  # Updated context name
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Memoir.objects.count()
        return context
    
class CorpusListView(ListView):
    model = Corpus
    template_name = 'resources/corpus_list.html'
    context_object_name = 'corpora'  # More appropriate plural
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Corpus.objects.count()
        return context

class ResourceDetailView(DetailView):
    """Detailed view for a generic resource"""
    template_name = 'resources/resource_detail.html'

    TYPE_MODELS = {
        'tool': NLPTool,  # Corrected model name
        'course': Course,  # Corrected model name
        'article': Article,
        'thesis': Thesis,  # Corrected model name
        'memoir': Memoir,  # Corrected model name
      
        'corpus': Corpus,
    }
    MODEL_VIEW_NAMES = {
    'nlptool': 'tool',
    'course': 'course',
    'article': 'article',
    'thesis': 'thesis',
    'memoir': 'memoir',

    'corpus': 'corpus',
}

    def get_object(self):
     resource_type = self.kwargs['type']
     pk = self.kwargs['pk']
    
    # Pour les sous-types de Document
     if resource_type in ['article', 'thesis', 'memoir']:
        # D'abord essayer de récupérer directement avec l'ID du sous-type
         model = self.TYPE_MODELS.get(resource_type)
         try:
            return get_object_or_404(model, pk=pk)
         except Http404:
            # Si ça échoue, essayer de récupérer via le Document parent
            document = get_object_or_404(Document, pk=pk)
            if resource_type == 'article' and hasattr(document, 'article'):
                return document.article
            elif resource_type == 'thesis' and hasattr(document, 'thesis'):
                return document.thesis
            elif resource_type == 'memoir' and hasattr(document, 'memoir'):
                return document.memoir
            raise Http404(f"No {resource_type.capitalize()} matches the given query.")
     else:
        # Pour les autres types de ressources
        model = self.TYPE_MODELS.get(resource_type)
        if not model:
            raise Http404("Invalid resource type")
        return get_object_or_404(model, pk=pk)

    def get_template_names(self):
        return [
            f"resources/{self.kwargs['type']}_detail.html",
            self.template_name
        ]
    
       
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.object._meta.model_name
        context['resource_type'] = self.MODEL_VIEW_NAMES.get(model_name, model_name)
    
      # Pour les sous-types de Document, nous voulons aussi passer l'objet Document
        if hasattr(self.object, 'document'):
          context['specific_object'] = self.object  # Le sous-type (Article, Thesis, Memoir)
          context['object'] = self.object.document  # L'objet Document parent
    
       # Ajouter des corpora liés pour la section "Related Corpora"
        if self.kwargs['type'] in ['article', 'thesis', 'memoir', 'course']:
        # Exemple simple: récupérer des corpus du même domaine/champ
           if hasattr(self.object, 'field'):
              field = self.object.field
           elif hasattr(self.object, 'document') and hasattr(self.object.document, 'field'):
              field = self.object.document.field
           else:
              field = None
            
           if field:
              context['related_corpora'] = Corpus.objects.filter(field__icontains=field)[:3]
           else:
              context['related_corpora'] = Corpus.objects.all()[:3]
    
        return context
  
class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = ResourceForm
    template_name = 'resources/resource_update_form.html'
    
    TYPE_MODELS = {
        'tool': NLPTool,
        'nlp_tool': NLPTool,  # Ajout pour la cohérence des types
        'course': Course,
        'document': Document,
        'corpus': Corpus,
        'article': Article,
        'thesis': Thesis,
        'memoir': Memoir,
    }

    def get_object(self):
        resource_type = self.kwargs['type']
        pk = self.kwargs['pk']
        
        # Pour les sous-types de Document
        if resource_type in ['article', 'thesis', 'memoir']:
            try:
                # Essayer d'abord de récupérer directement le sous-type
                model = self.TYPE_MODELS.get(resource_type)
                return get_object_or_404(model, pk=pk)
            except Http404:
                # Si ça échoue, essayer via le Document parent
                document = get_object_or_404(Document, pk=pk)
                if hasattr(document, resource_type):
                    return getattr(document, resource_type)
                raise Http404(f"{resource_type.capitalize()} not found for document ID {pk}")
        else:
            model = self.TYPE_MODELS.get(resource_type)
            if not model:
                raise Http404("Invalid resource type")
            return get_object_or_404(model, pk=pk)

    def get_initial(self):
      resource = self.get_object()
      initial = {}
    
    # Pour les sous-types de Document (Article, Thesis, Memoir)
      if hasattr(resource, 'document'):
        # Récupérer les champs du Document parent
        document = resource.document
        initial.update({
            'title': document.title,
            'description': document.description,
            'keywords': document.keywords,
            'access_link': document.access_link or '',
            'document_type': document.document_type,
            'document_format': document.file_format,
        })
        
        # Ajouter les champs spécifiques au sous-type
        if isinstance(resource, Article):
            initial.update({
                'doi': resource.doi,
                'journal': resource.journal,
                'publication_date': resource.publication_date,
            })
        elif isinstance(resource, Thesis):
            initial.update({
                'supervisor': resource.supervisor,
                'thesis_institution': resource.institution.id if resource.institution else None,
                'defense_year': resource.defense_year,
            })
        elif isinstance(resource, Memoir):
            initial.update({
                'memoir_level': resource.academic_level,
                'memoir_institution': resource.institution.id if resource.institution else None,
                'memoir_defense_year': resource.defense_year,
            })
        
        initial['resource_type'] = 'document'
      else:
        # Pour les autres types de ressources (Course, NLPTool, Corpus, Document de base)
        initial.update({
            'title': resource.title,
            'description': resource.description,
            'keywords': resource.keywords,
            'access_link': resource.access_link or '',
        })
        
        """if isinstance(resource, Document):
            initial.update({
                'document_type': resource.document_type,
                'document_format': resource.file_format,
            })
            initial['resource_type'] = 'document'"""
        if isinstance(resource, Course):
            initial.update({
                'course_field': resource.field,
                'academic_level': resource.academic_level,
                'course_institution': resource.institution.id if resource.institution else None,
                'academic_year': resource.academic_year,
            })
            initial['resource_type'] = 'course'
        elif isinstance(resource, NLPTool):
            initial.update({
                'tool_type': resource.tool_type,
                'tool_version': resource.version,
                'documentation': resource.documentation_link or '',
                'languages': resource.languages,
            })
            initial['resource_type'] = 'nlp_tool'
        elif isinstance(resource, Corpus):
            initial.update({
                'corpus_language': resource.language,
                'corpus_size': resource.size,
                'corpus_field': resource.field,
                'corpus_format': resource.file_format,
            })
            initial['resource_type'] = 'corpus'

      return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['is_update'] = True  # Important pour désactiver les champs de type
        return kwargs

    def _get_resource_type(self, resource):
        """Retourne le type de base"""
        if isinstance(resource, Article) or hasattr(resource, 'article'):
            return 'document'
        elif isinstance(resource, Thesis) or hasattr(resource, 'thesis'):
            return 'document'
        elif isinstance(resource, Memoir) or hasattr(resource, 'memoir'):
            return 'document'
        elif isinstance(resource, NLPTool):
            return 'nlp_tool'
        elif isinstance(resource, Course):
            return 'course'
        elif isinstance(resource, Corpus):
            return 'corpus'
        elif isinstance(resource, Document):
            return 'document'
        return resource._meta.model_name

    def form_valid(self, form):
        resource = self.get_object()
        resource_type = self._get_resource_type(resource)

        # Mise à jour des champs communs
        common_data = {
            'title': form.cleaned_data['title'],
            'description': form.cleaned_data['description'],
            'keywords': form.cleaned_data['keywords'],
            'access_link': form.cleaned_data['access_link'],
        }

        # Pour les sous-types de Document
        document = None
        if hasattr(resource, 'document'):
              # Si c'est un sous-type de Document
              document = resource.document
              for attr, value in common_data.items():
                setattr(document, attr, value)
              document.file_format = form.cleaned_data['document_format']
              document.save()

        elif resource_type == 'document':
            # Si c'est un Document de base
                for attr, value in common_data.items():
                    setattr(document, attr, value)
                resource.file_format = form.cleaned_data['document_format']
                resource.save()
                document = resource
        else:
            # Pour les autres types de ressources
            for attr, value in common_data.items():
                setattr(resource, attr, value)
            resource.save()

        # Mise à jour des champs spécifiques
        if resource_type == 'course':
            resource.field = form.cleaned_data['course_field']
            resource.academic_level = form.cleaned_data['academic_level']
            resource.institution = form.cleaned_data['course_institution']
            resource.academic_year = form.cleaned_data['academic_year']
            resource.save()
        elif resource_type == 'nlp_tool':
            resource.tool_type = form.cleaned_data['tool_type']
            resource.version = form.cleaned_data['tool_version']
            resource.documentation_link = form.cleaned_data['documentation']
            resource.languages = form.cleaned_data['languages']
            resource.save()
        elif resource_type == 'corpus':
            resource.language = form.cleaned_data['corpus_language']
            resource.size = form.cleaned_data['corpus_size']
            resource.field = form.cleaned_data['corpus_field']
            resource.file_format = form.cleaned_data['corpus_format']
            resource.save()
        
        # Traitement des sous-types de Document
        if document:
            doc_type = document.document_type
            if doc_type == 'article':
             if hasattr(document, 'article'):
                    article = document.article
             else:
                article, _ = Article.objects.get_or_create(document=document)
                article.doi = form.cleaned_data['doi']
                article.journal = form.cleaned_data['journal']
                article.publication_date = form.cleaned_data['publication_date']
                article.save()
            elif doc_type == 'thesis':
                if hasattr(document, 'thesis'):
                    thesis = document.thesis
                else:
                    thesis = Thesis(document=document)
                thesis.supervisor = form.cleaned_data['supervisor']
                thesis.institution = form.cleaned_data['thesis_institution']
                thesis.defense_year = form.cleaned_data['defense_year']
                thesis.save()
            elif doc_type == 'memoir':
                if hasattr(document, 'memoir'):
                    memoir = document.memoir
                else:
                    memoir = Memoir(document=document)
                memoir.academic_level = form.cleaned_data['memoir_level']
                memoir.institution = form.cleaned_data['memoir_institution']
                memoir.defense_year = form.cleaned_data['memoir_defense_year']
                memoir.save()

        if hasattr(resource, 'document'):
         messages.success(self.request, f"Ressource '{resource.document.title}' mise à jour avec succès !")
        else:
         messages.success(self.request, f"Ressource '{resource.title}' mise à jour avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        resource = self.get_object()
        resource_type = self.kwargs['type']
        pk = self.kwargs['pk']
        
        # Redirection vers la vue détaillée appropriée
        return reverse('resources:resource-detail', kwargs={
            'type': resource_type,
            'pk': pk
        })

    def test_func(self):
        resource = self.get_object()
        if hasattr(resource, 'document'):
            return resource.document.author == self.request.user
        return resource.author == self.request.user

class ResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vue générique pour supprimer une ressource."""
    template_name = 'resources/resource_confirm_delete.html'
    success_url = reverse_lazy('resources:list')
    
    TYPE_MODELS = {
        'tool': NLPTool,
        'course': Course,
        'document': Document,
        'corpus': Corpus,
        'article':Document,
        'memoir':Document,
        'thesis':Document
    }
    
    def get_object(self):
        model = self.TYPE_MODELS.get(self.kwargs['type'])
        if not model:
            raise Http404("Invalid resource type")
        return get_object_or_404(model, pk=self.kwargs['pk'])
    
    def delete(self, request, *args, **kwargs):
        resource = self.get_object()
        resource_title = resource.title
        
        # Suppression du sous-type de document si nécessaire
        if isinstance(resource, Document):
            if hasattr(resource, 'article'):
                resource.article.delete()
            elif hasattr(resource, 'thesis'):
                resource.thesis.delete()
            elif hasattr(resource, 'memoir'):
                resource.memoir.delete()
                
        # Suppression de la ressource principale
        response = super().delete(request, *args, **kwargs)
        
        messages.success(self.request, f"Resource '{resource_title}' deleted successfully!")
        return response
    
    def test_func(self):
        """Vérifier que l'utilisateur est bien le propriétaire de la ressource."""
        resource = self.get_object()
        return resource.author == self.request.user    
    
class ResourceCreateView(LoginRequiredMixin, FormView):
    template_name = 'resources/resource_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resources:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Passe l'utilisateur au formulaire
        return kwargs
    
    def form_valid(self, form):
        resource = form.save()
        messages.success(self.request, f"Resource '{resource.title}' created successfully!")
        return super().form_valid(form)
    
class ResourceSearchView(ListView):


    template_name = 'resources/search_results.html'
    context_object_name = 'resources'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return []
            
        # Search in all resource types
        documents = Document.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(keywords__icontains=query)
        )
        
        tools = NLPTool.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(keywords__icontains=query) |
            Q(languages__icontains=query)
        )
        
        courses = Course.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(keywords__icontains=query) |
            Q(field__icontains=query)
        )
        
        corpora = Corpus.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(keywords__icontains=query) |
            Q(field__icontains=query) |
            Q(language__icontains=query)
        )
        
        # Add resource_type attribute to each resource
        for doc in documents:
            doc.resource_type = 'document'
        for tool in tools:
            tool.resource_type = 'tool'
        for course in courses:
            course.resource_type = 'course'
        for corpus in corpora:
            corpus.resource_type = 'corpus'
            
        # Combine and sort results
        results = list(documents) + list(tools) + list(courses) + list(corpora)
        return sorted(results, key=lambda x: x.creation_date, reverse=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_count'] = len(context['resources'])
        return context

class CourseCreateView(LoginRequiredMixin, FormView):
    template_name = 'resources/course_create_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resources:course_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        initial['resource_type'] = 'course'
        return initial
    
    def form_valid(self, form):
        resource = form.save()
        messages.success(self.request, f"Cours '{resource.title}' créé avec succès!")
        return super().form_valid(form)

class CorpusCreateView(LoginRequiredMixin, FormView):
    template_name = 'resources/corpus_create_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resources:corpus_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        initial['resource_type'] = 'corpus'
        return initial
    
    def form_valid(self, form):
        resource = form.save()
        messages.success(self.request, f"Corpus '{resource.title}' créé avec succès!")
        return super().form_valid(form)

class ToolCreateView(LoginRequiredMixin, FormView):
    template_name = 'resources/tool_create_form.html'
    form_class = ResourceForm
    success_url = reverse_lazy('resources:tool_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        initial['resource_type'] = 'nlp_tool'
        return initial
    
    def form_valid(self, form):
        resource = form.save()
        messages.success(self.request, f"Tool '{resource.title}' créé avec succès!")
        return super().form_valid(form)