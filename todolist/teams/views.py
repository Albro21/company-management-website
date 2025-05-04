# Standard libs
import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
import json

# Django
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

# Local apps
from common.decorators import parse_json_body
from main.forms import ProjectForm, TaskForm
from main.models import Project, Task
from timetracker.models import TimeEntry
from .forms import CompanyForm, JobTitleForm, MemberForm
from .models import Company, Member, JoinRequest, JobTitle
from .decorators import employer_required


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

def seconds_to_hms(seconds):
    if seconds == 0:
        return "—"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            request.user.join_company(company)
            Member.objects.create(
                company=company,
                user=request.user
            )
            return redirect('teams:team') 
        
        return render(request, 'teams/create_company.html', {'form': form})
    
    else:
        form = CompanyForm()
    
    return render(request, 'teams/create_company.html', {'form': form})

@require_http_methods(["POST"])
@login_required
def create_join_request(request):
    name = request.POST.get('company_name')
    try:
        company = Company.objects.get(name__iexact=name)
        
        existing_request = JoinRequest.objects.filter(user=request.user, company=company).first()
        
        if existing_request:
            messages.error(request, f"You already requested to join {company.name}.")
        else:
            join_request = JoinRequest(user=request.user, company=company)
            join_request.save()
            messages.success(request, f"Join request for {company.name} has been submitted.")

        return redirect('teams:team')
    except Company.DoesNotExist:
        messages.error(request, f"No company found with the name: {name}")
        return redirect('teams:team')

@require_http_methods(["POST"])
@login_required
@employer_required
def accept_join_request(request, request_id):
    join_request = JoinRequest.objects.get(id=request_id)
    Member.objects.create(
        company=join_request.company,
        user=join_request.user
    )
    join_request.user.join_company(join_request.company)
    join_request.delete()
    return redirect('teams:team')

@require_http_methods(["POST"])
@login_required
@employer_required
def decline_join_request(request, request_id):
    join_request = JoinRequest.objects.get(id=request_id)
    join_request.delete()
    return redirect('teams:team')

@login_required
@employer_required
def settings(request):
    company = request.user.company

    company_form = CompanyForm(instance=company, prefix='company')
    job_title_form = JobTitleForm(prefix='job_title')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'company':
            company_form = CompanyForm(request.POST, request.FILES, instance=company, prefix='company')
            if company_form.is_valid():
                company_form.save()
                messages.success(request, 'Company updated successfully.')
                return redirect('teams:settings')

        elif form_type == 'job_title':
            job_title_form = JobTitleForm(request.POST, prefix='job_title')
            if job_title_form.is_valid():
                new_job_title = job_title_form.save(commit=False)
                new_job_title.company = company
                new_job_title.save()
                messages.success(request, 'Job title added successfully.')
                return redirect('teams:settings')
            else:
                messages.error(request, 'Please correct the errors below.')

    context = {
        'company': company,
        'company_form': company_form,
        'job_title_form': job_title_form,
    }

    return render(request, 'teams/settings.html', context)

@require_http_methods(["POST"])
@login_required
@employer_required
@parse_json_body
def create_job_title(request):
    job_title = JobTitle.objects.create(**request.json_data, company=request.user.company)
    return JsonResponse({'success': True, 'id': job_title.id}, status=201)

@require_http_methods(["DELETE"])
@login_required
@employer_required
def delete_job_title(request, job_title_id):
    try:
        job_title = get_object_or_404(JobTitle, id=job_title_id, company=request.user.company)
        job_title.delete()
        return JsonResponse({"success": True}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "error": "Job title not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

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
            daily_hours.append(seconds_to_hms(total_seconds))

        member_data.append({
            "member_name": user_full_name,
            "member_times": daily_hours,
            "member_total": seconds_to_hms(user_total)
        })
        grand_total += user_total

    project_row = [seconds_to_hms(s) for s in totals_by_day]
    project_total = seconds_to_hms(grand_total)

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

@require_http_methods(["POST"])
@login_required
def leave_company(request):
    request.user.leave_company()
    messages.success(request, "You have left the company.")
    return redirect("teams:team")

@require_http_methods(["POST"])
@login_required
@employer_required
def kick_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    user = member.user
    user.leave_company()
    messages.success(request, f"{user.full_name} was kicked from the company.")
    return redirect("teams:team")

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