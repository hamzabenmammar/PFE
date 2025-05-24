from django.urls import path, include
from .views import (
    SignUp, ProfileView, ProfileEditView, EmailVerificationView,
    InviteToProjectView, RespondToProjectInviteView, awaiting_verification_view , delete_account
)



urlpatterns = [
    path('accounts/signup/', SignUp.as_view(), name='signup'),
    path('accounts/profile/<uuid:pk>/', ProfileView.as_view(), name='profile'),
    path('accounts/profile/<uuid:pk>/edit/', ProfileEditView.as_view(), name='profile-edit'),
    path('accounts/email-verification/', EmailVerificationView.as_view(), name='email_verification_prompt'),
    path('accounts/profile/<uuid:pk>/invite/', InviteToProjectView.as_view(), name='invite_to_project'),
    path('accounts/project/<uuid:project_id>/respond-invite/', RespondToProjectInviteView.as_view(), name='respond_project_invite'),
    path('accounts/awaiting-verification/', awaiting_verification_view, name='awaiting_verification'),
    path('delete-account/', delete_account, name='delete_account'),
]

