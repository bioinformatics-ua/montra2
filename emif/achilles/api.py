# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/

# This program is free software: you can redistribute it and/or modify
# it under theight (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
# terms of the GNU General Public License as published by
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
from __builtin__ import file
from django.conf import settings

from django.http import HttpResponse

from django.contrib.auth.models import User, Group
from django.core.cache import cache

from rest_framework import permissions
from rest_framework import renderers
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated

import json
from string import Template
import os
import string

from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt


from public.utils import hasFingerprintPermissions
from .models import Datasource, DatasourceZip
from django.db import models
import requests
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.sites.models import Site
import zipfile
from rest_framework.authtoken.models import Token


VERIFICATION_SSL_API = settings.VERIFICATION_SSL_API

STORAGE_PATH=None
if settings.DEBUG:
	STORAGE_PATH = settings.PROJECT_DIR_ROOT+settings.MIDDLE_DIR+'achilles/files/'
else:
	STORAGE_PATH = settings.STATIC_ROOT +'achilles/files/'

ZIP_PATH = STORAGE_PATH + 'zip/'
REPORT_PATH = STORAGE_PATH + 'data/'

PATTERNS = {
		"conditioneras" : "condition_{id}.json",
		"conditions" 	: "condition_{id}.json",
		"drugeras"		: "drug_{id}.json",
		"drugs"			: "drug_{id}.json",
		"observations" 	: "observation_{id}.json",
		"procedures"	: "procedure_{id}.json",
		"visits"		: "visit_{id}.json"
	}

class DatasourceView(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (AllowAny,)
	renderer_classes = (JSONRenderer,)

	def get(self, request, fingerprint_id):
		if hasFingerprintPermissions(request,fingerprint_id):
			path = os.path.abspath('achilles/static/achilles/default_datasource.json')

			f = open(path, 'r')
			ds = json.load(f)
			for item in ds["datasources"]:
				item['rootUrl']= 'aw/'+fingerprint_id
			return Response(ds, status=status.HTTP_200_OK)
		else:
			return Response({"error": "User has no permissions"},status=status.HTTP_403_FORBIDDEN)

	def post(self, request, fingerprint_id):
		import achilles.tasks
		if hasFingerprintPermissions(request,fingerprint_id):
			ds = None
			try:
				ds = Datasource.objects.get(fingerprint_id=fingerprint_id)
			except:
				ds = Datasource()
			#print request.FILES.__dict__
			#print request.POST.__dict__
			ds.fingerprint_id = fingerprint_id
			ds.user = request.user
			ds.revision += 1

			if request.FILES:
				#print 'files: '
				if request.is_secure():
					scheme = 'https://'
				else:
					scheme = 'http://'

				if settings.DEBUG:
					ds.datasource_url = scheme + request.get_host() + settings.BASE_URL +'achilles/zip/ds/'+fingerprint_id+'/'
				else:
					ds.datasource_url = settings.BASE_URL +'achilles/zip/ds/'+fingerprint_id+'/'

				#print ds.datasource_url
				#ds.progress = Datasource.NOT_STARTED
				try:
					self.handle_uploaded_file(fingerprint_id, request.FILES['ds_zip'], ds.revision)
					achilles.tasks.unzip_file.delay(fingerprint_id)
					ds.save()

					return Response({"status": "success", "message": "created"},status=status.HTTP_201_CREATED)
				except:
					return Response({"status": "error", "message": "Error Processing The Upload"},status=status.HTTP_400_BAD_REQUEST)
			else:
				#print 'normal '
				ds.datasource_url = request.POST.get('ds_url', '')
				ds.progress = Datasource.COMPLETED

				if self.isValidDatasource(ds.datasource_url):
					ds.save()
					#print ds.__dict__
					return Response({"status": "success", "message": "created"},status=status.HTTP_201_CREATED)
				else:
					return Response({"status": "error", "message" : "URL does not provide a valid json"},status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"status": "error", "message" : "User has no permissions"},status=status.HTTP_401_UNAUTHORIZED)

	# Consider using Validictory for a more complete check http://pypi.python.org/pypi/validictory
	def isValidDatasource(self, url):
		"""
		:rtype : bool
		"""
		try:
			ds_req = requests.get(url, verify=VERIFICATION_SSL_API)
			ds = ds_req.json()
			return True
		except:
			return False

	def handle_uploaded_file(self, fingerprint_id, f, revision):
		if not os.path.exists(ZIP_PATH) or not os.path.isdir(ZIP_PATH):
			os.makedirs(ZIP_PATH)
		destZip = ('%s%s_%s.zip')%(ZIP_PATH, fingerprint_id, revision)
		os.remove(destZip) if os.path.exists(destZip) else None
		try:
			zds = DatasourceZip.objects.get(fingerprint_id=fingerprint_id)
		except:
			zds = DatasourceZip()
		zds.fingerprint_id = fingerprint_id
		zds.extracted_files = -1
		zds.save()
		with open(destZip, 'wb+') as destination:
			for chunk in f.chunks():
				destination.write(chunk)


