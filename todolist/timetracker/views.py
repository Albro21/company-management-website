from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from collections import defaultdict
from datetime import datetime, timedelta
import json

from main.models import Project, Task
from .models import TimeEntry
from .forms import TimeEntryForm


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:02}'

def process_form(request):
    time_entry_id = request.POST.get('time_entry_id')
    time_entry = get_object_or_404(TimeEntry, id=time_entry_id)

    post_data = request.POST.copy()

    start_time_str = post_data.get('start_time')
    end_time_str = post_data.get('end_time')

    if start_time_str:
        start_datetime = datetime.combine(
            time_entry.start_time.date(),
            datetime.strptime(start_time_str, "%H:%M").time()
        )
        post_data['start_time'] = start_datetime

    if end_time_str:
        end_datetime = datetime.combine(
            time_entry.end_time.date(),
            datetime.strptime(end_time_str, "%H:%M").time()
        )
        post_data['end_time'] = end_datetime

    task_id = post_data.get("task")
    if task_id:
        task = request.user.tasks.filter(id=task_id).first()
        if task:
            post_data['name'] = task.title
            post_data['project'] = task.project.id if task.project else ''

    time_entry_update_form = TimeEntryForm(post_data, instance=time_entry)

    if time_entry_update_form.is_valid():
        time_entry_update_form.save()
        return HttpResponseRedirect(reverse('timetracker:timetracker'))

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
    return JsonResponse({'success': True,})

@require_http_methods(["POST"])
def stop_timer(request):
    request.user.time_entries.filter(end_time__isnull=True).first().stop()
    return JsonResponse({'success': True})

@require_http_methods(["DELETE"])
def delete_time_entry(request, time_entry_id):
    time_entry = get_object_or_404(TimeEntry, id=time_entry_id)
    time_entry.delete()
    return JsonResponse({'success': True})