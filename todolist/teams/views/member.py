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

# Local apps
from common.decorators import parse_json_body
from main.forms import TaskForm
from main.models import Task
from timetracker.models import TimeEntry
from teams.forms import MemberForm
from teams.models import Member
from teams.decorators import employer_required


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

def process_member_bar_chart(member, start_date, end_date):
    date_labels = []
    project_time_by_date = defaultdict(lambda: defaultdict(int))
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%d/%m/%y")
        date_labels.append(date_str)
        daily_data = member.hours_spent_by_projects(current_date, member.company.projects.all())
        for project_title, duration in daily_data.items():
            project_time_by_date[project_title][date_str] += duration
        current_date += timedelta(days=1)

    project_titles = list(project_time_by_date.keys())

    project_color_map = {
        project.title: project.color
        for project in member.user.company.projects.filter(title__in=project_titles)
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

def process_member_donut_chart(member, start_date, end_date):
    project_time = defaultdict(int)
    
    current_date = start_date
    while current_date <= end_date:
        daily_data = member.hours_spent_by_projects(current_date, member.company.projects.all())
        for project_title, duration in daily_data.items():
            project_time[project_title] += duration
        current_date += timedelta(days=1)
    
    labels = list(project_time.keys())
    data = list(project_time.values())
    
    project_color_map = {
        project.title: project.color
        for project in member.user.company.projects.filter(title__in=labels)
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

def process_member_charts(request, member):
    try:
        data = json.loads(request.body)
        filter_option = data.get("filter")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    all_time_first_entry = (
        member.user.time_entries
        .filter(task__project__in=member.company.projects.all())
        .order_by('start_time')
        .first()
    )   
    
    date_range = get_date_range_from_filter(filter_option, all_time_first_entry)
    if not date_range:
        return JsonResponse({"success": False, "error": "Invalid filter or no time entries found"}, status=400)

    start_date, end_date = date_range

    bar_chart_data = process_member_bar_chart(member, start_date, end_date)
    donut_chart_data = process_member_donut_chart(member, start_date, end_date)
    
    time_entries = TimeEntry.objects.filter(
        user=member.user,
        task__project__in=member.user.company.projects.all(),
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
def member_analytics(request, member_id):
    
    member = get_object_or_404(Member, id=member_id, company=request.user.company)
    
    if request.method == 'POST':
        if request.POST.get('form_type') == 'edit_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('teams:member_analytics', member_id=member_id)
        else:
            return process_member_charts(request, member)
    else:
        
        assigned_tasks = Task.objects.filter(
            user=member.user,
            is_completed=False,
            project__in=member.company.projects.all()
        )
        
        context = {
            'member': member,
            'assigned_tasks': assigned_tasks,
            'form': TaskForm()
        }

        return render(request, 'teams/member_analytics.html', context)

@require_http_methods(["POST"])
@login_required
@employer_required
@parse_json_body
def assign_task(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    data = request.json_data
    category_ids = data.pop('categories', [])
    
    form = TaskForm(data)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = member.user
        task.save()
        
        if category_ids:
            task.categories.set(category_ids)
        
        return JsonResponse({'success': True, 'id': task.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors.as_json()}'}, status=400)

@require_http_methods(["PATCH"])
@login_required
@employer_required
@parse_json_body
def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    form = MemberForm(request.json_data, instance=member)

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors.as_json()}'}, status=400)

@login_required
def member_detail(request, member_id):
    member = request.user.member
    if member.id == member_id or member.is_employer:
        member = get_object_or_404(Member, id=member_id)
        return render(request, 'teams/member_detail.html', {'member': member})
    return HttpResponseForbidden("You do not have permission to view this page.")
