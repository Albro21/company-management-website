# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.models import Company, JoinRequest


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
    join_request.user.join_company(join_request.company, role="employee")
    join_request.delete()
    return redirect('teams:team')

@require_http_methods(["POST"])
@login_required
@employer_required
def decline_join_request(request, request_id):
    join_request = JoinRequest.objects.get(id=request_id)
    join_request.delete()
    return redirect('teams:team')
