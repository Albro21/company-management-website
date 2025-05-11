# Standard libs
from collections import defaultdict
from datetime import date, timedelta
import json

# Django
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import render

# Local apps
from teams.models import VacationRequest
from main.forms import ProjectForm, TaskForm
from timetracker.models import TimeEntry


def get_date_range_from_filter(filter_option, all_time_first_entry):
    today = date.today()

    if filter_option == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif filter_option == "lastWeek":
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif filter_option == "month":
        start_date = today.replace(day=1)
        end_date = today
    elif filter_option == "lastMonth":
        current_year = today.year
        current_month = today.month
        if current_month == 1:
            start_date = date(current_year - 1, 12, 1)
        else:
            start_date = date(current_year, current_month - 1, 1)
        _, last_day = calendar.monthrange(start_date.year, start_date.month)
        end_date = start_date.replace(day=last_day)
    elif filter_option == "allTime":
        start_date = all_time_first_entry.start_time.date()
        end_date = today
    else:
        return None

    return start_date, end_date

def process_company_bar_chart(company, start_date, end_date):
    date_labels = []
    project_time_by_date = defaultdict(lambda: defaultdict(int))

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%y")
        date_labels.append(date_str)

        for member in company.members.all():
            daily_data = member.hours_spent_by_projects(current_date, company.projects.all())
            for project_title, duration in daily_data.items():
                project_time_by_date[project_title][date_str] += duration

        current_date += timedelta(days=1)

    project_titles = list(project_time_by_date.keys())

    project_color_map = {
        project.title: project.color
        for project in company.projects.filter(title__in=project_titles)
    }

    datasets = []
    for project_title in project_titles:
        data = [project_time_by_date[project_title].get(day, 0) for day in date_labels]
        datasets.append({
            "label": project_title,
            "data": data,
            "backgroundColor": project_color_map.get(project_title, "#000000")
        })

    return {
        "labels": date_labels,
        "datasets": datasets
    }

def process_company_donut_chart(company, start_date, end_date):
    project_time = defaultdict(int)

    current_date = start_date
    while current_date <= end_date:
        for member in company.members.all():
            daily_data = member.hours_spent_by_projects(current_date, company.projects.all())
            for project_title, duration in daily_data.items():
                project_time[project_title] += duration
        current_date += timedelta(days=1)

    labels = list(project_time.keys())
    data = list(project_time.values())

    project_color_map = {
        project.title: project.color
        for project in company.projects.filter(title__in=labels)
    }

    datasets = [{
        "data": data,
        "backgroundColor": [project_color_map.get(title, "#000000") for title in labels],
        "borderWidth": 1
    }]

    return {
        "labels": labels,
        "datasets": datasets
    }

def process_company_charts(request):
    try:
        data = json.loads(request.body)
        filter_option = data.get("filter")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    all_time_first_entry = (
        TimeEntry.objects
        .filter(task__project__in=request.user.company.projects.all())
        .order_by('start_time')
        .first()
    )

    date_range = get_date_range_from_filter(filter_option, all_time_first_entry)
    if not date_range:
        return JsonResponse({"success": False, "error": "Invalid filter or no time entries found"}, status=400)

    start_date, end_date = date_range
    company = request.user.company
    
    bar_chart_data = process_company_bar_chart(company, start_date, end_date)
    donut_chart_data = process_company_donut_chart(company, start_date, end_date)
    
    time_entries = TimeEntry.objects.filter(
        project__in=company.projects.all(),
        start_time__date__gte=start_date,
        start_time__date__lte=end_date
    )

    total_seconds = int(sum(entry.duration.total_seconds() for entry in time_entries))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    total_time = f"{hours}h {minutes}m {seconds}s"
    
    return JsonResponse({
        "success": True,
        "bar_chart_data": bar_chart_data,
        "donut_chart_data": donut_chart_data,
        "total_time": total_time
    }, status=200)

@login_required
def team(request):
    if not request.user.company:
        return render(request, 'teams/no_company.html')

    if request.method == 'POST':
        return process_company_charts(request)

    if request.user.member.is_employer:
        task_form = TaskForm(prefix="task")
        project_form = ProjectForm(prefix="project")
        context = {
            'company': request.user.company,
            'task_form': task_form,
            'project_form': project_form,
        }
        return render(request, 'teams/team.html', context)
    
    return render(request, 'teams/team.html', {'company': request.user.company})

@login_required
def calendar(request):
    vacations = VacationRequest.objects.filter(company=request.user.member.company, status='approved')

    events = []
    for vacation in vacations:
        events.append({
            'title': f"Vacation – {vacation.member.user.get_full_name() or vacation.member.user.username}",
            'start': str(vacation.start_date),
            'end': str(vacation.end_date + timedelta(days=1)),
            'extendedProps': {
                'type': 'Vacation',
                'member': vacation.member.user.get_full_name(),
                'start_date': vacation.start_date.strftime('%d/%m/%y'),
                'end_date': vacation.end_date.strftime('%d/%m/%y'),
                'days': vacation.number_of_days(),
                'reason': vacation.reason
            }
        })

    context = {
        'events_json': json.dumps(events, cls=DjangoJSONEncoder)
    }
    return render(request, 'teams/calendar.html', context)
