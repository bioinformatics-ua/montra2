# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.conf.urls import url
from views import *
from documents import *

import docs_manager.views

urlpatterns = [
    # Upload Documents
    url(r'^uploadfile/(?P<fingerprint_id>[^/]+)/$', docs_manager.views.upload_file),
    url(r'^uploadcommunityfile/(?P<community_slug>[^/]+)/((?P<folder_name>[^/]+)/)?$', docs_manager.views.upload_community_file),

    # List Files
    url(r'^docfiles/(?P<fingerprint>[^/]+)/$', docs_manager.views.list_fingerprint_files),
    url(r'^communitydocfiles/(?P<community_slug>[^/]+)/((?P<folder_name>[^/]+)/)?$', docs_manager.views.list_community_files),
    

    url(r'^list_community_folder_documents/(?P<community_slug>[^/]+)/((?P<folder_name>.*)/)?$', docs_manager.views.list_community_folder_documents, name = "list_community_folder_documents"),
    url(r'^list_community_folders/((?P<community_slug>[^/]+)/)?$', docs_manager.views.list_community_folders, name = "list_community_folders"),
    #url(r'^list_community_folders/$', 'docs_manager.views.list_community_folders', name = "list_community_folders_no_args"),

  # Create folders

    url(r'^create_community_folder/(?P<community_slug>[^/]+)/((?P<folder_id>[^/]+)/)?((?P<dependency>[^/]+)/)?$', docs_manager.views.create_community_folder),
    url(r'^drag_community_folder/(?P<community_slug>[^/]+)/(?P<source_folder>[^/]+)/(?P<destination_folder>[^/]+)/$', docs_manager.views.drag_community_folder),
    url(r'^drag_community_file/(?P<community_slug>[^/]+)/(?P<file_id>[^/]+)/(?P<destination_folder>[^/]+)/$', docs_manager.views.drag_community_file),



    url(r'^get_community_file/(?P<file_name>[^/]+)/(?P<revision>[^/]+)/$', docs_manager.views.get_community_file),
]
