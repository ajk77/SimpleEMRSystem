"""
SEMRinterface/urls.py
package github.com/ajk77/SimpleEMRProject

This file contails the application's url patterns. 

"""
from django.urls import path
from . import views
from . import health_check

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('select/', views.unified_selection_view, name='unified_selection'),
    path('case_viewer/', views.case_viewer, name='case_viewer'),
    path('api/get_case_data/', views.get_case_data, name='get_case_data'),
    path('health/', health_check.health_check, name='health_check'),
    path('api/health/', health_check.health_check, name='api_health'),
    path('api/info/', health_check.system_info, name='system_info'),
    path('api/quickstart/', health_check.quick_start, name='quick_start'),
]
