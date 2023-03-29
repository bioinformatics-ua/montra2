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
import os
import uuid

from dateutil.tz import tzutc
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response

from api.views import respond_as_attachment
from community.models import Community
from population_characteristics.response import JSONResponse, response_mimetype
from population_characteristics.serialize import serialize
from public.utils import hasFingerprintPermissions
from .models import CommunityDocument, FingerprintDocuments, Folder
from .storage_handler import FileSystemHandleFile, HandleFile, PATH_STORE_FILES

UTC = tzutc()


def serialize_date(dt):
    """
    Serialize a date/time value into an ISO8601 text representation
    adjusted (if needed) to UTC timezone.

    For instance:
    >>> serialize_date(datetime(2012, 4, 10, 22, 38, 20, 604391))
    '2012-04-10T22:38:20.604391Z'
    """
    if dt.tzinfo:
        dt = dt.astimezone(UTC).replace(tzinfo=None)
    return dt.isoformat() + 'Z'


def get_revision():
    r = uuid.uuid1()
    r = str(r)
    r.replace("-","")
    return r


def upload_document_aux(request, fingerprint_id):
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
    fd = FingerprintDocuments()
    fd.user = request.user
    fd.fingerprint_id = fingerprint_id
    fd.revision = revision
    fd.path = path_file
    fd.file_name = file_name
    fd.name = request.POST['pc_name']
    fd.description = request.POST['pc_comments']
    fd.save()

    return data


def upload_document(request, fingerprint_id):
    """Store the files at the backend
    """

    data = upload_document_aux(request, fingerprint_id)

    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def upload_file(request, fingerprint_id):
    """ Upload files from Jerboa
    """
    # TODO: for now it is only calling the documents
    return upload_document(request, fingerprint_id)


def list_fingerprint_files_aux(request, fingerprint):
    # List the Jerboa files for a particular fingerprint
    jerboa_files = FingerprintDocuments.objects.filter(
            fingerprint_id=fingerprint,
            removed=False
        )

    files_latest_version = jerboa_files.values('file_name').annotate(latest=Max('latest_date'))

    file_records = []
    for file in files_latest_version:
        #print file['file_name']
        file_records.append(jerboa_files.get(file_name = file['file_name'], latest_date = file['latest']))

    #print file_records

    _data = []

    for f in file_records:
        _doc = {'name': f.name,
                'comments': f.description,
                'revision': f.revision,
                'file_name': f.file_name,
                #'path': f.path.replace(settings.PROJECT_DIR_ROOT, ''),
                'fingerprint_id': f.fingerprint_id  ,
                'latest_date': serialize_date(f.latest_date),
                }
        _data.append(_doc)

    return _data


def list_fingerprint_files(request, fingerprint):

    if not hasFingerprintPermissions(request, fingerprint):
        return HttpResponse("Access forbidden",status=403)

    data = {'conf': list_fingerprint_files_aux(request, fingerprint)}

    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


######################COMMUNITY DOCUMENTS###################################   

def get_dependencies(folder_name):

    folder = Folder.objects.get(name=folder_name)
    dependency_list = []

    dependency = folder.dependency

    while dependency != None:
        dependency_list.append(dependency.name)
        dependency = Folder.objects.get(id=dependency.id).dependency

    return dependency_list 

