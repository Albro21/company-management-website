# Standard libs
from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
import json

# Django
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

# Local apps
from teams.models import Holiday
from main.forms import ProjectForm, TaskForm
from timetracker.models import TimeEntry
from teams.choices import HOLIDAY_TYPES


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
        _, last_day = monthrange(start_date.year, start_date.month)
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
        
        for employee in company.employees.all():
            daily_data = employee.hours_spent_by_projects(current_date, company.projects.all())
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
        for employee in company.employees.all():
            daily_data = employee.hours_spent_by_projects(current_date, company.projects.all())
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
        .filter(project__in=request.user.company_projects.all())
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
        if request.user.company.projects.exists():
            return process_company_charts(request)

    if request.user.is_employer:
        task_form = TaskForm(prefix="task")
        project_form = ProjectForm(prefix="project")
        context = {
            'company': request.user.company,
            'task_form': task_form,
            'project_form': project_form,
        }
        return render(request, 'teams/team.html', context)
    
    return render(request, 'teams/team.html', {'company': request.user.company})

color_map_self = {
    'holiday': '#99d1ff',
    'bank_holiday': '#9999ff',
    'sick_day': '#ffdd99',
}

color_map_others = {
    'holiday': 'rgba(153, 209, 255, 0.4)',
    'bank_holiday': 'rgba(153, 153, 255, 0.4)',
    'sick_day': 'rgba(255, 221, 153, 0.4)',
}

@login_required
def calendar(request):
    holidays = Holiday.objects.filter(company=request.user.company, status__in=['approved', 'pending', 'pending_edit', 'pending_delete'])

    all_holidays = []
    for holiday in holidays:
        users = holiday.users.all()
        
        # Title
        if users.count() == 1:
            title = users.first().get_full_name()
            if holiday.status == 'pending':
                title = f'{title} (pending)'
            elif holiday.status == 'pending_delete':
                title = f'{title} (pending delete)'
            elif holiday.status == 'pending_edit':
                title = f'{title} (pending edit)'
        elif request.user in users:
            title = f'{request.user.get_full_name()} and {users.count() - 1} more'
        else:
            title = f'{users.first().get_full_name()} and {users.count() - 1} more'
        
        # Color
        if request.user in holiday.users.all():
            color = color_map_self.get(holiday.type, '#cccccc')
        else:
            color = color_map_others.get(holiday.type, '#cccccc')
        
        all_holidays.append({
            'id': holiday.id,
            'title': title,
            'start': str(holiday.start_date),
            'end': str(holiday.end_date + timedelta(days=1)),
            'color': color,
            'textColor': 'black',
            'extendedProps': {
                'type': holiday.type,
                'type_display': holiday.get_type_display(),
                'reason': holiday.reason,
                'users': ', '.join([user.get_full_name() for user in holiday.users.all()]),
                'start_date': holiday.start_date.strftime('%d/%m/%y'),
                'end_date': holiday.end_date.strftime('%d/%m/%y'),
                'days': holiday.number_of_days,
            }
        })
    
    user_holidays = request.user.holidays.all()
    
    holidays = [date.strftime('%Y-%m-%d') for event in user_holidays.filter(type='holiday') for date in event.dates]
    bank_holidays = [date.strftime('%Y-%m-%d') for event in user_holidays.filter(type='bank_holiday') for date in event.dates]
    sick_days = [date.strftime('%Y-%m-%d') for event in user_holidays.filter(type='sick_day') for date in event.dates]

    context = {
        'all_holidays_json': json.dumps(all_holidays, cls=DjangoJSONEncoder),
        'user_holidays': user_holidays,
        'holiday_types': HOLIDAY_TYPES,
        'holidays': holidays,
        'bank_holidays': bank_holidays,
        'sick_days': sick_days
    }
    return render(request, 'teams/calendar.html', context)
