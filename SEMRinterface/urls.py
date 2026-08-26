"""
SEMRinterface/urls.py
package github.com/ajk77/SimpleEMRProject

This file contails the application's url patterns.

Research-stable path routes from a2c35bf are the default study/user/case flow.
2024.2 routes (login, welcome, select, case_viewer_new, health) remain mounted
but unused by the research viewer. Specific paths are listed before the
catch-all study_id routes.
"""
from django.urls import path, re_path
from . import views, auth_views, health_check

urlpatterns = [
    # 2024.2 routes kept unused (must be before catch-all study_id)
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('change-password/', auth_views.change_password_view, name='change_password'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('select/', views.unified_selection_view, name='unified_selection'),
    path('case_viewer/', views.case_viewer_new, name='case_viewer_new'),
    path('api/get_case_data/', views.get_case_data, name='get_case_data'),
    path('health/', health_check.health_check, name='health_check'),
    path('api/health/', health_check.health_check, name='api_health'),
    path('api/info/', health_check.system_info, name='system_info'),
    path('api/quickstart/', health_check.quick_start, name='quick_start'),

    # Research-stable routes (a2c35bf)
    re_path(r'^$', views.select_study, name='select_study'),
    re_path(r'^casereset/$', views.case_reset, name='case_reset'),
    re_path(r'^markcomplete/$', views.mark_complete, name='mark_complete'),
    re_path(r'^markcompleteurl/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.mark_complete_url, name='mark_complete_url'),
    re_path(r'^selected_items/(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.save_selected_items, name='selected_items'),
    re_path(r'^(?P<study_id>\w+)/$', views.select_user, name='select_user'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/$', views.select_case, name='select_case'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/$', views.case_viewer, name='case_viewer'),
    re_path(r'^(?P<study_id>\w+)/(?P<user_id>\w+)/(?P<case_id>[a-zA-Z0-9_\-]+)/(?P<time_step>\d)/$', views.case_viewer, name='case_viewer'),
]
