# Standard libs
from datetime import datetime

# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.models import Holiday
from common.decorators import parse_json_body


User = get_user_model()

def get_validated_dates(data):
    start = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    if start > end:
        raise ValueError("Start date must be before end date.")
    return start, end

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

def get_days_diff(old_start, old_end, new_start, new_end):
    return calculate_days(new_start, new_end) - calculate_days(old_start, old_end)

@require_http_methods(["POST"])
@login_required
@parse_json_body
def create_holiday(request):
    data = request.json_data

    try:
        start_date, end_date = get_validated_dates(data)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    days_requested = calculate_days(start_date, end_date)
    holiday_type = data.get('type', 'other')
    reason = data.get('reason', '').strip()

    if holiday_type == 'bank_holiday':
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to create bank holidays.'}, status=403)

        users = list(User.objects.filter(id__in=data.get('employees', []), company=request.user.company))

        insufficient_users = [
            f"{user.get_full_name() or user.username} ({user.remaining_holidays} days left)"
            for user in users if not user.has_enough_holidays(days_requested)
        ]
        if insufficient_users:
            return JsonResponse({
                'success': False,
                'error': 'Not enough remaining holidays for: ' + ', '.join(insufficient_users)
            }, status=400)

    else:
        users = [request.user]
        if not request.user.has_enough_holidays(days_requested):
            return JsonResponse({
                'success': False,
                'error': 'Your holiday exceeds your remaining annual holiday days.'
            }, status=400)

    holiday = Holiday.objects.create(
        company=request.user.company,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        type=holiday_type,
        status='approved' if request.user.is_employer else 'pending'
    )
    holiday.users.set(users)

    for user in users:
        user.adjust_holidays(days_requested)
    User.objects.bulk_update(users, ['used_holidays'])

    return JsonResponse({'success': True, 'id': holiday.id}, status=201)

@require_http_methods(["PATCH"])
@login_required
@parse_json_body
@employer_required
def edit_holiday(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)

    data = request.json_data
    try:
        start_date, end_date = get_validated_dates(data)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    diff = get_days_diff(holiday.start_date, holiday.end_date, start_date, end_date)
    old_days = calculate_days(holiday.start_date, holiday.end_date)
    new_days = calculate_days(start_date, end_date)

    holiday_type = data.get('type', 'other')
    reason = data.get('reason', '').strip()

    if holiday_type == 'bank_holiday':
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to edit bank holidays.'}, status=403)

        new_user_ids = data.get('employees', [])
        new_users = set(User.objects.filter(id__in=new_user_ids, company=request.user.company))
        old_users = set(holiday.users.all())

        added_users = new_users - old_users
        kept_users = new_users & old_users

        insufficient_users = []

        if diff > 0:
            for user in kept_users:
                if not user.has_enough_holidays(diff):
                    insufficient_users.append(f"{user.get_full_name() or user.username} ({user.remaining_holidays} days left)")

        for user in added_users:
            if not user.has_enough_holidays(new_days):
                insufficient_users.append(f"{user.get_full_name() or user.username} ({user.remaining_holidays} days left)")

        if insufficient_users:
            return JsonResponse({
                'success': False,
                'error': 'Not enough remaining holidays for: ' + ', '.join(insufficient_users)
            }, status=400)

    else:
        new_users = {request.user}
        old_users = {request.user}
        diff = new_days - old_days

        if diff > 0 and not request.user.has_enough_holidays(diff):
            return JsonResponse({
                'success': False,
                'error': 'Your holiday exceeds your remaining annual holiday days.'
            }, status=400)

    for user in old_users - new_users:
        user.adjust_holidays(-old_days)

    for user in new_users & old_users:
        user.adjust_holidays(diff)

    for user in new_users - old_users:
        user.adjust_holidays(new_days)

    holiday.start_date = start_date
    holiday.end_date = end_date
    holiday.reason = reason
    holiday.type = holiday_type
    holiday.status = 'approved'
    holiday.save()

    holiday.users.set(new_users)

    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["DELETE"])
@login_required
@employer_required
def delete_holiday(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)

    days_to_return = holiday.number_of_days

    users = list(holiday.users.all())
    for user in users:
        user.adjust_holidays(-days_to_return)

    User.objects.bulk_update(users, ['used_holidays'])

    holiday.delete()
    return JsonResponse({'success': True, 'id': holiday_id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@parse_json_body
def request_edit(request, holiday_id):
    holiday = Holiday.objects.filter(id=holiday_id, users=request.user).first()
    if not holiday:
        return JsonResponse({'success': False, 'error': 'Holiday not found or access denied.'}, status=404)
    if holiday.type == 'bank_holiday':
        return JsonResponse({'success': False, 'error': 'Bank holidays cannot be edited by employees.'}, status=403)

    data = request.json_data

    try:
        start_date, end_date = get_validated_dates(data)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    diff = get_days_diff(holiday.start_date, holiday.end_date, start_date, end_date)

    if diff > 0 and not request.user.has_enough_holidays(diff):
        return JsonResponse({
            'success': False,
            'error': f'You do not have enough remaining holidays to extend this request. You need {diff} more days.'
        }, status=400)

    if request.user.is_employer:
        user = holiday.users.first()
        user.adjust_holidays(diff)
        user.save()

        holiday.start_date = start_date
        holiday.end_date = end_date
        holiday.reason = data.get('reason', '').strip()
        holiday.type = data.get('type', holiday.type)
        holiday.status = "approved"

        holiday.clear_pending()
    else:
        holiday.pending_start_date = start_date
        holiday.pending_end_date = end_date
        holiday.pending_reason = data.get('reason', '').strip()
        holiday.pending_type = data.get('type', holiday.type)
        holiday.status = 'pending_edit'

    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id})

@require_http_methods(["PATCH"])
@login_required
def request_delete(request, holiday_id):
    holiday = Holiday.objects.filter(id=holiday_id, users=request.user).first()
    if not holiday:
        return JsonResponse({'success': False, 'error': 'Holiday not found or access denied.'}, status=404)
    if holiday.type == 'bank_holiday':
        return JsonResponse({'success': False, 'error': 'Bank holidays cannot be deleted by employees.'}, status=403)

    if request.user.is_employer:
        user = holiday.users.first()
        user.adjust_holidays(-holiday.number_of_days)
        user.save()
        holiday.delete()
    else:
        holiday.status = 'pending_delete'
        holiday.save()

    return JsonResponse({'success': True, 'id': holiday.id})

@require_http_methods(["PATCH"]) 
@login_required
@employer_required
def accept_edit_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)

    diff = get_days_diff(holiday.start_date, holiday.end_date, holiday.pending_start_date, holiday.pending_end_date)
    
    user = holiday.users.first()
    user.adjust_holidays(diff)
    user.save()
    
    holiday.apply_pending()
    holiday.status = "approved"
    holiday.save()
    
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_edit_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
    holiday.clear_pending()
    holiday.status = "approved"
    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def accept_delete_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
    user = holiday.users.first()
    user.adjust_holidays(-holiday.number_of_days)
    user.save()
    holiday.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_delete_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
    holiday.status = "approved"
    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def accept_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
    holiday.status = "approved"
    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
    holiday.users.first().adjust_holidays(-holiday.number_of_days)
    holiday.users.first().save()
    holiday.delete()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@login_required
@employer_required
def bank_holidays(request):
    bank_holidays = request.user.company.holidays.filter(type='bank_holiday').order_by('-end_date')
    return render(request, 'teams/bank_holidays.html' , {'bank_holidays': bank_holidays})
