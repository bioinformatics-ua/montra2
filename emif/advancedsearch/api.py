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


from emif.models import AdvancedQuery

############################################################
##### Update a title for an advanced search - Web service
############################################################


class UpdateTitleView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request):

        if request.user.is_authenticated():

            qid = request.POST.get('id', None)
            title = request.POST.get('title', None)

            if qid and title:
                try:
                    advq = AdvancedQuery.objects.get(id=qid)

                    advq.title = title
                    advq.save()

                except AdvancedQuery.DoesNotExist:
                    pass

            return Response({'success': True}, status=status.HTTP_200_OK)

        return  Response({}, status=status.HTTP_403_FORBIDDEN)
