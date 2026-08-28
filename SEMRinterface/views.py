"""
SEMRinterface/views.py
package github.com/ajk77/SimpleEMRSystem

Research-stable views restored from a2c35bf (file-backed study/user/case flow).
2024.2 helpers (welcome, unified_selection, get_case_data, case_viewer_new)
remain defined but unused by the default research URL routes.
"""
from functools import wraps
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.template import loader
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings as django_settings
import os.path
import json
import logging

# Global variables
dir_local = os.getcwd()
dir_resources = os.path.join(dir_local, "resources")

logger = logging.getLogger(__name__)


def _login_required_if_configured(view_func):
    """Apply login_required only when SEMR_REQUIRE_LOGIN is enabled (default off)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if getattr(django_settings, 'SEMR_REQUIRE_LOGIN', False):
            from django.contrib.auth.decorators import login_required as _lr
            return _lr(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return _wrapped


@ensure_csrf_cookie
def select_study(request):
    print(request.path_info)
    from SEMRinterface.utils import get_list_study_id
    from SEMRinterface.lab_settings import get_eye_tracking_mode, save_lab_settings

    if request.method == 'POST':
        save_lab_settings(request, {
            'SEMR_EYE_TRACKING_MODE': request.POST.get('eye_tracking_mode') == '1',
        })
        return redirect('select_study')

    list_study_id = get_list_study_id(dir_resources)

    template = loader.get_template('SEMRinterface/study_selection_screen.html')
    context_dict = {
        'list_study_id': list_study_id,
        'eye_tracking_mode': get_eye_tracking_mode(request),
        'test': 'test'
    }
    return HttpResponse(template.render(context_dict, request))


def select_user(request, study_id):
    print(request.path_info)

    dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')
    with open(dir_study_user_details) as f:
        dict_user_2_details = json.load(f)

    template = loader.get_template('SEMRinterface/user_selection_screen.html')
    context_dict = {
        'dict_user_2_details': dict_user_2_details,
        'study_id': study_id,
        'test': 'test'
    }
    return HttpResponse(template.render(context_dict, request))


def select_case(request, study_id, user_id):
    print(request.path_info)

    dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')
    with open(dir_study_user_details) as f:
        dict_user_2_details = json.load(f)

    list_cases_assigned = dict_user_2_details[user_id]['cases_assigned']
    list_cases_completed = dict_user_2_details[user_id]['cases_completed']

    template = loader.get_template('SEMRinterface/case_selection_screen.html')
    context_dict = {
        'list_cases_assigned': list_cases_assigned,
        'list_cases_completed': list_cases_completed,
        'user_id': user_id,
        'study_id': study_id,
        'test': 'test'
    }
    return HttpResponse(template.render(context_dict, request))


def case_reset(request):
    print(request.path_info)

    message = " in case_reset "
    if request.method == 'GET':

        # load GET vars #
        study_id = request.GET['study_id']
        user_id = request.GET['user_id']
        case_id = request.GET['case_id']

        # load user details #
        dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')
        with open(dir_study_user_details) as f:
            dict_user_2_details = json.load(f)

        # remove case from completed list #
        dict_user_2_details[user_id]['cases_completed'].remove(case_id)

        # save user details #
        with open(dir_study_user_details, 'w') as f:
            json.dump(dict_user_2_details, f)

        message = "case_reset = SUCCESS"

    else:
        message = "not a GET. No action performed."

    return HttpResponse(message)


def mark_complete(request):
    print(request.path_info)

    message = " in mark_complete "
    if request.method == 'GET':

        # load GET vars #
        study_id = request.GET['study_id']
        user_id = request.GET['user_id']
        case_id = request.GET['case_id']

        # load user details #
        dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')
        with open(dir_study_user_details) as f:
            dict_user_2_details = json.load(f)

        dict_user_2_details[user_id]['cases_completed'].append(case_id)

        # save user details #
        with open(dir_study_user_details, 'w') as f:
            json.dump(dict_user_2_details, f)

        message = "mark_complete = SUCCESS"

    else:
        message = "not a GET. No action performed."

    return HttpResponse(message)


def mark_complete_url(request, study_id, user_id, case_id):
    print(request.path_info)

    dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')
    with open(dir_study_user_details) as f:
        dict_user_2_details = json.load(f)

    dict_user_2_details[user_id]['cases_completed'].append(case_id)

    # save user details #
    with open(dir_study_user_details, 'w') as f:
        json.dump(dict_user_2_details, f)

    return select_case(request, study_id, user_id)


def save_selected_items(request, study_id, user_id, case_id):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':  # is ajax
        message = "Yes, AJAX!"
        if request.method == 'POST':
            selected_ids = json.loads(request.POST.get("selected_ids"))
            dir_study_stored_results = os.path.join(dir_resources, study_id, 'stored_results.txt')
            with open(dir_study_stored_results, 'a+') as f:
                f.write(json.dumps({"user_id": user_id, "case_id": case_id, "selected_ids": selected_ids}) + '\n')
    else:
        message = "Not Ajax"

    return HttpResponse(message)


@ensure_csrf_cookie
def case_viewer(request, study_id, user_id, case_id, time_step=0):
    print(request.path_info)
    from SEMRinterface.lab_settings import get_eye_tracking_mode
    time_step = int(time_step)

    ## load global files ##
    load_dir = os.path.join(dir_resources, study_id)
    dict_case_2_details = json.load(open(os.path.join(load_dir, 'case_details.json'), 'r'))
    dict_data_layout = json.load(open(os.path.join(load_dir, 'data_layout.json'), 'r'))
    dict_med_2_details = json.load(open(os.path.join(load_dir, 'med_details.json'), 'r'))
    dict_user_2_details = json.load(open(os.path.join(load_dir, 'user_details.json'), 'r'))
    dict_variable_2_details = json.load(open(os.path.join(load_dir, 'variable_details.json'), 'r'))

    ## load case specific files ##
    load_dir = os.path.join(dir_resources, study_id, 'cases_all', case_id)
    dict_demographics = json.load(open(os.path.join(load_dir, 'demographics.json'), 'r'))
    dict_medications = json.load(open(os.path.join(load_dir, 'medications.json'), 'r'))
    dict_notes = json.load(open(os.path.join(load_dir, 'note_panel_data.json'), 'r'))
    dict_observations = json.load(open(os.path.join(load_dir, 'observations.json'), 'r'))

    ## define user instructions dict ##
    instructions = {}
    instructions["familiar"] = "Please use the available information to become familiar with this patient."
    instructions["select"] = "Please select the information you used when preparing to present this case."

    template = loader.get_template('SEMRinterface/case_viewer.html')
    context_dict = {
        'case_id': case_id,
        'user_id': user_id,
        'study_id': study_id,
        'time_step': time_step,
        'show_checkboxes': dict_case_2_details[case_id][time_step]["check_boxes"],
        'instructions': instructions[dict_case_2_details[case_id][time_step]["instruction_set"]],
        'dict_case_details': dict_case_2_details[case_id],
        'dict_data_layout': dict_data_layout,
        'dict_med_2_details': dict_med_2_details,
        'dict_user_details': dict_user_2_details[user_id],
        'dict_variable_2_details': dict_variable_2_details,
        'dict_demographics': dict_demographics,
        'dict_medications': dict_medications,
        'dict_notes': dict_notes,
        'dict_observations': dict_observations,
        'test': 'test',
        'list_1_2': [1, 2],
        'list_3_4_5_6': [3, 4, 5, 6],
        'eye_tracking_mode': get_eye_tracking_mode(request),
    }
    return HttpResponse(template.render(context_dict, request))


# ---------------------------------------------------------------------------
# 2024.2 helpers kept unused (not deleted). Research flow does not call these.
# ---------------------------------------------------------------------------

def welcome_view(request: HttpRequest) -> HttpResponse:
    """Welcome page with tutorial. Unused by the research-stable routes."""
    if getattr(django_settings, 'SEMR_REQUIRE_LOGIN', False) and not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    return render(request, 'SEMRinterface/welcome.html')


@_login_required_if_configured
@require_http_methods(["GET", "POST"])
def unified_selection_view(request: HttpRequest) -> HttpResponse:
    """Unused 2024.2 unified selection (single definition; not the research flow)."""
    from .services import get_study_ids, get_user_details, get_case_assignments

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
@_login_required_if_configured
def get_case_data(request: HttpRequest) -> JsonResponse:
    """Unused 2024.2 JSON case-data endpoint."""
    from .services import get_case_files

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
@_login_required_if_configured
def case_viewer_new(request: HttpRequest) -> HttpResponse:
    """Unused 2024.2 query-param viewer (case_viewer_new.html)."""
    from .services import load_case_details

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
