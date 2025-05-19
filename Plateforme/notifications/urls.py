from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('api/list/', views.api_notification_list, name='api_list'),
    path('ajax/count/', views.count_ajax, name='count_ajax'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]