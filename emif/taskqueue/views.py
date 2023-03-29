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

from .models import QueueJob
from django.shortcuts import render
from django.conf import settings
from community.models import Community


def list(request, template_name='queue_list.html'):

    comm = None
    if settings.SINGLE_COMMUNITY:
        comm = Community.objects.all()[:1].get()

    tq = None
    tq = QueueJob.objects.filter(runner=request.user)

    return render(request, template_name,
        {
            'request': request,
            'breadcrumb': True,
            'taskqueue': tq,
            'activemenu': 'jobqueue',
            'comm': comm
        })
