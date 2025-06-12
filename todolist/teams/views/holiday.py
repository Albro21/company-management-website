# Standard libs
from datetime import datetime

# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.forms import HolidayForm
from teams.models import Holiday
from common.decorators import parse_json_body


User = get_user_model()

@require_http_methods(["POST"])
@login_required
@parse_json_body
def create_holiday(request):
    data = request.json_data

    # --- Validate dates ---
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid or missing start/end date.'}, status=400)

    if start_date > end_date:
        return JsonResponse({'success': False, 'error': 'Start date must be before end date.'}, status=400)

    days_requested = (end_date - start_date).days + 1
    holiday_type = data.get('type', 'other')
    reason = data.get('reason', '').strip()

    def has_enough_holidays(user):
        return user.remaining_holidays >= days_requested

    if holiday_type == 'bank_holiday':
        # Only employer allowed to create bank holidays
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to create bank holidays.'}, status=403)

        employee_ids = data.get('employees', [])
        if not employee_ids:
            return JsonResponse({'success': False, 'error': 'No employees selected for bank holiday.'}, status=400)

        users = list(User.objects.filter(id__in=employee_ids, company=request.user.company))
        if not users:
            return JsonResponse({'success': False, 'error': 'No valid employees found.'}, status=400)

        insufficient_users = [
            f"{user.get_full_name() or user.username} ({user.remaining_holidays} days left)"
            for user in users if not has_enough_holidays(user)
        ]
        if insufficient_users:
            return JsonResponse({
                'success': False,
                'error': 'Not enough remaining holidays for: ' + ', '.join(insufficient_users)
            }, status=400)

    else:
        # Personal or sick day: only the requesting user
        users = [request.user]
        if not has_enough_holidays(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Your holiday exceeds your remaining annual holiday days.'
            }, status=400)

    # --- Create Holiday ---
    holiday = Holiday.objects.create(
        company=request.user.company,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        type=holiday_type,
        status='approved' if request.user.is_employer else 'pending'
    )
    holiday.users.set(users)

    # --- Deduct days in bulk ---
    for user in users:
        user.used_holidays += days_requested
    User.objects.bulk_update(users, ['used_holidays'])

    return JsonResponse({'success': True, 'id': holiday.id}, status=201)

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
    holiday.users.first().used_holidays -= holiday.number_of_days
    holiday.users.first().save()
    holiday.delete()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@login_required
@employer_required
def bank_holidays(request):
    bank_holidays = request.user.company.holidays.filter(type='bank_holiday').order_by('-end_date')
    return render(request, 'teams/bank_holidays.html' , {'bank_holidays': bank_holidays})
