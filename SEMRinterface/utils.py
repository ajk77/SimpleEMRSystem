"""
SEMRinterface/utils.py
version 3.0
package github.com/ajk77/SimpleEMRProject
Created by AndrewJKing.com|@andrewsjourney

This file contails utility functions.

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
import os
import time


def get_list_study_id(dir_resources):
    list_study_id = []
    for root, dirs, files in os.walk(dir_resources, topdown=True):
        for d in dirs:
            if '_study' in d:
                list_study_id.append(d)
        break  # only care about top level directory
    return list_study_id
    
