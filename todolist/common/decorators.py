from functools import wraps
from django.http import JsonResponse
import json

def parse_json_body(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            request.json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
