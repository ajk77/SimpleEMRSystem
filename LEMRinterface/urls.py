"""
LEMRinterface/urls.py
version 2.0
package github.com/ajk77/LEMRinterface
Modified by AndrewJKing.com|@andrewsjourney

This file contails the application's url patterns. 

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
from django.conf.urls import url
from . import views

# nothing is for home screen
# \NUM\ is a patient id in demo mode
# \NUM\NUM\ is patient id and user id (used during labeling study)
# \NUM\NUM\\NUM\ is patient id, user id, and previous patient id (used during labeling study)
# \retrain\ will be used later when model building
# \save_pixelmap\ saves current screen layout
# \save_input\ saves elemnt selections and linkert scale data
# \eye_test\NUM\NUM\ is user_id and next patient Id. (always initiated from home screen)
# end \NUM\NUM\ is user_id and previous patient id. It closes study
# \load_cases\ is used to load the cases.

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<patient_id>\d+)/$', views.detail, name='detail'),
    url(r'^home/(?P<user_id>\w+)/$', views.index, name='index'),
    url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/$', views.detail, name='detail'),
    url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/(?P<time_cutoff>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/(?P<time_cutoff>\d+)/(?P<previous_patient_id>\d+)/$',
        views.detail, name='detail'),
    url(r'^save_input/$', views.save_input, name='save_input'),
    url(r'^end/(?P<user_id>\w+)/1/$', views.end_of_study, name='end_of_study'),
    url(r'^load_cases/$', views.loadcasedata, name='load_cases'),
    url(r'^case_reset/$', views.case_reset, name='case_reset')
    ]
# The .* catches all the special cases for lab names
