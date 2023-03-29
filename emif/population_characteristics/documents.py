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

import logging

from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render

from community.utils import getComm
from developer.models import PluginFingeprint
from docs_manager.storage_handler import FileSystemHandleFile, HandleFile
from docs_manager.views import get_revision
from fingerprint.models import Fingerprint
from fingerprint.services import attachPermissions
from questionnaire.services import createqsets
from .models import Characteristic
from .parseJerboaFile import import_population_characteristics_data
from .response import JSONResponse, response_mimetype
from .serialize import serialize
from .services import PopulationCharacteristic
from .tasks import aggregation

logger = logging.getLogger(__name__)


def document_form_view_upload(request, fingerprint_id):
    """Store the files at the backend
    """

    # compute revision
    revision = get_revision()

    # Create the backend to store the file
    fh = FileSystemHandleFile()
    g_fh = HandleFile(fh)

    files = []
    # Run it for all the sent files (apply the persistence storage)
    path_file = None
    file_name = None
    if request.FILES:
        for name, f in request.FILES.items():
            # Handle file
            path_file = g_fh.handle_file(f, revision=revision)
            file_name = f.name
            # Serialize the response
            files.append(serialize(f))


    data = {'files': files}

    # Store the metadata in the database
    chracteristic = Characteristic()
    chracteristic.user = request.user
    chracteristic.fingerprint_id = fingerprint_id
    chracteristic.revision = revision
    chracteristic.path = path_file
    chracteristic.file_name = file_name
    chracteristic.name = request.POST['pc_name']
    chracteristic.description = request.POST['pc_comments']
    chracteristic.save()

    # Parse the Jerboa and insert it in MongoDB
    # The best option will be use django-celery

    #_json = import_population_characteristics_data(request.user, fingerprint_id,filename=path_file)

    pc = PopulationCharacteristic()
    data_jerboa = pc.submit_new_revision(request.user, fingerprint_id, revision, path_file)


    #aggregation.apply_async([fingerprint_id, data_jerboa])
    aggregation(fingerprint_id, data_jerboa)

    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def jerboa_form_view_upload(request, fingerprint_id):
    """ Upload files from Jerboa
    """
    # TODO: for now it is only calling the documents
    return document_form_view_upload(request, fingerprint_id)


def parsejerboa(request):
    """ Parse files from Jerboa
    """
    path_file = "C:/Users/lbastiao/Projects/TEST_DataProfile_v1.5.6b.txt"
    path_file = "/Volumes/EXT1/Dropbox/MAPi-Dropbox/EMIF/Jerboa/TEST_DataProfile_v1.5.6b.txt"


    _json = import_population_characteristics_data(request.user, filename=path_file)

    pc = PopulationCharacteristic()
    pc.submit_new_revision(request.user, fingerprint_id, revision)
    data = {'data': _json}
    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


# ======================================
# ====== JERBOA BAREBONES


def jerboa_view(request, community, runcode, plugin,  readOnly=False, public_key = None, force=False,
    template_name='database_info_Jerboa.html'):

    if not PluginFingeprint.exists(plugin_hash=plugin,fingerprint_hash=runcode):
        PluginFingeprint.create(plugin_hash=plugin,fingerprint_hash=runcode,boolean=True)

    activetab='pc'

    comm = getComm(community, request.user, force=force)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm
    
    h = None

    # GET fingerprint primary key (for comments)
    fingerprint = None

    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=runcode)
        fingerprint_pk = fingerprint.id
    except:
        fingerprint_pk = 0
        raise Http404
    
    qsets, name, db_owners, fingerprint_ttype = createqsets(runcode, highlights=h)
    
    if fingerprint_ttype == "":
        raise "There is a missing type of questionnarie, something is really wrong"

    qsets = attachPermissions(runcode, qsets)
    
    jerboa_files = Characteristic.objects.filter(fingerprint_id=runcode).order_by('-latest_date')

    contains_population = False
    latest_pop = None
    if len(jerboa_files)!=0:
        contains_population = True
        latest_pop = jerboa_files[0]


    return render(request, template_name,
        {   'qsets': qsets,
            'fingerprint_id': runcode,
            'fingerprint': fingerprint,
            'contains_population': contains_population,
            'latest_pop': latest_pop,
            'activetab': activetab,
            'readOnly': readOnly,
            'comm': comm,
            'plugin': plugin 
        })


