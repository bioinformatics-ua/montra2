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


from django.db import models
from django.contrib.auth.models import User
from community.models import Community


class Study(models.Model):
    community = models.ForeignKey(Community)
    created_date = models.DateField(auto_now_add=True)
    latest_date = models.DateField(auto_now=True)
    user = models.ForeignKey(User, blank=False, null=False)
    name = models.CharField(max_length=255)
    deadline = models.DateField(blank=True, null=True)
    requester_position = models.TextField(blank=True, null=True)
    question = models.TextField()
    status = models.TextField(blank=False, null=False)
    databases = models.TextField(blank=False, null=False, default="")
    removed = models.BooleanField(default=False)
    status_list = ["SUBMITTED", "INPROGRESS", "COMPLETED", "CLOSED", "REJECTED"]
    
    @staticmethod
    def create(name, user):
        pass


    @staticmethod
    def delete(study):
        pass


class StudyDocument(models.Model):
    user = models.ForeignKey(User, unique=False, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)        

class StudyMessage(models.Model):
    study = models.ForeignKey(Study)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    message = models.TextField()
    sender = models.ForeignKey(User, related_name='study_message_sender',blank=False, null=False )
    users = models.ManyToManyField(User, related_name='study_message_users',blank=False)
    documents = models.ManyToManyField(StudyDocument, blank=True, default = None)




