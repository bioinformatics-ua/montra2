# -*- coding: utf-8 -*-
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
from __future__ import absolute_import

from datetime import timedelta

from constance import config
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django_comments.models import Comment
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import FingerprintAPI
from community.models import Community
from community.models import PluginPermission
from docs_manager.views import list_fingerprint_files_aux, upload_document_aux
from fingerprint.models import Fingerprint, FingerprintSubscription
from literature.views import getListPublications
from notifications.services import sendNotification
from public.utils import hasFingerprintPermissions
from questionnaire.models import Questionnaire
from .models import Plugin, PluginFingeprint, PluginVersion, VersionDep
from .serializers import AnswerSerializer, ChoiceSerializer, CommentSerializer, CommunityPluginSerializer, \
    CommunitySerializer, EmifProfileSerializer, FingerprintAPISerializer, FingerprintSerializer, \
    QuestionSerializer, QuestionSetSerializer, QuestionnaireSerializer


############################################################
##### Global Plugin - Web services
############################################################

## databaseSchemas()
class DatabaseSchemasView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kw):

        if request.user.is_authenticated():
            schemas = QuestionnaireSerializer(Questionnaire.objects.filter(disable='False'), many=True)

            response = Response({'schemas': schemas.data}, status=status.HTTP_200_OK)

        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response

## getProfileInformation()
class getProfileInformationView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kw):

        if request.user.is_authenticated():
            user = EmifProfileSerializer(request.user.emif_profile)

            response = Response({'profile': user.data}, status=status.HTTP_200_OK)

        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response

## getFingerprints()
class getFingerprintsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, quest_slug=None):

        if request.user.is_authenticated():
            q=None
            if quest_slug:
                try:
                    q = Questionnaire.objects.get(slug=quest_slug)
                except Questionnaire.DoesNotExist:
                    return Response({}, status=status.HTTP_403_FORBIDDEN)

            fingerprints = FingerprintSerializer(
                Fingerprint.objects.valid(questionnaire=q, owner=request.user, include_drafts=True),
                many=True,
            )

            return Response({'fingerprints': fingerprints.data}, status=status.HTTP_200_OK)



        return Response({}, status=status.HTTP_403_FORBIDDEN)

## getFingerprintsOfCommunity()
class getFingerprintsOfCommunityView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community_slug):

        if request.user.is_authenticated():
            community = None
            try:
                community = Community.objects.get(slug=community_slug)
            except Community.DoesNotExist:
                return Response({}, status=status.HTTP_403_FORBIDDEN)

            questionnaire=community.questionnaires.all()[0]
            fingerprints = Fingerprint.objects.filter(questionnaire=questionnaire, removed=False, community=community, draft=False )
            fingerprints_including_drafts = Fingerprint.objects.filter(questionnaire=questionnaire, removed=False, community=community )
            fingerprints_mine = Fingerprint.objects.filter(questionnaire=questionnaire, removed=False, community=community, draft=True, owner=request.user)
            fingerprints_shared_with_me = Fingerprint.objects.filter(questionnaire=questionnaire, removed=False, community=community, draft=True, shared=request.user)

            is_comm_manager = community.is_owner(request.user)

            if is_comm_manager:
                result_fingerprints = fingerprints_including_drafts
            else:
                result_fingerprints = fingerprints | fingerprints_mine | fingerprints_shared_with_me
            
            result_fingerprints = result_fingerprints.distinct()

            results_serialized = FingerprintSerializer(result_fingerprints, many=True)
            

            return Response({'fingerprints': results_serialized.data}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)

############################################################


## getSubscribed()
class getSubscribedView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request, community=None):

        if request.user.is_authenticated():
            q=None
            fingerprints = None

            subscriptions = FingerprintSubscription.objects.filter(user=request.user).values_list('fingerprint__id', flat=True)

            if community:
                try:
                    c = Community.objects.get(slug=community)
                except Community.DoesNotExist:
                    return Response({}, status=status.HTTP_403_FORBIDDEN)

                fingerprints = FingerprintSerializer(c.getDatabases().filter(id__in=subscriptions), many=True)
            else:
                fingerprints = FingerprintSerializer(
                    Fingerprint.objects.valid(include_drafts=True).filter(id__in=subscriptions),
                    many=True,
                )

            return Response({'fingerprints': fingerprints.data}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)


