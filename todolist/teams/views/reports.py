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

    company_members = project.company.members.all()

    member_data = []
    totals_by_day = [0] * 7
    grand_total = 0

    for member in company_members:
        user = member.user
        user_full_name = user.full_name
        daily_hours = []
        user_total = 0

        for i, current_date in enumerate(week_dates):
            entries = user.time_entries.filter(
                start_time__date=current_date,
                project=project
            )
            total_seconds = sum(entry.duration.total_seconds() for entry in entries)
            user_total += total_seconds
            totals_by_day[i] += total_seconds
            daily_hours.append(seconds_to_hm(total_seconds))

        member_data.append({
            "member_name": user_full_name,
            "member_times": daily_hours,
            "member_total": seconds_to_hm(user_total)
        })
        grand_total += user_total

    project_row = [seconds_to_hm(s) for s in totals_by_day]
    project_total = seconds_to_hm(grand_total)

    context = {
        'project': project,
        'week_dates': week_dates,
        'project_row': project_row,
        'project_total': project_total,
        'member_data': member_data,
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

    company_members = project.company.members.all()

    member_data = []
    totals_by_day = [0] * month_days
    grand_total = 0

    for member in company_members:
        user = member.user
        user_full_name = user.full_name
        daily_hours = []
        user_total = 0

        for i, current_date in enumerate(month_dates):
            entries = user.time_entries.filter(
                start_time__date=current_date,
                project=project
            )
            total_seconds = sum(entry.duration.total_seconds() for entry in entries)
            user_total += total_seconds
            totals_by_day[i] += total_seconds
            daily_hours.append(seconds_to_hm(total_seconds))

        member_data.append({
            "member_name": user_full_name,
            "member_times": daily_hours,
            "member_total": seconds_to_hm(user_total)
        })
        grand_total += user_total

    project_row = [seconds_to_hm(s) for s in totals_by_day]
    project_total = seconds_to_hm(grand_total)

    context = {
        'project': project,
        'month_dates': month_dates,
        'project_row': project_row,
        'project_total': project_total,
        'member_data': member_data,
        'start_date': start_of_month.strftime('%d/%m/%y'),
        'end_date': end_of_month.strftime('%d/%m/%y'),
    }

    return render(request, 'teams/project_monthly_report.html', context)
