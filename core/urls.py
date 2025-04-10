from django.urls import path , include
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.home , name="home" ),
    # path('corpus/', RedirectView(url='/resources/corpus/' ),name="corpus"), 
   # path('outils/', RedirectView(url='/resources/outils/' ),name="outils"),
    path('resources/' ,include('resources.urls' )),
    path('projets/', views.projets , name="projets" ), 
    path('communaute/', views.communaute , name="communaute" ), 
    
]
