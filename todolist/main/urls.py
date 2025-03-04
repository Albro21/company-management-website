from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<int:project_id>/delete-project/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('<int:category_id>/delete-category/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('archive/', views.archive, name='archive'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
]