from pyexpat.errors import messages
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# Import the correct model names from your models.py
from .models import Document, NLPTool, Article, Thesis, Memoir, Course, Corpus, ResourceBase

class ResourceListView(ListView):
    template_name = 'resources/list.html'
    context_object_name = 'resources'
    paginate_by = 40

    def get_queryset(self):
        # Use the correct model names
        documents = list(Document.objects.all().select_related('article', 'thesis', 'memoir'))
        tools = list(NLPTool.objects.all())
        courses = list(Course.objects.all())
        corpora = list(Corpus.objects.all())

        # Set resource_type attribute for each resource
        for doc in documents:
            doc.resource_type = 'document'
            # Use get_absolute_url if implemented
            # doc.detail_url = doc.get_absolute_url()
        
        for tool in tools:
            tool.resource_type = 'tool'
            # tool.detail_url = tool.get_absolute_url()

        for course in courses:
            course.resource_type = 'course'   
            # course.detail_url = course.get_absolute_url()   
        
        for corpus in corpora:
            corpus.resource_type = 'corpus'
            # corpus.detail_url = corpus.get_absolute_url()

        # Combine and sort resources
        resources = documents + tools + courses + corpora
        return sorted(resources, key=lambda x: x.creation_date, reverse=True)  # corrected field name
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = (
            Document.objects.count() + 
            NLPTool.objects.count() + 
            Course.objects.count() + 
            Corpus.objects.count()
        )
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


# Import your form
from .forms import ResourceForm

# Dans views.py
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
