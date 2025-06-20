# Standard libs
from datetime import datetime
from datetime import timedelta

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

def calculate_weekdays(start_date, end_date):
    delta = timedelta(days=1)
    current = start_date
    count = 0
    while current <= end_date:
        if current.weekday() < 5:
            count += 1
        current += delta
    return count

def get_days_diff(old_start, old_end, new_start, new_end):
    return calculate_weekdays(new_start, new_end) - calculate_weekdays(old_start, old_end)

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

        old_days = calculate_weekdays(holiday.start_date, holiday.end_date)
        new_days = calculate_weekdays(start_date, end_date)
        diff = new_days - old_days

        is_paid = {"none": True, "on": False}.get(data.get("paid"), True)
        old_paid = holiday.paid

        if holiday.type == 'bank_holiday':
            if not request.user.is_employer:
                return JsonResponse({'success': False, 'error': 'Bank holidays cannot be edited by employees.'}, status=403)

            new_type = data.get('type', 'bank_holiday')
            if new_type != 'bank_holiday':
                return self._convert_bank_to_personal(request, holiday, data, start_date, end_date, new_type, is_paid)

            return self._process_bank_holiday(request, holiday, data, start_date, end_date, old_days, new_days, diff, is_paid)
        else:
            return self._process_normal_holiday(request, holiday, data, start_date, end_date, diff, is_paid, old_paid, old_days, new_days)

    def _process_bank_holiday(self, request, holiday, data, start_date, end_date, old_days, new_days, diff, is_paid):
        new_user_ids = data.get('employees', [])
        new_users = set(User.objects.filter(id__in=new_user_ids, company=request.user.company))
        old_users = set(holiday.users.all())
        kept_users = new_users & old_users
        added_users = new_users - old_users

        insufficient_users = []

        if diff > 0:
            for user in kept_users:
                if not user.has_enough_holidays(diff):
                    insufficient_users.append(f"{user.get_full_name() or user.email} ({user.remaining_holidays} left)")

        for user in added_users:
            if not user.has_enough_holidays(new_days):
                insufficient_users.append(f"{user.get_full_name() or user.email} ({user.remaining_holidays} left)")

        if insufficient_users:
            return JsonResponse({
                'success': False,
                'error': 'Not enough holidays for: ' + ', '.join(insufficient_users)
            }, status=400)

        for user in old_users - new_users:
            user.adjust_holidays(old_days)
            user.save()

        for user in kept_users:
            user.adjust_holidays(-diff)
            user.save()

        for user in added_users:
            user.adjust_holidays(-new_days)
            user.save()

        if holiday.paid != is_paid:
            multiplier = 1 if is_paid else -1
            for user in new_users:
                user.adjust_holidays(multiplier * new_days)
                user.save()


        holiday.users.set(new_users)
        holiday.start_date = start_date
        holiday.end_date = end_date
        holiday.reason = data.get('reason', '').strip()
        holiday.type = 'bank_holiday'
        holiday.status = 'approved'
        holiday.paid = is_paid
        holiday.save()

        return JsonResponse({'success': True, 'id': holiday.id})

    def _convert_bank_to_personal(self, request, holiday, data, start_date, end_date, new_type, is_paid):
        new_days = calculate_weekdays(start_date, end_date)
        reason = data.get('reason', '').strip()
        users = holiday.users.all()

        for user in users:
            user.adjust_holidays(-calculate_weekdays(holiday.start_date, holiday.end_date))
            user.save()

        insufficient = [
            f"{u.get_full_name() or u.email} ({u.remaining_holidays} left)"
            for u in users if not u.has_enough_holidays(new_days)
        ]
        if insufficient:
            for user in users:
                user.adjust_holidays(calculate_weekdays(holiday.start_date, holiday.end_date))
                user.save()
            return JsonResponse({'success': False, 'error': 'Not enough holidays for: ' + ', '.join(insufficient)}, status=400)

        for user in users:
            new_holiday = Holiday.objects.create(
                company=holiday.company,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                type=new_type,
                status='approved',
                paid=is_paid,
            )
            new_holiday.users.add(user)
            user.adjust_holidays(new_days)
            user.save()

        holiday.delete()

        return JsonResponse({'success': True})

    def _process_normal_holiday(self, request, holiday, data, start_date, end_date, diff, is_paid, old_paid, old_days, new_days):
        user = holiday.users.first()

        if diff > 0 and (old_paid or is_paid):
            if not user.has_enough_holidays(diff):
                return JsonResponse({
                    'success': False,
                    'error': f'Not enough remaining holidays. You need {diff} more days.'
                }, status=400)

        if request.user.is_employer:
            if old_paid and is_paid:
                user.adjust_holidays(diff)
            elif old_paid and not is_paid:
                user.adjust_holidays(-old_days)
            elif not old_paid and is_paid:
                user.adjust_holidays(new_days)

            user.save()

            holiday.start_date = start_date
            holiday.end_date = end_date
            holiday.reason = data.get('reason', '').strip()
            holiday.type = data.get('type', holiday.type)
            holiday.paid = is_paid
            holiday.status = 'approved'
            holiday.clear_pending()

        else:
            holiday.pending_start_date = start_date
            holiday.pending_end_date = end_date
            holiday.pending_reason = data.get('reason', '').strip()
            holiday.pending_type = data.get('type', holiday.type)
            holiday.pending_paid = is_paid
            holiday.status = 'pending_edit'

        holiday.save()

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
        users = list(holiday.users.all())
        if holiday.paid:
            days_to_return = holiday.number_of_days
            for user in users:
                user.adjust_holidays(-days_to_return)
            User.objects.bulk_update(users, ['used_holidays'])
        holiday.delete()


