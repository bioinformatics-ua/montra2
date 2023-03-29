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
import json

from django.shortcuts import render

from emif.views import get_api_info
from population_characteristics.parseJerboaFile import import_population_characteristics_data
from population_characteristics.response import JSONResponse, response_mimetype
from population_characteristics.serialize import serialize
from population_characteristics.services import PopulationCharacteristic
from questionnaire.services import createqsets
from .storage_handler import FileSystemHandleFile, HandleFile


def document_form_view_upload(request):
    """Store the files at the backend
    """

    # Create the backend to store the file
    fh = FileSystemHandleFile()
    g_fh = HandleFile(fh)

    files = []
    # Run it for all the sent files (apply the persistence storage)
    if request.FILES:
        for name, f in request.FILES.items():
            # Handle file
            g_fh.handle_file(f)

            # Serialize the response
            files.append(serialize(f))

    data = {'files': files}
    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def jerboa_form_view_upload(request):
    """ Upload files from Jerboa
    """
    # TODO: for now it is only calling the documents
    return document_form_view_upload(request)


def parsejerboa(request):
    """ Parse files from Jerboa
    """
    path_file = "C:/Users/lbastiao/Projects/TEST_DataProfile_v1.5.6b.txt"
    #path_file = "/Volumes/EXT1/Dropbox/MAPi-Dropbox/EMIF/Jerboa/TEST_DataProfile_v1.5.6b.txt"


    _json = import_population_characteristics_data(filename=path_file)

    pc = PopulationCharacteristic()
    pc.submit_new_revision()
    data = {'data': _json}
    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def document_form_view(request, runcode, qs):

    qsets, name, db_owners, fingerprint_ttype = createqsets(runcode, getAnswers=False)

    if fingerprint_ttype == "":
        raise "There is missing ttype of questionarie, something is really wrong"

    apiinfo = json.dumps(get_api_info(runcode));
    owner_fingerprint = False
    for owner in db_owners.split(" "):
        #print owner
        #print request.user.username
        if (owner == request.user.username):
            owner_fingerprint = True

    return render(request, 'database_info.html',
        {'request': request, 'qsets': qsets, 'export_bd_answers': True,
        'apiinfo': apiinfo, 'fingerprint_id': runcode,
                   'breadcrumb': True, 'breadcrumb_name': name.decode('ascii', 'ignore'),
                    'style': qs, 'collapseall': False,
                    'owner_fingerprint':True,
                    'fingerprint_dump': True,
                    'contains_population': False,
                    'fingerprint_ttype': fingerprint_ttype,
                    })




