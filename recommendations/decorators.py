from functools import wraps

from django.conf import settings
from django.http import JsonResponse


def require_api_key(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        expected = getattr(settings, 'API_SECRET_KEY', '').strip()
        provided = request.headers.get('X-Api-Key', '').strip()
        if not expected or provided != expected:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
