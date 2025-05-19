from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Project, ProjectMember
from django.db.models import Q
from django.db.models import Exists, OuterRef
from django.urls import reverse_lazy
from .forms import ProjectForm  
from django.contrib.auth import get_user_model
from notifications.models import Notification
from django.contrib import messages
from notifications.services import NotificationService


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
        response = super().form_valid(form)
        # NOTIFICATION à tous les utilisateurs actifs via le service
        User = get_user_model()
        for user in User.objects.filter(is_active=True):
            NotificationService.create_notification(
                recipient=user,
                notification_type='SYSTEM', # Ou un type spécifique si tu en crées un pour les nouveaux projets
                title="Nouveau projet de recherche",
                message=f"Le projet « {form.instance.title} » vient d'être publié."
            )
        return response


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
            # Créer une demande en attente
            ProjectMember.objects.create(
                project=project,
                member=request.user,
                role='member',
                status='pending'
            )
            # Notification au coordinateur du projet via le service
            NotificationService.create_membership_request(
                recipient=project.coordinator,
                project=project,
                sender=request.user
            )
            messages.success(request, "Votre demande d'adhésion a été envoyée au coordinateur du projet.")
        return redirect('projects:project_detail', pk=pk)


class AcceptMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.coordinator

    def post(self, request, pk, member_id):
        project = get_object_or_404(Project, pk=pk)
        member = get_object_or_404(ProjectMember, project=project, member_id=member_id)
        
        if member.status == 'pending':
            member.status = 'accepted'
            member.save()
            
            # Notification au membre accepté via le service
            NotificationService.create_notification(
                recipient=member.member,
                notification_type='SYSTEM', # Ou un type spécifique
                title="Demande d'adhésion acceptée",
                message=f"Votre demande pour rejoindre le projet « {project.title} » a été acceptée."
            )
            messages.success(request, f"{member.member.full_name} a été accepté dans le projet.")
        
        return redirect('projects:project_members', pk=pk)


class RejectMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.coordinator

    def post(self, request, pk, member_id):
        project = get_object_or_404(Project, pk=pk)
        member = get_object_or_404(ProjectMember, project=project, member_id=member_id)
        
        if member.status == 'pending':
            member.status = 'rejected'
            member.save()
            
            # Notification au membre refusé via le service
            NotificationService.create_notification(
                recipient=member.member,
                notification_type='SYSTEM', # Ou un type spécifique
                title="Demande d'adhésion refusée",
                message=f"Votre demande pour rejoindre le projet « {project.title} » a été refusée."
            )
            messages.success(request, f"La demande de {member.member.full_name} a été refusée.")
        
        return redirect('projects:project_members', pk=pk)


class ProjectMembersView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'project_members.html'
    context_object_name = 'project'
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.coordinator
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context['pending_members'] = project.members.filter(status='pending')
        context['accepted_members'] = project.members.filter(status='accepted')
        context['rejected_members'] = project.members.filter(status='rejected')
        return context


class LeaveProjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        # Trouver le membre avant suppression
        member = ProjectMember.objects.filter(project=project, member=request.user, status='accepted').first()
        if member:
            # Notification au coordinateur via le service
            NotificationService.create_notification(
                recipient=project.coordinator,
                notification_type='SYSTEM', # Ou un type spécifique
                title="Départ d'un membre",
                message=f"{request.user.full_name} a quitté votre projet « {project.title} »."
            )
            member.delete()
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


class RemoveMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.coordinator

    def post(self, request, pk, member_id):
        project = get_object_or_404(Project, pk=pk)
        member = get_object_or_404(ProjectMember, project=project, member_id=member_id, status='accepted')
        # Notification au membre retiré via le service
        NotificationService.create_notification(
            recipient=member.member,
            notification_type='SYSTEM', # Ou un type spécifique
            title="Retrait du projet",
            message=f"Vous avez été retiré du projet « {project.title} » par le coordinateur."
        )
        member.delete()
        messages.success(request, "Le membre a été retiré du projet.")
        return redirect('projects:project_members', pk=pk)