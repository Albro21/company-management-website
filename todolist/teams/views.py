from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods

from main.forms import ProjectForm, TaskForm
from main.models import Project
from .forms import CompanyForm, RoleForm, MemberForm
from .models import Company, Member, JoinRequest, Role


@login_required
def team(request):
    if not request.user.profile.company:
        return render(request, 'teams/no_company.html')

    task_form = TaskForm(prefix="task")
    project_form = ProjectForm(prefix="project")

    if request.method == 'POST':
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