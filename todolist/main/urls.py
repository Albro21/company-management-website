from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('<int:project_id>/delete-project/', views.delete_project, name='delete_project'),
    path('<int:category_id>/delete-category/', views.delete_category, name='delete_category'),
    path('archive/', views.archive, name='archive'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('profile', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)