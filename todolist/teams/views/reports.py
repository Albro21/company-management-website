# Standard libs
import calendar
from datetime import datetime, timedelta

# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

# Local apps
from main.models import Project
from teams.decorators import employer_required


def seconds_to_hm(seconds):
    if seconds == 0:
        return "—"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

@login_required
@employer_required
def project_weekly_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_of_week = datetime.strptime(start_date_str, '%b %d, %Y')
        end_of_week = datetime.strptime(end_date_str, '%b %d, %Y')
    else:
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
    
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    company_employees = project.company.employees.all()

    employee_data = []
    totals_by_day = [0] * 7
    grand_total = 0

    for employee in company_employees:
        employee_full_name = employee.full_name
        daily_hours = []
        employee_total = 0

        for i, current_date in enumerate(week_dates):
            entries = employee.time_entries.filter(
                start_time__date=current_date,
                project=project
            )
            total_seconds = sum(entry.duration.total_seconds() for entry in entries)
            employee_total += total_seconds
            totals_by_day[i] += total_seconds
            daily_hours.append(seconds_to_hm(total_seconds))

        employee_data.append({
            "employee_name": employee_full_name,
            "employee_times": daily_hours,
            "employee_total": seconds_to_hm(employee_total)
        })
        grand_total += employee_total

    project_row = [seconds_to_hm(s) for s in totals_by_day]
    project_total = seconds_to_hm(grand_total)

    context = {
        'project': project,
        'week_dates': week_dates,
        'project_row': project_row,
        'project_total': project_total,
        'employee_data': employee_data,
        'start_date': start_of_week.strftime('%d/%m/%y'),
        'end_date': end_of_week.strftime('%d/%m/%y'),
    }

    return render(request, 'teams/project_weekly_report.html', context)

@login_required
@employer_required
def project_monthly_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str and end_date_str:
        start_of_month = datetime.strptime(start_date_str, '%b %d, %Y')
        end_of_month = datetime.strptime(end_date_str, '%b %d, %Y')
    else:
        today = datetime.today()
        start_of_month = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end_of_month = today.replace(day=last_day)

    month_days = (end_of_month - start_of_month).days + 1
    month_dates = [start_of_month + timedelta(days=i) for i in range(month_days)]

    company_employees = project.company.employees.all()

    employee_data = []
    totals_by_day = [0] * month_days
    grand_total = 0

    for employee in company_employees:
        employee_full_name = employee.full_name
        daily_hours = []
        employee_total = 0

        for i, current_date in enumerate(month_dates):
            entries = employee.time_entries.filter(
                start_time__date=current_date,
                project=project
            )
            total_seconds = sum(entry.duration.total_seconds() for entry in entries)
            employee_total += total_seconds
            totals_by_day[i] += total_seconds
            daily_hours.append(seconds_to_hm(total_seconds))

        employee_data.append({
            "employee_name": employee_full_name,
            "employee_times": daily_hours,
            "employee_total": seconds_to_hm(employee_total)
        })
        grand_total += employee_total

    project_row = [seconds_to_hm(s) for s in totals_by_day]
    project_total = seconds_to_hm(grand_total)

    context = {
        'project': project,
        'month_dates': month_dates,
        'project_row': project_row,
        'project_total': project_total,
        'employee_data': employee_data,
        'start_date': start_of_month.strftime('%d/%m/%y'),
        'end_date': end_of_month.strftime('%d/%m/%y'),
    }

    return render(request, 'teams/project_monthly_report.html', context)
