"""
SEMRinterface/utils.py
package github.com/ajk77/SimpleEMRProject

This file contails utility functions.

"""
import os


def get_list_study_id(dir_resources):
    list_study_id = []
    for root, dirs, files in os.walk(dir_resources, topdown=True):
        for d in dirs:
            if '_study' in d:
                list_study_id.append(d)
        break  # only care about top level directory
    return list_study_id


def get_study_ids(dir_resources=None):
    """List *_study folders on disk when the SQLite study table is empty."""
    if dir_resources is None:
        dir_resources = os.path.join(os.getcwd(), "resources")
    return get_list_study_id(dir_resources)
