from django.urls import path
from .views import (
    SignUp, ProfileView, ProfileEditView, EmailVerificationView,
    InviteToProjectView, RespondToProjectInviteView
)

app_name = 'accounts'
urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('profile/<uuid:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/<uuid:pk>/edit/', ProfileEditView.as_view(), name='profile-edit'),
    path('email-verification/', EmailVerificationView.as_view(), name='email_verification_prompt'),
    path('profile/<uuid:pk>/invite/', InviteToProjectView.as_view(), name='invite_to_project'),
    path('project/<uuid:project_id>/respond-invite/', RespondToProjectInviteView.as_view(), name='respond_project_invite'),
]

