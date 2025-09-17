#!/usr/bin/env python3
"""
Simple EMR System Setup Wizard
Interactive setup for first-time users
"""

import os
import sys
import json
import secrets
import subprocess
from pathlib import Path
from django.core.management import execute_from_command_line

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(50)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def create_config():
    """Create configuration file"""
    config = {
        'SECRET_KEY': generate_secret_key(),
        'DEBUG': True,
        'ALLOWED_HOSTS': ['localhost', '127.0.0.1', '0.0.0.0'],
        'TIME_ZONE': 'America/Chicago',
        'LANGUAGE_CODE': 'en-us',
        'DATABASE': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3'
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✓ Configuration file created")
    return config

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def setup_database():
    """Set up the database"""
    print("Setting up database...")
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SEMRproject.settings')
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Database setup complete")
        return True
    except Exception as e:
        print(f"ERROR: Failed to setup database: {e}")
        return False

def create_resources_directory():
    """Create resources directory if it doesn't exist"""
    resources_dir = Path('resources')
    if not resources_dir.exists():
        resources_dir.mkdir()
        print("✓ Resources directory created")
    else:
        print("✓ Resources directory already exists")

def create_sample_data():
    """Create sample data for testing"""
    sample_study_dir = Path('resources/sample_study')
    if not sample_study_dir.exists():
        sample_study_dir.mkdir(parents=True)
        
        # Create sample study files
        sample_files = {
            'user_details.json': {
                'user1': {
                    'name': 'Test User 1',
                    'cases_assigned': ['case1', 'case2'],
                    'cases_completed': []
                },
                'user2': {
                    'name': 'Test User 2',
                    'cases_assigned': ['case3'],
                    'cases_completed': ['case1']
                }
            },
            'case_details.json': {
                'case1': {
                    'patient_id': 'P001',
                    'age': 45,
                    'gender': 'M',
                    'diagnosis': 'Sample Case 1'
                },
                'case2': {
                    'patient_id': 'P002',
                    'age': 32,
                    'gender': 'F',
                    'diagnosis': 'Sample Case 2'
                },
                'case3': {
                    'patient_id': 'P003',
                    'age': 67,
                    'gender': 'M',
                    'diagnosis': 'Sample Case 3'
                }
            },
            'data_layout.json': {
                'groups': ['Vitals', 'Labs', 'Medications'],
                'display_order': ['Vitals', 'Labs', 'Medications']
            },
            'med_details.json': {
                'medication1': {
                    'name': 'Sample Medication 1',
                    'dosage': '10mg',
                    'route': 'oral'
                }
            },
            'variable_details.json': {
                'vital1': {
                    'name': 'Blood Pressure',
                    'unit': 'mmHg',
                    'normal_range': '120/80'
                }
            }
        }
        
        for filename, data in sample_files.items():
            with open(sample_study_dir / filename, 'w') as f:
                json.dump(data, f, indent=2)
        
        print("✓ Sample data created")
    else:
        print("✓ Sample data already exists")

def create_superuser():
    """Create a superuser account"""
    print("\nWould you like to create an admin user? (y/n): ", end='')
    create_admin = input().lower().strip()
    
    if create_admin in ['y', 'yes']:
        try:
            execute_from_command_line(['manage.py', 'createsuperuser'])
            print("✓ Admin user created")
        except Exception as e:
            print(f"ERROR: Failed to create admin user: {e}")
    else:
        print("Skipping admin user creation")

def update_settings():
    """Update Django settings to use configuration"""
    settings_file = Path('SEMRproject/settings.py')
    if settings_file.exists():
        # Read current settings
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Update SECRET_KEY if it's still the default
        if '$$$$$ENTER SECRET KEY$$$$$' in content:
            config = json.load(open('config.json'))
            content = content.replace(
                "SECRET_KEY = '$$$$$ENTER SECRET KEY$$$$$'",
                f"SECRET_KEY = '{config['SECRET_KEY']}'"
            )
            
            with open(settings_file, 'w') as f:
                f.write(content)
            
            print("✓ Settings updated with secure secret key")

def main():
    print("Simple EMR System Setup Wizard")
    print("=" * 40)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create configuration
    print("Creating configuration...")
    create_config()
    
    # Update settings
    update_settings()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Set up database
    if not setup_database():
        sys.exit(1)
    
    # Create resources directory
    create_resources_directory()
    
    # Create sample data
    create_sample_data()
    
    # Create superuser
    create_superuser()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("=" * 40)
    print()
    print("To start the Simple EMR System:")
    print("  python manage.py runserver")
    print()
    print("Then open your browser to: http://127.0.0.1:8000")
    print()
    print("For help, see the documentation in the 'docs' folder")
    print()

if __name__ == "__main__":
    main()
