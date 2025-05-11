# Django
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

# Local apps
from common.decorators import parse_json_body
from teams.decorators import employer_required
from teams.models import JobTitle


@require_http_methods(["POST"])
@login_required
@employer_required
@parse_json_body
def create_job_title(request):
    job_title = JobTitle.objects.create(**request.json_data, company=request.user.company)
    return JsonResponse({'success': True, 'id': job_title.id}, status=201)

@require_http_methods(["DELETE"])
@login_required
@employer_required
def delete_job_title(request, job_title_id):
    try:
        job_title = get_object_or_404(JobTitle, id=job_title_id, company=request.user.company)
        job_title.delete()
        return JsonResponse({"success": True}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"success": False, "error": "Job title not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
