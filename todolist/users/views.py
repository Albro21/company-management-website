# Standard libs
import calendar
from collections import defaultdict
from datetime import date, timedelta
from django.db import IntegrityError
import pytz
import json

# Django
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

# Local apps
from common.decorators import parse_json_body
from timetracker.models import TimeEntry
from main.models import Task


User = get_user_model()

@require_http_methods(['GET'])
@login_required
def settings(request):
    return render(request, 'users/settings.html')

@require_http_methods(['POST'])
@login_required
def edit_user(request):
    try:
        user = request.user
            
        for key, value in request.POST.items():
            if value:
                setattr(user, key, value)

        for key, value in request.FILES.items():
            if value:
                setattr(user, key, value)
        
        user.save()
        return JsonResponse({'success': True}, status=200)
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'The username already exists'}, status=400)

@login_required
def filter_chart(request):
    user = request.user

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filter_option = data.get('filter')
            project_title = data.get('project_title')
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

        tasks = user.tasks.filter(is_completed=True)

        if project_title:
            project = user.all_projects.filter(title=project_title).first()
            if project:
                tasks = tasks.filter(project=project)
            else:
                return JsonResponse({"success": False, "error": "Project not found"}, status=404)

        # Filter by date range
        if filter_option == "week":
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = start_date + timedelta(days=6)
        elif filter_option == "lastWeek":
            start_date = date.today() - timedelta(days=date.today().weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif filter_option == "month":
            start_date = date.today().replace(day=1)
            end_date = date.today()
        elif filter_option == "lastMonth":
            current_year = date.today().year
            current_month = date.today().month
            if current_month == 1:
                start_date = date(current_year - 1, 12, 1)
            else:
                start_date = date(current_year, current_month - 1, 1)
            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            end_date = start_date.replace(day=last_day)
        elif filter_option == "allTime":
            try:
                start_date = tasks.earliest("completed_at").completed_at
            except ObjectDoesNotExist:
                start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = date.today()
        else:
            return JsonResponse({"success": False, "error": "Invalid filter option"}, status=400)

        # Filter tasks by date
        filtered_tasks = tasks.filter(completed_at__gte=start_date)

        # Generate date list for the chart
        date_list = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Prepare chart data
        task_counts = filtered_tasks.values("completed_at").annotate(count=Count("id"))
        task_data = {entry["completed_at"]: entry["count"] for entry in task_counts}

        chart_labels = [d.strftime("%d.%m") for d in date_list]
        chart_data = [task_data.get(d, 0) for d in date_list]

        return JsonResponse({"success": True, "labels": chart_labels, "data": chart_data}, status=200)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@require_http_methods(["PATCH"])
@login_required
def switch_theme(request):
    user = request.user
    user.switch_theme()
    return JsonResponse({'success': True, 'theme': user.theme})

@require_http_methods(["PATCH"])
@parse_json_body
def set_timezone(request):
    if request.user.is_authenticated:
        tz = request.json_data.get("timezone")
        if tz in pytz.common_timezones:
            request.user.timezone = tz
            request.user.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "User not authenticated"}, status=400)

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

    return start_date, end_date

def process_donut_time_chart(user, start_date, end_date):
    project_time = defaultdict(int)
    
    current_date = start_date
    while current_date <= end_date:
        daily_data = user.hours_spent_by_projects(current_date, user.company.projects.all())
        for project_title, duration in daily_data.items():
            project_time[project_title] += duration
        current_date += timedelta(days=1)
    
    labels = list(project_time.keys())
    data = list(project_time.values())
    
    project_color_map = {
        project.title: project.color
        for project in user.company.projects.filter(title__in=labels)
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

def process_bar_time_chart(user, start_date, end_date):
    date_labels = []
    project_time_by_date = defaultdict(lambda: defaultdict(int))
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%y")
        date_labels.append(date_str)
        daily_data = user.hours_spent_by_projects(current_date, user.company.projects.all())
        for project_title, duration in daily_data.items():
            project_time_by_date[project_title][date_str] += duration
        current_date += timedelta(days=1)

    project_titles = list(project_time_by_date.keys())

    project_color_map = {
        project.title: project.color
        for project in user.company.projects.filter(title__in=project_titles)
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

def process_donut_task_chart(user, start_date, end_date):
    project_task_count = defaultdict(int)

    tasks = Task.objects.filter(
        user=user,
        project__in=user.company.projects.all(),
        completed_at__gte=start_date,
        completed_at__lte=end_date
    )

    for task in tasks:
        project_task_count[task.project.title] += 1

    labels = list(project_task_count.keys())
    data = list(project_task_count.values())

    project_color_map = {
        project.title: project.color
        for project in user.company.projects.filter(title__in=labels)
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

def process_bar_task_chart(user, start_date, end_date):
    date_labels = []
    project_tasks_by_date = defaultdict(lambda: defaultdict(int))

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%y")
        date_labels.append(date_str)

        tasks = Task.objects.filter(
            user=user,
            project__in=user.company.projects.all(),
            completed_at=current_date
        )

        for task in tasks:
            project_tasks_by_date[task.project.title][date_str] += 1

        current_date += timedelta(days=1)

    project_titles = list(project_tasks_by_date.keys())

    project_color_map = {
        project.title: project.color
        for project in user.company.projects.filter(title__in=project_titles)
    }

    datasets = []
    for project_title in project_titles:
        data = [project_tasks_by_date[project_title].get(day, 0) for day in date_labels]
        datasets.append({
            "label": project_title,
            "data": data,
            "backgroundColor": project_color_map.get(project_title, "#000000")
        })

    return {
        "labels": date_labels,
        "datasets": datasets
    }

def calculate_total_time(user, start_date, end_date):
    time_entries = TimeEntry.objects.filter(
        user=user,
        task__project__in=user.company.projects.all(),
        start_time__date__gte=start_date,
        start_time__date__lte=end_date
    )

    total_seconds = int(sum(entry.duration.total_seconds() for entry in time_entries))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}h {minutes}m {seconds}s"

def calculate_total_tasks(user, start_date, end_date):
    tasks = Task.objects.filter(
        user=user,
        project__in=user.company.projects.all(),
        completed_at__gte=start_date,
        completed_at__lte=end_date
    )

    return tasks.count()

@require_http_methods(["POST"])
@login_required
@parse_json_body
def user_analytics(request, user_id):
    user = get_object_or_404(User, id=user_id, company=request.user.company)
    
    if not user.company:
        return JsonResponse({'success': False, 'error': 'Current user does not belong to any company.'}, status=400)
    
    data = request.json_data
    filter_option = data.get("filter")
    
    all_time_first_entry = user.time_entries.filter(task__project__in=user.company.projects.all()).order_by('start_time').first()
    start_date, end_date = get_date_range_from_filter(filter_option, all_time_first_entry)
    
    donut_time_chart_data = process_donut_time_chart(user, start_date, end_date)
    bar_time_chart_data = process_bar_time_chart(user, start_date, end_date)
    donut_task_chart_data = process_donut_task_chart(user, start_date, end_date)
    bar_task_chart_data = process_bar_task_chart(user, start_date, end_date)
    
    total_time = calculate_total_time(user, start_date, end_date)
    total_tasks = calculate_total_tasks(user, start_date, end_date)
    
    context = {
        'donut_time_chart_data': donut_time_chart_data,
        'bar_time_chart_data': bar_time_chart_data,
        'donut_task_chart_data': donut_task_chart_data,
        'bar_task_chart_data': bar_task_chart_data,
        'total_time': total_time,
        'total_tasks': total_tasks,
    }
    
    return JsonResponse({'success': True, 'data': context}, status=200)
