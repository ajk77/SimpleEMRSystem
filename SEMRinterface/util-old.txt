"""
LEMRinterface/utils.py
version 2.0
package github.com/ajk77/LEMRinterface
Created by AndrewJKing.com|@andrewsjourney

This file contails utility functions.

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
from LEMRinterface.models import marstorootcodes
from LEMRinterface.models import rootgroupmember
from LEMRinterface.models import displayparams
from LEMRinterface.models import a_groupmember
import os
import time


def load_med_maps(med_map_filename):
    """
    this function loads the med-display-id_to_name file.
    Returns two dictionaries:
        med_cd_id - > catalog_display[name] = id
        med_or_id -> ordered_as[name] = id
    id's are integers
    multiple ordered_as names can map to the same ID
    """
    med_cd_id = {}
    med_or_id = {}
    with open(med_map_filename, 'r') as f:
        for line in f:
            s_line = line.rstrip().split('\t')
            if s_line:
                med_cd_id[s_line[1]] = s_line[0]
                med_or_id[s_line[2]] = s_line[0]

    return [med_cd_id, med_or_id]


def print_to_pixelmap_file(local_dir, is_new_patient, patient_id, str_map, timestamp):
    out_file = open(os.path.join(local_dir, "pixelmaps", "pat_"+str(patient_id)+".txt"), 'a+')
    if is_new_patient == 1:
        str_out = "#refresh\n"
        out_file.write(str_out)
        print_to_notemap_file(local_dir, 1, patient_id, str_out)
        print('\t...starting pixelmap for ' + str(patient_id))
    elif is_new_patient == 2:
        str_out = '#end:'+str(float(timestamp)/1000)+'\n'
        out_file.write(str_out)
        print_to_notemap_file(local_dir, 2, patient_id, str_out)
        print('\t...ending pixelmap for ' + str(patient_id))
    else:
        out_file.write('>>>' + str(float(timestamp)/1000)+'\n')
        out_file.write(str_map+'\n')
    out_file.close()

    return


def print_to_manual_input_file(local_dir, patient_id, timestamp, selections, rating, reason):
    print('\t___printing to input file ' + str(patient_id))
    out_file = open(os.path.join(local_dir, "manual_input", "pat_" + str(patient_id) + '.txt'), 'w+')
    out_file.write('>>>' + str(float(timestamp) / 1000) + '\n')
    out_file.write(selections + '\n')
    out_file.write('### difficulty rating ###\n')
    out_file.write(rating + '\n')
    out_file.write('--- has audio recording ---\n')
    out_file.write(reason + '\n')
    out_file.close()
    return


def print_to_notemap_file(local_dir, is_new_patient, patient_id, str_out):
    out_file_note = open(os.path.join(local_dir, "notemaps", "pat_" + str(patient_id) + '.txt'), 'a')
    if is_new_patient == 1:     # new interaction
        out_file_note.write(str_out)
    elif is_new_patient == 2:   # end of interaction
        out_file_note.write(str_out)
    else:   # during interaction
        out_file_note.write(str_out+'\n')
    return


def print_to_issue_report_file(local_dir, patient_id, timestamp, issue_text):
    print('\t---printing to issue report file ' + str(patient_id))
    out_file = open(os.path.join(local_dir, "manual_input", "issues_for_pat_" + str(patient_id) + '.txt'), 'a+')
    out_file.write('>>>' + str(float(timestamp) / 1000) + '\n')
    out_file.write(issue_text + '\n')
    out_file.close()
    return


def find_first_case(location, user_id):
    next_patient_id = 0
    in_file = open(os.path.join(location, 'participant_info.txt'), 'r')
    lines = in_file.readlines()
    in_file.close()
    num_cases = 0
    for line in lines:
        line_split = line.split(',')
        if line_split[0] == user_id:
            num_cases = int(line_split[2])
    if num_cases == 32:
        return 'end'
    else:
        in_file = open(location + user_id + '.txt', 'r')
        lines = in_file.readlines()
        in_file.close()
        for line in lines:
            if line[0] == '#':
                continue
            else:
                if num_cases == 0:
                    next_patient_id = line.split(',')[0]
                    break
                else:
                    num_cases -= 1
        return next_patient_id


def update_participant_info(user_id, location):
    import datetime
    in_file = open(location + '.txt', 'r+')
    out_lines = []
    for line in in_file:
        line_split = line.split(',')
        if line_split[0] == user_id:
            now = datetime.datetime.now()
            out_lines.append(user_id+','+now.strftime("%Y-%m-%d")+','+str(int(line_split[2])+1)+','+line_split[3])
        else:
            out_lines.append(line)
    in_file.close()
    with open(location + '.txt', 'w') as out_file:
        out_file.write(''.join(out_lines))

    return


def get_next_case(user_file, case_count):
    with open(user_file, 'r') as in_file:
        curr_case = 0
        for line in in_file:
            if line[0] == '#':
                continue
            else:
                if case_count != curr_case:
                    curr_case += 1
                    continue
                else:
                    split_line = line.rstrip().split(',')
                    if len(split_line):
                        return split_line[0]
    print('*** Matching ID was not found (1)')
    return 'user_finished'


def determine_next_url(location, user_id, time_cutoff, curr_patient_id):
    in_file = open(os.path.join(location, user_id + '.txt'), 'r')
    lines = in_file.readlines()
    in_file.close()
    for i in range(len(lines)):
        if lines[i][0] == '#':
            continue
        split_line = lines[i].rstrip().split(',')
        if len(split_line) and split_line[0] == curr_patient_id:
            store = split_line[6: 8]
            if time_cutoff == 1:
                return [split_line[0], 2, '0', '0']  # no highlights on first view
            else:
                if i == len(lines)-1:  # end of list
                    return ['end', '',  store[0], store[1]]
                split_line = lines[i+1].split(',')
                update_participant_info(user_id, location)
                return [split_line[0], 1, store[0], store[1]]  # show_highlights and only_highlights from previous row
    print('*** Matching ID was not found (2)')
    return ['error', 'here']


def load_marstoroot():
    mtr = {}  # mars to root
    rtm = {}  # root to mars
    results = marstorootcodes.objects.all()
    for result in results:
        mtr[result.marscode] = result.rootcode
        if result.rootcode in rtm.keys():
            rtm[result.rootcode].append(result.marscode)
        else:
            rtm[result.rootcode] = [result.marscode]
    return [mtr, rtm]


def load_rootgroupmember():
    groups = {}  # [groupname] = [root1, root2, ...]
    lab_group_order = [0] * 19
    rtn = {}  # root to name
    rtt = {}  # root to table
    results = rootgroupmember.objects.all()
    for result in results:
        if result.groupname in groups.keys():
            groups[result.groupname].append(result.root)
        else:
            groups[result.groupname] = [result.root]
            if result.grouprank < 20:
                lab_group_order[result.grouprank-1] = result.groupname
        rtn[result.root] = result.labname
        rtt[result.root] = result.datatable
    return [groups, lab_group_order, rtn, rtt]


def find_discrete_roots():
    discrete_roots = []
    results = rootgroupmember.objects.all()
    for result in results:
        if result.datatype == 'd':
            discrete_roots.append(result.root)
    return discrete_roots


def load_displayparams():
    rtdt = {}   # root to display type
    default_ranges = {}  # [root] -> [display min, normal range min, normal range max, display max]
    default_units = {}  # [root] -> units
    results = displayparams.objects.all()
    for result in results:
        rtdt[result.root] = result.displaytype
        default_ranges[result.root] = [None, None, None, None]
        if result.mindd is not None:
            default_ranges[result.root][0] = result.mindd
        if result.maxdd is not None:
            default_ranges[result.root][3] = result.maxdd
        default_units[result.root] = result.unitsdefault
    return [rtdt, default_ranges, default_units]


def load_a_groupmember():
    clinical_event_ranges = {'M': {}, 'F': {}}  # normal ranges for learningemr.clinicalEvent items
    results = a_groupmember.objects.all()
    for result in results:
        clinical_event_ranges['M'][result.name] = [result.lowernormal, result.uppernormal]
        clinical_event_ranges['F'][result.name] = [result.femalelowernormal, result.femaleuppernormal]
    return clinical_event_ranges


def reset_directories(local_dir, user_id=False):
    """
    Copies files into a timestamped directory and clears the working directories
    """
    import shutil
    save_time = str(time.time())
    # create study dir
    if user_id:
        interaction_dir = os.path.join(local_dir, 'evaluation_study', 'eye_tracking', str(user_id), 'run-' + save_time)
    else:
        interaction_dir = os.path.join(local_dir, 'run-' + save_time)

    if not os.path.exists(interaction_dir):
        os.makedirs(interaction_dir)
    # move dirs recreate moved dirs
    shutil.move(os.path.join(local_dir, 'interaction_stream'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir, 'interaction_stream')):
        os.makedirs(os.path.join(local_dir, 'interaction_stream'))
    shutil.move(os.path.join(local_dir, 'pixelmaps'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir,'pixelmaps')):
        os.makedirs(os.path.join(local_dir, 'pixelmaps'))
    shutil.move(os.path.join(local_dir, 'eye_stream'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir, 'eye_stream')):
        os.makedirs(os.path.join(local_dir, 'eye_stream'))
    shutil.move(os.path.join(local_dir, 'manual_input'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir, 'manual_input')):
        os.makedirs(os.path.join(local_dir, 'manual_input'))
    shutil.move(os.path.join(local_dir, 'notemaps'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir, 'notemaps')):
        os.makedirs(os.path.join(local_dir, 'notemaps'))
    shutil.move(os.path.join(local_dir, 'audio_recordings'), interaction_dir)
    if not os.path.exists(os.path.join(local_dir, 'audio_recordings')):
        os.makedirs(os.path.join(local_dir, 'audio_recordings'))

    # map the pixelmap files
    if os.path.isfile(os.path.join(interaction_dir, 'pixelmaps', 'pat_calibration.txt')):
        return interaction_dir
    else:
        return False