class ZipStatus(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)
	renderer_classes = (JSONRenderer,)
	def get(self, request, fid):
		try:
			zds = DatasourceZip.objects.get(fingerprint_id=fid)
			ds = Datasource.objects.get(fingerprint_id=fid)
			return Response({ "status": ds.status(),
							  "total" : zds.total_files,
							  "partial" : zds.extracted_files })
		except Exception as e:
			return Response({ "status" : "error",
							  "message": "ERROR: Does not exist" + str(e) }, status=status.HTTP_404_NOT_FOUND)

def getDataSource(request, fingerprint_id):
	#print 'Start Datasource ZIP'
	#print request.__dict__

	path = os.path.abspath('achilles/static/achilles/zip_datasource.json')
	#print path
	f = open(path, 'r')
	rs = json.load(f)
	for item in rs["datasources"]:
		if request.is_secure():
			scheme = 'https://'
		else:
			scheme = 'http://'


		if settings.DEBUG:
			item['rootUrl'] = scheme + request.get_host() + settings.BASE_URL +'achilles/zip/'+fingerprint_id+'/'
		else:
			item['rootUrl'] = settings.BASE_URL +'achilles/zip/'+fingerprint_id+'/'

	#	print item['rootUrl']
	#print 'End Datasource ZIP'
	return rs

def getReportView(request, fingerprint_id, name):
	#print 'Start Report ' + name
	try:
		ds_obj = Datasource.objects.get(fingerprint_id=fingerprint_id)
	except Datasource.DoesNotExist:
		return Response({"error": 'datasource invalid'},status=status.HTTP_406_NOT_ACCEPTABLE)
	if ds_obj.progress != Datasource.COMPLETED:
		return Response({"error": 'Datasource not completed', "message" : ds_obj.status()},status=status.HTTP_406_NOT_ACCEPTABLE)

	path = os.path.join(REPORT_PATH, fingerprint_id ,'reports', name + '.json')
	#print 'PATH = ' +path

	f = open(path, 'r')
	rs = json.load(f)
	#print "Report Done"
	return rs

def getCollectionView(request, fingerprint_id, name, id):
	#print 'Start Collection ' + name + '/' + id + ':' + string.replace(self.patterns[name],'{id}', id)
	try:
		ds_obj = Datasource.objects.get(fingerprint_id=fingerprint_id)
	except Datasource.DoesNotExist:
		return Response({"error": 'datasource invalid'},status=status.HTTP_406_NOT_ACCEPTABLE)
	if ds_obj.progress != Datasource.COMPLETED:
		return Response({"error": 'Datasource not completed', "message" : ds_obj.status()},status=status.HTTP_406_NOT_ACCEPTABLE)


	print ">>"
	print name
	print "<<"

	path = os.path.join(REPORT_PATH, fingerprint_id ,'reports', name, string.replace(PATTERNS[name],'{id}', id))

	#print 'File: ' + path
	f = open(path, 'r')
	rs = json.load(f)
	#print 'End Collection'
	return rs

