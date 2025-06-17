from django.shortcuts import redirect
from django.urls import path

from . import views


urlpatterns = [
    path('', lambda request: redirect('teams:team', permanent=True)),
    
    path('todolist', views.todolist, name='todolist'),
    path('archive/', views.archive, name='archive'),
    
    path('task/create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
]