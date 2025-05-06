from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('team/', views.team, name='team'),
    
    path('member/<int:member_id>/analytics/', views.member_analytics, name='member_analytics'),
    path('member/<int:member_id>/assign-task/', views.assign_task, name='assign_task'),
    path('member/<int:member_id>/edit/', views.edit_member, name='edit_member'),
    
    path('project-weekly-report/<int:project_id>/', views.project_weekly_report, name='project_weekly_report'),
    path('project-monthly-report/<int:project_id>/', views.project_monthly_report, name='project_monthly_report'),
    
    path('company/create/', views.create_company, name='create_company'),
    path('company/settings/', views.settings, name='settings'),
    path('company/leave/', views.leave_company, name='leave_company'),
    path('company/kick/<int:member_id>/', views.kick_member, name='kick_member'),
    
    path('join-request/create/', views.create_join_request, name='create_join_request'),
    path('join-request/<int:request_id>/accept/', views.accept_join_request, name='accept_join_request'),
    path('join-request/<int:request_id>/decline/', views.decline_join_request, name='decline_join_request'),
    
    path('job-title/create/', views.create_job_title, name='create_job_title'),
    path('job-title/<int:job_title_id>/delete/', views.delete_job_title, name='delete_job_title'),
]
