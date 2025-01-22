from django.urls import path
from .views import index, archive, complete_task

urlpatterns = [
    path('', index, name='index'),
    path('<int:task_id>/complete/', complete_task, name='complete_task'),
    path('archive/', archive, name='archive'),
]
