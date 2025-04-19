from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods

import calendar
from collections import defaultdict
from datetime import date, timedelta
import json

from main.forms import ProjectForm, TaskForm
from main.models import Project
from timetracker.models import TimeEntry
from .forms import CompanyForm, RoleForm, MemberForm
from .models import Company, Member, JoinRequest, Role


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

def process_forms(request):
    form_type = request.POST.get('form_type')
    
    if form_type == 'update_member':
            member_id = request.POST.get('member_id')
            member = Member.objects.get(id=member_id)
            member_update_form = MemberForm(request.POST, instance=member, prefix=f"member_{member_id}")
            if member_update_form.is_valid():
                member_update_form.save()
                return HttpResponseRedirect(reverse('teams:team'))

    elif form_type == 'update_project':
        project_id = request.POST.get('project_id')
        project = Project.objects.get(id=project_id)
        project_update_form = ProjectForm(request.POST, instance=project, prefix=f"project_{project_id}")
        if project_update_form.is_valid():
            project_update_form.save()
            return HttpResponseRedirect(reverse('teams:team'))

    elif form_type == 'create_task':
        member_id = request.POST.get('member_id')
        user = Member.objects.get(id=member_id).user
        task_create_form = TaskForm(request.POST, prefix="task")
        if task_create_form.is_valid():
            task = task_create_form.save(commit=False)
            task.user = user
            task.save()
            return HttpResponseRedirect(reverse('teams:team'))

    elif form_type == 'create_project':
        project_create_form = ProjectForm(request.POST, prefix="project")
        if project_create_form.is_valid():
            project = project_create_form.save(commit=False)
            project.created_by = request.user
            project.company = request.user.profile.company
            project.save()
            project.assigned_users.set(User.objects.filter(profile__company=request.user.profile.company))
            return HttpResponseRedirect(reverse('teams:team'))

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
        return JsonResponse({"success": False, "error": "Invalid JSON"})

    all_time_first_entry = (
        TimeEntry.objects
        .filter(task__project__in=request.user.profile.company.projects.all())
        .order_by('start_time')
        .first()
    )

    date_range = get_date_range_from_filter(filter_option, all_time_first_entry)
    if not date_range:
        return JsonResponse({"success": False, "error": "Invalid filter or no time entries found"})

    start_date, end_date = date_range
    company = request.user.profile.company
    
    bar_chart_data = process_company_bar_chart(company, start_date, end_date)
    donut_chart_data = process_company_donut_chart(company, start_date, end_date)
    
    return JsonResponse({
        "success": True,
        "bar_chart_data": bar_chart_data,
        "donut_chart_data": donut_chart_data
    })

@login_required
def team(request):
    if not request.user.profile.company:
        return render(request, 'teams/no_company.html')

    task_form = TaskForm(prefix="task")
    project_form = ProjectForm(prefix="project")

    if request.method == 'POST':
        if request.POST.get('form_type'):
            return process_forms(request)
        else:
            return process_company_charts(request)

    context = {
        'company': request.user.profile.company,
        'task_form': task_form,
        'project_form': project_form,
    }

    return render(request, 'teams/team.html', context)

@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            request.user.profile.set_company(company)
            Member.objects.create(
                company=company,
                user=request.user
            )
            return redirect('teams:team') 
        
        return render(request, 'teams/create_company.html', {'form': form})
    
    else:
        form = CompanyForm()
    
    return render(request, 'teams/create_company.html', {'form': form})

@require_POST
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

@require_POST
@login_required
def accept_join_request(request, request_id):
    try:
        join_request = JoinRequest.objects.get(id=request_id)
        Member.objects.create(
            company=join_request.company,
            user=join_request.user
        )
        join_request.user.profile.set_company(join_request.company)
        join_request.delete()
        return JsonResponse({'success': True})
    except JoinRequest.DoesNotExist:
        return JsonResponse({'success': False})

@require_POST
@login_required
def decline_join_request(request, request_id):
    try:
        join_request = JoinRequest.objects.get(id=request_id)
        join_request.delete()
        return JsonResponse({'success': True})
    except JoinRequest.DoesNotExist:
        return JsonResponse({'success': False})

@login_required
def settings(request):
    company = request.user.profile.company

    company_form = CompanyForm(instance=company, prefix='company')
    role_form = RoleForm(prefix='role')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'company':
            company_form = CompanyForm(request.POST, request.FILES, instance=company, prefix='company')
            if company_form.is_valid():
                company_form.save()
                messages.success(request, 'Company updated successfully.')
                return redirect('teams:settings')

        elif form_type == 'role':
            role_form = RoleForm(request.POST, prefix='role')
            if role_form.is_valid():
                new_role = role_form.save(commit=False)
                new_role.company = company
                new_role.save()
                messages.success(request, 'Role added successfully.')
                return redirect('teams:settings')
            else:
                messages.error(request, 'Please correct the errors below.')

    context = {
        'company': company,
        'company_form': company_form,
        'role_form': role_form,
    }

    return render(request, 'teams/settings.html', context)

@require_http_methods(["DELETE"])
@login_required
def delete_role(request, role_id):
    try:
        role = get_object_or_404(Role, id=role_id, company=request.user.profile.company)
        role.delete()
        return JsonResponse({"success": True}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "error": "Role not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

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
        for project in member.user.projects.filter(title__in=project_titles)
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
        for project in member.user.projects.filter(title__in=labels)
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
        return JsonResponse({"success": False, "error": "Invalid JSON"})

    all_time_first_entry = (
        member.user.time_entries
        .filter(task__project__in=member.company.projects.all())
        .order_by('start_time')
        .first()
    )   
    
    date_range = get_date_range_from_filter(filter_option, all_time_first_entry)
    if not date_range:
        return JsonResponse({"success": False, "error": "Invalid filter or no time entries found"})

    start_date, end_date = date_range

    bar_chart_data = process_member_bar_chart(member, start_date, end_date)
    donut_chart_data = process_member_donut_chart(member, start_date, end_date)
    
    return JsonResponse({
        "success": True,
        "bar_chart_data": bar_chart_data,
        "donut_chart_data": donut_chart_data
    })

@login_required
def member_analytics(request, member_id):
    
    member = get_object_or_404(Member, id=member_id, company=request.user.profile.company)
    
    if request.method == 'POST':
        return process_member_charts(request, member)
    else:
        context = {
            'member': member
        }

        return render(request, 'teams/member_analytics.html', context)
