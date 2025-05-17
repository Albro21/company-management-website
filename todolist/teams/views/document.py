# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

# Local apps
from teams.forms import DocumentForm
from teams.models import Document


@require_http_methods(["POST"])
@login_required
def create_document(request):
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.member = request.user.member
        document.save()

        return JsonResponse({'success': True, 'id': document.id}, status=201)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, member=request.user.member)
    document.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id, member=request.user.member)
    
    if 'file' not in request.FILES:
        form = DocumentForm(request.POST, instance=document)
    else:
        form = DocumentForm(request.POST, request.FILES, instance=document)
    
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f"Form contains errors: {form.errors.as_json()}"}, status=400)
