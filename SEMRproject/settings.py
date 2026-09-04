"""
SEMRproject/settings.py
version 2024.1
package github.com/ajk77/SimpleEMRSystem
Modified by AndrewJKing.com|@andrewsjourney

Settings file for SEMR deployment. To use:
update DATABASES{} to reflect your database
set DJANGO_SECRET_KEY (or SECRET_KEY) in the environment for non-DEBUG runs

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

# Django settings for Simple EMR System project.

import os
import json

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load private configuaration file. (only needed if connecting to a database)
# ^ if using, you must undate the DATABASES content below. 
# config = json.loads(json.load(open("SEMRproject/config.json", 'r')))

# Default True for local single-user runserver lab use.
DEBUG = os.environ.get('DJANGO_DEBUG', '1').lower() in ('1', 'true', 'yes')

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Custom user model
AUTH_USER_MODEL = 'SEMRinterface.User'

# Research-stable default: no login. Set SEMR_REQUIRE_LOGIN=1 to enable Django auth.
SEMR_REQUIRE_LOGIN = os.environ.get('SEMR_REQUIRE_LOGIN', '0').lower() in ('1', 'true', 'yes')
LOGIN_URL = '/SEMRinterface/login/'

# Eye-tracking / highlighting studies need a locked 1920x1080 viewer.
# Default off. Toggle from Lab settings on the study selection (home) screen,
# or set SEMR_EYE_TRACKING_MODE=1 in the environment as the factory default.
SEMR_EYE_TRACKING_MODE = os.environ.get('SEMR_EYE_TRACKING_MODE', '0').lower() in ('1', 'true', 'yes')

DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
_allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
if _allowed_hosts:
    ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '::1']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Match existing models/migrations (explicit AutoField PKs).
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# USE_L10N removed (dropped in Django 5); locale formatting follows USE_I18N / FORMAT_MODULE_PATH.

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Secret key: prefer env; loud insecure default only when DEBUG is True.
_PLACEHOLDER_SECRET = '$$$$$ENTER SECRET KEY$$$$$'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Loud insecure default for local single-user runserver only.
        SECRET_KEY = 'django-insecure-local-lab-only-set-DJANGO_SECRET_KEY-for-shared-hosts'
    else:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY (or SECRET_KEY) must be set when DJANGO_DEBUG is False.'
        )
elif not DEBUG and SECRET_KEY == _PLACEHOLDER_SECRET:
    raise ImproperlyConfigured(
        'Refusing to start with DEBUG=False and the placeholder SECRET_KEY '
        '$$$$$ENTER SECRET KEY$$$$$. Set DJANGO_SECRET_KEY to a long random string.'
    )


MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'SEMRproject.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'SEMRproject.wsgi.application'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SEMRinterface',
    'django.contrib.admin',
    'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
