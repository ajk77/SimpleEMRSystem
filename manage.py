"""
manage.py
package github.com/ajk77/SimpleEMRSystem

To localy deploy interface:
Open Bitnami Django Stack Environment with use_djangostack.bat.
cd into your project directory (the directory containing this file)
enter>"python manage.py runserver"
open web browser to http://127.0.0.1:8000/SEMRinterface/


"""

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SEMRproject.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
