from django import forms
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from .models import CustomUser
ALLOWED_EMAIL_DOMAINS = ["example.com", "gmail.com", "usthb.dz"] 
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['full_name', 'email', 'institution']
    

class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = CustomUser
    fields = ['full_name', 'email', 'institution','bio']
