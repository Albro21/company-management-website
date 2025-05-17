from django.urls import path
from teams.views import company, general, job_title, join_request, member, reports, vacation_request

app_name = 'teams'

urlpatterns = [
    path('team/', general.team, name='team'),
    path('calendar/', general.calendar, name='calendar'),
    
    path('member/<int:member_id>/analytics/', member.member_analytics, name='member_analytics'),
    path('member/<int:member_id>/assign-task/', member.assign_task, name='assign_task'),
    path('member/<int:member_id>/edit/', member.edit_member, name='edit_member'),
    path('member/<int:member_id>/', member.member_detail, name='member_detail'),
    
    path('document/create/', member.create_document, name='create_document'),
    path('document/<int:document_id>/delete/', member.delete_document, name='delete_document'),
    path('document/<int:document_id>/edit/', member.edit_document, name='edit_document'),
    
    path('expense/create/', member.create_expense, name='create_expense'),
    path('expense/<int:expense_id>/delete/', member.delete_expense, name='delete_expense'),
    path('expense/<int:expense_id>/edit/', member.edit_expense, name='edit_expense'),
    
    path('project-weekly-report/<int:project_id>/', reports.project_weekly_report, name='project_weekly_report'),
    path('project-monthly-report/<int:project_id>/', reports.project_monthly_report, name='project_monthly_report'),
    
    path('company/create/', company.create_company, name='create_company'),
    path('company/settings/', company.settings, name='settings'),
    path('company/leave/', company.leave_company, name='leave_company'),
    path('company/kick/<int:member_id>/', company.kick_member, name='kick_member'),
    
    path('join-request/create/', join_request.create_join_request, name='create_join_request'),
    path('join-request/<int:request_id>/accept/', join_request.accept_join_request, name='accept_join_request'),
    path('join-request/<int:request_id>/decline/', join_request.decline_join_request, name='decline_join_request'),
    
    path('vacation-request/create/', vacation_request.create_vacation_request, name='create_vacation_request'),
    path('vacation-request/<int:request_id>/accept/', vacation_request.accept_vacation_request, name='accept_vacation_request'),
    path('vacation-request/<int:request_id>/decline/', vacation_request.decline_vacation_request, name='decline_vacation_request'),
    
    path('job-title/create/', job_title.create_job_title, name='create_job_title'),
    path('job-title/<int:job_title_id>/delete/', job_title.delete_job_title, name='delete_job_title'),
]
