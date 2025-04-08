from django.urls import path
from . import views

app_name = 'timetracker'

urlpatterns = [
    path('', views.timetracker, name='timetracker'),
    path('start/', views.start_timer, name='start_timer'),
    path('stop/', views.stop_timer, name='stop_timer'),
]
