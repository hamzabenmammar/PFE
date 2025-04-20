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


