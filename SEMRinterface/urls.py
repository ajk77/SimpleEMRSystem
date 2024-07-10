"""
SEMRinterface/urls.py
package github.com/ajk77/SimpleEMRProject

This file contails the application's url patterns. 

"""
from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.select_study, name='select_study'),
    re_path(r'^casereset/$', views.case_reset, name='case_reset'),
    re_path(r'^markcomplete/$', views.mark_complete, name='mark_complete'),
    re_path(r'^markcompleteurl/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.mark_complete_url, name='mark_complete_url'),
    re_path(r'^selected_items/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.save_selected_items, name='selected_items'),
    re_path(r'^(?P<study_id>\w+)/$', views.select_user, name='select_user'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/$', views.select_case, name='select_case'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.case_viewer, name='case_viewer'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/(?P<time_step>\d)/$', views.case_viewer, name='case_viewer')

    ]
# The .* catches all the special cases for lab names

