"""
Custom template tags and filters used by the SEMR interface.

These helpers format domain objects and case metadata for presentation in
templates. They aim to be side-effect free and defensive when possible, so
templates can degrade gracefully when certain fields are missing.
"""

from django import template
import html

register = template.Library()


@register.filter(name='get_json_arr')
def get_json_arr(lab_info, lab):
    """Return the JSON array for a given lab key from `lab_info`."""
    return lab_info[lab]

@register.filter(name='get_fixed_name')
def get_fixed_name(lab_names, lab):
    """Return an escaped, trimmed display name for a lab."""
    return html.escape(lab_names[lab][0].rstrip())


@register.filter(name='get_fixed_name2')
def get_fixed_name2(lab_names, lab):
    """Return a composite label for a lab (primary - secondary)."""
    return lab_names[lab][0] + ' - ' +lab_names[lab][1]


@register.filter(name='get_labnames')
def get_group_members(group_info, group_name):
     """Return the lab names for a group identifier."""
     return group_info[group_name]


@register.filter(name='shorten_name')
def shorten_name(group_name):
    """Return a shortened group name by dropping the suffix 'istry'."""
    return group_name.replace('istry', '')


@register.filter(name="get_recent_value")
def get_recent_value(recent, lab):
    """Return the recent value for `lab` or "Never" if not present."""
    if lab in recent.keys():
        return recent[lab]
    else:
        return "Never"

@register.simple_tag
def note_count(arg_dict, arg_key):
    """Return the count of items for `arg_key` inside `arg_dict`."""
    if arg_key in arg_dict:
        count = len(arg_dict[arg_key])
    else:
        count = 0
    return count


@register.filter(name="next_lab")
def next_lab(value, arg):
    """Return the element following index `arg` in `value`, or None."""
    try:
        next_index = int(arg) + 1
        return value[next_index]
    except (ValueError, TypeError, IndexError):
        return None


@register.filter(name="date_only")
def date_only(full_date):
    """Return the YYYY-MM-DD portion of an ISO-like date string."""
    try:
        return full_date[0:10]
    except (TypeError, IndexError):
        return full_date


@register.filter(name="full_gender")
def full_gender(gender_char):
    """Map gender character codes to full text labels."""
    if gender_char == 'F':
        return 'female'
    elif gender_char == 'M':
        return 'male'
    else:
        return ''


@register.filter(name='get_meds')
def get_meds(route_mapping, route):
    """Return the list of medication strings for a given `route`."""
    return [str(x) for x in route_mapping[route]]


@register.simple_tag
def date_line(case_detials, time_step=0):
    """Return a human-readable timeline string for the current case window.

    Uses timestamps (milliseconds) under `min_t` and `max_t` placed in the
    case details to render admission date, current date, and ICU day.
    """
    import datetime
    admit = datetime.datetime.fromtimestamp(case_detials[time_step]["min_t"]/1000.0)
    current = datetime.datetime.fromtimestamp(case_detials[time_step]["max_t"]/1000.0)
    delta =  current - admit
    return 'Admitted to the ICU on: ' + admit.strftime("%m/%d") + ' | Current date: ' + current.strftime("%m/%d") + ' | Current ICU day: ' + str(delta.days+1)


'''
# this tag is used #
@ register.filter(name='date_line')
def date_line(case_detials, time_step=0):
    import datetime
    admit = datetime.datetime.fromtimestamp(case_detials[time_step]["min_t"]/1000.0)
    current = datetime.datetime.fromtimestamp(case_detials[time_step]["max_t"]/1000.0)
    delta =  current - admit
    return 'Admitted to the ICU on: ' + admit.strftime("%m/%d") + ' | Current date: ' + current.strftime("%m/%d") + ' | Current ICU day: ' + str(delta.days+1)
'''

# this tag is used #
@register.filter
def keyvalue(mapping, key):    
    """Return `mapping[key]` for convenient key access in templates."""
    return mapping[key]




@register.filter(name='short_id')
def short_id(long_id):
    """Return the last three characters of an identifier."""
    return str(long_id)[-3:]