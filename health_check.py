"""
Health check system for Simple EMR System
Provides system status and diagnostics
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.db import connection
import os
import json
import time

@require_http_methods(["GET"])
def health_check(request):
    """
    System health check endpoint
    
    Returns:
        JsonResponse: System health status and diagnostics
    """
    start_time = time.time()
    
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '2024.2',
        'uptime': time.time() - start_time,
        'checks': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                health_status['checks']['database'] = {
                    'status': 'ok',
                    'response_time': (time.time() - start_time) * 1000
                }
            else:
                health_status['checks']['database'] = {
                    'status': 'error',
                    'message': 'Database query returned no results'
                }
                health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check resources directory
    resources_dir = os.path.join(settings.BASE_DIR, 'resources')
    if os.path.exists(resources_dir):
        try:
            studies = [d for d in os.listdir(resources_dir) 
                      if os.path.isdir(os.path.join(resources_dir, d))]
            health_status['checks']['resources'] = {
                'status': 'ok',
                'studies_count': len(studies),
                'studies': studies
            }
        except Exception as e:
            health_status['checks']['resources'] = {
                'status': 'error',
                'message': str(e)
            }
            health_status['status'] = 'unhealthy'
    else:
        health_status['checks']['resources'] = {
            'status': 'warning',
            'message': 'Resources directory not found'
        }
    
    # Check static files
    static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
    static_root = getattr(settings, 'STATIC_ROOT', None)
    
    static_status = 'ok'
    static_message = 'Static files available'
    
    if static_root and not os.path.exists(static_root):
        static_status = 'warning'
        static_message = 'Static files not collected'
    elif not static_dirs and not static_root:
        static_status = 'warning'
        static_message = 'No static files configuration found'
    
    health_status['checks']['static_files'] = {
        'status': static_status,
        'message': static_message
    }
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(settings.BASE_DIR)
        health_status['checks']['disk_space'] = {
            'status': 'ok',
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'free_percent': round((free / total) * 100, 2)
        }
        
        # Warning if less than 1GB free
        if free < 1024**3:
            health_status['checks']['disk_space']['status'] = 'warning'
            health_status['checks']['disk_space']['message'] = 'Low disk space'
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Check memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'status': 'ok',
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent_used': memory.percent
        }
        
        # Warning if memory usage is high
        if memory.percent > 90:
            health_status['checks']['memory']['status'] = 'warning'
            health_status['checks']['memory']['message'] = 'High memory usage'
    except ImportError:
        health_status['checks']['memory'] = {
            'status': 'info',
            'message': 'psutil not available for memory monitoring'
        }
    except Exception as e:
        health_status['checks']['memory'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Check configuration
    config_issues = []
    
    if settings.SECRET_KEY == '$$$$$ENTER SECRET KEY$$$$$':
        config_issues.append('Default secret key in use')
    
    if settings.DEBUG:
        config_issues.append('Debug mode enabled')
    
    if not settings.ALLOWED_HOSTS:
        config_issues.append('ALLOWED_HOSTS not configured')
    
    health_status['checks']['configuration'] = {
        'status': 'warning' if config_issues else 'ok',
        'issues': config_issues
    }
    
    # Overall status determination
    error_count = sum(1 for check in health_status['checks'].values() 
                     if check.get('status') == 'error')
    warning_count = sum(1 for check in health_status['checks'].values() 
                       if check.get('status') == 'warning')
    
    if error_count > 0:
        health_status['status'] = 'unhealthy'
    elif warning_count > 0:
        health_status['status'] = 'degraded'
    
    # Add summary
    health_status['summary'] = {
        'total_checks': len(health_status['checks']),
        'errors': error_count,
        'warnings': warning_count,
        'response_time_ms': round((time.time() - start_time) * 1000, 2)
    }
    
    # Set appropriate HTTP status code
    status_code = 200
    if health_status['status'] == 'unhealthy':
        status_code = 503
    elif health_status['status'] == 'degraded':
        status_code = 200  # Still functional but with warnings
    
    return JsonResponse(health_status, status=status_code)

@require_http_methods(["GET"])
def system_info(request):
    """
    System information endpoint
    
    Returns:
        JsonResponse: Detailed system information
    """
    info = {
        'application': {
            'name': 'Simple EMR System',
            'version': '2024.2',
            'django_version': settings.DJANGO_VERSION,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        },
        'environment': {
            'debug': settings.DEBUG,
            'timezone': str(settings.TIME_ZONE),
            'language': settings.LANGUAGE_CODE,
            'allowed_hosts': settings.ALLOWED_HOSTS,
        },
        'database': {
            'engine': settings.DATABASES['default']['ENGINE'],
            'name': settings.DATABASES['default'].get('NAME', 'N/A'),
        },
        'paths': {
            'base_dir': str(settings.BASE_DIR),
            'static_root': str(getattr(settings, 'STATIC_ROOT', 'Not set')),
            'media_root': str(getattr(settings, 'MEDIA_ROOT', 'Not set')),
        }
    }
    
    return JsonResponse(info)

@require_http_methods(["GET"])
def quick_start(request):
    """
    Quick start information endpoint
    
    Returns:
        JsonResponse: Quick start instructions
    """
    quick_start_info = {
        'title': 'Simple EMR System Quick Start',
        'steps': [
            {
                'step': 1,
                'title': 'Access the System',
                'description': 'Open your web browser and navigate to the application URL',
                'url': request.build_absolute_uri('/')
            },
            {
                'step': 2,
                'title': 'Select a Study',
                'description': 'Choose a research study from the dropdown menu',
                'url': request.build_absolute_uri('/')
            },
            {
                'step': 3,
                'title': 'Choose a User',
                'description': 'Select your user profile from the list',
                'url': request.build_absolute_uri('/')
            },
            {
                'step': 4,
                'title': 'Review Cases',
                'description': 'Click on a case to view patient data and complete tasks',
                'url': request.build_absolute_uri('/case_viewer/')
            }
        ],
        'help': {
            'documentation': request.build_absolute_uri('/docs/'),
            'api_reference': request.build_absolute_uri('/api/'),
            'health_check': request.build_absolute_uri('/health/'),
        }
    }
    
    return JsonResponse(quick_start_info)