def list_community_folder_documents(request, community_slug, folder_name):


    if community_slug != "":


        dependency = Folder.objects.get(name = folder_name, removed = False)

        if type(dependency.dependency) == Folder:
            parent = dependency.dependency.name
            parent_id = dependency.dependency.id
        else:
            parent = dependency.dependency
            parent_id = None

        community_folders = Folder.objects.filter(
                community__slug=community_slug,
                dependency = dependency,
                removed=False
            ).order_by("name")

        community_files = CommunityDocument.objects.filter(
            community__slug=community_slug,
            folder = dependency,
            removed=False
        ).order_by("file_name")

        if not community_folders:
            if community_files:
                folder_name = community_files[0].folder.name

                if type(community_files[0].folder.dependency) == Folder:
                    parent = community_files[0].folder.dependency.name
                    parent_id = community_files[0].folder.dependency.id
                else:
                    parent = community_files[0].folder.dependency
                    parent_id = None


        dependencies = list(reversed(get_dependencies(folder_name)))

        try:
            comm = Community.objects.get(slug=community_slug)
            comm_manager = comm.is_owner(request.user)
        except:
            comm_manager = False

    else:
        community_folders = None
        comm_manager = True

    return render(
            request,
            'community_folders.html',
            {
            'community_folders': community_folders,
            'community_manager': comm_manager,
            'community_slug': community_slug,
            'community_files': community_files,
            'folder_name': folder_name,
            'show_parent': True,
            'parent': parent,
            'parent_id': parent_id,
            'folder_id':dependency.id,
            'dependencies': dependencies
            }
            ) 


def list_community_folders(request, community_slug=""):

    if community_slug != "":


        community_folders = Folder.objects.filter(
                community__slug=community_slug,
                removed=False,
                dependency = None
            ).order_by("name")

        community_files = CommunityDocument.objects.filter(
            community__slug=community_slug,
            folder = None,
            removed=False
        ).order_by("file_name")

        try:
            comm = Community.objects.get(slug=community_slug)
            comm_manager = comm.is_owner(request.user)
        except:
            comm_manager = False

    else:
        community_folders = None
        comm_manager = True

    return render(
            request,
            'community_folders.html',
            {
            'community_folders': community_folders,
            'community_manager': comm_manager,
            'community_slug': community_slug,
            'community_files': community_files,
            }
            ) 