@require_http_methods(["PATCH"])
@login_required
@parse_json_body
@employer_required
def process_holiday_request(request, holiday_id):
    data = request.json_data
    action = data.get("action")

    holiday = get_object_or_404(Holiday, id=holiday_id, company=request.user.company)
    user = holiday.users.first()

    if action == "accept_edit":
        diff = holiday.number_of_pending_days - holiday.number_of_days
        if holiday.paid:
            user.adjust_holidays(diff)
            user.save()

        holiday.apply_pending()
        holiday.status = "approved"
        holiday.save()

    elif action == "decline_edit":
        holiday.clear_pending()
        holiday.status = "approved"
        holiday.save()

    elif action == "accept_delete":
        if holiday.paid:
            user.adjust_holidays(-holiday.number_of_days)
            user.save()
        holiday.delete()
        return JsonResponse({'success': True})

    elif action == "decline_delete":
        holiday.status = "approved"
        holiday.save()

    elif action == "accept":
        holiday.status = "approved"
        holiday.save()

    elif action == "decline":
        if holiday.paid:
            user.adjust_holidays(-holiday.number_of_days)
            user.save()
        holiday.delete()
        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    return JsonResponse({'success': True, 'id': holiday.id})

@require_http_methods(["POST"])
@login_required
@parse_json_body
def create_holiday(request):
    data = request.json_data

    try:
        start_date, end_date = get_validated_dates(data)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    days_requested = calculate_weekdays(start_date, end_date)
    holiday_type = data.get('type', 'other')
    reason = data.get('reason', '').strip()
    
    is_paid = {"none": True, "on": False}.get(data.get("paid"), True)

    if holiday_type == 'bank_holiday':
        if not request.user.is_employer:
            return JsonResponse({'success': False, 'error': 'Unauthorized to create bank holidays.'}, status=403)

        users = list(User.objects.filter(id__in=data.get('employees', []), company=request.user.company))

        if is_paid:
            insufficient_users = [
                f"{user.get_full_name() or user.email} ({user.remaining_holidays} days left)"
                for user in users if not user.has_enough_holidays(days_requested)
            ]
            if insufficient_users:
                return JsonResponse({
                    'success': False,
                    'error': 'Not enough remaining holidays for: ' + ', '.join(insufficient_users)
                }, status=400)

        holiday = Holiday.objects.create(
            company=request.user.company,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            type=holiday_type,
            status='approved',
            paid=is_paid
        )
        holiday.users.set(users)

        if is_paid:
            for user in users:
                user.adjust_holidays(days_requested)
            User.objects.bulk_update(users, ['used_holidays'])

        return JsonResponse({'success': True, 'id': holiday.id}, status=201)

    else:
        if len(data.get('employees', [])) > 0:
            users = list(User.objects.filter(id__in=data.get('employees', []), company=request.user.company))
        else:
            users = [request.user]

        if is_paid:
            insufficient_users = [
                f"{user.get_full_name() or user.email} ({user.remaining_holidays} days left)"
                for user in users if not user.has_enough_holidays(days_requested)
            ]
            if insufficient_users:
                return JsonResponse({
                    'success': False,
                    'error': 'Not enough remaining holidays for: ' + ', '.join(insufficient_users)
                }, status=400)

        holidays = []
        for user in users:
            holiday = Holiday.objects.create(
                company=request.user.company,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                type=holiday_type,
                status='approved' if request.user.is_employer else 'pending',
                paid=is_paid
            )
            holiday.users.add(user)

            if is_paid:
                user.adjust_holidays(days_requested)

            holidays.append(holiday)

        if is_paid:
            User.objects.bulk_update(users, ['used_holidays'])

        return JsonResponse({'success': True, 'ids': [h.id for h in holidays]}, status=201)

@login_required
@employer_required
def manage_holidays(request):
    bank_holidays = request.user.company.holidays.filter(type='bank_holiday').order_by('-end_date')
    context = {
        'bank_holidays': bank_holidays, 
        'holiday_types': HOLIDAY_TYPES
    }
    return render(request, 'teams/manage_holidays.html' , context)
