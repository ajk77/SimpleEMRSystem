"""
SEMRinterface/views.py
package github.com/ajk77/SimpleEMRSystem

This is the view processing file. 
"""
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
import os.path
import json

# Global variables
dir_local = os.getcwd()
dir_resources = os.path.join(dir_local, "resources")


def select_study(request):
    print(request.path_info)
    from SEMRinterface.utils import get_list_study_id
    
    list_study_id = get_list_study_id(dir_resources)

    template = loader.get_template(os.path.join('SEMRinterface', 'study_selection_screen.html'))
    context_dict = {
        'list_study_id': list_study_id,
        'test': 'test'
    }
    return HttpResponse(template.render(context_dict))
    

def select_user(request, study_id):
    print(request.path_info)

    dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')   
    with open(dir_study_user_details) as f:
        dict_user_2_details = json.load(f)
    
    template = loader.get_template(os.path.join('SEMRinterface', 'user_selection_screen.html'))
    context_dict = {
        'dict_user_2_details': dict_user_2_details,
        'study_id': study_id,
        'test': 'test'
    }
    return HttpResponse(template.render(context_dict)) 
    
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
    return HttpResponse(template.render(context_dict)) 

def case_reset(request):
    print(request.path_info)
    from urllib.parse import urlparse
    
    #if request.is_ajax():
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
    from urllib.parse import urlparse
    
    #if request.is_ajax():
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
        
        # remove case from completed list #
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
    from urllib.parse import urlparse

    dir_study_user_details = os.path.join(dir_resources, study_id, 'user_details.json')   
    with open(dir_study_user_details) as f:
        dict_user_2_details = json.load(f)
    
    # remove case from completed list #
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
                f.write(json.dumps({"user_id": user_id, "case_id": case_id, "selected_ids": selected_ids}) +'\n')
    else:
        message = "Not Ajax"
    
    return HttpResponse(message)

@ensure_csrf_cookie    
def case_viewer(request, study_id, user_id, case_id, time_step=0):
    print(request.path_info)
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
        'list_3_4_5_6': [3, 4, 5, 6]
    }
    return HttpResponse(template.render(context_dict)) 
