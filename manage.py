"""
manage.py
version 1.0
package github.com/ajk77/LEMRinterface
Modified by AndrewJKing.com|@andrewsjourney

To localy deploy interface:
Open Bitnami Django Stack Environment with use_djangostack.bat.
cd into your project directory (the directory containing this file)
enter>"python manage.py runserver"
open web browser to http://127.0.0.1:8000/LEMRinterface/

---LICENSE---
This file is part of LEMRinterface

LEMRinterface is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or 
any later version.

LEMRinterface is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LEMRinterface.  If not, see <https://www.gnu.org/licenses/>.
"""

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LEMRProject.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
