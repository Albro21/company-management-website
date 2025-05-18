# Standard libs
import calendar
from collections import defaultdict
from datetime import date, timedelta
import json

# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

# Local apps
from common.decorators import parse_json_body
from main.forms import TaskForm
from main.models import Task
from timetracker.models import TimeEntry
from teams.models import Document, JobTitle
from teams.decorators import employer_required


User = get_user_model()

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

def process_employee_bar_chart(employee, start_date, end_date):
    date_labels = []
    project_time_by_date = defaultdict(lambda: defaultdict(int))
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%y")
        date_labels.append(date_str)
        daily_data = employee.hours_spent_by_projects(current_date, employee.company.projects.all())
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

def process_employee_donut_chart(employee, start_date, end_date):
    project_time = defaultdict(int)
    
    current_date = start_date
    while current_date <= end_date:
        daily_data = employee.hours_spent_by_projects(current_date, employee.company.projects.all())
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

def process_employee_charts(request, employee):
    try:
        data = json.loads(request.body)
        filter_option = data.get("filter")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    all_time_first_entry = (
        user.time_entries
        .filter(task__project__in=employee.company.projects.all())
        .order_by('start_time')
        .first()
    )   
    
    date_range = get_date_range_from_filter(filter_option, all_time_first_entry)
    if not date_range:
        return JsonResponse({"success": False, "error": "Invalid filter or no time entries found"}, status=400)

    start_date, end_date = date_range

    bar_chart_data = process_employee_bar_chart(employee, start_date, end_date)
    donut_chart_data = process_employee_donut_chart(employee, start_date, end_date)
    
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
    total_time = f"{hours}h {minutes}m {seconds}s"
    
    return JsonResponse({
        "success": True,
        "bar_chart_data": bar_chart_data,
        "donut_chart_data": donut_chart_data,
        "total_time": total_time
    }, status=200)

@login_required
@employer_required
def employee_analytics(request, employee_id):
    
    employee = get_object_or_404(User, id=employee_id, company=request.user.company)
    
    if request.method == 'POST':
        if request.POST.get('form_type') == 'edit_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('teams:employee_analytics', employee_id=employee_id)
        else:
            return process_employee_charts(request, employee)
    else:
        
        assigned_tasks = Task.objects.filter(
            user=employee,
            is_completed=False,
            project__in=employee.company.projects.all()
        )
        
        context = {
            'employee': employee,
            'assigned_tasks': assigned_tasks,
            'form': TaskForm()
        }

        return render(request, 'teams/employee_analytics.html', context)

@require_http_methods(["POST"])
@login_required
@employer_required
@parse_json_body
def assign_task(request, employee_id):
    data = request.json_data
    category_ids = data.pop('categories', [])
    
    form = TaskForm(data)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = get_object_or_404(User, id=employee_id)
        task.save()
        
        if category_ids:
            task.categories.set(category_ids)
        
        return JsonResponse({'success': True, 'id': task.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors.as_json()}'}, status=400)

@require_http_methods(["PATCH"])
@login_required
@parse_json_body
def edit_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id)
    data = request.json_data
    
    for key, value in data.items():
        if value:
            if key == 'supervisor':
                value = get_object_or_404(User, id=value)
            elif key == 'job_title':
                value = get_object_or_404(JobTitle, id=value)
            
            setattr(employee, key, value)
    
    employee.save()
    return JsonResponse({'success': True}, status=200)


@login_required
def employee_detail(request, user_id):
    user = request.user
    if user.id == user_id or user.is_employer:
        employee = get_object_or_404(User, id=user_id)
        selected_tab = request.GET.get('tab', 'information')
        return render(request, 'teams/employee_detail.html', {'employee': employee, 'selected_tab': selected_tab, 'document_types': Document.DOCUMENT_TYPES})
    return HttpResponseForbidden("You do not have permission to view this page.")
