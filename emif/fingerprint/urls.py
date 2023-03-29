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

from .api import ManageDraftView
from .views import ImportFingerprintView, export_database_montra_file, export_database_pdf_file

urlpatterns = [
    url(r'^api/draft/(?P<fingerprint_hash>[0-9a-zA-Z]+)$', ManageDraftView.as_view()),
    url(r'^api/pdf/(?P<fingerprint_hash>[0-9a-zA-Z]+)$', export_database_pdf_file),
    url(r'^api/montra/(?P<fingerprint_hash>[0-9a-zA-Z]+)$', export_database_montra_file),
    url(r'^import$', ImportFingerprintView.as_view()),
]
