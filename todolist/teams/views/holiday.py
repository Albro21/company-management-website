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
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to create bank holidays.'}, status=403)

        users = list(User.objects.filter(id__in=data.get('employees', []), company=request.user.company))

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
        users = [request.user]
        if not has_enough_holidays(request.user):
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
        user.used_holidays += days_requested
    User.objects.bulk_update(users, ['used_holidays'])

    return JsonResponse({'success': True, 'id': holiday.id}, status=201)

@require_http_methods(["PATCH"])
@login_required
@parse_json_body
@employer_required
def edit_holiday(request, holiday_id):
    data = request.json_data
    
    try:
        holiday = Holiday.objects.get(id=holiday_id, company=request.user.company)
    except Holiday.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Holiday not found.'}, status=404)
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return JsonResponse({'success': False, 'error': 'Invalid or missing start/end date.'}, status=400)

    if start_date > end_date:
        return JsonResponse({'success': False, 'error': 'Start date must be before end date.'}, status=400)

    old_days = (holiday.end_date - holiday.start_date).days + 1
    new_days = (end_date - start_date).days + 1
    diff = new_days - old_days

    holiday_type = data.get('type', 'other')
    reason = data.get('reason', '').strip()

    def has_enough_holidays(user, needed_days):
        return user.remaining_holidays >= needed_days

    if holiday_type == 'bank_holiday':
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to edit bank holidays.'}, status=403)

        new_user_ids = data.get('employees', [])
        new_users = set(User.objects.filter(id__in=new_user_ids, company=request.user.company))
        old_users = set(holiday.users.all())

        removed_users = old_users - new_users
        added_users = new_users - old_users
        kept_users = new_users & old_users

        insufficient_users = []

        if diff > 0:
            for user in kept_users:
                if not has_enough_holidays(user, diff):
                    insufficient_users.append(f"{user.get_full_name() or user.username} ({user.remaining_holidays} days left)")

        # For added users, need to check if they have enough holidays for new_days
        for user in added_users:
            if not has_enough_holidays(user, new_days):
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

        if diff > 0 and not has_enough_holidays(request.user, diff):
            return JsonResponse({
                'success': False,
                'error': 'Your holiday exceeds your remaining annual holiday days.'
            }, status=400)

    # Adjust used_holidays for users removed: subtract old_days
    for user in removed_users:
        user.used_holidays -= old_days

    # Adjust used_holidays for kept users: add diff (positive or negative)
    for user in kept_users:
        user.used_holidays += diff

    # Adjust used_holidays for newly added users: add new_days
    for user in added_users:
        user.used_holidays += new_days

    # Bulk update all affected users at once
    User.objects.bulk_update(removed_users | kept_users | added_users, ['used_holidays'])

    # Update holiday fields
    holiday.start_date = start_date
    holiday.end_date = end_date
    holiday.reason = reason
    holiday.type = holiday_type
    holiday.status = 'approved' if request.user.is_employer else 'pending'
    holiday.save()

    # Update holiday users
    holiday.users.set(new_users)

    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["DELETE"])
@login_required
@employer_required
def delete_holiday(request, holiday_id):
    try:
        holiday = Holiday.objects.get(id=holiday_id, company=request.user.company)
    except Holiday.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Holiday not found.'}, status=404)

    # Calculate the number of days for this holiday
    days_to_return = (holiday.end_date - holiday.start_date).days + 1

    users = list(holiday.users.all())
    for user in users:
        user.used_holidays = max(user.used_holidays - days_to_return, 0)  # Prevent negative values

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
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except (KeyError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid dates.'}, status=400)

    if start_date > end_date:
        return JsonResponse({'success': False, 'error': 'Start date must be before end date.'}, status=400)

    old_days = (holiday.end_date - holiday.start_date).days + 1
    new_days = (end_date - start_date).days + 1
    diff = new_days - old_days

    if diff > 0 and diff > request.user.remaining_holidays:
        return JsonResponse({
            'success': False,
            'error': f'You do not have enough remaining holidays to extend this request. You need {diff} more days.'
        }, status=400)

    # If employer, apply immediately
    if request.user.is_employer:
        user = holiday.users.first()
        user.used_holidays = max(0, user.used_holidays + diff)
        user.save()

        holiday.start_date = start_date
        holiday.end_date = end_date
        holiday.reason = data.get('reason', '').strip()
        holiday.type = data.get('type', holiday.type)
        holiday.status = "approved"

        holiday.pending_start_date = None
        holiday.pending_end_date = None
        holiday.pending_reason = None
        holiday.pending_type = None
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
        if user:
            user.used_holidays = max(0, user.used_holidays - holiday.number_of_days)
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
    holiday = Holiday.objects.get(id=request_id)

    old_days = (holiday.end_date - holiday.start_date).days + 1
    new_days = (holiday.pending_end_date - holiday.pending_start_date).days + 1
    diff = new_days - old_days

    user = holiday.users.first()
    user.used_holidays = max(0, user.used_holidays + diff)
    user.save()

    holiday.start_date = holiday.pending_start_date
    holiday.end_date = holiday.pending_end_date
    holiday.reason = holiday.pending_reason
    holiday.type = holiday.pending_type

    holiday.pending_start_date = None
    holiday.pending_end_date = None
    holiday.pending_reason = None
    holiday.pending_type = None

    holiday.status = "approved"
    holiday.save()

    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_edit_holiday(request, request_id):
    holiday = Holiday.objects.get(id=request_id)

    holiday.pending_start_date = None
    holiday.pending_end_date = None
    holiday.pending_reason = None
    holiday.pending_type = None

    holiday.status = "approved"
    holiday.save()

    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def accept_delete_holiday(request, request_id):
    holiday = Holiday.objects.get(id=request_id)

    user = holiday.users.first()
    if user:
        user.used_holidays = max(0, user.used_holidays - holiday.number_of_days)
        user.save()
        
    holiday.delete()
    
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["PATCH"])
@login_required
@employer_required
def decline_delete_holiday(request, request_id):
    holiday = Holiday.objects.get(id=request_id)
    holiday.status = "approved"
    holiday.save()
    return JsonResponse({'success': True, 'id': holiday.id}, status=200)

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
