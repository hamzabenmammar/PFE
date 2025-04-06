from django.urls import path
from . import views
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView, JoinProjectView, LeaveProjectView, ProjectSearchView
app_name = 'projects'
urlpatterns = [
  path('', ProjectListView.as_view(), name='project_list'),
  path('<uuid:pk>/', ProjectDetailView.as_view(), name='project_detail'),
  path('new/', ProjectCreateView.as_view(), name='project_new'),
  path('<uuid:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
  path('<uuid:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
  path('<uuid:pk>/join/', JoinProjectView.as_view(), name='join_project'),
  path('<uuid:pk>/leave/', LeaveProjectView.as_view(), name='leave_project'),
  path('search/', ProjectSearchView.as_view(), name='project_search'),

]

