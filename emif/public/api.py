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
from django.conf import settings

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

from public.models import PublicFingerprintShare
from emif.utils import send_custom_mail
from community.models import Community

from constance import config

############################################################
##### Send Private Link through email to several users - Web service
############################################################

class PrivateLinkEmailView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kw):

        if request.user.is_authenticated():
            success=False

            private_link = request.POST.get('plid', -1)
            emails = request.POST.getlist('emails[]', [])
            community = request.POST.get('community', -1)

            try:
                plink  = PublicFingerprintShare.objects.get(id=private_link)

                if len(emails)>0:
                    fname = plink.fingerprint.findName()

                    message = """Dear Colleague,\n
                            %s shared with you a private link to their database "%s" on the platform <a href="http://bioinformatics.ua.pt/%s">%s</a>. \n\n
                            The database can be visualised in the link below:\n
                            <a href="%s">%s</a>\n\n
                            \n\nSincerely,\n%s
                    """ % (request.user.get_full_name(), fname, config.project_name, config.brand, settings.BASE_URL+'public/c/' + community + '/fingerprint/'+plink.hash, fname, config.brand)

                    try:
                        send_custom_mail(config.brand+": A private link for a database is being shared with you.",
                            message, settings.DEFAULT_FROM_EMAIL, emails)

                        success=True
                    except:
                        print "-- Error: Couldn't send the email for private link sharing"


            except PublicFingerprintShare.DoesNotExist:
                print "-- Error: Retrieving public fingerprint share"

            response = Response({'success': success}, status=status.HTTP_200_OK)

        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response
