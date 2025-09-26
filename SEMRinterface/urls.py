"""
SEMRinterface/urls.py
package github.com/ajk77/SimpleEMRProject

This file contails the application's url patterns.

"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, auth_views, health_check

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    path('change-password/', auth_views.change_password_view, name='change_password'),

    # Main application URLs
    path('', views.welcome_view, name='welcome'),
    path('select/', views.unified_selection_view, name='unified_selection'),
    path('case_viewer/', views.case_viewer, name='case_viewer'),
    path('api/get_case_data/', views.get_case_data, name='get_case_data'),

    # Health monitoring
    path('health/', health_check.health_check, name='health_check'),
    path('api/health/', health_check.health_check, name='api_health'),
    path('api/info/', health_check.system_info, name='system_info'),
    path('api/quickstart/', health_check.quick_start, name='quick_start'),
]
