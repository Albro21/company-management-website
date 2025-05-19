# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods

# Local apps
from common.decorators import parse_json_body
from main.forms import TaskForm
from main.models import Task
from teams.models import Document, JobTitle
from teams.decorators import employer_required


User = get_user_model()

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
    employee = get_object_or_404(User, id=user_id)
    if user.id == user_id or user.is_employer and user.company == employee.company:
        selected_tab = request.GET.get('tab', 'information')
        
        assigned_tasks = Task.objects.filter(
            user=employee,
            is_completed=False,
            project__in=employee.company.projects.all()
        )
        
        context = {
            'employee': employee,
            'assigned_tasks': assigned_tasks,
            'selected_tab': selected_tab,
            'document_types': Document.DOCUMENT_TYPES
        }
        
        return render(request, 'teams/employee_detail.html', context)
    return HttpResponseForbidden("You do not have permission to view this page.")

@require_http_methods(["POST"])
@login_required
def kick_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id, company=request.user.company)

    employee.leave_company()
    messages.success(request, f"{employee.get_full_name() } was kicked from the company.")
    return redirect("teams:team")
