from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('team/', views.team, name='team'),
    path('member/<int:member_id>/analytics/', views.member_analytics, name='member_analytics'),
    
    path('project-weekly-report/<int:project_id>/', views.project_weekly_report, name='project_weekly_report'),
    
    path('company/create/', views.create_company, name='create_company'),
    path('company/settings/', views.settings, name='settings'),
    
    path('join-request/create/', views.create_join_request, name='create_join_request'),
    path('join-request/<int:request_id>/accept/', views.accept_join_request, name='accept_join_request'),
    path('join-request/<int:request_id>/decline/', views.decline_join_request, name='decline_join_request'),
    
    path('role/<int:role_id>/delete/', views.delete_role, name='delete_role'),
]
