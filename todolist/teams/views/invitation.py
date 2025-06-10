# Django
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.models import Invitation


@require_http_methods(["DELETE"])
@login_required
@employer_required
def delete_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, company=request.user.company)
    invitation.delete()
    return JsonResponse({'success': True}, status=200)