class AchillesServicesView(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (AllowAny,)
	renderer_classes = (JSONRenderer,)
	collections = ["conditioneras",
			"conditions",
			"drugeras",
			"drugs",
			"observations",
			"procedures",
			"visits"
	]

	def get(self, request, fid, report_name):
		if not hasFingerprintPermissions(request, fid):
			return Response('Forbidden', status=status.HTTP_401_UNAUTHORIZED)
		#print 'Catalogue Start '+ report_name + ' -> ' + fid
		headers = {}

		try:
			ds_obj = Datasource.objects.get(fingerprint_id=fid)
		except Datasource.DoesNotExist:
			return Response({"error": 'datasource invalid'},status=status.HTTP_406_NOT_ACCEPTABLE)
		#print 'Get DS ' + report_name + ' -> ' + fid + ':'
		#print 'URL:'+ ds_obj.datasource_url
		token = None
		if request.user.is_authenticated():
			token, tcreated = Token.objects.get_or_create(user=request.user)
		else:
			# if public key is valid, and there is no user object, just use the admin token
			token, tcreated = Token.objects.get_or_create(user=User.objects.get(id=1))

		headers={'Authorization': 'Token %s' % token.key}
		#print 'Headers: '
		#print headers

		ds = ''

		try:
			if ds_obj.datasource_url.startswith(settings.BASE_URL):
				print "GOING THE WAY OF USING FiLES"
				ds = getDataSource(request, fid)
			else:
				ds_req = requests.get(ds_obj.datasource_url, verify=VERIFICATION_SSL_API, headers=headers, timeout=6)
				#print 'REQ:'
				#print ds_req.headers
				#print ds_req.__dict__
				ds = ds_req.json()
		except:
			raise
			return Response({"status":"error", "message": "JSON Data cannot be found, contact database owner"} ,
			 status=status.HTTP_404_NOT_FOUND)

		#print 'DS:'
		#print ds.__dict__
		#print 'Got DS ' + report_name + ' -> ' + fid
		urlfrags = []
		for item in ds['datasources']:
			is_collection = False
			name = ''

			if 'rootUrl' in item:
				urlfrags.append(item['rootUrl'])
			if 'map' in item:
				if report_name in item['map']:
					reportpart = name = item['map'][report_name]["url"]
					if (report_name in self.collections):
						is_collection = True
						reportpart = string.replace(reportpart, '{id}', request.GET['id'],1)
					urlfrags.append(reportpart)
				else:
					return Response({},status=status.HTTP_403_FORBIDDEN)
			elif 'url' in item or 'folder' in item:
				return Response({"status": "error", "message": "not supported"},status=status.HTTP_403_FORBIDDEN)
			else:
				return Response({"status": "error", "message": "unknown"},status=status.HTTP_403_FORBIDDEN)
			url = ''.join(urlfrags)
			#print 'Get Content ' + report_name + ' -> ' + fid + '/' + url
			try:
				contnt = ''
				if url.startswith(settings.BASE_URL):
					name = name.split('/')[0]
					if not is_collection:
						contnt = getReportView(request, fid, name)
					else:
						contnt = getCollectionView(request, fid, name, request.GET['id'])
				else:
					rep_req = requests.get(url, verify=VERIFICATION_SSL_API, headers=headers)

					#print rep_req.__dict__
					contnt = rep_req.json()
				print contnt

			#	print 'Got Content ' + report_name + ' -> ' + fid + '/' + url
				return Response(contnt)
			except Exception, e:
				raise
				return Response({"status": "error", "message": e.message},status=status.HTTP_403_FORBIDDEN)
		else:
			return Response({"status": "error", "message": "unknown2"},status=status.HTTP_403_FORBIDDEN)

class AchillesReportView(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)
	renderer_classes = (JSONRenderer,)
	def get(self, request, fingerprint_id, name):
		return Response(getReportView(request, fingerprint_id, name))




class AchillesCollectionView(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)
	renderer_classes = (JSONRenderer,)
	patterns = PATTERNS

	def get(self, request, fingerprint_id, name, id):

		return Response(getCollectionView(request, fingerprint_id, name, id))

class AchillesDatasourceView(APIView):
	authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
	permission_classes = (IsAuthenticated,)
	renderer_classes = (JSONRenderer,)
	def get(self, request, fingerprint_id):
		return Response(getDataSource(request, fingerprint_id))

