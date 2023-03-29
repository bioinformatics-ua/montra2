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

from api import *
import advancedsearch.views

urlpatterns = [

    # Literature tab, on database info view
    url(r'^history$', advancedsearch.views.history_defer),
    url(r'^history_advanced$', advancedsearch.views.history_defer_advanced),
    url(r'^history/(?P<source>[0-9]+)/(?P<page>[0-9]+)$', advancedsearch.views.history),
    url(r'^results/(?P<query_id>[0-9]+)$', advancedsearch.views.resultsdiff_history),
    url(r'^results_simple/(?P<query_id>[0-9]+)$', advancedsearch.views.resultsdiff_historysimple),
    url(r'^history/remove/(?P<query_id>[0-9]+)$', advancedsearch.views.remove),
    url(r'^history/remove_simple/(?P<query_id>[0-9]+)$', advancedsearch.views.removesimple),
    url(r'^history/remove_all$', advancedsearch.views.remove_all),
    url(r'^history/remove_all_simple$', advancedsearch.views.remove_allsimple),
    url(r'^savename$', UpdateTitleView.as_view(), name='updatetitle'),


]
