"""
SEMRinterface/views.py
version 3.0
package github.com/ajk77/SimpleEMRSystem
Modified by AndrewJKing.com|@andrewsjourney

This is the view processing file. 

---LICENSE---
This file is part of SimpleEMRSystem

SimpleEMRSystem is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or 
any later version.

SimpleEMRSystem is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SimpleEMRSystem.  If not, see <https://www.gnu.org/licenses/>.
"""
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
import os.path
import json
import datetime

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
'''
@api_view(['POST'])
def save_selected_items(request, study_id, user_id, case_id):
    if request.method == 'POST':
        tutorial_data = JSONParser().parse(request)
        print(tutorial_data)
        return JsonResponse('good', status=status.HTTP_201_CREATED) 
        return JsonResponse('bad', status=status.HTTP_400_BAD_REQUEST)
    

'''
def save_selected_items(request, study_id, user_id, case_id):
    if request.is_ajax():
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
    
'''
def index_synthea(request, user_id=False):
    print(request.path_info)
    dir_part_info = os.path.join(local_dir, 'synthea_study', 'case_list')
    cases = []
    pt_list = []  # used to limit interface to 1 encounter per patient
    with open(dir_part_info + '.txt', 'r') as in_file:
        for line in in_file:
            if line[0] == '#':
                continue
            else:
                split_line = line.split(',')
                if split_line[5] not in pt_list:
                    
                    cases.append({'id': split_line[0], 'name': split_line[6], 'admittime': split_line[3],
                                  'dischargetime': split_line[4]})
                    pt_list.append(split_line[5])
                if len(cases) > 20:
                    break

    template = loader.get_template('LEMRinterface/home_screen_synthea.html')
    context_dict = {
        'cases': cases
    }
    return HttpResponse(template.render(context_dict))


def case_reset(request):
    print(request.path_info)
    dir_part_info = os.path.join(local_dir, 'demo_study', 'participant_info')
    now = datetime.datetime.now()
    file_content = []
    with open(dir_part_info + '.txt', 'r') as in_file:
        for line in in_file:
            if line[0] == '#':
                file_content.append(line.rstrip())
            else:
                split_line = line.split(',')
                file_content.append(split_line[0] + ',' + now.strftime("%Y-%m-%d") + ',0,')
    with open(dir_part_info + '.txt', 'w') as out_file:
        out_file.write('\n'.join(file_content))
    return HttpResponse("<h2>Cases have been reset</h2><br>"
                        "<a href=http://127.0.0.1:8000/LEMRinterface/><button>Home</button></a>")

def end_of_study(request, user_id, previous_patient_id=0):
    """
    Closes the previous cases's final pixelmap and displays completion info to participant.
     Does not need to include study_id info because it will never be navigated to unless within a study.
    """
    print(request.path_info)
    update_participant_info(user_id, os.path.join(local_dir, 'demo_study', 'participant_info'))
    return HttpResponse("<h2>You have completed all of the cases!"
                        "</h2><br><a href=http://127.0.0.1:8000/LEMRinterface/home/"+user_id+"/><button>Home</button></a>")


def loadcasedata(request):
    update_cases()
    return HttpResponse("<h2>Cases have been updated!</h2><br>"
                        "<a href=http://127.0.0.1:8000/LEMRinterface/><button>Home</button></a>")


def save_input(request):
    if request.is_ajax():
        message = "Yes, AJAX!"
        if request.method == 'POST':
            print_to_manual_input_file(local_dir, request.POST.get('pat_id'), request.POST.get('the_timestamp'),
                                       request.POST.get('selections'), request.POST.get('rating'),
                                       request.POST.get('reason'))
    else:
        message = "Not Ajax"
    return HttpResponse(message)


@ensure_csrf_cookie
def detail(request, patient_id, user_id='interface_demo', time_cutoff=1):
    time_cutoff = int(time_cutoff)

    template = loader.get_template(os.path.join('LEMRinterface', 'index_3.html'))
    print("New request: " + request.path_info)

    p_info_location = os.path.join(local_dir, 'demo_study', 'participant_info')
    returned_data = determine_next_url(p_info_location, user_id, time_cutoff, patient_id)
    next_patient, next_view, show_highlights, highlights_only = returned_data  # from line above

    current_arm = 'C'
    if time_cutoff == 1:
        first_view = True
        only_show_highlights = 'false'  # first view is always the same
        show_highlights = False  # first view is always the same
    else:
        first_view = False
        show_highlights = int(show_highlights)
        if show_highlights:
            current_arm = '1'
        if highlights_only == '1':  # depends on user
            current_arm = '2'
            only_show_highlights = 'true'
        else:
            only_show_highlights = 'false'

    record_report = 'true'

    load_dir = os.path.join(local_dir, 'demo_study', 'cases_t' + str(time_cutoff), str(patient_id))

    data_fields_to_highlight = []
    if show_highlights:
        # load med mappings. catalog_display is used as machine learning names, ordered as is the longer display name
        catalog_display_dic, ordered_as_dic = load_med_maps(os.path.join(load_dir, 'med-display-id_to_name.txt'))
        # highlights = load_highlights(path)
        with open(os.path.join(local_dir, 'demo_study', 'case_highlights.txt'), 'r') as f:
            for line in f:
                s_line = line.rstrip().split(': ')
                if s_line[0] == str(patient_id):
                    data_fields_to_highlight = s_line[1].split(',')
                    break

        for idx, data_field in enumerate(data_fields_to_highlight):
            if data_field in catalog_display_dic.keys():
                data_fields_to_highlight[idx] = catalog_display_dic[data_field]

    demographics_dict = json.load(open(os.path.join(load_dir, 'demographics.txt'), 'r'))
    global_time = json.load(open(os.path.join(load_dir, 'global_time.txt'), 'r'))
    lab_info = json.load(open(os.path.join(load_dir, 'labs.txt'), 'r'))
    vital_info = json.load(open(os.path.join(load_dir, 'vitals.txt'), 'r'))
    group_order_labs = json.load(open(os.path.join(local_dir, 'demo_study', 'stored_data_structures', 'group_order_labs.txt'), 'r'))
    group_info = json.load(open(os.path.join(local_dir, 'demo_study', 'stored_data_structures', 'group_membership.txt'), 'r'))
    global_params = json.load(open(os.path.join(local_dir, 'demo_study', 'stored_data_structures', 'global_params.txt'), 'r'))
    display_names = json.load(open(os.path.join(local_dir, 'demo_study', 'stored_data_structures', 'display_names.txt'), 'r'))
    recent_results = json.load(open(os.path.join(load_dir, 'recent_results.txt'), 'r'))
    med_info = json.load(open(os.path.join(load_dir, 'case_test_meds.txt'), 'r'))
    display_med_names = json.load(open(os.path.join(load_dir, 'display_med_names.txt'), 'r'))
    med_routes = json.load(open(os.path.join(load_dir, 'med_routes.txt'), 'r'))
    routes_mapping = json.load(open(os.path.join(load_dir, 'routes_mapping.txt'), 'r'))
    procedure_dict = json.load(open(os.path.join(load_dir, 'procedures.txt'), 'r'))
    micro_report_dict = json.load(open(os.path.join(load_dir, 'micro_report.txt'), 'r'))
    op_note = json.load(open(os.path.join(load_dir, 'OP.txt'), 'r'))
    rad_note = json.load(open(os.path.join(load_dir, 'RAD.txt'), 'r'))
    ekg_note = json.load(open(os.path.join(load_dir, 'EKG.txt'), 'r'))
    other_note = json.load(open(os.path.join(load_dir, 'other_notes.txt'), 'r'))
    pgn_note = json.load(open(os.path.join(load_dir, 'PGN.txt'), 'r'))
    hp_note = json.load(open(os.path.join(load_dir, 'HP.txt'), 'r'))

    context_dict = {
        'first_view': first_view,
        'global_time': global_time,
        'next_patient': next_patient,
        'next_view': next_view,
        'user_id': str(user_id),
        'demographics_dict': demographics_dict,
        'OP_note': op_note,
        'RAD_note': rad_note,
        'EKG_note': ekg_note,
        'other_note': other_note,
        'PGN_note': pgn_note,
        'HP_note': hp_note,
        'micro_report_dict': micro_report_dict,
        'lab_info': lab_info,
        'vital_info': vital_info,
        'group_info': group_info,
        'global_display_info': global_params,
        'labs_to_highlight': data_fields_to_highlight,
        'only_show_highlights': only_show_highlights,
        'arm': current_arm,
        'display_names': display_names,
        'group_order': group_order_labs,
        'procedures': procedure_dict,
        'recent': recent_results,
        'med_info': med_info,
        'med_routes': med_routes,
        'routes_mapping': routes_mapping,
        'display_med_names': display_med_names,
        'record_report': record_report
    }
    return HttpResponse(template.render(context_dict))

@ensure_csrf_cookie
def detail_synthea(request, encounter_id, user_id='synthea_demo'):

    template = loader.get_template(os.path.join('LEMRinterface', 'index_3_synthea.html'))
    print("New request: " + request.path_info)

    load_dir = os.path.join(local_dir, 'synthea_study', 'cases_all', str(encounter_id))

    demographics_dict = json.load(open(os.path.join(load_dir, 'demographics.txt'), 'r'))
    global_time = json.load(open(os.path.join(load_dir, 'global_time.txt'), 'r'))
    lab_info = json.load(open(os.path.join(load_dir, 'labs.txt'), 'r'))
    vital_info = json.load(open(os.path.join(load_dir, 'vitals.txt'), 'r'))
    group_order_labs = json.load(open(os.path.join(local_dir, 'synthea_study', 'stored_data_structures', 'group_order_labs.txt'), 'r'))
    group_info = json.load(open(os.path.join(local_dir, 'synthea_study', 'stored_data_structures', 'group_membership.txt'), 'r'))
    #global_params = json.load(open(os.path.join(local_dir, 'synthea_study', 'stored_data_structures', 'global_params.txt'), 'r'))
    display_names = json.load(open(os.path.join(local_dir, 'synthea_study', 'stored_data_structures', 'display_names.txt'), 'r'))
    #recent_results = json.load(open(os.path.join(load_dir, 'recent_results.txt'), 'r'))
    med_info = json.load(open(os.path.join(load_dir, 'case_test_meds.txt'), 'r'))
    display_med_names = json.load(open(os.path.join(load_dir, 'display_med_names.txt'), 'r'))
    med_routes = json.load(open(os.path.join(load_dir, 'med_routes.txt'), 'r'))
    routes_mapping = json.load(open(os.path.join(load_dir, 'route_mapping.txt'), 'r'))
    procedure_dict = json.load(open(os.path.join(load_dir, 'procedure.txt'), 'r'))
    #micro_report_dict = json.load(open(os.path.join(load_dir, 'micro_report.txt'), 'r'))
    #op_note = json.load(open(os.path.join(load_dir, 'OP.txt'), 'r'))
    #rad_note = json.load(open(os.path.join(load_dir, 'RAD.txt'), 'r'))
    #ekg_note = json.load(open(os.path.join(load_dir, 'EKG.txt'), 'r'))
    #other_note = json.load(open(os.path.join(load_dir, 'other_notes.txt'), 'r'))
    #pgn_note = json.load(open(os.path.join(load_dir, 'PGN.txt'), 'r'))
    #hp_note = json.load(open(os.path.join(load_dir, 'HP.txt'), 'r'))
    allergies = json.load(open(os.path.join(load_dir, 'allergies.txt'), 'r'))
    careplan = json.load(open(os.path.join(load_dir, 'careplan.txt'), 'r'))
    condition = json.load(open(os.path.join(load_dir, 'condition.txt'), 'r'))
    device = json.load(open(os.path.join(load_dir, 'device.txt'), 'r'))
    imagingstudy = json.load(open(os.path.join(load_dir, 'imagingstudy.txt'), 'r'))
    immunizations = json.load(open(os.path.join(load_dir, 'immunizations.txt'), 'r'))

    context_dict = {
        'first_view': True,
        'global_time': global_time,
        #'next_patient': next_patient,
        #'next_view': next_view,
        #'user_id': str(user_id),
        'demographics_dict': demographics_dict,
        #'OP_note': op_note,
        #'RAD_note': rad_note,
        #'EKG_note': ekg_note,
        #'other_note': other_note,
        #'PGN_note': pgn_note,
        #'HP_note': hp_note,
        #'micro_report_dict': micro_report_dict,
        'lab_info': lab_info,
        'vital_info': vital_info,
        'group_info': group_info,
        #'global_display_info': global_params,
        #'labs_to_highlight': data_fields_to_highlight,
        #'only_show_highlights': only_show_highlights,
        #'arm': current_arm,
        'display_names': display_names,
        'group_order': group_order_labs,
        'procedures': procedure_dict,
        #'recent': recent_results,
        'med_info': med_info,
        'med_routes': med_routes,
        'routes_mapping': routes_mapping,
        'display_med_names': display_med_names,
        #'record_report': record_report,
        'allergies': allergies,
        'careplan': careplan,
        'condition': condition,
        'device': device,
        'imagingstudy': imagingstudy,
        'immunizations': immunizations
    }
    return HttpResponse(template.render(context_dict))
'''
