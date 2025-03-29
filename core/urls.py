from django.urls import path
from . import views

urlpatterns = [
    path('', views.home , name="home" ),
    path('corpus/', views.corpus , name="corpus" ),
    path('outils/', views.outils , name="outils" ),
    path('ressources/' , views.ressources , name="ressources"),
    path('projets/', views.projets , name="projets" ), 
    path('communaute/', views.communaute , name="communaute" ), 
    
]
