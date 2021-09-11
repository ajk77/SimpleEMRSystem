"""
SEMRinterface/urls.py
version 3.0
package github.com/ajk77/SimpleEMRProject
Modified by AndrewJKing.com|@andrewsjourney

This file contails the application's url patterns. 

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
    url(r'^$', views.select_study, name='select_study'),
    url(r'^casereset/$', views.case_reset, name='case_reset'),
    url(r'^markcomplete/$', views.mark_complete, name='mark_complete'),
    url(r'^markcompleteurl/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.mark_complete_url, name='mark_complete_url'),
    url(r'^selected_items/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.save_selected_items, name='selected_items'),
    url(r'^(?P<study_id>\w+)/$', views.select_user, name='select_user'),
    url(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/$', views.select_case, name='select_case'),
    url(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.case_viewer, name='case_viewer'),
    url(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/(?P<time_step>\d)/$', views.case_viewer, name='case_viewer')

    ]
# The .* catches all the special cases for lab names

''',
url(r'^(?P<patient_id>\d+)/$', views.detail, name='detail'),
url(r'^home/(?P<user_id>\w+)/$', views.index, name='index'),
url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/$', views.detail, name='detail'),
url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/(?P<time_cutoff>\d+)/$', views.detail, name='detail'),
url(r'^(?P<patient_id>\d+)/(?P<user_id>\w+)/(?P<time_cutoff>\d+)/(?P<previous_patient_id>\d+)/$',views.detail, name='detail'),
url(r'^save_input/$', views.save_input, name='save_input'),
url(r'^end/(?P<user_id>\w+)/1/$', views.end_of_study, name='end_of_study'),
url(r'^load_cases/$', views.loadcasedata, name='load_cases'),
url(r'^case_reset/$', views.case_reset, name='case_reset'),
url(r'^SyntheaViewer$', views.index_synthea, name='index_synthea'),
url(r'^SyntheaViewer/(?P<encounter_id>[a-zA-Z0-9\-]+)$', views.detail_synthea, name='detail_synthea')
'''
