from django.urls import path
from .views import EmailVerificationView, SignUp , ProfileView , ProfileEditView

app_name = 'accounts'
urlpatterns = [
  path('signup/', SignUp.as_view(), name='signup'),
  path('profile/<uuid:pk>/', ProfileView.as_view(), name='profile'),
  path('profile/<uuid:pk>/edit/', ProfileEditView.as_view(), name='profile-edit'),
  path('verify-email/', EmailVerificationView.as_view(), name='email_verification_prompt'),
   
]

