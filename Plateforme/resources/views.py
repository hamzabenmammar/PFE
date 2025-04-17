
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
        if resource_type in ['', 'document']:
            docs = Document.objects.all()
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
            return 'document'
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
        'document': Document,
        'corpus': Corpus,
    }

    def get_object(self):
        model = self.TYPE_MODELS.get(self.kwargs['type'])
        if not model:
            raise Http404("Invalid type")
        return get_object_or_404(model, pk=self.kwargs['pk'])

    def get_template_names(self):
        return [
            f"resources/{self.kwargs['type']}_detail.html",
            self.template_name
        ]

class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vue générique pour mettre à jour une ressource."""
    template_name = 'resources/resource_form.html'
    
    TYPE_MODELS = {
        'tool': NLPTool,
        'course': Course,
        'document': Document,
        'corpus': Corpus,
    }
    
    def get_model(self):
        return self.TYPE_MODELS.get(self.kwargs['type'])
        
    def get_object(self):
        model = self.get_model()
        if not model:
            raise Http404("Invalid resource type")
        return get_object_or_404(model, pk=self.kwargs['pk'])
    
    def get_form(self):
        """Initialiser le formulaire avec les données de la ressource."""
        resource = self.get_object()
        form_kwargs = {
            'user': self.request.user,
            'initial': self.get_initial_data(resource),
        }
        if self.request.method == 'POST':
            form_kwargs['data'] = self.request.POST
        return ResourceForm(**form_kwargs)
    
    def get_initial_data(self, resource):
        """Préparer les données initiales pour le formulaire selon le type de ressource."""
        data = {
            'resource_type': self.kwargs['type'],
            'title': resource.title,
            'description': resource.description,
            'access_type': resource.access_type,
            'keywords': resource.keywords or '',
            'access_link': resource.access_link or '',
        }
        
        # Ajouter les champs spécifiques selon le type de ressource
        if isinstance(resource, Course):
            data.update({
                'course_field': resource.field,
                'academic_level': resource.academic_level,
                'course_institution': resource.institution,
                'academic_year': resource.academic_year,
            })
        elif isinstance(resource, NLPTool):
            data.update({
                'tool_type': resource.tool_type,
                'tool_version': resource.version,
                'documentation': resource.documentation_link or '',
                'languages': resource.languages,
            })
        elif isinstance(resource, Corpus):
            data.update({
                'corpus_language': resource.language,
                'corpus_size': resource.size,
                'corpus_field': resource.field,
                'corpus_format': resource.file_format,
            })
        elif isinstance(resource, Document):
            data.update({
                'document_type': resource.document_type,
                'document_format': resource.file_format,
            })
            
            # Ajouter les champs spécifiques au sous-type de document
            if hasattr(resource, 'article'):
                data.update({
                    'doi': resource.article.doi or '',
                    'journal': resource.article.journal,
                    'publication_date': resource.article.publication_date,
                })
            elif hasattr(resource, 'thesis'):
                data.update({
                    'supervisor': resource.thesis.supervisor,
                    'thesis_institution': resource.thesis.institution,
                    'defense_year': resource.thesis.defense_year,
                })
            elif hasattr(resource, 'memoir'):
                data.update({
                    'memoir_level': resource.memoir.academic_level,
                    'memoir_institution': resource.memoir.institution,
                    'memoir_defense_year': resource.memoir.defense_year,
                })
                
        return data
    
    def form_valid(self, form):
        """Traiter le formulaire et mettre à jour la ressource."""
        resource = self.get_object()
        resource_type = form.cleaned_data['resource_type']
        
        # Mettre à jour les champs communs
        resource.title = form.cleaned_data['title']
        resource.description = form.cleaned_data['description']
        resource.access_type = form.cleaned_data['access_type']
        resource.keywords = form.cleaned_data['keywords']
        resource.access_link = form.cleaned_data['access_link'] or None
        resource.save()
        
        # Mettre à jour les champs spécifiques selon le type
        if isinstance(resource, Course):
            resource.field = form.cleaned_data['course_field']
            resource.academic_level = form.cleaned_data['academic_level']
            resource.institution = form.cleaned_data['course_institution']
            resource.academic_year = form.cleaned_data['academic_year']
            resource.save()
        elif isinstance(resource, NLPTool):
            resource.tool_type = form.cleaned_data['tool_type']
            resource.version = form.cleaned_data['tool_version']
            resource.documentation_link = form.cleaned_data['documentation']
            resource.languages = form.cleaned_data['languages']
            resource.save()
        elif isinstance(resource, Corpus):
            resource.language = form.cleaned_data['corpus_language']
            resource.size = form.cleaned_data['corpus_size']
            resource.field = form.cleaned_data['corpus_field']
            resource.file_format = form.cleaned_data['corpus_format']
            resource.save()
        elif isinstance(resource, Document):
            # Mettre à jour le document
            resource.file_format = form.cleaned_data['document_format']
            resource.save()
            
            # Mettre à jour le sous-type de document
            doc_type = resource.document_type
            if doc_type == 'article' and hasattr(resource, 'article'):
                resource.article.doi = form.cleaned_data['doi']
                resource.article.journal = form.cleaned_data['journal']
                resource.article.publication_date = form.cleaned_data['publication_date']
                resource.article.save()
            elif doc_type == 'thesis' and hasattr(resource, 'thesis'):
                resource.thesis.supervisor = form.cleaned_data['supervisor']
                resource.thesis.institution = form.cleaned_data['thesis_institution']
                resource.thesis.defense_year = form.cleaned_data['defense_year']
                resource.thesis.save()
            elif doc_type == 'memoir' and hasattr(resource, 'memoir'):
                resource.memoir.academic_level = form.cleaned_data['memoir_level']
                resource.memoir.institution = form.cleaned_data['memoir_institution']
                resource.memoir.defense_year = form.cleaned_data['memoir_defense_year']
                resource.memoir.save()
        
        messages.success(self.request, f"Resource '{resource.title}' updated successfully!")
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        """Rediriger vers la page de détail après la mise à jour."""
        return reverse('resources:resource-detail', kwargs={
            'type': self.kwargs['type'],
            'pk': self.kwargs['pk']
        })
    
    def test_func(self):
        """Vérifier que l'utilisateur est bien le propriétaire de la ressource."""
        resource = self.get_object()
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
