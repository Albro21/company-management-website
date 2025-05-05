# Standard libs
import calendar
from datetime import date, timedelta
import pytz
import json

# Django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

# Local apps
from .forms import ProfileForm
from common.decorators import parse_json_body


@login_required
def settings(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()

            if 'profile_picture' in request.FILES:
                profile = request.user
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/settings.html', {'form': form})


@login_required
def profile(request):
    tasks = request.user.tasks.all()

    completed_tasks = tasks.filter(is_completed=True).count()
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=date.today()).count()
    remaining_tasks = tasks.filter(is_completed=False).count()

    project_labels = []
    project_data = []
    project_colors = []

    for project in request.user.all_projects:
        completed_task_count = project.tasks.filter(is_completed=True).count()
        project_labels.append(project.title)
        project_data.append(completed_task_count)
        project_colors.append(project.color)

    context = {
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'remaining_tasks': remaining_tasks,
        'project_data': project_data,
        'project_labels': project_labels,
        'project_data': project_data,
        'project_colors': project_colors,
    }
    
    return render(request, 'users/profile.html', context)


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