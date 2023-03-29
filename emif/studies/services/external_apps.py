# -*- coding: utf-8 -*-
# Copyright (C) 2017 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
# and BMD software, Lda
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
from django.http import HttpResponse

from django.contrib.auth.models import User, Group
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)


from developer.serializers import UserSerializer


class StudyManage(object):
    def __init__(self):
        pass 

    """
    Create a study 
    """
    def create_study(self, user_study_requester, fingerprint_ids, ):
        pass 
    
    """
    Get a study 
    """
    def get_study(self, hash):
        pass 


