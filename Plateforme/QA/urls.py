from django.urls import path
from . import views

app_name = 'QA'

urlpatterns = [
    path('', views.qa_home, name='qa_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('search/', views.search_questions, name='search'),
]
