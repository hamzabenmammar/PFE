from django import forms
from django.contrib.auth.forms import UserCreationForm , UserChangeForm
from .models import CustomUser

ALLOWED_EMAIL_DOMAINS = ["usthb.dz"] 
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['full_name', 'email', 'institution']
        def clean_email(self):
          email = self.cleaned_data.get('email', '').lower()
          domain = email.split('@')[-1]
          if domain not in ALLOWED_EMAIL_DOMAINS:
              raise forms.ValidationError(
                  f"Votre e‑mail doit se terminer par une des extensions suivantes : "
                  f"{', '.join(ALLOWED_EMAIL_DOMAINS)}"
              )
          return email
      

class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = CustomUser
    fields = ['full_name', 'email', 'institution','bio']
