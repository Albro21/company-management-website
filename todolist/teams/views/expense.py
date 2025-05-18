# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

# Local apps
from teams.forms import ExpenseForm
from teams.models import Expense


@require_http_methods(["POST"])
@login_required
def create_expense(request):
    form = ExpenseForm(request.POST, request.FILES)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.company = request.user.company
        expense.user = request.user
        expense.save()

        return JsonResponse({'success': True, 'id': expense.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if 'receipt' not in request.FILES:
        form = ExpenseForm(request.POST, instance=expense)
    else:
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
    
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)
