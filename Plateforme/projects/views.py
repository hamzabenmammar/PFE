from django.contrib.auth.mixins import UserPassesTestMixin
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
from accounts.views import LoginAndVerifiedRequiredMixin
from django.utils.translation import gettext_lazy as _


class ProjectListView(LoginAndVerifiedRequiredMixin, ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        membership = ProjectMember.objects.filter(
            project=OuterRef('pk'),
            member=self.request.user
        )
        
        # Filtrer les projets créés par l'utilisateur si le paramètre my_projects est présent
        if self.request.GET.get('my_projects'):
            qs = qs.filter(coordinator=self.request.user)
            
        # Ajouter le filtre par statut
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
            
        # Ajouter la recherche
        search_query = self.request.GET.get('search')
        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(institution__name__icontains=search_query) |
                Q(coordinator__full_name__icontains=search_query)
            )
            
        return qs.annotate(is_member=Exists(membership))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Project # Importer ici pour éviter les problèmes de dépendance circulaire si Project utilise cette vue
        context['project_statuses'] = Project.STATUS_CHOICES
        return context


class ProjectDetailView(LoginAndVerifiedRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Récupérer les membres de l'équipe (exclure les rejetés)
        team_members = project.members.filter(
            status='accepted'
        ).select_related('member')
        
        # Récupérer les demandes en attente
        pending_requests = project.members.filter(
            status='pending'
        ).select_related('member')
        
        context.update({
            'team_members': [pm.member for pm in team_members],
            'pending_requests': pending_requests,
            'is_coordinator': project.coordinator == self.request.user,
            'is_member': project.members.filter(member=self.request.user, status='accepted').exists(),
            'has_pending_request': project.members.filter(
                member=self.request.user,
                status='pending'
            ).exists()
        })
        return context


class ProjectCreateView(LoginAndVerifiedRequiredMixin, CreateView):
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
                title="New research project",
                message=f"The project « {form.instance.title} » has just been published."
            )
        return response


class ProjectUpdateView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, UpdateView):  
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


class ProjectDeleteView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, DeleteView):
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


class JoinProjectView(LoginAndVerifiedRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Vérifier si le projet est terminé
        if project.status == 'completed':
            messages.error(request, "This project is closed and is no longer accepting new members..")
            return redirect('projects:project_detail', pk=pk)

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
            messages.success(request, "Your membership request has been sent to the project coordinator.")
        return redirect('projects:project_detail', pk=pk)


class AcceptMemberView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, View):
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
                title="Membership application accepted",
                message=f"Your request to join the project « {project.title} » was accepted."
            )
            messages.success(request, f"{member.member.full_name} was accepted into the project.")
        
        return redirect('projects:project_members', pk=pk)


class RejectMemberView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, View):
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
                title="Membership application refused",
                message=f"Your request to join the project « {project.title} » was refused."
            )
            messages.success(request, f"The request for {member.member.full_name} was refused.")
        
        return redirect('projects:project_members', pk=pk)


class ProjectMembersView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, DetailView):
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


class LeaveProjectView(LoginAndVerifiedRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        # Trouver le membre avant suppression
        member = ProjectMember.objects.filter(project=project, member=request.user, status='accepted').first()
        if member:
            # Notification au coordinateur via le service
            NotificationService.create_notification(
                recipient=project.coordinator,
                notification_type='SYSTEM', # Ou un type spécifique
                title="Departure of a member",
                message=f"{request.user.full_name} left your project « {project.title} »."
            )
            member.delete()
        return redirect('projects:project_detail', pk=pk)


class ProjectSearchView(LoginAndVerifiedRequiredMixin, ListView):
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


class RemoveMemberView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return project.coordinator == self.request.user

    def post(self, request, pk, member_id):
        project = get_object_or_404(Project, pk=pk)
        member = get_object_or_404(ProjectMember, project=project, member_id=member_id)
        member.delete()
        messages.success(request, _('Member removed successfully.'))
        return redirect('projects:project_members', pk=pk)


class RespondToRequestView(LoginAndVerifiedRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return project.coordinator == self.request.user

    def post(self, request, pk, request_id):
        project = get_object_or_404(Project, pk=pk)
        join_request = get_object_or_404(ProjectMember, pk=request_id, project=project)
        
        response = request.POST.get('response')
        if response == 'accept':
            join_request.status = 'accepted'
            join_request.save()
            messages.success(request, _('Request accepted successfully.'))
            
            # Créer une notification pour le membre
            NotificationService.create_notification(
                recipient=join_request.member,
                title=_('Project Request Accepted'),
                message=_('Your request to join {} has been accepted.').format(project.title),
                notification_type='project_request_accepted',
                related_object=project
            )
        elif response == 'reject':
            join_request.status = 'rejected'
            join_request.save()
            messages.success(request, _('Request rejected successfully.'))
            
            # Créer une notification pour le membre
            NotificationService.create_notification(
                recipient=join_request.member,
                title=_('Project Request Rejected'),
                message=_('Your request to join {} has been rejected.').format(project.title),
                notification_type='project_request_rejected',
                related_object=project
            )
        
        return redirect('projects:project_detail', pk=pk)