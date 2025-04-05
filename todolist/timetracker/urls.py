from django.urls import path
from . import views

app_name = 'timetracker'

urlpatterns = [
    path('', views.timetracker, name='timetracker'),
]
