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
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction
from django.core.urlresolvers import *

from questionnaire.services import createqsets

from community.utils import getComm
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def results_comp(request, template_name='results_comp.html'):
    return results_comp_comm(request, None, template_name)

def results_comp_comm(request, community, template_name='results_comp.html'):

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    list_fingerprint_to_compare = []

    if request.POST:
        for k, v in request.POST.items():
            if k.startswith("chks_") and v == "on":
                arr = k.split("_")

                list_fingerprint_to_compare.append(arr[1])

    class Results:
        num_results = 0
        list_results = []

    class DatabaseFields:
        id = ''
        name = ''
        date = ''
        fields = None

    first_name = None
    list_qsets = {}
    for db_id in list_fingerprint_to_compare:
        try:
            qsets, name, db_owners, fingerprint_ttype = createqsets(db_id, validateAccessPermission=True, user=request.user)
 
            list_qsets[db_id] = { 'name': name, 'qset': qsets}

            if(first_name == None):
                first_name = name
        except:
            logger.error("Problem unpack createqsets while comparing " +db_id )
            
    '''for fingerprint_id, (name, qset) in list_qsets.items:
        print "--------------------------------"
        print content['name']
    '''
    
    return render(request, template_name, {'request': request, 'breadcrumb': True, 'comm': comm,
                                           'results': list_qsets, 'database_to_compare': first_name})
