"""
SEMRproject/urls.py
version 2024.1
package github.com/ajk77/SimpleEMRSystem
Modified by AndrewJKing.com|@andrewsjourney

This file sets the base URL pattern. 

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

from django.urls import include, path
from django.contrib import admin

app_name = "SEMRinterface"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("SEMRinterface.urls")),  # Redirects the root URL to SEMRinterface
    path("SEMRinterface/", include("SEMRinterface.urls")),  # Additional base URL for the app
]


