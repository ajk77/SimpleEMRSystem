#!/usr/bin/env python
"""
Test script for registration functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SEMRproject.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from django.urls import reverse
from SEMRinterface.models import Study

def test_registration_page():
    """Test that the registration page loads correctly"""
    client = Client()

    # Test GET request
    response = client.get(reverse('register'))
    print(f"Registration page status: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode()
        checks = [
            ('Create New Account', 'Page title'),
            ('study_id', 'Study selection field'),
            ('user_id', 'User ID field'),
            ('password', 'Password field'),
            ('confirm_password', 'Confirm password field'),
            ('Create Account', 'Submit button'),
        ]

        for check_text, description in checks:
            found = check_text in content
            print(f"✓ {description}: {'Found' if found else 'NOT FOUND'}")

        return True
    else:
        print("✗ Registration page failed to load")
        return False

def test_registration_submission():
    """Test user registration submission"""
    client = Client()

    # Get a study for testing
    try:
        study = Study.objects.first()
        if not study:
            print("✗ No studies found in database")
            return False
    except Exception as e:
        print(f"✗ Error getting study: {e}")
        return False

    # Test POST request with valid data
    data = {
        'user_id': 'testreguser',
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
        'study_id': study.study_id,
    }

    response = client.post(reverse('register'), data)
    print(f"Registration submission status: {response.status_code}")

    # Should redirect to login on success
    if response.status_code == 302 and 'login' in response['Location']:
        print("✓ Registration successful - redirected to login")
        return True
    else:
        print("✗ Registration failed")
        print("Response content:", response.content.decode()[:500])
        return False

if __name__ == '__main__':
    print("Testing registration functionality...")
    print("=" * 50)

    page_ok = test_registration_page()
    print()

    if page_ok:
        submission_ok = test_registration_submission()
        print()

        if submission_ok:
            print("🎉 All registration tests passed!")
        else:
            print("❌ Registration submission test failed")
    else:
        print("❌ Registration page test failed")