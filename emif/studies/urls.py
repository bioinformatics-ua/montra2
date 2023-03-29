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
import studies.views

urlpatterns = [
    # Upload Documents
    url(r'^display_studies/(?P<community_slug>[\w]+)/$', studies.views.display_studies,  name = "display_studies"),
    url(r'^display_studies/$', studies.views.display_studies_dummy,  name = "display_studies_dummy"),
    url(r'^create_study/$', studies.views.create_study),
    url(r'^studies_details/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.studies_details),
    url(r'^create_study_message/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.create_study_message),
    url(r'^reject_study/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.reject_study),
    url(r'^accept_study/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.accept_study),
    url(r'^delete_study/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.delete_study),
    url(r'^complete_study/(?P<community_slug>[\w]+)/(?P<study_id>[\w]+)/$', studies.views.complete_study),
    url(r'^update_study_status/$', studies.views.update_study_status),
]