def list_community_files(request, community_slug, folder_name=None):

    community_files = CommunityDocument.objects.filter(
                community__slug=community_slug,
                folder__name = folder_name,
                removed=False
            )

    files_latest_version = community_files.values('file_name').annotate(latest=Max('latest_date'))

    file_records = []
    for file in files_latest_version:
        file_records.append(community_files.get(file_name = file['file_name'], latest_date = file['latest']))

    _data = []

    for f in file_records:
        _doc = {'name': f.name,
                'comments': f.description,
                'revision': f.revision,
                'file_name': f.file_name,
                'community_id': f.community_id  ,
                'latest_date': serialize_date(f.latest_date),
                'file_id': f.id
                }
        _data.append(_doc)

    data = {'conf': _data}

    response = JSONResponse(data, mimetype=response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response    




def upload_community_file(request,community_slug,folder_name=None,template_name='community_folders.html'):
    # compute revision
    revision = get_revision()
    file_id = 0

    #try:
    file_id = request.POST['cd_id']
    community_id = Community.objects.get(slug = community_slug).id
    #except:
        #pass

    try:
        folder_name = request.POST['folder_name_upload']
    except:
        folder_name = None   
    

    if folder_name != None:
        try:
            folder = Folder.objects.get(name = folder_name, removed = False)
        except:
            folder = None
    else:
        folder = None

    # Create the backend to store the file
    fh = FileSystemHandleFile()
    g_fh = HandleFile(fh)

    files = []
    # Run it for all the sent files (apply the persistence storage)
    path_file = None
    file_name = None

    if request.FILES:
        for f in request.FILES.getlist("file"):
            # Handle file
            path_file = g_fh.handle_file(f, revision=revision)
            file_name = f.name
            # Serialize the response
            files.append(serialize(f))

    # Store the metadata in the database

            if file_id:
                try:
                    cd = CommunityDocument.objects.get(community_id = community_id, id = file_id, removed = False)
                    cd.user = request.user
                    if file_name:
                        cd.file_name = file_name
                    if path_file:
                        cd.path = path_file
                        cd.revision = revision
                    #cd.name = request.POST['cd_name']
                    cd.description = request.POST['cd_comments']
                    cd.folder = folder
                    cd.save()
                except:
                    pass
    

            else:
                cd = CommunityDocument()
                cd.user = request.user
                cd.community_id = community_id
                cd.revision = revision
                cd.path = path_file
                cd.file_name = file_name
                #cd.name = request.POST['cd_name']
                cd.description = request.POST['cd_comments']
                cd.folder = folder
                cd.save()


    else:
        if file_id:
                try:
                    cd = CommunityDocument.objects.get(community_id = community_id, id = file_id, removed = False)
                    cd.user = request.user
                    if file_name:
                        cd.file_name = file_name
                    if path_file:
                        cd.path = path_file
                        cd.revision = revision
                    #cd.name = request.POST['cd_name']
                    cd.description = request.POST['cd_comments']
                    cd.folder = folder
                    cd.save()
                except:
                    pass
    

        else:
            cd = CommunityDocument()
            cd.user = request.user
            cd.community_id = community_id
            cd.revision = revision
            cd.path = path_file
            cd.file_name = file_name
            #cd.name = request.POST['cd_name']
            cd.description = request.POST['cd_comments']
            cd.folder = folder
            cd.save()


    if folder_name != "":

        return HttpResponseRedirect('/docsmanager/list_community_folder_documents/' + community_slug + '/' + folder_name + '/')

    else:
        return HttpResponseRedirect('/docsmanager/list_community_folders/' + community_slug + '/')



def drag_community_folder(request,community_slug,source_folder,destination_folder):

    try:
        folder = Folder.objects.get(id=int(source_folder))
        if destination_folder != 'None':
            dependency = Folder.objects.get(id=int(destination_folder))
        else:
            dependency = None
        folder.dependency = dependency
        folder.save()
    except:
        pass

    if folder.dependency == None:

        return HttpResponseRedirect('/docsmanager/list_community_folders/community_slug/')

    else:

        return HttpResponseRedirect('/docsmanager/list_community_folder_documents/community_slug/' + folder.name + '/')


def drag_community_file(request,community_slug,file_id,destination_folder):

    folder = None

    try:
        comm_file = CommunityDocument.objects.get(id=int(file_id), community__slug=community_slug)

        if destination_folder != 'None':
            folder = Folder.objects.get(id=int(destination_folder))
            comm_file.folder = folder
        else:
            comm_file.folder = None
        comm_file.save()
    except:
        pass

    if folder: 
        if folder.dependency == None:

            return HttpResponseRedirect('/docsmanager/list_community_folders/community_slug/')

        else:

            return HttpResponseRedirect('/docsmanager/list_community_folder_documents/community_slug/' + folder.name + '/')

    else:
        return HttpResponseRedirect('/docsmanager/list_community_folders/community_slug/')



def create_community_folder(request,community_slug,folder_id=None,dependency=None,template_name='community_folders.html'):

    if "folder_id" in request.POST and request.POST["folder_id"] != "":
        folder_id = request.POST["folder_id"]
    else:
        folder_id = None

    if "folder_dependency" in request.POST and request.POST["folder_dependency"] !="":
        folder_dependency = request.POST["folder_dependency"]
        dependency = Folder.objects.get(id = folder_dependency)
    else:
        dependency = None

    if folder_id != None:
        try:
            folder = Folder.objects.get(id=request.POST["folder_id"])
            folder.name = request.POST["folder_name"]
            folder.description = request.POST["folder_description"]
            folder.dependency = dependency
            folder.save()

        except:
           pass

    else:
        try:
            folder_name = request.POST['folder_name']
            folder_description = request.POST["folder_description"]
            community = Community.objects.get(slug = community_slug)
            folder = Folder.objects.create(name=folder_name, description=folder_description, dependency = dependency, community=community)
        except:
            pass

    if dependency != None:
        return HttpResponseRedirect('/docsmanager/list_community_folder_documents/' + community_slug + '/' + dependency.name + '/')
    
    else:

        return HttpResponseRedirect('/docsmanager/list_community_folders/' + community_slug + '/')

def get_community_file(request, file_name, revision):

    if not (file_name == None or file_name=='' or revision == None or revision == ''):

        path_to_file = os.path.join(os.path.abspath(PATH_STORE_FILES), revision+file_name)
        #print path_to_file
        return respond_as_attachment(request, path_to_file, file_name)

    return Response({}, status=status.HTTP_400_BAD_REQUEST)


