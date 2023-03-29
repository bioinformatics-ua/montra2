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
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from community.views import notify_draft_submission
from .models import Fingerprint, FingerprintPending


############################################################
##### Manage Draft Status - Web service
############################################################
class ManageDraftView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, fingerprint_hash, *args, **_):

        if request.user.is_authenticated():
            new_draft_status = (request.data.get('draft', "false") == "true")

            fp = get_object_or_404(Fingerprint, fingerprint_hash=fingerprint_hash)

            if request.user.is_staff or request.user == fp.owner or request.user in fp.shared.all():

                # TODO we could add a check if all required questions were answered.
                #  If not we dont allow to publish the database

                if fp.community.auto_accept:
                    if fp.draft != new_draft_status:
                        fp.draft = new_draft_status
                        fp.save()
                        fp.indexFingerprint()
                else:
                    if hasattr(fp, "fingerprintpending"):
                        if new_draft_status:  # make draft
                            fp.fingerprintpending.delete()

                            if not fp.draft:
                                fp.draft = True
                                fp.save()
                                fp.indexFingerprint()
                        # else:
                        #     do nothing if there is already a FingerprintPending and the fingerprint is in draft
                    else:
                        if not new_draft_status:  # wants to publish and is currently draft
                            if fp.draft:
                                FingerprintPending.objects.create(fingerprint=fp)

                                notify_draft_submission(request, fp)
                        elif not fp.draft:
                            fp.draft = True
                            fp.save()
                            fp.indexFingerprint()

                return Response({'status': new_draft_status}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)
