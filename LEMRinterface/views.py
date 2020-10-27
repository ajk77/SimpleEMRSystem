"""
LEMRinterface/views.py
version 2.0
package github.com/ajk77/LEMRinterface
Modified by AndrewJKing.com|@andrewsjourney

This is the view processing file. 

---LICENSE---
This file is part of LEMRinterface

LEMRinterface is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or 
any later version.

LEMRinterface is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LEMRinterface.  If not, see <https://www.gnu.org/licenses/>.
"""
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from LEMRinterface.loaddata import *
from LEMRinterface.utils import load_med_maps
import os.path
import json
import datetime

# Global variables
local_dir = os.path.join(os.getcwd(), "resources")


def index(request, user_id=False):
    print(request.path_info)
    dir_part_info = os.path.join(local_dir, 'demo_study', 'participant_info')
    users = []
    with open(dir_part_info + '.txt', 'r') as in_file:
        for line in in_file:
            if line[0] == '#':
                continue
            else:
                split_line = line.split(',')
                next_case = get_next_case(os.path.join(dir_part_info, split_line[0] + '.txt'), int(split_line[2]))
                if next_case == 'user_finished':
                    users.append({'name': split_line[0], 'user_id': split_line[0], 'access': split_line[1],
                                  'count': split_line[2], 'next_case': next_case, 'isFinished': True})
                else:
                    users.append({'name': split_line[0], 'user_id': split_line[0], 'access': split_line[1],
                                  'count': split_line[2], 'next_case': next_case, 'isFinished': False})

    template = loader.get_template('LEMRinterface/home_screen.html')
    context_dict = {
        'full': users
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
