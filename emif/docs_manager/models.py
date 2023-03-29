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
from django.db import models
from django.contrib.auth.models import User
from community.models import Community

class Document(models.Model):
    user = models.ForeignKey(User, unique=False, blank=True, null=True)
    fingerprint_id = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    description = models.TextField()
    removed = models.BooleanField(default=False)

    def get_name(self):
        pass

    def get_description(self):
        pass

    def store(self):
        pass

    def load(self):
        pass

class FingerprintDocuments(Document):
    pass

class Folder(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    community = models.ForeignKey(Community, blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    removed = models.BooleanField()
    dependency = models.ForeignKey('self', blank=True, null=True)
    description = models.TextField(blank=True)

class CommunityDocument(models.Model):
    user = models.ForeignKey(User, unique=False, blank=True, null=True)
    community = models.ForeignKey(Community, blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    description = models.TextField()
    removed = models.BooleanField()
    folder = models.ForeignKey(Folder, blank=True, null=True)

