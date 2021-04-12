"""
SEMRinterface/loaddata_synthea.py
version 3.0
package github.com/ajk77/SimpleEMRSystem
Created by AndrewJKing.com|@andrewsjourney

This file is for ETL on a folder of synthea CSV files. 

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


#from SimpleEMRSystem.utils import *

import os
import time
import datetime
import pickle
import json
import unicodedata
import re
import shutil
from dateutil.relativedelta import relativedelta
from datetime import datetime



def save_obj(obj, store_path):
    pickle.dump(obj, open(store_path, 'wb'))
    return


def load_obj(load_path):
    obj = pickle.load(open(load_path, 'rb'))
    return obj
    
def try_to_parse_date(in_str):
    return_date = False
    try:
        return_date = datetime.strptime(in_str,"%Y-%m-%dT%H:%M:%SZ")
    except:
        try:
            return_date = datetime.strptime(in_str,"%Y-%m-%d")
        except:
            pass
    return return_date

def load_encounters(curr_dir, encounter_codes_to_keep=False, number_of_encounters_to_load=-1):
    '''
    load encounters
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_details = {}
    patient_encounters = {}
    SNOMED_TO_TEXT_subset = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if encounter_codes_to_keep and split_line[8] not in encounter_codes_to_keep: 
            continue  

        # calculate length of stay 
        start_date = datetime.strptime(split_line[1], "%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.strptime(split_line[2], "%Y-%m-%dT%H:%M:%SZ")
        length_of_stay = (end_date-start_date).days

        # populate encounter details)
        encounter_details[split_line[0]] = {} 
        encounter_details[split_line[0]]['PATIENT_ID'] = split_line[3]
        encounter_details[split_line[0]]['START_DATETIME'] = start_date
        encounter_details[split_line[0]]['END_DATETIME'] = end_date
        encounter_details[split_line[0]]['SNOMED_CODE'] = split_line[8]
        encounter_details[split_line[0]]['SNOMED_REASONCODE'] = split_line[13]
        encounter_details[split_line[0]]['ENCOUNTER_TYPE'] = split_line[7]
        encounter_details[split_line[0]]['LENGTH_OF_STAY'] = length_of_stay
        
        # populate patient_encounters #
        if split_line[3] not in patient_encounters:
            patient_encounters[split_line[3]] = []
        patient_encounters[split_line[3]].append(split_line[0])

        # update and return SNOMED to text #
        if split_line[8] and split_line[8] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[8]] = split_line[9]
        if split_line[13] and split_line[13] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[13]] = split_line[14]
            
        if len(encounter_details) == number_of_encounters_to_load:
            break
    in_file.close()

    return encounter_details, patient_encounters, SNOMED_TO_TEXT_subset


def load_patient_details(curr_dir, patient_ids):
    '''
    load patient details of pateints with encounters 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    patient_details = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[0] not in patient_ids: 
            continue # skips patients without a loaded encounter encounters
        patient_details[split_line[0]] = {} 
        patient_details[split_line[0]]['BIRTHDATE'] = split_line[1]
        patient_details[split_line[0]]['DEATHDATE'] = split_line[2]
        patient_details[split_line[0]]['SSN'] = split_line[3]
        patient_details[split_line[0]]['PREFIX'] = split_line[6]
        patient_details[split_line[0]]['FIRST'] = split_line[7]
        patient_details[split_line[0]]['LAST'] = split_line[8]
        patient_details[split_line[0]]['SUFFIX'] = split_line[9]
        patient_details[split_line[0]]['MAIDEN'] = split_line[10]
        patient_details[split_line[0]]['MARITAL'] = split_line[11]
        patient_details[split_line[0]]['RACE'] = split_line[12]
        patient_details[split_line[0]]['ETHNICITY'] = split_line[13]
        patient_details[split_line[0]]['GENDER'] = split_line[14]
    in_file.close()

    return patient_details


def load_observations(curr_dir, encounter_ids):
    '''
    load observations linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_observations[encounter_id][LOINC_CODE] = [{observation_details}, {observation_details}, ...]
        where observation_details include {date}, {value}, {units}, {type}
    also retuns LOINC_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_observations = {}
    LOINC_TO_TEXT_subset = {}
    for line in in_file:
        split_line = line.rstrip().split(',')

        if split_line[2] not in encounter_ids: 
            continue # skips observations not linked to a loaded encounter

        if split_line[2] not in encounter_observations: # determine if encounter is in observation dict
            encounter_observations[split_line[2]] = {} 
        
        if split_line[3] not in encounter_observations[split_line[2]]: # determine if observation code is in encounter's observation dict
            encounter_observations[split_line[2]][split_line[3]] = []

        # load details of current observation #
        current_observation = {}
        parsed_date = try_to_parse_date(split_line[0])
        if parsed_date:
            current_observation['DATETIME'] = parsed_date
        else:
            continue 
        current_observation['VALUE'] = split_line[5]
        current_observation['UNITS'] = split_line[6]
        current_observation['TYPE'] = split_line[7]
        encounter_observations[split_line[2]][split_line[3]].append(current_observation)

        # add observation code to the LOINC to text dict, if it was not already added
        if split_line[3] not in LOINC_TO_TEXT_subset:
            LOINC_TO_TEXT_subset[split_line[3]] = split_line[4]
    in_file.close()

    return encounter_observations, LOINC_TO_TEXT_subset

def load_medications(curr_dir, encounter_ids, SNOMED_TO_TEXT_subset):
    '''
    load medications linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_medications[encounter_id][RXNORM_CODE] = [{medication_details}, {medication_details}, ...]
        where medication_details include {START_TIME}, {STOP_TIME}, {DISPENSES}, {REASON_CODE}
    also retuns RXNORM_TO_TEXT_subset dictionary 
    also returns SNOMED_TO_TEXT_subset dictionary
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_medications = {}
    RXNORM_TO_TEXT_subset = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[4] not in encounter_ids: 
            continue # skips medications not linked to a loaded encounter
        if split_line[4] not in encounter_medications: # determine if encounter is in medication dict
            encounter_medications[split_line[4]] = {} 
        
        if split_line[5] not in encounter_medications[split_line[4]]: # determine if medication code is in encounter's medicaition dict
            encounter_medications[split_line[4]][split_line[5]] = []

        # load details of current medication #
        current_medication = {}
        parsed_date = try_to_parse_date(split_line[0])
        if parsed_date:
            current_medication['START_DATETIME'] = parsed_date
        else:
            continue 
        parsed_date = try_to_parse_date(split_line[1])
        if parsed_date:
            current_medication['STOP_DATETIME'] = parsed_date
        else:
            current_medication['STOP_DATETIME'] = '' 
        current_medication['DISPENSES'] = split_line[10]
        current_medication['SNOMED_REASONCODE'] = split_line[11]
        encounter_medications[split_line[4]][split_line[5]].append(current_medication)

        # add medication code to the RXNORM to text dict, if it was not already added
        if split_line[5] not in RXNORM_TO_TEXT_subset:
            RXNORM_TO_TEXT_subset[split_line[5]] = split_line[6]
        # uodate SNOMED codes, if one was not already added
        if split_line[11] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[11]] = split_line[12]
    in_file.close()

    return encounter_medications, RXNORM_TO_TEXT_subset, SNOMED_TO_TEXT_subset

def load_procedures(curr_dir, encounter_ids, SNOMED_TO_TEXT_subset):
    '''
    load procedures linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_procedures[encounter_id] = [{procedure_details}, {procedure_details}, ...]
        where procedure_details include {SNOMED_CODE}, {date}, {SNOMED_REASONCODE}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_procedures = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[2] not in encounter_ids: 
            continue # skips procedures not linked to a loaded encounter
        if split_line[2] not in encounter_procedures: # determine if encounter is in procedure dict
            encounter_procedures[split_line[2]] = [] 

        # load details of current procedure #
        current_procedure = {}
        current_procedure['SNOMED_CODE'] = split_line[3]
        parsed_date = try_to_parse_date(split_line[0])
        if parsed_date:
            current_procedure['DATETIME'] = parsed_date
        else:
            continue
        current_procedure['SNOMED_REASONCODE'] = split_line[5]
        encounter_procedures[split_line[2]].append(current_procedure)

        # add procedure and reason codes to the SNOMED to text dict, if they was not already added
        if split_line[3] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[3]] = split_line[4]
        if split_line[5] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[5]] = split_line[6]
    in_file.close()

    return encounter_procedures, SNOMED_TO_TEXT_subset


def load_conditions(curr_dir, encounter_ids, SNOMED_TO_TEXT_subset):
    '''
    load careplans linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_conditions[encounter_id] = [{condition_details}, {condition_details}, ...]
        where condition_details include {SNOMED_CODE}, {START_DATE}, {END_DATE}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_conditions = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[3] not in encounter_ids: 
            continue # skips conditions not linked to a loaded encounter
        if split_line[3] not in encounter_conditions: # determine if encounter is in condition dict
            encounter_conditions[split_line[3]] = [] 

        # load details of current condition #
        current_condition = {}
        current_condition['SNOMED_CODE'] = split_line[4]
        current_condition['START_DATE'] = datetime.strptime(split_line[0],"%Y-%m-%d")
        if split_line[1]:
            current_condition['END_DATE'] = datetime.strptime(split_line[1],"%Y-%m-%d")
        else:
            current_condition['END_DATE'] = ''
        encounter_conditions[split_line[3]].append(current_condition)

        # add careplan and reason codes to the SNOMED to text dict, if they was not already added
        if split_line[4] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[4]] = split_line[5]
    in_file.close()

    return encounter_conditions, SNOMED_TO_TEXT_subset

def load_careplans(curr_dir, encounter_ids, SNOMED_TO_TEXT_subset):
    '''
    load careplans linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_careplan[encounter_id] = [{careplan_details}, {careplan_details}, ...]
        where careplan_details include {SNOMED_CODE}, {START_DATE}, {END_DATE}, {SNOMED_REASONCODE}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_careplans = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[4] not in encounter_ids: 
            continue # skips careplans not linked to a loaded encounter
        if split_line[4] not in encounter_careplans: # determine if encounter is in careplan dict
            encounter_careplans[split_line[4]] = [] 

        # load details of current careplan #
        current_careplan = {}
        current_careplan['SNOMED_CODE'] = split_line[5]
        current_careplan['START_DATE'] = datetime.strptime(split_line[1],"%Y-%m-%d")
        if split_line[2]:
            current_careplan['END_DATE'] = datetime.strptime(split_line[2],"%Y-%m-%d")
        else:
            current_careplan['END_DATE'] = ''
        current_careplan['SNOMED_REASONCODE'] = split_line[7]
        encounter_careplans[split_line[4]].append(current_careplan)

        # add careplan and reason codes to the SNOMED to text dict, if they was not already added
        if split_line[5] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[5]] = split_line[6]
        if split_line[7] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[7]] = split_line[8]
    in_file.close()

    return encounter_careplans, SNOMED_TO_TEXT_subset


def load_imagingstudies(curr_dir, encounter_ids, SNOMED_TO_TEXT_subset):
    '''
    load imagingstudies linked to loaded encounters

    returns a dictionary of the following structure:
        encounter_imagingstudies[encounter_id] = [{imagingstudy_details}, {imagingstudy_details}, ...]
        where imagingstudy_details include {SNOMED_BODYSITECODE}, {DATETIME}, {MODALITY_DESCRIPTION}, {MODALITY_CODE}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    encounter_imagingstudies = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[3] not in encounter_ids: 
            continue # skips careplans not linked to a loaded encounter
        if split_line[3] not in encounter_imagingstudies: # determine if encounter is in careplan dict
            encounter_imagingstudies[split_line[3]] = [] 

        # load details of current careplan #
        current_careplan = {}
        current_careplan['SNOMED_BODYSITECODE'] = split_line[4]
        parsed_date = try_to_parse_date(split_line[1])
        if parsed_date:
            current_careplan['DATETIME'] = parsed_date
        else:
            continue
        current_careplan['MODALITY_DESCRIPTION'] = split_line[7]
        current_careplan['MODALITY_CODE'] = split_line[6]
        encounter_imagingstudies[split_line[3]].append(current_careplan)

        # add bodysite code to the SNOMED to text dict, if they was not already added
        if split_line[4] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[4]] = split_line[5]
    in_file.close()

    return encounter_imagingstudies, SNOMED_TO_TEXT_subset


def load_immunizations(curr_dir, patient_ids):
    '''
    load immunizations linked to loaded patients

    returns a dictionary of the following structure:
        patient_immunizations[patient_id] = [{immunization_details}, {immunization_details}, ...]
        where immunization_details include {CVX_CODE}, {DATE}
    also retuns CVX_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    patient_immunizations = {}
    CVX_TO_TEXT_subset = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[1] not in patient_ids: 
            continue # skips immunizations not linked to a loaded patient
        if split_line[1] not in patient_immunizations: # determine if patient is in immunization dict
            patient_immunizations[split_line[1]] = [] 

        # load details of current immunization #
        current_immunization = {}
        parsed_date = try_to_parse_date(split_line[0])
        if parsed_date:
            current_immunization['DATETIME'] = parsed_date
        else:
            continue
        current_immunization['CVX_CODE'] = split_line[3]
        patient_immunizations[split_line[1]].append(current_immunization)

        # add procedure and reason codes to the SNOMED to text dict, if they was not already added
        if split_line[3] not in CVX_TO_TEXT_subset:
            CVX_TO_TEXT_subset[split_line[3]] = split_line[4]
    in_file.close()

    return patient_immunizations, CVX_TO_TEXT_subset


def load_devices(curr_dir, patient_ids, SNOMED_TO_TEXT_subset):
    '''
    load devices linked to loaded patients

    returns a dictionary of the following structure:
        patient_devices[patient_id] = [{device_details}, {device_details}, ...]
        where device_details include {SNOMED_CODE}, {START_DATETIME}, {END_DATETIME}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    patient_devices = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[2] not in patient_ids: 
            continue # skips immunizations not linked to a loaded patient
        if split_line[2] not in patient_devices: # determine if patient is in immunization dict
            patient_devices[split_line[2]] = [] 

        # load details of current device #
        current_device = {}
        parsed_date = try_to_parse_date(split_line[0])
        if parsed_date:
            current_device['START_DATETIME'] = parsed_date
        else:
            continue
        parsed_date = try_to_parse_date(split_line[1])
        if parsed_date:
            current_device['END_DATETIME'] = parsed_date
        else:
            current_device['END_DATETIME'] = ''
        current_device['SNOMED_CODE'] = split_line[4]
        patient_devices[split_line[2]].append(current_device)

        # add device to the SNOMED to text dict, if they was not already added
        if split_line[4] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[4]] = split_line[5]
    in_file.close()

    return patient_devices, SNOMED_TO_TEXT_subset


def load_allergies(curr_dir, patient_ids, SNOMED_TO_TEXT_subset):
    '''
    load allergies linked to loaded patient

    returns a dictionary of the following structure:
        patient_allergies[patient_id] = [{allergy_details}, {allergy_details}, ...]
        where allergy_details include {SNOMED_CODE}, {START_DATE}, {END_DATE}
    also retuns SNOMED_TO_TEXT_subset dictionary 
    '''
    in_file = open(curr_dir, 'r', encoding="utf8")
    patient_allergies = {}
    for line in in_file:
        split_line = line.rstrip().split(',')
        if split_line[2] not in patient_ids: 
            continue # skips allergies not linked to a loaded patient
        if split_line[2] not in patient_allergies: # determine if patient is in allergy dict
            patient_allergies[split_line[2]] = [] 

        # load details of current allergy #
        current_allergy = {}
        current_allergy['START_DATETIME'] = datetime.strptime(split_line[0],"%Y-%m-%d")
        if split_line[1]:
            current_allergy['END_DATETIME'] = datetime.strptime(split_line[1],"%Y-%m-%d")
        else:
            current_allergy['END_DATETIME'] = ''
        current_allergy['SNOMED_CODE'] = split_line[4]
        patient_allergies[split_line[2]].append(current_allergy)

        # add procedure and reason codes to the SNOMED to text dict, if they was not already added
        if split_line[4] not in SNOMED_TO_TEXT_subset:
            SNOMED_TO_TEXT_subset[split_line[4]] = split_line[5]
    in_file.close()

    return patient_allergies, SNOMED_TO_TEXT_subset


def load_and_store_source_files(load_dir, store_dir, encounter_codes_to_keep, number_of_encounters_to_load):
    '''
    I: a path to a dirctory containg sythea CVS data, a path to a directory to store output, sythea encounter_types to keep (default is just encounter code = 305351004, 'Admission to intensive care unit (procedure)')
    P: ETL on each of the csv files, loaded objects are saved to store_dir
    O: no return data
    '''
    encounter_details, patient_encounters, SNOMED_TO_TEXT_subset = load_encounters(load_dir+'encounters.csv', encounter_codes_to_keep, number_of_encounters_to_load)
    loaded_encounter_list = list(encounter_details.keys())
    loaded_patient_list = list(patient_encounters.keys())
    patient_details = load_patient_details(load_dir+'patients.csv', loaded_patient_list)
    encounter_observations, LOINC_TO_TEXT_subset = load_observations(load_dir+'observations.csv', loaded_encounter_list)
    encounter_medications, RXNORM_TO_TEXT_subset, SNOMED_TO_TEXT_subset = load_medications(load_dir+'medications.csv', loaded_encounter_list, SNOMED_TO_TEXT_subset)
    encounter_procedures, SNOMED_TO_TEXT_subset = load_procedures(load_dir+'procedures.csv', loaded_encounter_list, SNOMED_TO_TEXT_subset)
    encounter_conditions, SNOMED_TO_TEXT_subset = load_conditions(load_dir+'conditions.csv', loaded_encounter_list, SNOMED_TO_TEXT_subset)
    encounter_careplans, SNOMED_TO_TEXT_subset = load_careplans(load_dir+'careplans.csv', loaded_encounter_list, SNOMED_TO_TEXT_subset)
    encounter_imagingstudies, SNOMED_TO_TEXT_subset = load_imagingstudies(load_dir+'imaging_studies.csv', loaded_encounter_list, SNOMED_TO_TEXT_subset)
    patient_immunizations, CVX_TO_TEXT_subset = load_immunizations(load_dir+'immunizations.csv', loaded_patient_list)
    patient_devices, SNOMED_TO_TEXT_subset = load_devices(load_dir+'devices.csv', loaded_patient_list, SNOMED_TO_TEXT_subset)
    patient_allergies, SNOMED_TO_TEXT_subset = load_allergies(load_dir+'allergies.csv', loaded_patient_list, SNOMED_TO_TEXT_subset)
    
    save_obj(encounter_details, store_dir+'encounter_details.p')
    save_obj(patient_encounters, store_dir+'patient_encounters.p')
    save_obj(loaded_encounter_list, store_dir+'loaded_encounter_list.p')
    save_obj(loaded_patient_list, store_dir+'loaded_patient_list.p')
    save_obj(patient_details, store_dir+'patient_details.p')
    save_obj(encounter_observations, store_dir+'encounter_observations.p')
    save_obj(encounter_medications, store_dir+'encounter_medications.p')
    save_obj(encounter_procedures, store_dir+'encounter_procedures.p')
    save_obj(encounter_conditions, store_dir+'encounter_conditions.p')
    save_obj(encounter_careplans, store_dir+'encounter_careplans.p')
    save_obj(encounter_imagingstudies, store_dir+'encounter_imagingstudies.p')
    save_obj(patient_immunizations, store_dir+'patient_immunizations.p')
    save_obj(patient_devices, store_dir+'patient_devices.p')
    save_obj(patient_allergies, store_dir+'patient_allergies.p')
    save_obj(SNOMED_TO_TEXT_subset, store_dir+'SNOMED_TO_TEXT_subset.p')
    save_obj(CVX_TO_TEXT_subset, store_dir+'CVX_TO_TEXT_subset.p')
    save_obj(LOINC_TO_TEXT_subset, store_dir+'LOINC_TO_TEXT_subset.p')
    save_obj(RXNORM_TO_TEXT_subset, store_dir+'RXNORM_TO_TEXT_subset.p')

    print('COMPLETE: load_and_store_source_files()')
    return


def save_json_dumps(obj, save_path):
    '''
    I: Takes in a python object and a file path to save to
    P: Converts object to json string
    O: saves he json string at the filepath location
    '''
    with open(save_path, 'w') as f:
        f.write(json.dumps(obj))
    return


def process_observation_type(list_observations, time_cut, dflt_normal_ranges, dflt_y_axis_ranges, display_text):
    '''
    I: list of observations, case time cut, global normal range for lab of this type
    P: process numeric and descrete data into separte series
    O: [[numeric series, discrete series], descrete string values]
    '''
    data_numeric = {'x': [], 'y': [], 'unit': [], 'text': []}  # x, y, unit, string_value
    data_nominal = {'x': [], 'y': [], 'unit': [], 'text': []} # x, y, unit, string_value
    nominal_to_yIndex = []
    for observation in list_observations:
        t = observation['DATETIME'].timestamp() * 1000
        if t > time_cut:
            continue
        
        if observation['TYPE'] == 'numeric':
            data_numeric['x'].append(t)
            data_numeric['y'].append(float(observation['VALUE']))
            data_numeric['unit'].append(observation['UNITS'])
            data_numeric['text'].append(observation['VALUE'])
        elif observation['TYPE'] in ['nominal', 'text']:
            if observation['VALUE'] not in nominal_to_yIndex:
                nominal_to_yIndex.append(observation['VALUE'])
            data_nominal['x'].append(t)
            data_nominal['y'].append(nominal_to_yIndex.index(observation['VALUE']))
            data_nominal['unit'].append(observation['UNITS'])
            data_nominal['text'].append(observation['VALUE'])
        else:
            print("***WARNING: unaccounted for observation['TYPE']:", observation['TYPE'], "***")

    ## creating numeric time series ##
    numeric = {"name": "numeric_values", 
                "zones": [], 
                "data": list(zip(data_numeric['x'], data_numeric['y'])), 
                "marker": {"symbol": "circle"}}
    if dflt_normal_ranges[0] and dflt_normal_ranges[1]:  # high values red & low values blue
        numeric["zones"].append({"value": dflt_normal_ranges[0], "color": "#00CCFF"})  # blue
        numeric["zones"].append({"value": dflt_normal_ranges[1], "color": "#33CC33"})  # green
        numeric["zones"].append({"color": "#BF0B23"})  # red
    elif dflt_normal_ranges[0] == "" and dflt_normal_ranges[1]:  # high values red & rest green
        numeric["zones"].append({"value": dflt_normal_ranges[1], "color": "#33CC33"})  # green
        numeric["zones"].append({"color": "#BF0B23"})  # red
    elif dflt_normal_ranges[0] and dflt_normal_ranges[1] == "":  # low values blue & rest green
        numeric["zones"].append({"value": dflt_normal_ranges[0], "color": "#00CCFF"})  # blue
        numeric["zones"].append({"color": "#33CC33"})  # green
    else:  # all values black
        numeric["zones"].append({"color": "#000000"})  # black

    ## creating nominal time series ## 
    discrete = {"name": "discrete_values", 
                "color": "#000000", 
                "data": list(zip(data_nominal['x'], data_nominal['y'])), 
                "marker": {"symbol": "square"}}

    # insert ranges with default values #
    y_axis_ranges = dflt_y_axis_ranges
    # replace ranges with actual ranges #
    if len(data_numeric['y']):  
        y_axis_ranges = [min(data_numeric['y']), max(data_numeric['y'])]
    elif len(data_nominal['y']):
        y_axis_ranges = [min(data_nominal['y']), max(data_nominal['y'])]
        
    dict_result = {}
    dict_result["display_text"] = display_text
    dict_result["numeric_lab_data"] = [numeric] if len(numeric["data"]) else []
    dict_result["discrete_lab_data"] = [discrete] if len(discrete["data"]) else []
    dict_result["discrete_nominal_to_yIndex"] = nominal_to_yIndex
    dict_result["y_axis_ranges"] = y_axis_ranges
    
    return dict_result

def process_medication_type(list_medication_orders, time_cut, display_name, SNOMED_TO_TEXT):
    '''

    '''
    ## parsing data ##
    data_med = {'x': [], 'dispenses': [], 'reason_code': [], 'reason_text': []}
    for order in list_medication_orders:
        t = order['START_DATETIME'].timestamp() * 1000
        if t > time_cut:
            continue
        data_med['x'].append(t)
        data_med['dispenses'].append(float(order['DISPENSES']))
        data_med['reason_code'].append(order['SNOMED_REASONCODE'])
        data_med['reason_text'].append(SNOMED_TO_TEXT[order['SNOMED_REASONCODE']])

    ## settin y_axis_ranges ##
    if len(data_med['x']): 
        y_axis_ranges = [min(data_med['dispenses']), max(data_med['dispenses'])]
    else:
        y_axis_ranges = [0, 0]

    ## creating med time series ## 
    med_data = {"name": "medication_data", 
                "color": "#000000", 
                "data": list(zip(data_med['x'], data_med['dispenses'])), 
                "marker": {"symbol": "circle"},
                "med_reason_tooltips": data_med['reason_text']}    
    
    dict_result = {}
    dict_result["display_text"] = display_name
    dict_result["med_data"] = [med_data]
    dict_result["y_axis_ranges"] = y_axis_ranges
    
    return dict_result

def process_free_text_type(list_free_texts, time_cut, text_type, CODE_TO_TEXT):
    '''

    '''
    data_curr = []
    date_list = []
    i = 0
    for dict_text in list_free_texts:
        curr_text = {}
        ## time and date ##
        if text_type in ['procedure', 'imagingstudy', 'immunization']:
            t = dict_text['DATETIME'].timestamp() * 1000
            dt = dict_text['DATETIME']
        else:  # means text_type in ['condition', 'careplan', 'allergy', 'device']:
            t = dict_text['START_DATE'].timestamp() * 1000
            dt = dict_text['START_DATE']
        if t > time_cut:
            continue

        date_list.append((t, i))
        curr_text['js_time'] = t
        curr_text['date'] = dt.strftime("%m/%d")
        
        ## note text ##
        if text_type in ['procedure', 'careplan']:
            curr_text['text'] = 'Reason: ' + CODE_TO_TEXT[dict_text['SNOMED_REASONCODE']]
        elif text_type in ['imagingstudy']:
            curr_text['text'] = 'Type of study: ' + dict_text['MODALITY_DESCRIPTION']
        elif text_type in ['immunization']:
            curr_text['text'] = CODE_TO_TEXT[dict_text['CVX_CODE']]
        else:  # means text_type in ['condition', 'allergy', 'device']
            curr_text['text'] = CODE_TO_TEXT[dict_text['SNOMED_CODE']]
        
        ## note type ##
        if text_type in ['procedure', 'condition', 'careplan', 'allergy', 'device']:
            curr_text['type'] = CODE_TO_TEXT[dict_text['SNOMED_CODE']]
        elif text_type in ['imagingstudy']:
            curr_text['type'] = dict_text['MODALITY_CODE'] + '-' + CODE_TO_TEXT[dict_text['SNOMED_BODYSITECODE']]
        else:  # means text_type in ['immunization']:
            curr_text['type'] = CODE_TO_TEXT[dict_text['CVX_CODE']]
        data_curr.append(curr_text)

    date_list.sort(key = lambda x: x[0], reverse=True)
    for q in range(len(date_list)):
        data_curr[date_list[q][1]]['upk'] = q
                
    return data_curr



def update_cases_synthea(source_file_dir, base_dir, load_source_files, replace_files, encounter_codes_to_keep=['305351004'], number_of_encounters_to_load=50, min_observation_fields=15, min_medication_types=3):
    '''
    '305351004' is the code for an ICU encounter
    '''
    print('^^^^^^^^^^^^^^^^^^^in load_synthea.py^^^^^^^^^^^^^^^^^^^^^^^')

    obj_store_dir = os.path.join(base_dir, 'stored_objects/')

    ## ETL on source files to create store data objects ###
    if load_source_files:
        load_and_store_source_files(source_file_dir, obj_store_dir, encounter_codes_to_keep, number_of_encounters_to_load)
    
    ## load stored data objects ##
    # load patients and encounters #
    encounter_details = load_obj(obj_store_dir+'encounter_details.p')
    patient_encounters = load_obj(obj_store_dir+'patient_encounters.p')
    loaded_encounter_list = load_obj(obj_store_dir+'loaded_encounter_list.p')
    loaded_patient_list = load_obj(obj_store_dir+'loaded_patient_list.p')
    patient_details = load_obj(obj_store_dir+'patient_details.p')
    # load observations, meds, and notes #
    encounter_observations = load_obj(obj_store_dir+'encounter_observations.p')
    encounter_medications = load_obj(obj_store_dir+'encounter_medications.p')
    encounter_procedures = load_obj(obj_store_dir+'encounter_procedures.p')
    encounter_conditions = load_obj(obj_store_dir+'encounter_conditions.p')
    encounter_careplans = load_obj(obj_store_dir+'encounter_careplans.p')
    encounter_imagingstudies = load_obj(obj_store_dir+'encounter_imagingstudies.p')
    patient_immunizations = load_obj(obj_store_dir+'patient_immunizations.p')
    patient_devices = load_obj(obj_store_dir+'patient_devices.p')
    patient_allergies = load_obj(obj_store_dir+'patient_allergies.p')
    # load code to text dictionaries #
    SNOMED_TO_TEXT_subset = load_obj(obj_store_dir+'SNOMED_TO_TEXT_subset.p')
    CVX_TO_TEXT_subset = load_obj(obj_store_dir+'CVX_TO_TEXT_subset.p')
    LOINC_TO_TEXT_subset = load_obj(obj_store_dir+'LOINC_TO_TEXT_subset.p')
    RXNORM_TO_TEXT_subset = load_obj(obj_store_dir+'RXNORM_TO_TEXT_subset.p')
        
    print('LOADED: ', len(loaded_patient_list), 'pateints and', len(loaded_encounter_list), 'encounters') 

    ## load global files ##
    dict_variable_detail = json.load(open(os.path.join(base_dir, 'variable_details.json'), 'r'))  # file needs manual edits  
    dict_med_detail = json.load(open(os.path.join(base_dir, 'med_details.json'), 'r'))  # file needs manual edits  
    
    ## empty existing directory and create case_list.txt ##
    if replace_files:
        try:
            shutil.rmtree(os.path.join(base_dir, 'cases_all'))
        except:
            pass
        os.mkdir(os.path.join(base_dir, 'cases_all'))

    ## create list_case_dicts ##
    list_case_dicts = []
    
    ### Process for each encounter ###
    n = 0
    for enc_id in loaded_encounter_list:
        if enc_id in encounter_observations and enc_id in encounter_medications and len(encounter_observations[enc_id]) >= min_observation_fields and len(encounter_medications[enc_id]) >= min_medication_types:
            pass
        else:
            continue 
    
        if enc_id in encounter_observations:
            if replace_files:
                os.mkdir(os.path.join(base_dir, 'cases_all', enc_id))
                case_dir = os.path.join(base_dir, 'cases_all', enc_id)
        else:
            continue  

        # create case_dict #
        dict_case = {}
        
        ## global_time ##
        dict_curr = {}
        dict_curr['min_t'] = encounter_details[enc_id]['START_DATETIME'].timestamp() * 1000
        dict_curr['max_t'] = encounter_details[enc_id]['END_DATETIME'].timestamp() * 1000
        time_cut = dict_curr['max_t']  # defult time_cut is discharge time

        # update case_dict ##
        dict_case["case_id"] = enc_id
        dict_case["min_t"] = dict_curr['min_t']
        dict_case["max_t"] = dict_curr['max_t']
        dict_case["START_DATETIME"] = encounter_details[enc_id]['START_DATETIME'].strftime("%Y/%m/%d")
        dict_case["END_DATETIME"] = encounter_details[enc_id]['END_DATETIME'].strftime("%Y/%m/%d")
        dict_case["admit_reason"] = SNOMED_TO_TEXT_subset[encounter_details[enc_id]['SNOMED_REASONCODE']]
        dict_case["encounter_type"] = encounter_details[enc_id]['ENCOUNTER_TYPE']
        dict_case["length_of_stay"] = encounter_details[enc_id]['LENGTH_OF_STAY']

        ## demographics ##
        dict_curr = {}
        patient_id = encounter_details[enc_id]['PATIENT_ID']
        birthdate = datetime.strptime(patient_details[patient_id]['BIRTHDATE'],"%Y-%m-%d")
        dict_curr['age'] = relativedelta(encounter_details[enc_id]['START_DATETIME'], birthdate).years
        dict_curr['sex'] = patient_details[patient_id]['GENDER']
        dict_curr['race'] = patient_details[patient_id]['RACE']
        dict_curr['ethnicity'] = patient_details[patient_id]['ETHNICITY']
        dict_curr['id'] = enc_id
        dict_curr['name'] = patient_details[patient_id]['FIRST'] + ' ' + patient_details[patient_id]['LAST']
        if replace_files:
            save_json_dumps(dict_curr, os.path.join(case_dir, 'demographics.json'))
        
        # update case_dict #
        dict_case["patient_id"] = patient_id
        dict_case["patient_name"] = dict_curr['name']

        ## observations (labs and vitals) ##
        dict_curr = {}
        if enc_id in encounter_observations:
            for observation_code in encounter_observations[enc_id]:
                if observation_code not in dict_variable_detail:
                    dict_variable_detail[observation_code] = {}
                    dict_variable_detail[observation_code]["display_group"] = "UNASSIGNED"
                    dict_variable_detail[observation_code]["original_name"] = LOINC_TO_TEXT_subset[observation_code]
                    split_on_bracket = LOINC_TO_TEXT_subset[observation_code].split('[')
                    if len(split_on_bracket) == 2:
                        dict_variable_detail[observation_code]["display_name"] = split_on_bracket[0].rstrip()
                        dict_variable_detail[observation_code]["units"] = split_on_bracket[1].split(']')[0]
                    else:
                        dict_variable_detail[observation_code]["display_name"] = LOINC_TO_TEXT_subset[observation_code]
                        dict_variable_detail[observation_code]["units"] = ""
                    dict_variable_detail[observation_code]["dflt_normal_ranges"] = ["", ""]
                    dict_variable_detail[observation_code]["dflt_y_axis_ranges"] = [0, 0]
                    
                dict_curr[observation_code] = process_observation_type(
                                            encounter_observations[enc_id][observation_code], 
                                            time_cut, 
                                            dict_variable_detail[observation_code]["dflt_normal_ranges"],
                                            dict_variable_detail[observation_code]["dflt_y_axis_ranges"],
                                            dict_variable_detail[observation_code]["original_name"]
                                            )
        if replace_files:
            save_json_dumps(dict_curr, os.path.join(case_dir, 'observations.json'))
            
        # update case_dict #
        if enc_id in encounter_observations:
            dict_case["number_of_observation_fields"] = len(encounter_observations[enc_id])
        else:
            dict_case["number_of_observation_fields"] = 0

        ## meds ##
        dict_curr = {}
        if enc_id in encounter_medications:
            for medication_code in encounter_medications[enc_id]:
                if medication_code not in dict_med_detail:
                    dict_med_detail[medication_code] = {}
                    dict_med_detail[medication_code]["med_route"] = "All_routes"
                    dict_med_detail[medication_code]["display_name"] = RXNORM_TO_TEXT_subset[medication_code]
                med_result = process_medication_type(
                    encounter_medications[enc_id][medication_code],
                    time_cut,
                    dict_med_detail[medication_code]["display_name"],
                    SNOMED_TO_TEXT_subset
                    )
                dict_curr[medication_code] = med_result        
        if replace_files:
            save_json_dumps(dict_curr, os.path.join(case_dir, 'medications.json'))
            
        # update case_dict #
        if enc_id in encounter_medications:
            dict_case["number_of_medication_fields"] = len(encounter_medications[enc_id])
        else:
            dict_case["number_of_medication_fields"] = 0

        ### note_panel_groups ###
        note_panel_data = {}

        ## procedures ##
        result = []
        if enc_id in encounter_procedures:
            #print(encounter_procedures[enc_id])
            # [{SNOMED_CODE, DATETIME, SNOMED_REASONCODE}, ...
            result = process_free_text_type(
                encounter_procedures[enc_id],
                time_cut,
                'procedure',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Procedure'] = result

        ## conditions ##
        result = []
        if enc_id in encounter_conditions:
            #print(encounter_conditions[enc_id])            
            # [{SNOMED_CODE, START_DATE, END_DATE}, ...
            result = process_free_text_type(
                encounter_conditions[enc_id],
                time_cut,
                'condition',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Condition'] = result        

        ## careplans ##
        result = []
        if enc_id in encounter_careplans:
            #print(encounter_careplans[enc_id])            
            # [{SNOMED_CODE, START_DATE, END_DATE, SNOMED_REASONCODE}, ...
            result = process_free_text_type(
                encounter_careplans[enc_id],
                time_cut,
                'careplan',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Careplan'] = result

        ## imagingstudies ##
        result = []
        if enc_id in encounter_imagingstudies:
            #print(encounter_imagingstudies[enc_id])            
            # [{SNOMED_BODYSITECODE, DATETIME, MODALITY_DESCRIPTION, MODALITY_CODE}, ...
            result = process_free_text_type(
                encounter_imagingstudies[enc_id],
                time_cut,
                'imagingstudy',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Images'] = result

        ## immunizations ##
        result = []
        if enc_id in patient_immunizations:
            #print(patient_immunizations[enc_id])            
            # [{CVX_CODE, DATETIME},...
            result = process_free_text_type(
                patient_immunizations[enc_id],
                time_cut,
                'immunization',
                CVX_TO_TEXT_subset
                )
        note_panel_data['Immunizations'] = result

        ## allergies ##
        result = []
        if enc_id in patient_allergies:
            #print(patient_allergies[enc_id])            
            # [{SNOMED_CODE, START_DATE, END_DATE},...
            result = process_free_text_type(
                patient_allergies[enc_id],
                time_cut,
                'allergy',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Allergies'] = result

        ## devices ##
        result = []
        if enc_id in patient_devices:
            #print(patient_devices[enc_id])            
            # [{SNOMED_CODE, START_DATE, END_DATE},...
            result = process_free_text_type(
                patient_devices[enc_id],
                time_cut,
                'device',
                SNOMED_TO_TEXT_subset
                )
        note_panel_data['Device'] = result

        if replace_files:
           save_json_dumps(result, os.path.join(case_dir, 'note_panel_data.json'))
        ### end note_panel_groups ###

        # add case_dict to list_case_dicts #
        list_case_dicts.append(dict_case)

        ## break after number_of_encounters_to_load is exceeded ##
        n += 1
        if n > number_of_encounters_to_load:
            break

    if replace_files:
        save_json_dumps(dict_variable_detail, os.path.join(base_dir, 'variable_details.json'))
        save_json_dumps(dict_med_detail, os.path.join(base_dir, 'med_details.json'))
        save_json_dumps(list_case_dicts, os.path.join(base_dir, 'list_case_dicts.json'))   

    return


if __name__=='__main__':

    ### Generate cases_all for synthea ### 
    source_file_dir = '../resources/100k_synthea_covid19_csv/100k_synthea_covid19_csv/'  # the source synthea CSV dir
    base_dir = '../resources/synthea_study'  # the study dir 
    obj_store_dir = os.path.join(base_dir, 'stored_objects/')  # where data objects are stored
    load_source_files = False  # if False, existing ETL from source_file_dir to data objects will be used. 
    replace_files = True  # If False, no data will be replaced
    encounter_codes_to_keep = ['305351004'] # the encounter codes to load ('305351004' is an ICU encounter)
    number_of_encounters_to_load = 25 # max number of cases to load
    min_observation_fields = 15  # min number of observation types for encounter to process
    min_medication_types = 3  # min number of observation types for encounter to process


    update_cases_synthea(source_file_dir, base_dir, load_source_files, replace_files, encounter_codes_to_keep, number_of_encounters_to_load, min_observation_fields, min_medication_types)
