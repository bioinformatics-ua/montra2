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
from django.db import models
from datetime import timedelta, date
from django.utils import timezone
from django.contrib.auth.models import User
from fingerprint.models import Fingerprint

class PublicFingerprintShare(models.Model):
    fingerprint = models.ForeignKey(Fingerprint)
    user = models.ForeignKey(User)
    hash = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(null=True)
    expiration_date = models.DateTimeField()
    remaining_views = models.IntegerField()
    
    def is_valid(self):
        return self.remaining_views>0 and timezone.now() < self.expiration_date
    
    
    def __str__(self):
        return str(self.expiration_date)
    

