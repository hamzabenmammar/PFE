from django.urls import path
from . import views
from .views import ResourceListView , OutilListView, CoursListView , CorpusListView, ArticleListView, TheseListView, MemoireListView, ResourceDetailView ,ResourceCreateView

app_name = 'resources'
urlpatterns = [

    
    path('', ResourceListView.as_view(), name="list"),
    path('details/<str:type>/<int:pk>/', ResourceDetailView.as_view(), name="resource-detail"),
    path('outils/', OutilListView.as_view(), name="outil_list"),
    path('cours/', CoursListView.as_view(), name="cours_list"),
    path('corpus/', CorpusListView.as_view(), name="corpus_list"),  
    path('articles/', ArticleListView.as_view(), name="article_list"),
    path('theses/', TheseListView.as_view(), name="these_list"),
    path('memoires/', MemoireListView.as_view(), name="memoire_list"),
    path('ajouter/', ResourceCreateView.as_view(), name="create"),
    #path('<slug:slug>/', views.ResourceDetailView.as_view(), name="detail"),
]

