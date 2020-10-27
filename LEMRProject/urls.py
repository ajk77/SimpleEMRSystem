"""
LEMRProject/urls.py
version 2.0
package github.com/ajk77/LEMRinterface
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

from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

app_name = "LEMRinterface"

urlpatterns = [
    url(r'^LEMRinterface/', include('LEMRinterface.urls'))
    ]
# Examples:
# url(r'^$', 'LEMRProject.views.home', name='home'),
# url(r'^LEMRProject/', include('LEMRProject.foo.urls')),

# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
# url(r'^admin/', include(admin.site.urls)),

