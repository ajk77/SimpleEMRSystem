from django import template
import html
import json

register = template.Library()


@register.filter(name='get_json_arr')
def get_json_arr(lab_info, lab):
    return lab_info[lab]

@register.filter(name='get_fixed_name')
def get_fixed_name(lab_names, lab):
    return html.escape(lab_names[lab][0].rstrip())


@register.filter(name='get_fixed_name2')
def get_fixed_name2(lab_names, lab):
    return lab_names[lab][0] + ' - ' +lab_names[lab][1]


@register.filter(name='get_labnames')
def get_group_members(group_info, group_name):
     return group_info[group_name]


@register.filter(name='shorten_name')
def shorten_name(group_name):
    return group_name.replace('istry', '')


@register.filter(name="get_recent_value")
def get_recent_value(recent, lab):
    if lab in recent.keys():
        return recent[lab]
    else:
        return "Never"


@register.filter(name="next_lab")
def next_lab(value, arg):
    try:
        return value[int(arg)+1]
    except:
        return None


@register.filter(name="date_only")
def date_only(full_date):
    try:
        return full_date[0:10]
    except:
        return full_date


@register.filter(name="full_gender")
def full_gender(gender_char):
    if gender_char == 'F':
        return 'female'
    elif gender_char == 'M':
        return 'male'
    else:
        return ''


@register.filter(name='get_meds')
def get_meds(route_mapping, route):
    return [str(x) for x in route_mapping[route]]


# this tag is used #
@ register.filter(name='date_line')
def date_line(case_detials, time_step=0):
    import datetime
    admit = datetime.datetime.fromtimestamp(case_detials[time_step]["min_t"]/1000.0)
    current = datetime.datetime.fromtimestamp(case_detials[time_step]["max_t"]/1000.0)
    delta =  current - admit
    return 'Admitted to the ICU on: ' + admit.strftime("%m/%d") + ' | Current date: ' + current.strftime("%m/%d") + ' | Current ICU day: ' + str(delta.days+1)

# this tag is used #
@register.filter
def keyvalue(dict, key):    
    return dict[key]




@ register.filter(name='short_id')
def short_id(long_id):
    return str(long_id)[-3:]