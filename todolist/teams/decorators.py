from django.http import HttpResponseForbidden
from functools import wraps

def employer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        member = getattr(request.user, "member", None)
        if not member or not member.is_employer:
            return HttpResponseForbidden("You do not have permission to perform this action.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
