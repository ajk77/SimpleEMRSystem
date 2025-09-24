"""
Authentication views for the Simple EMR System.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext as _

from .services import get_study_ids, get_user_details


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('welcome')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        study_id = request.POST.get('study_id')

        if not all([username, password, study_id]):
            messages.error(request, _('Please fill in all fields.'))
            return redirect('login')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user belongs to the selected study
            if user.study and user.study.study_id == study_id:
                login(request, user)
                messages.success(request, _('Welcome back, %(name)s!') % {'name': user.get_full_name()})

                # Update last accessed time
                from django.utils import timezone
                user.last_accessed = timezone.now()
                user.save(update_fields=['last_accessed'])

                return redirect('unified_selection')
            else:
                messages.error(request, _('You do not have access to the selected study.'))
        else:
            messages.error(request, _('Invalid username or password.'))

    # GET request - show login form
    studies = get_study_ids()
    return render(request, 'SEMRinterface/login.html', {
        'studies': studies
    })


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('login')


@login_required
def profile_view(request):
    """Show user profile and study information."""
    context = {
        'user': request.user,
    }
    return render(request, 'SEMRinterface/profile.html', context)


@require_http_methods(["POST"])
@csrf_protect
@login_required
def change_password_view(request):
    """Handle password change for authenticated users."""
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')

    if not all([current_password, new_password, confirm_password]):
        return JsonResponse({
            'status': 'error',
            'message': _('Please fill in all fields.')
        }, status=400)

    if new_password != confirm_password:
        return JsonResponse({
            'status': 'error',
            'message': _('New passwords do not match.')
        }, status=400)

    if len(new_password) < 8:
        return JsonResponse({
            'status': 'error',
            'message': _('Password must be at least 8 characters long.')
        }, status=400)

    # Verify current password
    if not request.user.check_password(current_password):
        return JsonResponse({
            'status': 'error',
            'message': _('Current password is incorrect.')
        }, status=400)

    # Change password
    request.user.set_password(new_password)
    request.user.save()

    return JsonResponse({
        'status': 'success',
        'message': _('Password changed successfully.')
    })


@login_required
def study_selection_view(request):
    """Show available studies for the logged-in user."""
    # For now, show all studies. In a real implementation,
    # you might filter based on user permissions
    studies = get_study_ids()
    return render(request, 'SEMRinterface/study_selection.html', {
        'studies': studies
    })