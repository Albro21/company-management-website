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


@login_required
def timetracker(request):
    user = request.user

    running_entry = user.time_entries.filter(end_time__isnull=True).order_by('-start_time').first()

    start_date_str = request.GET.get('start_date')
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())

    end_date = start_date + timedelta(days=6)
    week_dates = [start_date + timedelta(days=i) for i in range(7)]

    time_entries = TimeEntry.objects.filter(
        user=user,
        start_time__date__range=(start_date, end_date)
    ).order_by('start_time')

    grouped_entries = defaultdict(lambda: defaultdict(list))
    for entry in time_entries:
        grouped_entries[entry.project][entry.start_time.date()].append(entry)

    grouped_entries_cleaned = {
        project: dict(date_dict)
        for project, date_dict in grouped_entries.items()
    }

    context = {
        'running_entry': running_entry,
        'grouped_entries': grouped_entries_cleaned,
        'week_dates': week_dates,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'timetracker/timetracker.html', context)

@require_http_methods(["POST"])
@login_required
def start_timer(request):
    data = json.loads(request.body)

    project_id = data.get('project_id')
    project = get_object_or_404(Project, id=project_id)
    
    time_entry = TimeEntry.objects.create(
        user=request.user, 
        name=data.get('name'), 
        project=project,
    )
    
    time_entry.start()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def stop_timer(request):
    request.user.time_entries.filter(end_time__isnull=True).first().stop()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["PATCH"])
@login_required
@parse_json_body
def update_time_entry_times(request, time_entry_id):
    data = request.json_data

    if request.user.is_employer:
        time_entry = get_object_or_404(TimeEntry, id=time_entry_id, user__in=request.user.company.employees.all())
    else:
        time_entry = get_object_or_404(TimeEntry, id=time_entry_id, user=request.user)

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
