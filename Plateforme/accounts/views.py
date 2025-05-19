from django.views.generic import CreateView ,  DetailView , UpdateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm  , CustomUserChangeForm, EmailVerificationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from projects.models import Project, ProjectMember
from notifications.models import Notification
from notifications.services import NotificationService







class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:email_verification_prompt')
    template_name = 'account/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        user.is_active = False  # désactive le compte temporairement
        user.generate_verification_code()
        
        # Envoi de l'email avec le code
        send_mail(
            subject='Vérification de votre adresse email',
            message=f'Votre code de vérification est : {user.email_verification_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        self.request.session['user_id_to_verify'] = str(user.pk)
        return redirect('accounts:email_verification_prompt')  # nouvelle vue

  
class ProfileView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    template_name = 'account/profile.html'
    context_object_name = 'user'
class ProfileEditView(LoginRequiredMixin, UpdateView):
   model = get_user_model()
   form_class = CustomUserChangeForm
   template_name='account/profile_edit.html'
   context_object_name = 'user'
   def get_success_url(self):
    return reverse_lazy('accounts:profile', kwargs={'pk': self.object.pk})






class EmailVerificationView(View):
    form_class = EmailVerificationForm
    template_name = 'account/email_verification.html'

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user_id = request.session.get('user_id_to_verify')
            user = get_object_or_404(get_user_model(), pk=user_id)

            if user.email_verification_code == code:
                user.is_active = True
                user.is_email_verified = True
                user.email_verification_code = ''
                user.save()
                messages.success(request, "Email vérifié avec succès. Vous pouvez maintenant vous connecter.")
                return redirect('account_login')
            else:
                messages.error(request, "Code incorrect. Réessayez.")
        return render(request, self.template_name, {'form': form})

class InviteToProjectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user_to_invite = get_object_or_404(get_user_model(), pk=pk)
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, pk=project_id, coordinator=request.user)
        # Vérifier que l'utilisateur n'est pas déjà membre ou invité
        if not ProjectMember.objects.filter(project=project, member=user_to_invite).exists():
            ProjectMember.objects.create(
                project=project,
                member=user_to_invite,
                role='member',
                status='pending'
            )
            # Utiliser NotificationService pour envoyer l'invitation
            NotificationService.create_notification(
                recipient=user_to_invite,
                notification_type='PROJECT_INVITE', # Ou un type spécifique
                title="Invitation à rejoindre un projet",
                message=f"Vous avez été invité à rejoindre le projet « {project.title} » par {request.user.full_name}.",
                project_id=project.pk,
                sender=request.user # Ajouter l'expéditeur
            )
            messages.success(request, f"Invitation envoyée à {user_to_invite.full_name}.")
        else:
            messages.warning(request, f"{user_to_invite.full_name} est déjà membre ou a déjà une invitation en attente.")
        return redirect('accounts:profile', pk=pk)

class RespondToProjectInviteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        member = ProjectMember.objects.filter(project=project, member=request.user, status='pending').first()
        if not member:
            messages.error(request, "Aucune invitation en attente pour ce projet.")
            return redirect('projects:project_detail', pk=project_id)
        response = request.POST.get('response')
        if response == 'accept':
            member.status = 'accepted'
            member.save()
            # Utiliser NotificationService pour la notification d'acceptation
            NotificationService.create_notification(
                recipient=project.coordinator,
                notification_type='PROJECT_INVITE_ACCEPTED', # Type spécifique pour l'acceptation
                title="Invitation acceptée",
                message=f"{request.user.full_name} a accepté l'invitation à rejoindre le projet « {project.title} ».",
                project_id=project.pk,
                sender=request.user # L'utilisateur qui accepte est l'expéditeur ici
            )
            messages.success(request, f"Vous avez rejoint le projet « {project.title} ».")
        elif response == 'reject':
            member.status = 'rejected'
            member.save()
            # Utiliser NotificationService pour la notification de refus
            NotificationService.create_notification(
                recipient=project.coordinator,
                notification_type='PROJECT_INVITE_REJECTED', # Type spécifique pour le refus
                title="Invitation refusée",
                message=f"{request.user.full_name} a refusé l'invitation à rejoindre le projet « {project.title} ».",
                project_id=project.pk,
                sender=request.user # L'utilisateur qui refuse est l'expéditeur ici
            )
            messages.info(request, f"Vous avez refusé l'invitation.")
        return redirect('projects:project_detail', pk=project_id)


