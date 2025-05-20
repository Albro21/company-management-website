# Standard libs
from collections import defaultdict
from datetime import datetime, date, timedelta
import json

# Django
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.dateparse import parse_date

# Local apps
from main.models import Project, Task
from common.decorators import parse_json_body
from .models import TimeEntry
from .forms import TimeEntryForm
from teams.decorators import employer_required


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:02}'

def process_form(request):
    time_entry_id = request.POST.get('time_entry_id')
    time_entry = get_object_or_404(TimeEntry, id=time_entry_id, user=request.user)

    post_data = request.POST.copy()

    start_time_str = post_data.get('start_time')
    end_time_str = post_data.get('end_time')
    date_str = post_data.get('date')

    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            post_data['start_time'] = datetime.combine(date, start_time)

        if end_time_str:
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            post_data['end_time'] = datetime.combine(date, end_time)

    task_id = post_data.get("task")
    if task_id:
        task = request.user.tasks.filter(id=task_id).first()
        if task:
            post_data['name'] = task.title
            post_data['project'] = task.project.id if task.project else ''

    time_entry_update_form = TimeEntryForm(post_data, instance=time_entry)

    if time_entry_update_form.is_valid():
        time_entry_update_form.save()
        return redirect("timetracker:timetracker")

@login_required
def timetracker(request):
    if request.method == 'POST':
        if request.POST.get('time_entry_id'):
            return process_form(request)
    
    user = request.user
    
    tasks = user.tasks.filter(is_completed=False)
    time_entries = user.time_entries.filter(end_time__isnull=False)

    running_entry = user.time_entries.filter(end_time__isnull=True).order_by('-start_time').first()

    grouped_time_entries = defaultdict(lambda: defaultdict(lambda: {'time_entries': [], 'total_duration': timedelta()}))

    for entry in time_entries:
        date_key = entry.end_time.strftime('%A, %d-%m')
        name_key = entry.name

        grouped_time_entries[date_key][name_key]['time_entries'].append(entry)
        grouped_time_entries[date_key][name_key]['total_duration'] += entry.duration
    
    def recursive_dict(d):
        if isinstance(d, defaultdict):
            d = {k: recursive_dict(v) for k, v in d.items()}
        return d

    grouped_time_entries = recursive_dict(grouped_time_entries)

    for date_key, name_groups in grouped_time_entries.items():
        date_total_duration = timedelta()
        
        for name_key, group in name_groups.items():
            date_total_duration += group['total_duration']
            group['total_duration'] = format_timedelta(group['total_duration'])

        grouped_time_entries[date_key]['date_total_duration'] = format_timedelta(date_total_duration)
    
    context = {
        'tasks': tasks,
        'grouped_time_entries': grouped_time_entries,
        'running_entry': running_entry,
    }

    return render(request, 'timetracker/timetracker.html', context)

@require_http_methods(["POST"])
@login_required
def start_timer(request):
    data = json.loads(request.body)
    task_id = data.get('task_id')

    if task_id:
        task = get_object_or_404(Task, id=task_id)
        
        time_entry = TimeEntry.objects.create(
            user=request.user, 
            task=task, 
            name=task.title, 
            project=task.project,
        )
    else:
        name = data.get('name')
        project_id = data.get('project_id')
        project = get_object_or_404(Project, id=project_id) if project_id else None
        
        time_entry = TimeEntry.objects.create(
            user=request.user, 
            name=name, 
            project=project,
        )
    
    time_entry.start()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def stop_timer(request):
    request.user.time_entries.filter(end_time__isnull=True).first().stop()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["DELETE"])
@login_required
def delete_time_entry(request, time_entry_id):
    time_entry = get_object_or_404(TimeEntry, id=time_entry_id, user=request.user)
    time_entry.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def duplicate_time_entry(request, time_entry_id):
    original = get_object_or_404(TimeEntry, id=time_entry_id, user=request.user)

    TimeEntry.objects.create(
        user=original.user,
        task=original.task,
        name=original.name,
        project=original.project,
        start_time=original.start_time,
        end_time=original.end_time,
    )

    return JsonResponse({'success': True}, status=200)

@login_required
@employer_required
def timesheet(request):
    start_date_str = request.GET.get('start_date')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
    
    end_date = start_date + timedelta(days=6)
    
    week_dates = [start_date + timedelta(days=i) for i in range(7)]

    time_entries = TimeEntry.objects.filter(
        project__in=request.user.company.projects.all(),
        start_time__date__range=(start_date, end_date)
    ).order_by('start_time')
    
    grouped_entries = defaultdict(lambda: defaultdict(list))

    for entry in time_entries:
        project = entry.project
        entry_date = entry.start_time.date()
        grouped_entries[project][entry_date].append(entry)

    # Convert both levels of defaultdict to regular dicts
    grouped_entries_cleaned = {
        project: dict(date_dict)
        for project, date_dict in grouped_entries.items()
    }
    
    context = {
        'grouped_entries': grouped_entries_cleaned,
        'week_dates': week_dates,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'timetracker/timesheet.html', context)

@require_http_methods(["PATCH"])
@login_required
@employer_required
@parse_json_body
def update_time_entry_times(request, time_entry_id):
    data = request.json_data

    time_entry = get_object_or_404(TimeEntry, id=time_entry_id, user__in=request.user.company.employees.all())

    def combine_date_and_time(base_datetime, time_str):
        new_time = datetime.strptime(str(time_str), "%H:%M").time()
        naive_dt = datetime.combine(base_datetime.date(), new_time)
        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
        return aware_dt

    new_start = combine_date_and_time(time_entry.start_time, data.get('start_time'))
    new_end = combine_date_and_time(time_entry.start_time, data.get('end_time'))

    if new_end <= new_start:
        new_end += timedelta(days=1)

    time_entry.start_time = new_start
    time_entry.end_time = new_end
    time_entry.save()

    return JsonResponse({'success': True}, status=200)
