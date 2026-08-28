"""Slim GET health check for Simple EMR System."""

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import os


@require_http_methods(["GET"])
def health_check(request):
    """JSON ok/unhealthy: db ping and whether resources/ exists (study count only)."""
    payload = {
        'status': 'ok',
        'checks': {},
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        payload['checks']['database'] = {'status': 'ok'}
    except Exception:
        payload['checks']['database'] = {'status': 'error'}
        payload['status'] = 'unhealthy'

    resources_dir = os.path.join(settings.BASE_DIR, 'resources')
    if os.path.exists(resources_dir):
        try:
            studies_count = sum(
                1 for name in os.listdir(resources_dir)
                if os.path.isdir(os.path.join(resources_dir, name))
            )
            payload['checks']['resources'] = {
                'status': 'ok',
                'studies_count': studies_count,
            }
        except Exception:
            payload['checks']['resources'] = {'status': 'error'}
            payload['status'] = 'unhealthy'
    else:
        payload['checks']['resources'] = {'status': 'missing'}
        payload['status'] = 'unhealthy'

    status_code = 200 if payload['status'] == 'ok' else 503
    return JsonResponse(payload, status=status_code)
