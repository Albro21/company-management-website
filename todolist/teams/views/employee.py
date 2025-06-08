# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.views.decorators.http import require_http_methods

# Local apps
from common.decorators import parse_json_body
from main.forms import TaskForm
from main.models import Task
from teams.models import Document, JobTitle, Invitation
from teams.decorators import employer_required


User = get_user_model()

@require_http_methods(["POST"])
def invite_employee(request):
    if not request.user.is_employer:
        return HttpResponseForbidden("You do not have permission to invite employees.")
    
    email = request.POST.get('email')

    # Delete any existing invitation for the email, if any
    Invitation.objects.filter(email=email).delete()

    # Generate unique token
    token = get_random_string(16)
    while Invitation.objects.filter(token=token).exists():
        token = get_random_string(16)

    invite_url = request.build_absolute_uri(f"/accounts/register/?invite={token}")

    subject = f"You're invited to join {request.user.company.name}"
    message = (
        f"You've been invited to join {request.user.company.name}.\n\n"
        f"Click the link below to accept the invitation:\n{invite_url}\n\n"
        "If you did not expect this invitation, please ignore this email."
    )

    email_message = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    email_message.send()
    
    # Create and save the invitation
    Invitation.objects.create(
        email=email,
        token=token,
        company=request.user.company,
        invited_by=request.user
    )

    return redirect("teams:team")

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

    # Authorization check
    if not (user.id == user_id or (user.is_employer and user.company == employee.company)):
        return HttpResponseForbidden("You do not have permission to view this page.")

    selected_tab = request.GET.get('tab', 'information')

    # Only query tasks if the employee has a company
    assigned_tasks = Task.objects.filter(
        user=employee,
        is_completed=False,
        project__company=employee.company
    ) if employee.company else Task.objects.none()

    context = {
        'employee': employee,
        'assigned_tasks': assigned_tasks,
        'selected_tab': selected_tab,
        'document_types': Document.DOCUMENT_TYPES
    }

    return render(request, 'teams/employee_detail.html', context)

@require_http_methods(["POST"])
@login_required
def kick_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id, company=request.user.company)

    employee.leave_company()
    messages.success(request, f"{employee.get_full_name() } was kicked from the company.")
    return redirect("teams:team")
