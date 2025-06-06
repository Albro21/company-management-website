# Django
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

# Local apps
from teams.forms import DocumentForm
from teams.models import Document


User = get_user_model()

@require_http_methods(["POST"])
@login_required
def create_document(request, employee_id):
    if request.user.id != employee_id and not request.user.is_employer:
        return JsonResponse({'success': False, 'error': 'You are not allowed to create a document for this employee.'}, status=403)
    
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.user = User.objects.get(id=employee_id)
        document.save()

        return JsonResponse({'success': True, 'id': document.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_document(request, document_id):
    if request.user.is_employer:
        document = get_object_or_404(Document, id=document_id, user__company=request.user.company)
    else:
        raise PermissionDenied("You do not have permission to delete this document.")
    
    document.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def edit_document(request, document_id):
    if request.user.is_employer:
        document = get_object_or_404(Document, id=document_id, user__company=request.user.company)
    else:
        raise PermissionDenied("You do not have permission to edit this document.")
    
    if 'file' not in request.FILES:
        form = DocumentForm(request.POST, instance=document)
    else:
        form = DocumentForm(request.POST, request.FILES, instance=document)
    
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)
