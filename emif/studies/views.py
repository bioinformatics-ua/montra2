# -*- coding: utf-8 -*-
# Copyright (C) 2017 Universidade de Aveiro, Bioinformatics Group - http://bioinformatics.ua.pt/
#               and BMD software, Lda
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


from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponseRedirect
from fingerprint.models import *
from community.models import *
from accounts.models import *
from studies.models import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from docs_manager.storage_handler import *
from docs_manager.views import get_revision
from population_characteristics.serialize import serialize
from fingerprint.listings import get_databases_from_solr_v2, paginator_process_list
import json
from community.views import *


def display_studies_dummy(request):
    return render(
            request,
            'studies_request.html',
            {
            'study_manager': True
            }
            ) 



def display_studies(request, community_slug):
    # TODO: check if the user belong to the community (always)
    community = Community.objects.get(slug=community_slug)
    
    fingerprints = community.getDatabases()

    database_names = []

    for fingerprint in fingerprints:
        database_names.append(fingerprint.findName())

    try:
        cg = CommunityGroup.objects.get(community=community, name=CommunityGroup.STUDY_MANAGERS_GROUP)
        study_managers = cg.members.all().values_list("user", flat = True)
        study_manager = request.user.id in study_managers
    except:
        study_manager = None
        study_managers = None

    my_studies = ""

    if study_manager or request.user.is_superuser:
        my_studies = Study.objects.filter(community = community, removed = False)
    else:
        my_studies = Study.objects.filter(user = request.user, community = community, removed = False)


    institution = EmifProfile.objects.get(user = request.user).organization

    order = ['SUBMITTED', 'INPROGRESS', 'COMPLETED', 'CLOSED', 'REJECTED']
    my_studies = sorted(my_studies, key = lambda s: order.index(s.status))

    

    return render(
            request,
            'studies_request.html',
            {
            'institution': institution,
            'my_studies': my_studies,
            'study_manager': study_manager,
            'comm':community,
            'comm_id':community.id,
            'databases_names': database_names,
            }
            ) 


@api_view(['GET', 'POST', ])

def create_study(request):

    community_slug = request.POST["community_slug"]
    community = Community.objects.get(slug = community_slug)

    study = Study()
    user = User.objects.get(id=request.POST["user"])
    study.user = User.objects.get(id=request.POST["user"])
    #print request.POST["user"]
    study.community = community
    study.name = request.POST["title"] 
    study.deadline = request.POST["deadline"]
    study.question = request.POST["question"]
    study.requester_position = request.POST["user_position"]
    try:
        database_names = request.POST["database_names"]
        database_names = eval(database_names)
        #print database_names
        if "all" in database_names:
            database_names.remove("all")
        study.databases = ','.join(database_names)
    except:
        pass
    study.status = "SUBMITTED"
    
    study.save()

    try:
        notify_study_submission(community, user, study.name)
    except:
        pass

    return   Response({'result': 1, 'url':'/studies/display_studies/'+ community_slug + '/' }, status=status.HTTP_200_OK)

    

def studies_details(request, community_slug, study_id ):

    
    study = Study.objects.get(community__slug = community_slug, id = study_id, removed = False)
    community = Community.objects.get(slug = community_slug)
    study_user = study.user
    institution = EmifProfile.objects.get(user = study_user).organization
    position = study.requester_position

    messages = StudyMessage.objects.filter(study = study)

    databases_names =""


    try:
        cg = CommunityGroup.objects.get(community=community, name=CommunityGroup.STUDY_MANAGERS_GROUP)
        study_managers = cg.members.all().values_list("user", flat = True)
        study_manager = request.user.id in study_managers
    except:
        study_manager = None


    if study.databases:
        databases_names = study.databases.split(',')

    return render(
            request,
            'studies_details.html',
            {
            'institution': institution,
            'position': position,
            'study_user': study_user,
            'study': study,
            'messages': messages,
            'comm':community,
            'comm_id':community.id,
            'databases_names': databases_names,
            'study_manager': study_manager,
            }
            ) 

def create_study_message(request, community_slug, study_id):

    study = Study.objects.get(community__slug = community_slug, id = study_id)
    community = Community.objects.get(slug = community_slug)

    message = StudyMessage()
    message.study = study
    message.sender = request.user
    message.message = request.POST["chat_message"]

    message.save()

    message.users.add(request.user)

    try:
        cg = CommunityGroup.objects.get(community=community, name=CommunityGroup.STUDY_MANAGERS_GROUP)
        study_managers_ids = cg.members.all().values_list("user", flat = True)
        users = User.objects.filter(id__in = study_managers_ids)
        for user in users:
            message.users.add(user)
    except:
        pass
   
    # Create the backend to store the file
    fh = FileSystemHandleFile()
    g_fh = HandleFile(fh)

    files = []
    # Run it for all the sent files (apply the persistence storage)
    path_file = None
    file_name = None

    if request.FILES:
        for f in request.FILES.getlist("file"):
            revision = get_revision()
            # Handle file
            path_file = g_fh.handle_file(f, revision=revision)
            file_name = f.name
            # Serialize the response
            #files.append(serialize(f))
            sd = StudyDocument()
            sd.user = request.user
            sd.revision = revision
            sd.path = path_file
            sd.file_name = file_name 
            sd.save()
            message.documents.add(sd)
    

    return HttpResponseRedirect('/studies/studies_details/'  + community_slug + '/' + study_id + '/')
    
    
def reject_study(request, community_slug, study_id):

    study = Study.objects.get(id = study_id)
    study.status = "REJECTED"
    study.save()

    community = Community.objects.get(slug = community_slug)

    cg = CommunityGroup.objects.get(community=community, name=CommunityGroup.STUDY_MANAGERS_GROUP)
    study_managers_ids = cg.members.all().values_list("user", flat = True)

    users = User.objects.filter(id__in = study_managers_ids)
    message = StudyMessage()
    message.study = study
    message.sender = request.user
    message.message = request.POST["chat_message"]


    message.save()

    for user in users:
        message.users.add(user)


    message.users.add(request.user)



    return HttpResponseRedirect('/studies/display_studies/'+ community_slug + '/')

def accept_study(request, community_slug, study_id):

    study = Study.objects.get(id = study_id)
    study.accepted = True
    study.status = "INPROGRESS"
    study.save()

    return HttpResponseRedirect('/studies/display_studies/'+ community_slug + '/')

@api_view(['GET', 'POST', ])
def delete_study(request, community_slug, study_id):

    study = Study.objects.get(id = study_id)
    study.removed = True
    study.save()

    #return HttpResponseRedirect('/studies/display_studies/'+ community_slug + '/')

    return   Response({'result': 1, 'url':'/studies/display_studies/'+ community_slug + '/' }, status=status.HTTP_200_OK)


def complete_study(request, community_slug, study_id):

    study = Study.objects.get(id = study_id)
    study.status = "COMPLETED"
    study.save()

    #return HttpResponseRedirect('/studies/display_studies/'+ community_slug + '/')
    Response({}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', ])
def update_study_status(request):

    study_id = request.POST["study_id"]
    community_slug = request.POST["community_slug"]
    study_status = request.POST["study_status"]

    study = Study.objects.get(id = study_id)
    study.status = study_status
    study.save()

    return    Response({'result': 1, 'url':'/studies/studies_details/'+ community_slug + '/'+ study_id+ '/' }, status=status.HTTP_200_OK)

    #return Response({}, status=status.HTTP_400_BAD_REQUEST)


