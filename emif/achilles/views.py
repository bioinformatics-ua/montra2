from django.shortcuts import render, redirect
from rest_framework import permissions
from rest_framework import renderers
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer

from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Datasource
from questionnaire.services import createqsets

from fingerprint.models import Fingerprint
from developer.models import PluginFingeprint

class AchillesBase(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny, )
    renderer_classes = (TemplateHTMLRenderer,)
    def get(self, request):
        fid = request.GET.get('fingerprint_id', '')
        pid = request.GET.get('plugin_id', '')

        if not PluginFingeprint.exists(plugin_hash=pid,fingerprint_hash=fid):
            PluginFingeprint.create(plugin_hash=pid,fingerprint_hash=fid,boolean=True)

        ds = Datasource.objects.filter(fingerprint_id=fid)
        #qsets, name, db_owners, fingerprint_ttype = createqsets(fid)
        owner_fingerprint = False

        fingerprint = Fingerprint.objects.get(fingerprint_hash=fid)

        try:
            for owner in fingerprint.unique_users():
                #print request.user.username
                if (owner.email == request.user.email):
                    owner_fingerprint = True
        except AttributeError:
            owner_fingerprint = False
            
        if not PluginFingeprint.exists(plugin_hash=pid,fingerprint_hash=fid):
            PluginFingeprint.create(plugin_hash=pid,fingerprint_hash=fid,boolean=True)


        context = dict(contains_datasource=ds.exists(),
                    updadd='Update' if ds.exists() else 'Add',
                    url=ds[0].datasource_url if ds.exists() else '',
                    fid=fid,
                    pid=pid,
                    unzip_in_progress=(ds[0].status() if ds.exists() else Datasource.UNZIP_STATUS[Datasource.NOT_STARTED][1]),
                    owner_fingerprint=owner_fingerprint
                       )

        return Response(context, template_name="achilles_base.html")


