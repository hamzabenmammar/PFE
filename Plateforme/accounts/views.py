from django.views.generic import CreateView ,  DetailView , UpdateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm  , CustomUserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

class SignUp(CreateView):
  form_class = CustomUserCreationForm
  success_url = reverse_lazy('account_login')
  template_name = 'account/signup.html'

  
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


