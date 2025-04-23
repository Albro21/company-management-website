from django.urls import path
from . import views

app_name = 'timetracker'

urlpatterns = [
    path('', views.timetracker, name='timetracker'),
    path('start/', views.start_timer, name='start_timer'),
    path('stop/', views.stop_timer, name='stop_timer'),
    
    path('time-entry/<int:time_entry_id>/delete/', views.delete_time_entry, name='delete_time_entry'),
    path('time-entry/<int:time_entry_id>/duplicate/', views.duplicate_time_entry, name='duplicate_time_entry'),
]
