from django.urls import path
from teams.views import company, document, expense, general, job_title, join_request, employee, reports, holiday, invitation

app_name = 'teams'

urlpatterns = [
    path('team/', general.team, name='team'),
    path('calendar/', general.calendar, name='calendar'),
    
    path("employee/invite/", employee.invite_employee, name="invite_employee"),
    path('employee/<int:employee_id>/assign-task/', employee.assign_task, name='assign_task'),
    path('employee/<int:employee_id>/edit/', employee.edit_employee, name='edit_employee'),
    path('employee/<int:employee_id>/kick/', employee.kick_employee, name='kick_employee'),
    path('employee/<int:user_id>/', employee.employee_detail, name='employee_detail'),
    
    path('document/create/<int:employee_id>/', document.create_document, name='create_document'),
    path('document/<int:document_id>/delete/', document.delete_document, name='delete_document'),
    path('document/<int:document_id>/edit/', document.edit_document, name='edit_document'),
    
    path('expense/create/', expense.create_expense, name='create_expense'),
    path('expense/<int:expense_id>/delete/', expense.delete_expense, name='delete_expense'),
    path('expense/<int:expense_id>/edit/', expense.edit_expense, name='edit_expense'),
    
    path('project-weekly-report/<int:project_id>/', reports.project_weekly_report, name='project_weekly_report'),
    path('project-monthly-report-pdf/<int:project_id>/', reports.project_monthly_report_pdf, name='project_monthly_report_pdf'),
    path('project-monthly-report-xlsx/<int:project_id>/', reports.project_monthly_report_xlsx, name='project_monthly_report_xlsx'),
    
    path('company/create/', company.create_company, name='create_company'),
    path('company/expenses/', company.expenses, name='expenses'),
    path('company/settings/', company.settings, name='settings'),
    
    path('join-request/create/', join_request.create_join_request, name='create_join_request'),
    path('join-request/<int:request_id>/accept/', join_request.accept_join_request, name='accept_join_request'),
    path('join-request/<int:request_id>/decline/', join_request.decline_join_request, name='decline_join_request'),
    
    path('holiday/<int:holiday_id>/edit/', holiday.HolidayEditView.as_view(), name='edit_holiday'),
    path('holiday/<int:holiday_id>/delete/', holiday.HolidayDeleteView.as_view(), name='delete_holiday'),
    path('holiday/<int:holiday_id>/process/', holiday.process_holiday_request, name='process_holiday'),
    path('holiday/create/', holiday.create_holiday, name='create_holiday'),
    path('bank-holidays/', holiday.bank_holidays, name='bank_holidays'),
    
    path('job-title/create/', job_title.create_job_title, name='create_job_title'),
    path('job-title/<int:job_title_id>/delete/', job_title.delete_job_title, name='delete_job_title'),
    
    path('invitation/<int:invitation_id>/delete/', invitation.delete_invitation, name='delete_invitation'),
]
