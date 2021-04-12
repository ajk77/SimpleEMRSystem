"""
LEMRinterface/loaddata.py
version 1.0
package github.com/ajk77/LEMRinterface
Created by AndrewJKing.com|@andrewsjourney

This file is for connecting to a database and loading data for the LEMR interface. 

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

# crisma server
from LEMRinterface.models import a_demographics
from LEMRinterface.models import a_ClinicalEvents
from LEMRinterface.models import a_HomeMeds
from LEMRinterface.models import a_ICDCPT
from LEMRinterface.models import a_ICUpatients
from LEMRinterface.models import a_IO
from LEMRinterface.models import a_Medication
from LEMRinterface.models import a_Micro
from LEMRinterface.models import a_MicroReport
from LEMRinterface.models import a_Surgical
from LEMRinterface.models import a_Ventilator
# local_lemr
from LEMRinterface.models import lab_739

from LEMRinterface.utils import *

import os
import time
import datetime
import pickle
import json
import unicodedata
import re


run_queries = True
save_labs = False
save_notes = True

if os.path.isdir("../../models/"):
    local_dir = os.getcwd() + "/../../models/"


def save_query(query, file_name):
    pickle.dump(query, open(local_dir + 'evaluation_study/query_saving/' + file_name + '.p', 'wb'))
    return


def load_query(file_name):
    query = pickle.load(open(local_dir + 'evaluation_study/query_saving/' + file_name + '.p', 'rb'))
    return query


def uni_norm(uni_text):
    if uni_text:
        return unicodedata.normalize('NFKD', uni_text).encode('ascii', 'ignore')
    else:
        return ''


def val_unit_split(text):
    q = re.findall(r'\d\s?[a-z,A-Z]', text)
    if q:
        i = text.index(q[0])
        return [text[0:i+1], text[i+1:]]
    else:
        return [text, '']


def io_to_day(io_data):
    # #### Need to calculate 8 to 8s ###
    return io_data


def load_admit_discharge(case_id, time_cut):
    if run_queries:
        results = a_ICUpatients.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'admit_case_id')
    else:
        results = load_query('admit_case_id')
    curr_min = time_cut
    curr_max = 0
    for result in results:
        t_admit = (time.mktime(result.admit.timetuple()) - 18000) * 1000
        t_icu_discharge = (time.mktime(result.ICUdischarge.timetuple()) - 18000) * 1000
        if t_admit < curr_min:
            curr_min = t_admit
        if t_icu_discharge > curr_max:
            curr_max = t_icu_discharge
    return {"min_t": curr_min, "max_t": min(curr_max, time_cut)}, min(curr_max, time_cut)


def load_demographics(case_id):
    if run_queries:
        result = a_demographics.objects.using('remote').get(patientvisitid=case_id)
        save_query(result, 'demographics')
    else:
        result = load_query('demographics')
    if result.sex is None:
        sex = 'M'
    else:
        sex = result.sex
    return [{"id": case_id, "age": result.age, "sex": result.sex, "height": result.height,
            "weight": result.weight, "bmi": result.bmi, "race": result.race}, sex]


def load_clinical_event(case_id, event_name, time_cut):
    if run_queries:
        results = a_ClinicalEvents.objects.using('remote').filter(patientvisitid=case_id, rollname=event_name)
        save_query(results, event_name)
    else:
        results = load_query(event_name)
    curr_data = [[], [], [], []]  # [[datetime], [value], [unit], [text]]
    recent_result = [0, 0, None]  # [time, value]
    abs_ranges = [9999, -9999]
    for result in results:
        t = (time.mktime(result.date.timetuple()) - 18000) * 1000
        if t < time_cut:
            if result.rollval is None:
                continue
            curr_data[0].append(t)
            curr_data[1].append(float(result.rollval))
            curr_data[2].append(result.rollunit)
            if t > recent_result[0]:
                recent_result = [t, float(result.rollval), str(result.rollunit)]
            if result.rollvaltext is not None:
                curr_data[3].append(result.rollvaltext)
            abs_ranges = [min(abs_ranges[0], float(result.rollval)), max(abs_ranges[1], float(result.rollval))]

    return [{'datetime': curr_data[0], 'value': curr_data[1], 'unit': curr_data[2], 'text': curr_data[3]}, 
            recent_result[1:], abs_ranges]


def find_most_frequent_not_empty(input_arr):
    count_arr = [(x, input_arr.count(x)) for x in set(input_arr)]  # [(value, count), ...]
    count_arr.sort(key=lambda w: w[1], reverse=True)
    if count_arr[0][0] is not None:
        return count_arr[0][0]
    elif len(count_arr) > 1:
        return count_arr[1][0]
    else:
        return None


def process_other_ranges(input_arr):
    other_range = find_most_frequent_not_empty(input_arr)
    if other_range is None:
        return [None, None]
    else:
        if '<' in other_range:
            return [None, float(other_range.replace('<', ''))]
        elif '>' in other_range:
            return [float(other_range.replace('>', '')), None]
        else:
            return [None, None]


def load_mars_labs(case_id, root, mars_names, time_cut):
    del root
    curr_data = [[], [], [], [], [], [], []]  # [[datetime], [value], [unit], [text], [normmin], [normmax], [normother]]
    discrete_data = [[], []]  # [[datetime], [text]]
    for mars_name in mars_names:
        if run_queries:
            results = lab_739.objects.filter(patientvisitid=case_id, eventcode=mars_name)
            save_query(results, mars_name)
        else:
            results = load_query(mars_name)

        for result in results:
            t = (time.mktime(result.eventdate.timetuple()) - 18000) * 1000
            if t < time_cut:
                if result.eventvalue is None:  # if no value, try to fill it
                    try:  # strip <, >, and +, then parse to float
                        result.eventvalue = float(result.eventtext.replace('<', '').replace('>', '').replace('+', ''))
                    except ValueError:  # test if word in lookup dictionary
                        discrete_data[0].append(t)
                        discrete_data[1].append(result.eventtext)
                        continue  # do not add to curr_data
                curr_data[0].append(t)
                curr_data[1].append(float(result.eventvalue))
                curr_data[2].append(result.eventunit)
                curr_data[3].append(result.eventtext)
                curr_data[4].append(result.rangelow)
                curr_data[5].append(result.rangehigh)
                curr_data[6].append(result.rangeother)

    if len(curr_data[0]):  # if length > 0 then has results
        most_recent_t = curr_data[0].index(max(curr_data[0]))
        recent_result = [curr_data[1][most_recent_t], curr_data[2][most_recent_t]]  # most recent [value, unit]
        abs_ranges = [min(curr_data[1]), max(curr_data[1])]
        norm_ranges = [find_most_frequent_not_empty(curr_data[4]), find_most_frequent_not_empty(curr_data[5])]
        if norm_ranges[0] is None or norm_ranges[1] is None:
            norm_ranges = process_other_ranges(curr_data[6])
        return [{'datetime': curr_data[0], 'value': curr_data[1], 'unit': curr_data[2], 'text': curr_data[3]},
                recent_result, abs_ranges, norm_ranges, discrete_data]
    elif len(discrete_data[0]):
        most_recent_t = discrete_data[0].index(max(discrete_data[0]))
        recent_result = [discrete_data[1][most_recent_t], None]  # most recent [value, unit]
        return [{'datetime': curr_data[0], 'value': curr_data[1], 'unit': curr_data[2], 'text': curr_data[3]}, 
                recent_result, [None, None], [None, None], discrete_data]
    else:
        return [False, False, False, False, False]


def load_bp(case_id, time_cut, rollnames):
    curr_data = [[], [], [], []]
    recent_results = [0, 0, 0, 0]
    low_high = [[9999.9, -9999.9], [9999.9, -9999.9]]
    for i in range(len(rollnames)):
        recent_t = 0
        if run_queries:
            results = a_ClinicalEvents.objects.using('remote').filter(patientvisitid=case_id, rollname=rollnames[i])
            save_query(results, rollnames[i])
        else:
            results = load_query(rollnames[i])
        for result in results:
            t = (time.mktime(result.date.timetuple()) - 18000) * 1000
            if t < time_cut:
                if result.rollval is None:
                    continue
                curr_data[i].append([t, float(result.rollval)])
                if t > recent_t:
                    recent_t = t
                    recent_results[i] = int(result.rollval)
                if i < 2:
                    low_high[0][0] = min(low_high[0][0], float(result.rollval))
                    low_high[0][1] = max(low_high[0][1], float(result.rollval))
                else:
                    low_high[1][0] = min(low_high[1][0], float(result.rollval))
                    low_high[1][1] = max(low_high[1][1], float(result.rollval))

    diastolic = {"name": "dias", "color": "#FF8C00", "data": curr_data[0], "marker": {"symbol": "circle"}}
    systolic = {"name": "syst", "color": "#A0522D", "data": curr_data[1], "marker": {"symbol": "circle"}}
    art_diastolic = {"name": "art_dia", "color": "#FF8C00", "data": curr_data[2], "marker": {"symbol": "circle"}}
    art_systolic = {"name": "art_sys", "color": "#A0522D", "data": curr_data[3], "marker": {"symbol": "circle"}}
    recent_return = [str(recent_results[1]) + '/' + str(recent_results[0]), str(recent_results[3]) + '/' 
                     + str(recent_results[2])]
    return [[[diastolic, systolic], [art_diastolic, art_systolic]], recent_return, low_high]


def load_vent(case_id, time_cut, ventnames):
    curr_data = [[], [], [], []]
    curr_names = [[], [], [], []]
    recent_results = [[], [], [], []]
    for i in range(len(ventnames)):
        if run_queries:
            results = a_Ventilator.objects.using('remote').filter(patientvisitid=case_id, eventname=ventnames[i])
            save_query(results, ventnames[i])
        else:
            results = load_query(ventnames[i])

        series_names = []
        series_timestamps = []
        recent_result = [0, '']
        for result in results:
            t = (time.mktime(result.date.timetuple()) - 18000) * 1000
            if t < time_cut:
                result_str = uni_norm(result.resultval)
                if result_str not in series_names:
                    series_names.append(result_str)
                    series_timestamps.append([t, len(series_names)-1])
                else:
                    q = series_names.index(result_str)
                    series_timestamps.append([t, q])
                if t > recent_result[0]:
                    recent_result = [t, result_str]
        curr_data[i] = [{"name": "discrete_values", "color": "#000000", "data": series_timestamps, 
                         "marker": {"symbol": "square"}}]
        curr_names[i] = series_names
        recent_results[i] = recent_result[1]
    return [curr_data, curr_names, recent_results]


def load_io(case_id, time_cut):
    curr_data = [[], [], [], [], [], [], []]  # urine, everything else, oral, intravenous, blood products, other, net
    existing_dates = []
    if run_queries:
        results = a_IO.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'io')
    else:
        results = load_query('io')
    for result in results:
        t = (time.mktime(result.date.timetuple()) - 18000) * 1000
        if t < time_cut:
            day = ((t // 86400000) * 86400000)  # reduce to day

            if result.type == 'Output':
                if result.name == 'Urine Output':
                    io_type = 0
                else:
                    io_type = 1
            else:
                if result.category == 6:
                    io_type = 2
                elif result.category in [1, 2, 3, 4, 5, 8, 9, 10]:
                    io_type = 3
                elif result.category == 7:
                    io_type = 4
                else:  # category > 10
                    io_type = 5

            if day not in existing_dates:
                existing_dates.append(day)
                for i in range(7):
                    curr_data[i].append([day, 0])
            curr_data[io_type][existing_dates.index(day)][1] += round(result.volume, 2)

    # make output negative
    for i in range(len(curr_data[1])):
        curr_data[0][i][1] = -curr_data[0][i][1]
        curr_data[1][i][1] = -curr_data[1][i][1]
    # calculate net
    low_high = [1, -1]
    for i in range(len(existing_dates)):
        day_net = 0
        day_pos = 0
        day_neg = 0
        for q in range(6):
            day_net += curr_data[q][i][1]
            if curr_data[q][i][1] > 0:
                day_pos += curr_data[q][i][1]
            if curr_data[q][i][1] < 0:
                day_neg += curr_data[q][i][1]
        curr_data[6][i][1] = day_net
        low_high[0] = min(low_high[0], day_neg)
        low_high[1] = max(low_high[1], day_pos)

    dict_results = [{"name": 'Urine', "step": 1, "data": io_to_day(curr_data[0]), "stack": "a"},
                    {"name": 'Everything Else', "step": 1, "data": io_to_day(curr_data[1]), "stack": "a"},
                    {"name": 'Oral', "step": 1, "data": io_to_day(curr_data[2]), "stack": "a"},
                    {"name": 'Intravenous', "step": 1, "data": io_to_day(curr_data[3]), "stack": "a"},
                    {"name": 'Blood Products', "step": 1, "data": io_to_day(curr_data[4]), "stack": "a"},
                    {"name": 'Other or unknown', "step": 1, "data": io_to_day(curr_data[5]), "stack": "a"},
                    {"name": 'Net', "step": 1, "data": io_to_day(curr_data[6]), "stack": "b"}]

    return [dict_results, low_high]


def load_meds(case_id, time_cut):
    curr_data = {}
    display_med_names = {}
    id_to_catalog_display = {}  # used for linking ids from highlighting back to catalogDisp names
    route_mapping = {}  # maps routes to [orderids]
    orders = {}  # orders[orderid] = [min_time, max_time, route, orderedAs, CatalogDisp]
    order_curr_data = {}
    order_curr_text = {}
    # meds
    if run_queries:
        results = a_Medication.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'med')
    else:
        results = load_query('med')
    order_names = []
    for result in results:
        t = (time.mktime(result.date.timetuple()) - 18000) * 1000
        if t < time_cut:
            order_as = (uni_norm(result.orderedas), result.route)
            if order_as not in order_names:
                order_names.append(order_as)
                assert (len(order_names)-1 == order_names.index(order_as))
                orders[len(order_names)-1] = [t, t, result.route, uni_norm(result.orderedas), uni_norm(result.name)]
                order_curr_data[len(order_names)-1] = [[t, float(result.resultval)]]
                order_curr_text[len(order_names)-1] = [val_unit_split(uni_norm(result.event))]
            else:
                i = order_names.index(order_as)
                order_curr_data[i].append([t, float(result.resultval)])
                order_curr_text[i].append(val_unit_split(uni_norm(result.event)))
                if t < orders[i][0]:
                    orders[i][0] = t
                elif t > orders[i][1]:
                    orders[i][1] = t
                if result.route != orders[i][2]:
                    print("*** WARNING Routes are Different for " + str(order_as) + ' != ' + orders[i][2] + ' ***')
                assert (order_as[0] == orders[i][3])
    # home meds
    if run_queries:
        results = a_HomeMeds.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'h_med')
    else:
        results = load_query('h_med')
    for result in results:
        t = (time.mktime(result.date.timetuple()) - 18000) * 1000
        if t < time_cut:
            order_as = (uni_norm(result.ordername), result.ordertype)
            if order_as not in order_names:
                order_names.append(order_as)
                assert (len(order_names) - 1 == order_names.index(order_as))
                orders[len(order_names) - 1] = [t, t, result.ordertype, uni_norm(result.ordername),
                                                uni_norm(result.genericname)]
                if result.dose is None:
                    result.dose = 0
                try:
                    dose = float(str(result.dose).replace('^', ''))
                except ValueError:
                    dose = 0
                order_curr_data[len(order_names) - 1] = [[t, dose]]
                order_curr_text[len(order_names) - 1] = [val_unit_split(uni_norm(result.frequency))]
            else:
                i = order_names.index(order_as)
                if result.dose is None:
                    result.dose = 0
                try:
                    dose = float(str(result.dose).replace('^', ''))  # need because of values that include '^'
                except ValueError:
                    dose = 0
                order_curr_data[i].append([t, dose])
                order_curr_text[i].append(val_unit_split(uni_norm(result.frequency)))
                if t < orders[i][0]:
                    orders[i][0] = t
                elif t > orders[i][1]:
                    orders[i][1] = t
                if result.ordertype != orders[i][2]:
                    print("*** WARNING Routes are Different for " + str(order_as) + ' != ' + orders[i][2] + ' ***')
                assert (order_as[0] == orders[i][3])
    # process all meds
    for l_id in orders:
        if orders[l_id][0] > time_cut:
            continue  # skips orders that occured after timecut
        else:
            min_val = min(b for (a, b) in order_curr_data[l_id])
            max_val = max(b for (a, b) in order_curr_data[l_id])
            curr_data[l_id] = [[{"name": str(l_id), "color": "#000000", "data": order_curr_data[l_id],
                                 "marker": {"symbol": "circle"}}], order_curr_text[l_id], [min_val, max_val]]
            display_med_names[l_id] = orders[l_id][3]
            id_to_catalog_display[l_id] = orders[l_id][4]
            if orders[l_id][2] not in route_mapping.keys():   # check if route is in dict
                route_mapping[orders[l_id][2]] = []
            route_mapping[orders[l_id][2]].append(l_id)         # add id to route in dict

    return curr_data, display_med_names, route_mapping.keys(), route_mapping, id_to_catalog_display


def load_procedures(case_id, time_cut):
    if run_queries:
        results = a_Surgical.objects.using('remote').filter(patientvisitid=case_id, primary='Y')
        save_query(results, 'surgical')
    else:
        results = load_query('surgical')
    report_dicts = []
    procedure_dates = []
    for result_row in results:
        t = (time.mktime(result_row.date.timetuple()) - 18000) * 1000
        if t < time_cut:
            curr_date = datetime.datetime.strftime(result_row.date, "%m/%d/%Y %H:%M:%S")
            if curr_date not in procedure_dates:
                report_info_dict = {"date": curr_date, "text": result_row.procedure
                                    + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PostDx: ' + str(result_row.postdx), "js_time": t}
                report_dicts.append(report_info_dict)
                procedure_dates.append(curr_date)
            else:
                not_added = True
                for l_dict in report_dicts:
                    if l_dict['date'] == curr_date:
                        l_dict['text'] = l_dict['text']+"<br />"+result_row.procedure \
                                       + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PostDx: ' + str(result_row.postdx)
                        not_added = False
                if not_added:
                    print("***procedure not added to procedures***+\n"+curr_date)
    sorted_report_dicts = sorted(report_dicts, key=lambda element: element['date'], reverse=True)
    return sorted_report_dicts


def load_micro_reports(case_id, time_cut):
    micro_event = {}  # [eventid] -> [result_time, js_time, eventname, source]
    if run_queries:
        results = a_Micro.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'micro')
    else:
        results = load_query('micro')
    for result_row in results:
        t = (time.mktime(result_row.date.timetuple()) - 18000) * 1000
        if t > time_cut:
            continue
        elif result_row.eventid not in micro_event.keys():
            micro_event[result_row.accession] = [result_row.date, t, result_row.eventname, result_row.source]
        else:
            assert (micro_event[result_row.accession] == [result_row.date, t, result_row.eventname, result_row.source])

    if run_queries:
        results = a_MicroReport.objects.using('remote').filter(patientvisitid=case_id)
        save_query(results, 'micro_r')
    else:
        results = load_query('micro_r')

    report_dicts = []
    report_dates = []
    report_day_js_times = []
    report_day_texts = []
    for result_row in results:
        if result_row.accession in micro_event.keys():
            curr_text = result_row.text
            q = re.findall(r'[a-z,0-9]+[A-Z]+', curr_text)
            for w in range(len(q)):
                curr_text = curr_text.replace(q[w], q[w][0:-1] + '<br>' + q[w][-1])
            curr_text = '<p class="thick">'+micro_event[result_row.accession][2]+'&nbsp;&nbsp;&nbsp;&nbsp;Date:&nbsp;'\
                        + datetime.datetime.strftime(micro_event[result_row.accession][0], "%m/%d/%Y %H:%M:%S") \
                        + '</p><p></p>' + curr_text
            curr_date = datetime.datetime.strftime(micro_event[result_row.accession][0], "%m/%d/%Y")
            day_index = 0
            if curr_date not in report_dates:  # create new day
                for w in range(len(report_dates)):
                    if report_dates[w] > curr_date:
                        day_index += 1
                report_dates.insert(day_index, curr_date)
                report_day_js_times.insert(day_index, [micro_event[result_row.accession][1]])
                report_day_texts.insert(day_index, [curr_text])
            else:   # find proper hour ordering
                day_index = report_dates.index(curr_date)
                hour_index = 0
                for w in range(len(report_day_js_times[day_index])):
                    if report_day_js_times[day_index][w] > micro_event[result_row.accession][1]:
                        hour_index += 1
                report_day_js_times[day_index].insert(hour_index, micro_event[result_row.accession][1])
                report_day_texts[day_index].insert(hour_index, curr_text)

    for i in range(len(report_dates)):
        report_info_dict = {
            "date": report_dates[i], "text": '<hr>'.join(report_day_texts[i]),
            "js_time": report_day_js_times[i][0], "upk": i}
        report_dicts.append(report_info_dict)

    return report_dicts


def load_local_report(case_id, time_cut, report_type, icu_admit_t, rare_type):
    report_dicts = []
    report_tuples = []  # (report_files, report_date, report_day_js_time)

    def get_report_type(l_lines):
        if rare_type:
            return report_type
        else:
            for l_line in l_lines:
                if l_line[0] in ['[', '\n', '*']:
                    continue
                elif l_line[0:2] in [' \n']:
                    continue
                elif l_line[0:17] == 'CLINICAL HISTORY:':
                    continue
                else:
                    return l_line.rstrip()

    detail_file = local_dir + 'note_details_3.txt'
    note_dir = local_dir + 'all_processed_notes/'

    with open(detail_file, 'r') as in_file:
        for line in in_file:
            split_line = line.split('_')
            if case_id == int(split_line[0]):
                if split_line[2].split('.')[0] == report_type:
                    js_time = float(split_line[3])*1000
                    if icu_admit_t < js_time < time_cut:
                        report_tuples.append(('_'.join(split_line[0:3]), split_line[4].rstrip(), js_time))

    # sort by js_time
    r_sorted_report_tuples = sorted(report_tuples, key=lambda tup: tup[2], reverse=True)

    for i in range(len(r_sorted_report_tuples)):
        with open(note_dir + r_sorted_report_tuples[i][0]) as in_file:
            lines = in_file.readlines()
            report_info_dict = {
                "date": r_sorted_report_tuples[i][1], "text": "<br />".join(lines),
                "js_time": r_sorted_report_tuples[i][2], "type": get_report_type(lines), "upk": i}
            report_dicts.append(report_info_dict)

    return report_dicts


def load_case_date(case_id, out_folder='all/', time_cut=1451688581000):

    lab_dict = {}  # dictionary that holds all lab
    vitals_dict = {}  # dictionary that holds all vitals and vent data
    recent_results = {}  # holds the most recent result of each lab, vital, and vent chart
    mtr, rtm = load_marstoroot()    # mars to root, root to mars
    groups, lab_group_order, rtn, rtt = load_rootgroupmember()  # root to name, root to table
    rtdt, default_ranges, default_units = load_displayparams()  # root to display type
    snr = load_a_groupmember()  # [sex][name] -> range; male and famle normal ranges from old a_groupmember
    numeric_bp = ['Diastolic BP', 'Systolic BP', 'Pulmonary artery diastolic', 'Pulmonary artery systolic']
    vent_names = ['Tube Status', 'Vent Status', 'MODE', 'Trial extubation']  # names pulled from a_vent

    # this function replaces missing ranges with default values
    # and will use default abs values if they are more extreme
    def determine_ranges(l_abs_ranges, l_norm_ranges, l_default_ranges):
        if l_abs_ranges[0] is None or l_abs_ranges[0] > l_default_ranges[0]:  # if min is > absolute min
            l_abs_ranges[0] = l_default_ranges[0]
        if l_abs_ranges[1] is None or l_abs_ranges[1] < l_default_ranges[3]:  # if max is < absolute max
            l_abs_ranges[1] = l_default_ranges[3]
        if l_norm_ranges[0] is None:
            l_norm_ranges[0] = l_default_ranges[1]
        if l_norm_ranges[1] is None:
            l_norm_ranges[1] = l_default_ranges[2]
        return l_abs_ranges, l_norm_ranges

    def process_data_into_series(x_, y_, p_norm_ranges, d_x, d_y):
        event_values = []
        numeric = {"name": "numeric_values", "zones": [], "data": [], "marker": {"symbol": "circle"}}
        discrete = {"name": "discrete_values", "color": "#000000", "data": [], "marker": {"symbol": "square"}}
        if p_norm_ranges[0] is not None and p_norm_ranges[1] is not None:  # high values red & low values blue
            numeric["zones"].append({"value": p_norm_ranges[0], "color": "#00CCFF"})  # blue
            numeric["zones"].append({"value": p_norm_ranges[1], "color": "#33CC33"})  # green
            numeric["zones"].append({"color": "#BF0B23"})  # red
        elif p_norm_ranges[0] is None and p_norm_ranges[1] is not None:  # high values red & rest green
            numeric["zones"].append({"value": p_norm_ranges[1], "color": "#33CC33"})  # green
            numeric["zones"].append({"color": "#BF0B23"})  # red
        elif p_norm_ranges[0] is not None and p_norm_ranges[1] is None:  # low values blue & rest green
            numeric["zones"].append({"value": p_norm_ranges[0], "color": "#00CCFF"})  # blue
            numeric["zones"].append({"color": "#33CC33"})  # green
        else:  # all values black
            numeric["zones"].append({"color": "#000000"})  # black

        for i in range(len(curr_data['datetime'])):
            numeric['data'].append([x_[i], y_[i]])
        for i in range(len(d_x)):
            if d_y[i] not in event_values:
                event_values.append(d_y[i])
            discrete['data'].append([d_x[i], event_values.index(d_y[i])])
        return [[numeric, discrete], event_values]

    # Demographics #
    demographics_dict, sex = load_demographics(case_id)
    # time min/max #
    global_time, time_cut = load_admit_discharge(case_id, time_cut)
    # load and process lab data #
    for lab_group in lab_group_order:
        for curr_root in groups[lab_group]:
            curr_data, curr_recent_result, abs_ranges, norm_ranges, discrete_data = \
                load_mars_labs(case_id, curr_root, rtm[curr_root], time_cut)
            if not curr_data and not discrete_data:
                continue
            abs_ranges, norm_ranges = determine_ranges(abs_ranges, norm_ranges, default_ranges[curr_root])
            series, discrete_text = process_data_into_series(curr_data['datetime'], curr_data['value'],
                                                             norm_ranges, discrete_data[0], discrete_data[1])
            lab_dict[curr_root] = json.dumps([series, curr_data['text'], abs_ranges, norm_ranges, curr_recent_result[0],
                                              curr_recent_result[1], discrete_text])

    # Vitals #
    for curr_root in groups['Vitals']:
        rollname = rtn[curr_root]
        curr_data, curr_recent_result, abs_ranges = load_clinical_event(case_id, rollname, time_cut)
        if abs_ranges[0] is None or abs_ranges[0] > default_ranges[curr_root][0]:  # if min is > absolute min
            abs_ranges[0] = default_ranges[curr_root][0]
        if abs_ranges[1] is None or abs_ranges[1] < default_ranges[curr_root][3]:  # if max is < absolute max
            abs_ranges[1] = default_ranges[curr_root][3]
        norm_ranges = snr[sex][rollname]
        series, discrete_text = process_data_into_series(curr_data['datetime'], curr_data['value'], norm_ranges, [], [])
        vitals_dict[curr_root] = json.dumps([series, curr_data['text'], abs_ranges, norm_ranges,
                                             round(curr_recent_result[0], 1), curr_recent_result[1], discrete_text])

    # Blood Pressure #
    curr_data, curr_recent_result, abs_ranges = load_bp(case_id, time_cut, numeric_bp)
    vitals_dict['VTDIAV'] = json.dumps([curr_data[0], [], abs_ranges[0], curr_recent_result[0]])
    vitals_dict['VTDIAA'] = json.dumps([curr_data[1], [], abs_ranges[1], curr_recent_result[1]])
    vitals_dict.pop('VTSYSA', None)
    vitals_dict.pop('VTSYSV', None)

    # Ventilator #  !!! Needs to be discrete !!!
    for curr_root in groups['Ventilator']:
        if rtt[curr_root] == 'lab_739':
            curr_data, curr_recent_result, abs_ranges, norm_ranges, discrete_data = \
                load_mars_labs(case_id, curr_root, rtm[curr_root], time_cut)
            if not curr_data and not discrete_data:
                continue
        elif rtt[curr_root] == 'a_clinicalevents':
            curr_data, curr_recent_result, abs_ranges = load_clinical_event(case_id, rtn[curr_root], time_cut)
            abs_ranges = [40, 60]
            norm_ranges = [None, None]
            discrete_data = [[], []]
        else:  # a_ventilator table. captured below with load_vent()
            continue
        series, discrete_text = process_data_into_series(curr_data['datetime'], curr_data['value'],
                                                         norm_ranges, discrete_data[0], discrete_data[1])
        vitals_dict[curr_root] = json.dumps([series, curr_data['text'], abs_ranges, norm_ranges,
                                             round(curr_recent_result[0], 1), curr_recent_result[1], discrete_text])

    four_series, four_discrete_text, four_recent_result = load_vent(case_id, time_cut, vent_names)
    vitals_dict['VSTUBE'] = json.dumps([four_series[0], [], [0, len(four_discrete_text[0])], [None, None],
                                        four_recent_result[0], None, four_discrete_text[0]])
    vitals_dict['VSVENT'] = json.dumps([four_series[1], [], [0, len(four_discrete_text[1])], [None, None],
                                        four_recent_result[1], None, four_discrete_text[1]])
    vitals_dict['MODE'] = json.dumps([four_series[2], [], [0, len(four_discrete_text[2])], [None, None],
                                      four_recent_result[2], None, four_discrete_text[2]])
    vitals_dict['VSTRIA'] = json.dumps([four_series[3], [], [0, len(four_discrete_text[3])], [None, None],
                                        four_recent_result[3], None, four_discrete_text[3]])
    
    # IO #
    curr_data, abs_ranges = load_io(case_id, time_cut)
    vitals_dict['IO'] = [curr_data, [], abs_ranges]

    # Meds (including home) #
    curr_data, display_med_names, med_routes, routes_mapping, id_mapping = load_meds(case_id, time_cut)
    json_meds_dict = curr_data  # data is loaded differently
    
    # Surgical #
    procedure_dict = load_procedures(case_id, time_cut)  # there are no procedures available for the normal test case
    
    # Micro Report #
    micro_report_dict = load_micro_reports(case_id, time_cut)

    note_types = ['OP', 'RAD', 'EKG', 'PGN', 'HP']
    rare_types = ['EMG', 'ER', 'LETT', 'PULM', 'CATH', 'NUCLEAR', 'CARD', 'MDX', 'EEG', 'PVL', 'CMORE', 'SP', 'ECHO']
    out_dir = local_dir + 'evaluation_study/' + out_folder

    if save_notes:  # save notes
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for note_type in note_types:
            curr_data = load_local_report(case_id, time_cut-18000000, note_type, global_time['min_t'], False)
            pickle.dump(curr_data, open(out_dir + note_type + '.p', 'wb'))
    
        curr_data = []
        for note_type in rare_types:
            curr_data += load_local_report(case_id, time_cut - 18000000, note_type, global_time['min_t'], True)
        pickle.dump(curr_data, open(out_dir + 'other_notes.p', 'wb'))
    
    if save_labs:  # save labs
        out_dir = local_dir + 'evaluation_study/' + out_folder
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        pickle.dump(demographics_dict, open(out_dir + 'demographics.p', 'wb'))
        pickle.dump(lab_dict, open(out_dir + 'labs.p', 'wb'))
        pickle.dump(vitals_dict, open(out_dir + 'vitals.p', 'wb'))
        pickle.dump(global_time, open(out_dir + 'global_time.p', 'wb'))
        pickle.dump(recent_results, open(out_dir + 'recent_results.p', 'wb'))
        pickle.dump(json_meds_dict, open(out_dir + 'case_test_meds.p', 'wb'))
        pickle.dump(display_med_names, open(out_dir + 'display_med_names.p', 'wb'))
        pickle.dump(med_routes, open(out_dir + 'med_routes.p', 'wb'))
        pickle.dump(routes_mapping, open(out_dir + 'routes_mapping.p', 'wb'))
        pickle.dump(procedure_dict, open(out_dir + 'procedures.p', 'wb'))
        pickle.dump(micro_report_dict, open(out_dir + 'micro_report.p', 'wb'))
        # save med id mapping
        with open(out_dir + 'med-display-id_to_name.txt', 'w') as out_file:
            for key in id_mapping:
                out_file.write(str(key) + '\t' + id_mapping[key] + '\t' + display_med_names[key] + '\n')

    return


def load_global_parameters():
    groups, lab_group_order, rtn, rtt = load_rootgroupmember()  # root to name, root to table
    rtdt, default_ranges, default_units = load_displayparams()  # root to display type

    if 1:
        pickle.dump(lab_group_order, open(local_dir + 'evaluation_study/tests/group_order_labs.p', 'wb'))
        pickle.dump(groups, open(local_dir + 'evaluation_study/tests/group_membership.p', 'wb'))
        pickle.dump(rtdt, open(local_dir + 'evaluation_study/tests/global_params.p', 'wb'))
        pickle.dump(rtn, open(local_dir + 'evaluation_study/tests/display_names.p', 'wb'))

    return


def determine_case_times():
    """
    This function was used to determine cuttimes for each cases. Should be one time use code.
    """
    if True:
        import datetime
        from random import randint

        def process_visit_id(case_id):
            results = a_ICUpatients.objects.using('remote').filter(patientvisitid=case_id)
            t_icu_admit = 0
            t_icu_discharge = 0
            first = True
            for result in results:
                if first:
                    t_icu_admit = (time.mktime(result.ICUadmit.timetuple()) - 18000)  # * 1000
                    t_icu_discharge = (time.mktime(result.ICUdischarge.timetuple()) - 18000)  # * 1000
                    first = False
                else:
                    t_icu_admit = min(t_icu_admit, (time.mktime(result.ICUadmit.timetuple()) - 18000))
                    t_icu_discharge = max(t_icu_discharge, (time.mktime(result.ICUdischarge.timetuple()) - 18000))
                    ####################
                    # it is possible that some of the cut times occur in between ICU admissions.
                    ######################
            day_diffence = (t_icu_discharge - t_icu_admit) // 86400
            if day_diffence == 2:
                cut2 = randint(1, day_diffence)
                print('****** day_difference = 2 here at case: ' + str(case_id))
            elif day_diffence == 3:
                print('****** day_difference = 3 here at case: ' + str(case_id))
                cut2 = randint(2, day_diffence)
            else:
                cut2 = randint(3, day_diffence)
            cut1 = cut2-1
            cuttime1 = (((t_icu_admit + (86400*cut1)) // 86400) * 86400)  # * to right day, floor num days
            cuttime2 = (((t_icu_admit + (86400*cut2)) // 86400) * 86400)  # * to day seconds, * to js

            return str(cuttime1), str(cuttime2), str(cut1), str(cut2)

        def find_condition(case_id):
            results = a_ICDCPT.objects.using('remote').filter(patientvisitid=case_id)
            for result in results:
                if float(result.IcdCpt) == 518.81:
                    return ['ARF']
                elif float(result.IcdCpt) in [584.9, 584.5]:
                    return ['AKF']
            return ['unmatched']

        files = ['selections-27AKF', '27ARF']
        for curr_file in files:
            print('current file is ' + curr_file)
            with open('$$$$$ENTER PATH FOR CASE ID FILE$$$$$'+curr_file+'.txt', 'r+') as in_file:
                lines = in_file.readlines()
            out_file = open(local_dir + 'evaluation_study/'+curr_file+'.txt', 'w+')
            for line in lines:
                curr_id = int(line.rstrip())
                out_line = [str(curr_id)]
                out_line += process_visit_id(curr_id)
                out_line += find_condition(curr_id)
                out_file.write(','.join(out_line))
                out_file.write('\n')
            out_file.close()
    return


def update_cases():
    print('^^^^^^^^^^^^^^^^^^^in update_cases()^^^^^^^^^^^^^^^^^^^^^^^')

    def determine_cases(curr_dir, skip_count):
        in_file = open(curr_dir, 'r')
        lines = in_file.readlines()
        in_file.close()
        u_cases = []
        u_cut_times = []
        for q in range(len(lines)):
            if lines[q][0] == '#':
                continue
            split_line = lines[q].split(',')
            if len(split_line) > 1:
                u_cases.append(int(split_line[0]))
                u_cut_times.append([float(split_line[1])*1000, float(split_line[2])*1000])

        return u_cases[skip_count:], u_cut_times[skip_count:]

    global run_queries
    # '''
    curr_files = ['27AKF', '27ARF']
    # curr_files = ['first_four', 'B9', 'F3', 'G9', 'K3', 'K8', 'L8', 'M8', 'P8', 'S8', 'T2', 'P23', 'S23']
    # curr_files = ['B9', 'F3', 'G9', 'K3', 'K8', 'L8', 'M8', 'P8', 'S8', 'T2', 'P23', 'S23']
    # curr_files = []

    for curr_file in curr_files:
        print('====== ' + curr_file + ' ======')
        if curr_file == 'first_four':
            cases, cut_times = determine_cases(local_dir+'/evaluation_study/participant_info/'+curr_file+'.txt', 0)
        else:
            cases, cut_times = determine_cases(local_dir+'/evaluation_study/participant_info/' + curr_file + '.txt', 0)
        for i in range(len(cases)):
            print('currently on number ' + str(i))
            run_queries = True
            load_case_date(cases[i], 'cases_t1/' + str(cases[i]) + '/', int(cut_times[i][0]+28800000))
            # ^added 28800000 for eight am
            run_queries = False
            load_case_date(cases[i], 'cases_t2/' + str(cases[i]) + '/', int(cut_times[i][1]+28800000))
            load_case_date(cases[i], 'cases_all/' + str(cases[i]) + '/')

    load_global_parameters()
    determine_case_times()  # run once

    return
