from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Project, ProjectMember
from django.db.models import Q
from django.db.models import Exists, OuterRef
from django.urls import reverse_lazy
from .forms import ProjectForm  


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        membership = ProjectMember.objects.filter(
            project=OuterRef('pk'),
            member=self.request.user
        )
        return qs.annotate(is_member=Exists(membership))


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context['is_member'] = ProjectMember.objects.filter(
            project=project,
            member=self.request.user
        ).exists()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm  # Utilisez votre formulaire au lieu de fields
    template_name = 'project_new.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        form.instance.coordinator = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  
    model = Project
    form_class = ProjectForm  
    template_name = 'project_update.html'
    success_url = reverse_lazy('projects:project_list')
    
    def test_func(self):
        obj = self.get_object()
        return (
        self.request.user.is_staff
        or self.request.user.is_superuser
        or obj.coordinator == self.request.user
    )


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'project_delete.html'
    success_url = reverse_lazy('projects:project_list')

    def test_func(self):
        obj = self.get_object()
        return (
        self.request.user.is_staff
        or self.request.user.is_superuser
        or obj.coordinator == self.request.user
    )


class JoinProjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        # Vérifie si l'utilisateur n'est pas déjà membre
        if not ProjectMember.objects.filter(project=project, member=request.user).exists():
            ProjectMember.objects.create(
                project=project,
                member=request.user,
                role='member'  # Vous pouvez définir un rôle par défaut
            )
        # Redirige vers la page de détail du projet (ou une autre page de votre choix)
        return redirect('projects:project_detail', pk=pk)


class LeaveProjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        ProjectMember.objects.filter(project=project, member=request.user).delete()
        return redirect('projects:project_detail', pk=pk)


class ProjectSearchView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'project_search.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Project.objects.filter(
                Q(title__icontains=query) |
                Q(institution__name__icontains=query) |
                Q(coordinator__full_name__icontains=query)
            )
        else:
            return Project.objects.all()