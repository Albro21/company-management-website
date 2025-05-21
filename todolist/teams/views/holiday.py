# Standard libs
from datetime import datetime

# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.forms import HolidayForm
from teams.models import Holiday
from common.decorators import parse_json_body


@require_http_methods(["POST"])
@login_required
@parse_json_body
def create_holiday(request):
    data = request.json_data
    
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    days_requested = (end_date - start_date).days + 1
    
    if start_date > end_date:
        return JsonResponse({'success': False, 'error': 'Start date must be before end date.'}, status=400)
    
    if request.user.remaining_holidays < days_requested:
        return JsonResponse({'success': False, 'error': 'Your holiday exceeds your remaining annual holiday days.'}, status=400)

    holiday_form = HolidayForm(data=data)
    if holiday_form.is_valid():
        holiday = holiday_form.save(commit=False)
        holiday.company = request.user.company
        holiday.user = request.user
        
        if request.user.is_employer:
            holiday.status = "approved"
        else:
            holiday.status = "pending"
        
        holiday.save()
        
        request.user.used_holidays += holiday.number_of_days
        request.user.save()
        
        return JsonResponse({'success': True, 'id': holiday.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': holiday_form.errors}, status=400)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def accept_holiday(request, request_id):
    holiday = Holiday.objects.get(id=request_id)
    holiday.status = "approved"
    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_holiday(request, request_id):
    holiday = Holiday.objects.get(id=request_id)
    holiday.user.used_holidays -= holiday.number_of_days
    holiday.user.save()
    holiday.delete()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)
