# Standard libs
from datetime import datetime

# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.models import Holiday
from common.decorators import parse_json_body
from teams.choices import HOLIDAY_TYPES
from teams.forms import HolidayForm


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

class HolidayEditView(LoginRequiredMixin, View):
    def get(self, request, holiday_id):
        holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)
        form = HolidayForm(instance=holiday)
        return render(request, 'teams/holiday_edit_form.html', {
            'form': form,
            'holiday': holiday,
            'holiday_types': HOLIDAY_TYPES
        })

    @method_decorator(parse_json_body)
    def patch(self, request, holiday_id):
        if request.user.is_employer:
            holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)
        else:
            holiday = get_object_or_404(Holiday, id=holiday_id, users__in=[request.user], company=request.user.company)

        data = request.json_data

        try:
            start_date, end_date = get_validated_dates(data)
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        old_days = calculate_days(holiday.start_date, holiday.end_date)
        new_days = calculate_days(start_date, end_date)
        diff = new_days - old_days

        if holiday.type == 'bank_holiday':
            if not request.user.is_employer:
                return JsonResponse({'success': False, 'error': 'Bank holidays cannot be edited by employees.'}, status=403)
            return self._process_bank_holiday(request, holiday, data, start_date, end_date, old_days, new_days, diff)
        else:
            return self._process_normal_holiday(request, holiday, data, start_date, end_date, diff)

    def _process_bank_holiday(self, request, holiday, data, start_date, end_date, old_days, new_days, diff):
        new_user_ids = data.get('employees', [])
        new_users = set(User.objects.filter(id__in=new_user_ids, company=request.user.company))
        old_users = set(holiday.users.all())
        kept_users = new_users & old_users
        added_users = new_users - old_users

        insufficient_users = []

        if diff > 0:
            for user in kept_users:
                if not user.has_enough_holidays(diff):
                    insufficient_users.append(f"{user.get_full_name() or user.username} ({user.remaining_holidays} left)")

        for user in added_users:
            if not user.has_enough_holidays(new_days):
                insufficient_users.append(f"{user.get_full_name() or user.username} ({user.remaining_holidays} left)")

        if insufficient_users:
            return JsonResponse({
                'success': False,
                'error': 'Not enough holidays for: ' + ', '.join(insufficient_users)
            }, status=400)

        for user in old_users - new_users:
            user.adjust_holidays(-old_days)
        for user in kept_users:
            user.adjust_holidays(diff)
        for user in added_users:
            user.adjust_holidays(new_days)

        holiday.users.set(new_users)
        holiday.start_date = start_date
        holiday.end_date = end_date
        holiday.reason = data.get('reason', '').strip()
        holiday.type = 'bank_holiday'
        holiday.status = 'approved'
        holiday.save()

        return JsonResponse({'success': True, 'id': holiday.id})

    def _process_normal_holiday(self, request, holiday, data, start_date, end_date, diff):
        if diff > 0 and not request.user.has_enough_holidays(diff):
            return JsonResponse({
                'success': False,
                'error': f'Not enough remaining holidays. You need {diff} more days.'
            }, status=400)

        if request.user.is_employer:
            holiday.start_date = start_date
            holiday.end_date = end_date
            holiday.reason = data.get('reason', '').strip()
            holiday.type = data.get('type', holiday.type)
            holiday.status = 'approved'
            holiday.clear_pending()
        else:
            holiday.pending_start_date = start_date
            holiday.pending_end_date = end_date
            holiday.pending_reason = data.get('reason', '').strip()
            holiday.pending_type = data.get('type', holiday.type)
            holiday.status = 'pending_edit'
        
        holiday.save()
        
        user = holiday.users.first()
        user.adjust_holidays(diff)
        user.save()
        
        return JsonResponse({'success': True, 'id': holiday.id})


class HolidayDeleteView(LoginRequiredMixin, View):
    def delete(self, request, holiday_id):
        holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)
        self._delete_holiday_and_restore_days(holiday)
        return JsonResponse({'success': True, 'id': holiday_id}, status=200)

    def patch(self, request, holiday_id):
        if request.user.is_employer:
            holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)
            return self.delete(request, holiday_id)
        else:
            holiday = get_object_or_404(Holiday, id=holiday_id, users__in=[request.user], company=request.user.company)
            
            if holiday.type == 'bank_holiday':
                return JsonResponse({'success': False, 'error': 'Bank holidays cannot be deleted by employees.'}, status=403)
            
            holiday.status = 'pending_delete'
            holiday.save()
            return JsonResponse({'success': True, 'id': holiday.id}, status=200)

    def _delete_holiday_and_restore_days(self, holiday):
        days_to_return = holiday.number_of_days
        users = list(holiday.users.all())
        for user in users:
            user.adjust_holidays(-days_to_return)
        User.objects.bulk_update(users, ['used_holidays'])
        holiday.delete()


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
@employer_required
def accept_edit_holiday(request, request_id):
    holiday = get_object_or_404(Holiday, id=request_id, company=request.user.company)
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
