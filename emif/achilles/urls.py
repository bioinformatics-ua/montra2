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

from django.conf.urls import url
from . import api, views


urlpatterns = [
    url(r'^ds/(?P<fingerprint_id>[^/]+)/$', api.DatasourceView.as_view()),
    url(r'^aw/(?P<fid>[^/]+)/(?P<report_name>[a-zA-Z0-9_]+)/$', api.AchillesServicesView.as_view()),

    url(r'^home', views.AchillesBase.as_view()),

    url(r'^zip/ds/(?P<fingerprint_id>[^/]+)/$', api.AchillesDatasourceView.as_view()),
    url(r'^zip/status/(?P<fid>[^/]+)/$', api.ZipStatus.as_view()),
	url(r'^zip/(?P<fingerprint_id>[^/]+)/(?P<name>[a-zA-Z0-9_]+)/$', api.AchillesReportView.as_view()),
	url(r'^zip/(?P<fingerprint_id>[^/]+)/(?P<name>[a-zA-Z0-9_]+)/(?P<id>[0-9]+)/$', api.AchillesCollectionView.as_view()),

]
