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

from django.http import HttpResponse

from django.contrib.auth.models import User, Group
from django.core.cache import cache

from rest_framework import permissions
from rest_framework import renderers
from rest_framework.authentication import TokenAuthentication

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated

from community.models import Community, CommunityUser, CommunityGroup

import logging
logger = logging.getLogger(__name__)


from developer.serializers import UserSerializer

############################################################
##### Checks if a slug is free - Web service
############################################################


class StudyInfo(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, slug):

        if request.user.is_authenticated():
            # retrieve study here. 

            return Response({'free': free}, status=status.HTTP_200_OK)

        return  Response({}, status=status.HTTP_403_FORBIDDEN)

