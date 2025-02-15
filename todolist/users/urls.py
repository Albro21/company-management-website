from django.urls import path
from . import views

urlpatterns = [
    path('settings', views.settings, name='settings'),
    path('profile', views.profile, name='profile'),
    path('chart/filter/', views.filter_chart, name='filter_chart'),
]