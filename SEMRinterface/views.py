"""
HTTP views for the SEMR interface.

This module exposes a minimal set of views used by the single-page-like
flow for study, user, and case selection, plus the case viewer itself and
an AJAX endpoint for case data. The heavy lifting for I/O is delegated to
`SEMRinterface.services` so the views remain thin.
"""
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging
from .services import (
    get_study_ids,
    get_user_details,
    get_case_assignments,
    load_case_details,
    get_case_files,
)

logger = logging.getLogger(__name__)


def welcome_view(request: HttpRequest) -> HttpResponse:
    """Welcome page with tutorial and getting started information."""
    return render(request, 'SEMRinterface/welcome.html')


@require_http_methods(["GET", "POST"])
def unified_selection_view(request: HttpRequest) -> HttpResponse:
    """Render or respond with selection data for studies, users, and cases.

    GET
        Renders the unified selection template populated with available
        studies discovered from the resources directory.
    POST
        Expects a `type` form value to indicate the intent and returns a
        JSON response:
        - type=fetch_users: requires `study_id`; returns available users
        - type=fetch_cases: requires `study_id` and `user_id`; returns case
          assignments for the user
    """
    if request.method == 'GET':
        studies = get_study_ids()
        context = {'studies': studies}
        return render(request, 'SEMRinterface/unified_selection_new.html', context)

    if request.method == 'POST':
        request_type = request.POST.get('type')
        study_id = request.POST.get('study_id')
        user_id = request.POST.get('user_id', None)

        if request_type == 'fetch_users':
            user_details = get_user_details(study_id)
            if user_details:
                users = [{'id': uid, 'name': details.get('name', uid)} for uid, details in user_details.items()]
                return JsonResponse({'status': 'success', 'users': users})
            return JsonResponse({'status': 'error', 'message': 'No users found'}, status=404)

        if request_type == 'fetch_cases':
            case_assignments = get_case_assignments(study_id, user_id)
            if case_assignments:
                cases = {
                    'assigned': case_assignments.get('cases_assigned', []),
                    'completed': case_assignments.get('cases_completed', []),
                }
                return JsonResponse({'status': 'success', 'cases': cases})
            return JsonResponse({'status': 'error', 'message': 'No cases found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
@require_http_methods(["GET"])
def get_case_data(request: HttpRequest) -> JsonResponse:
    """Return case data payloads for the client via JSON.

    Query parameters
    ----------------
    study_id: str
    case_id: str
    """
    study_id = request.GET.get('study_id')
    case_id = request.GET.get('case_id')

    if not all([study_id, case_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

    try:
        case_data = get_case_files(study_id, case_id)
        return JsonResponse({'status': 'success', 'case_data': case_data})
    except FileNotFoundError as exc:
        logger.info("Case data not found: %s", exc)
        return JsonResponse({'status': 'error', 'message': 'Case data not found'}, status=404)

@csrf_exempt
@require_http_methods(["GET"])
def case_viewer(request: HttpRequest) -> HttpResponse:
    """Render the case viewer for a given study, user, and case.

    Requires query string parameters `study_id`, `user_id`, and `case_id`.
    The function loads summary case details and passes them to the template.
    """
    study_id = request.GET.get('study_id')
    user_id = request.GET.get('user_id')
    case_id = request.GET.get('case_id')

    if not all([study_id, user_id, case_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing required parameters'}, status=400)

    try:
        case_details = load_case_details(study_id, case_id)

        context = {
            'study_id': study_id,
            'user_id': user_id,
            'case_id': case_id,
            'dict_case_details': case_details,
            'time_step': 0,

        }
        return render(request, 'SEMRinterface/case_viewer_new.html', context)
    except FileNotFoundError as exc:
        logger.info("Case viewer missing data: %s", exc)
        return JsonResponse({'status': 'error', 'message': 'Case data not found'}, status=404)