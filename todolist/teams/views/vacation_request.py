# Standard libs
from datetime import datetime

# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.forms import VacationRequestForm
from teams.models import VacationRequest
from common.decorators import parse_json_body


@require_http_methods(["POST"])
@login_required
@parse_json_body
def create_vacation_request(request):
    data = request.json_data
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    days_requested = (end_date - start_date).days + 1
    
    if start_date > end_date:
        return JsonResponse({'success': False, 'error': 'Start date must be before end date.'}, status=400)
    
    if request.user.member.remaining_vacation_days < days_requested:
        return JsonResponse({'success': False, 'error': 'Your vacation exceeds your remaining annual vacation days.'}, status=400)

    vacation_request_form = VacationRequestForm(data=data)
    if vacation_request_form.is_valid():
        vacation_request = vacation_request_form.save(commit=False)
        vacation_request.company = request.user.company
        vacation_request.member = request.user.member
        
        if request.user.member.is_employer:
            vacation_request.status = "approved"
        else:
            vacation_request.status = "pending"
        
        vacation_request.save()
        
        request.user.member.used_vacation_days += vacation_request.number_of_days()
        request.user.member.save()
        
        return JsonResponse({'success': True, 'id': vacation_request.id}, status=201)
    else:
        return JsonResponse({'success': False, 'errors': vacation_request_form.errors}, status=400)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def accept_vacation_request(request, request_id):
    vacation_request = VacationRequest.objects.get(id=request_id)
    vacation_request.status = "approved"
    vacation_request.save()
    return JsonResponse({'success': True, 'id': vacation_request.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_vacation_request(request, request_id):
    vacation_request = VacationRequest.objects.get(id=request_id)
    vacation_request.member.used_vacation_days -= vacation_request.number_of_days()
    vacation_request.member.save()
    vacation_request.delete()
    return JsonResponse({'success': True, 'id': vacation_request.id}, status=200)