class getCommunityPlugins(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community=None):
        if request.user.is_authenticated():
            if community:
                try:
                    c = Community.objects.get(name=community)
                except Community.DoesNotExist:
                    return Response({}, status=status.HTTP_403_FORBIDDEN)

                plugins = None
            
            if c:
                comm_plugins = c.getCommunityPlugins()
                authorized_plugins = []

                for comm_plugin in comm_plugins:
                    if PluginPermission.check_permission(c, request.user, comm_plugin):            
                        authorized_plugins.append(comm_plugin)

                comm_plugins = authorized_plugins  
                comm_plugins = CommunityPluginSerializer(comm_plugins,many=True)
                return Response({'comm_plugins': comm_plugins.data}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class getCommunities(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.is_authenticated():
            communities = []
            for comm in Community.objects.all():
                if comm.belongs(request.user):
                    communities.append(comm)
        
            communities = CommunitySerializer(communities,many=True)
            return Response({'communities': communities.data}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_403_FORBIDDEN)

############################################################



############################################################
##### Fingerprint Plugin - Web services
############################################################

class getFingerprintUIDView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)

    def get(self, request, fingerprint=None):
        f = None
        comm = ""

        if hasFingerprintPermissions(request, fingerprint):
            try:
                f = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint)

                # Get the community based on questionnaire. There is no true association
                # For now is the only way.
                cs = Community.objects.all()
                for c in cs:
                    qs = c.questionnaires.all()
                    for q in qs:
                        if (f.questionnaire.slug == q.slug):
                            comm=c.slug
                            break
                #####################################
              
                
            except Fingerprint.DoesNotExist:
                return Response({}, status=status.HTTP_403_FORBIDDEN)

            return Response(
                {
                    'community': comm,
                    'fingerprint': FingerprintSerializer(f).data
                }, status=status.HTTP_200_OK)



        return Response({}, status=status.HTTP_403_FORBIDDEN)

class getAnswersView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self, request, fingerprint=None):
        f = None
        if hasFingerprintPermissions(request, fingerprint):
            try:
                f = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint)

            except Fingerprint.DoesNotExist:
                return Response({}, status=status.HTTP_403_FORBIDDEN)

            return Response(
                {
                    'fingerprint': AnswerSerializer(f.answers(restriction=request.user), many=True).data
                }, status=status.HTTP_200_OK)



        return Response({}, status=status.HTTP_403_FORBIDDEN)

class getQuestionsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self,request,questionnaire=None):
        quest = None
        try:
            quest = Questionnaire.objects.get(id=questionnaire)
            q = Questionnaire.questions(quest)
            c = Questionnaire.questions_choices(quest,q)
            
            return Response(
                {
                    'questionnaire': {
                        'questions': QuestionSerializer(q, many=True).data,
                        'choices': ChoiceSerializer(c, many=True).data
                    }
                }, status=status.HTTP_200_OK)

        except Fingerprint.DoesNotExist:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

class getQuestionSetsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self,request,questionnaire=None):
        q = None
        try:
            q = Questionnaire.objects.get(id=questionnaire)
            q = Questionnaire.questionsets(q)

            return Response(
                {
                'questionnaire': QuestionSetSerializer(q, many=True).data
                }, status=status.HTTP_200_OK)

        except Fingerprint.DoesNotExist:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

class getQuestionsAndQuestionSetsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self,request,questionnaire=None):
        q = None
        try:
            q = Questionnaire.objects.get(id=questionnaire)
            questions = Questionnaire.questions(q)
            questionsets = Questionnaire.questionsets(q)

            return Response(
                {
                'questionnaire': { 
                        'questions': QuestionSerializer(questions, many=True).data,
                        'questionsets': QuestionSetSerializer(questionsets, many=True).data
                    }
                }, status=status.HTTP_200_OK)

        except Fingerprint.DoesNotExist:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

## store methods
class getExtraView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):
            print fingerprint
            print type(fingerprint)
            return Response(
                {
                    'api': FingerprintAPISerializer(
                        FingerprintAPI.objects.filter(fingerprintID=fingerprint), many=True
                    ).data
                }, status=status.HTTP_200_OK)



        return Response({}, status=status.HTTP_403_FORBIDDEN)

class getDocumentsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):

            documents = list_fingerprint_files_aux(request, fingerprint)

            return Response(
                {
                    'documents': documents
                }, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)

class putDocumentsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def post(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):

            return Response(
                {
                    'document': upload_document_aux(request, fingerprint)
                }, status=status.HTTP_200_OK)



        return Response({}, status=status.HTTP_403_FORBIDDEN)

class getPublicationsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):
            try:
                fp = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint)
                pubs = getListPublications(fp)

                return Response(
                    {
                        'publications': pubs
                    }, status=status.HTTP_200_OK)

            except Fingerprint.DoesNotExist:
                pass

        return Response({}, status=status.HTTP_403_FORBIDDEN)


class getCommentsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def get(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):
            try:
                fp = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint)

                comments = Comment.objects.filter(
                    content_type__pk=ContentType.objects.get_for_model(fp).id,
                    object_pk=fp.id,
                    is_removed=False,
                ).order_by('-id')

                return Response(
                    {
                        'can_moderate': (request.user.is_superuser or
                                         request.user.is_staff or
                                         fp.community.is_owner(request.user)),
                        'comments': CommentSerializer(comments, many=True).data
                    }, status=status.HTTP_200_OK)

            except Fingerprint.DoesNotExist:
                pass

        return Response({}, status=status.HTTP_403_FORBIDDEN)

class deleteCommentView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)

    def delete(self, request, fingerprint_hash=None, comment_id=None):
        try:
            fingerprint = (Fingerprint.objects
                           .valid(include_drafts=True)
                           .get(fingerprint_hash=fingerprint_hash))
        except Fingerprint.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not (request.user.is_superuser or
                request.user.is_staff or
                fingerprint.community.is_owner(request.user)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment = Comment.objects.get(pk=int(comment_id))
        comment.is_removed = True
        comment.save()

        return Response(status=status.HTTP_200_OK)

class putCommentView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)
    def post(self, request, fingerprint=None):

        if hasFingerprintPermissions(request, fingerprint):

            community = request.POST.get('community', None)

            if community:
                community = '/c/%s/' % community
            else:
                community = ''

            try:
                fp = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint)

                comment = Comment(
                    content_object=fp,
                    site = Site.objects.get_current(),
                    user=request.user,
                    user_name=(request.user.get_full_name() or request.user.email),
                    user_email=request.user.email,
                    user_url="",
                    comment=request.POST['comment'],
                    ip_address=request.META.get("REMOTE_ADDR", None)
                )
                comment.save()

                for this_user in fp.unique_users():
                    user_fullname = None
                    if(this_user.first_name != '' and this_user.last_name != ''):
                        user_fullname = this_user.first_name + ' ' + this_user.last_name
                    else:
                        user_fullname = this_user.username

                    notification_message = "%s has new comments." % (str(fp.findName()))

                    sendNotification(timedelta(hours=1), this_user, request.user,
                        community+"fingerprint/"+fp.fingerprint_hash+"/1/discussion/", notification_message,
                        custom_mail_message=(config.brand+': There\'s a new comment on one of your databases',
                           render_to_string('emails/new_db_comment.html', {
                                'fingerprint_id': fp.fingerprint_hash,
                                'fingerprint_name': fp.findName(),
                                'owner': user_fullname,
                                'comment': comment.comment,
                                'base_url': settings.BASE_URL,
                                'user_commented': request.user
                            })
                           )
                        )

                return Response(
                    {
                        'can_moderate': (request.user.is_superuser or
                                         request.user.is_staff or
                                         fp.community.is_owner(request.user)),
                        'comment': CommentSerializer(comment).data
                    }, status=status.HTTP_200_OK)

            except Fingerprint.DoesNotExist:
                pass

        return Response({}, status=status.HTTP_403_FORBIDDEN)

class setEmptyView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (AllowAny,)

    def post(self, request, fingerprint=None):
        if hasFingerprintPermissions(request, fingerprint):
            community = request.POST.get('community', None)
            if community:
                community = '/c/%s/' % community
            else:
                community = ''
                
            PluginFingeprint.create(plugin_hash=request.POST['plugin'],fingerprint_hash=fingerprint,boolean=str(request.POST['empty']))
            return Response(
                    {
                        'success': "SUCCESS"
                    }, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
    def get(self, request, fingerprint=None):
        pass

############################################################



############################################################
##### Checks if a plugin can take a name - Web service
############################################################
class CheckNameView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kw):

        if request.user.is_authenticated():
            success=False

            name = request.POST.get('name', None)
            slug = request.POST.get('slug', None)

            if name != None:
                try:
                    plugin = Plugin.all(owner=request.user).get(name__iexact=name)

                    if plugin.slug == slug:
                        success = True

                except Plugin.DoesNotExist:
                    success = True

            response = Response({'success': success}, status=status.HTTP_200_OK)

        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response

############################################################
##### Logical Deletes a plugin dependency - Web service
############################################################
class DeleteDepView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kw):

        if request.user.is_authenticated():
            success=False

            filename = request.POST.get('filename', None)
            pluginversion = int(request.POST.get('pluginversion', None))

            if filename != None and pluginversion != None:
                try:
                    pluginversion = PluginVersion.objects.get(id=pluginversion)

                    try:
                        file_versions = VersionDep.objects\
                            .filter(pluginversion=pluginversion,
                                    filename=filename
                            )

                        for version in file_versions:
                            version.removed=True
                            version.save()

                        success=True

                    except VersionDep.DoesNotExist:
                        success = False

                except PluginVersion.DoesNotExist:
                    success=False

            response = Response({'success': success}, status=status.HTTP_200_OK)

        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response
