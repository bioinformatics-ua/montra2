import datetime
import uuid

from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import PermissionDenied, ValidationError

from fingerprint.models import Answer, Fingerprint
from community.models import CommunityUser, CommunityGroup, Community
from api.fingerprint_api import serializers

class FingerprintAPIPermission(BasePermission):
    message = "You are not allowed to this community's API"

    def has_object_permission(self, request, view, obj):
        user = request.user
        comm = obj.community

        user_belongs = comm.belongs(user=request.user)
        if not user_belongs:
            return False

        cu = CommunityUser.objects.filter(community=comm, user=user)[0]
  
        return CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu)\
            or CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu)\
            or comm.is_owner(user)

class AnswerAPIPermission(BasePermission):
    message = "You are not allowed to this community's API"

    def has_object_permission(self, request, view, obj):
        user = request.user
        comm = obj.fingerprint_id.community
        user_belongs = comm.belongs(user=request.user)
        if not user_belongs:
            return False

        cu = CommunityUser.objects.filter(community=comm, user=user)[0]
        
        return CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu)\
            or CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu)\
            or comm.is_owner(user)

class FingerprintViewSet(viewsets.ModelViewSet):
    queryset = Fingerprint.objects.filter(removed=False)
    serializer_class = serializers.FingerprintSerializer
    lookup_field = 'fingerprint_hash'
    permission_classes = (IsAuthenticated, FingerprintAPIPermission, )

    def get_queryset(self):
        user = self.request.user

        #Get communities in which he's a user
        comm_users = CommunityUser.objects.filter(user=user)
        query = Q()

        for cu in comm_users:
            comm = cu.community
            
            # Check if user is a manager or an owner
            if CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu) or comm.is_owner(user):
                #If so he has access to all fingerprints that are not deleted
                query |= Q(removed=False, community__name=comm.name)

            # Check if the user has access to the API
            elif CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu):
                
                # Check if user is an editor
                if CommunityGroup.verify_pre_existing_group(CommunityGroup.EDITORS_GROUP, comm, cu):
                    #Then he has access only to the ones he created or with a draft to False
                    query |= Q(removed=False, community__name=comm.name, draft=False)
                    query |= Q(removed=False, community__name=comm.name, owner=user)
                
                # Check if user is a default user
                if CommunityGroup.verify_pre_existing_group(CommunityGroup.DEFAULT_GROUP, comm, cu):
                    #He will only have access to the ones with draft to false
                    query |= Q(removed=False, community__name=comm, draft=False)

        return Fingerprint.objects.filter(query)

    def post(self, request, *args, **kwargs):
        try:
             return super(FingerprintViewSet, self).post(request, *args, **kwargs)
        except ValidationError as e:
             return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except DuplicatedDatabaseNameError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response(e, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            raise Exception(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # TODO: This ought to be solved using model default field values and
        # django's signals.
        user = self.request.user
        database_name = self.request.data.get('database_name', None)
        questionnaire = serializer.validated_data['questionnaire']
        community = serializer.validated_data['community']

        comm = Community.objects.filter(name=community)[0]
        comm_user = CommunityUser.objects.filter(user__username=user, community__name=community)[0]

        if not CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, comm_user)\
            or not comm.is_owner(comm_user):
            raise PermissionDenied(detail="You are not allowed to create a new database in this community")

        if not CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, comm_user)\
            or not CommunityGroup.verify_pre_existing_group(CommunityGroup.EDITORS_GROUP, comm, comm_user):
            raise PermissionDenied(detail="You are not allowed to create a new database in this community")

        fingerprint_hash = uuid.uuid4().hex
        # Verify if database_name already exists for this questionnaire in this community 
        databaseNameAnswers = Answer.objects.filter(question__slug='database_name', 
                                                    data=database_name,
                                                    fingerprint_id__removed=False,
                                                    fingerprint_id__community=community, 
                                                    fingerprint_id__questionnaire=questionnaire)
        if len(databaseNameAnswers) != 0:
            raise DuplicatedDatabaseNameError

        fingerprint = serializer.save(
            fingerprint_hash=fingerprint_hash,
            # This is actually required or the fingerprint can not be indexed.
            last_modification=timezone.now(),
            owner=user)

        
        # database_name should belong to fingerprint model! This is just
        # a workarround and should be replaced by the code commented bellow
        # when the fingerprint model is fixed.
        answers = []
        for question in questionnaire.questions():
            answer = Answer(question=question, data='', fingerprint_id=fingerprint)
            if question.slug == 'database_name' and database_name:
                answer.data = database_name
            answers.append(answer)

        # answers = [Answer(question=question,
        #                   data='',
        #                   fingerprint_id=fingerprint)
        #            for question in questionnaire.questions()]
        Answer.objects.bulk_create(answers)

        fingerprint.updateFillPercentage()  
        fingerprint.indexFingerprint()
    
    def update(self, request, *args, **kwargs):


        obj = self.get_object()
        data = request.data
        previous_mutable = data._mutable
        data._mutable = True
        data.update({"community": obj.community.pk})
        data._mutable = previous_mutable
        try:
            return super(FingerprintViewSet, self).update(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response(e.detail, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):

        user = self.request.user
        community = serializer.validated_data['community']

        comm = Community.objects.filter(name=community)[0]
        comm_user = CommunityUser.objects.filter(user__username=user, community__name=community)[0]

        if self.get_object().owner != user\
            and not CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, comm_user)\
            and not comm.is_owner(comm_user):
            raise PermissionDenied(detail="You do not have the premissions necessary to perform this update")
        fingerprint = serializer.save()
        #index fingerprint into solr
        fingerprint.indexFingerprint()


class FingerprintView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kw):
        if True: #request.user.is_authenticated():
            com_slug = kw["community_slug"]
            db_name = kw["db_name"]

            try:
                an = Answer.objects.filter(fingerprint_id__community__slug=com_slug, question__slug_fk__slug1="database_name", data=db_name)
                fingerprint = an[0].fingerprint_id
                response = Response(serializers.FingerprintSerializer(fingerprint).data, status=status.HTTP_200_OK)
            except IndexError:
                response = Response({}, status=status.HTTP_404_NOT_FOUND)
        else:
            response = Response({}, status=status.HTTP_403_FORBIDDEN)
        return response


class AnswerViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin):
    serializer_class = serializers.AnswerSerializer
    lookup_field = 'question__slug'
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        fingerprint_hash = self.kwargs['fingerprint_fingerprint_hash']
        fingerprint = Fingerprint.objects.filter(fingerprint_hash=fingerprint_hash)[0]
        comm = fingerprint.community
        user = self.request.user

        cu = CommunityUser.objects.get(community=comm, user=user)

        # Check if user is a manager or an owner
        if CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu) or comm.is_owner(user):
            return Answer.objects.filter(
                fingerprint_id__fingerprint_hash=fingerprint_hash, fingerprint_id__removed=False)
       
        # Check if the user has access to the API
        elif CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu):
            
            # Check if user is an editor
            if CommunityGroup.verify_pre_existing_group(CommunityGroup.EDITORS_GROUP, comm, cu):
                #Then he has access only to the ones he created or with a draft to False
                return Answer.objects.filter(
                    Q(fingerprint_id__fingerprint_hash=fingerprint_hash, fingerprint_id__removed=False, fingerprint_id__draft=False) \
                    | Q(fingerprint_id__fingerprint_hash=fingerprint_hash, fingerprint_id__removed=False, fingerprint_id__owner=user))
            
            # Check if user is a default user
            if CommunityGroup.verify_pre_existing_group(CommunityGroup.DEFAULT_GROUP, comm, cu):
                return Answer.objects.filter(
                    Q(fingerprint_id__fingerprint_hash=fingerprint_hash, fingerprint_id__removed=False, fingerprint_id__draft=False) )
                
        return Answer.objects.none()
            

    def perform_update(self, serializer):
        fingerprint_hash = self.kwargs['fingerprint_fingerprint_hash']
        fingerprint = Fingerprint.objects.filter(fingerprint_hash=fingerprint_hash)[0]
        comm = fingerprint.community
        user = self.request.user

        cu = CommunityUser.objects.get(community=comm, user=user)

        if fingerprint.owner != user\
            and not CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu)\
            and not comm.is_owner(cu):
            raise PermissionDenied(detail="You do not have the premissions necessary to perform this update")

        serializer.save()
        serializer.instance.fingerprint_id.updateFillPercentage()
        serializer.instance.fingerprint_id.indexFingerprint()

class DuplicatedDatabaseNameError(Exception):
    ''' Raised when the database name exists on same community and questionnaire '''
    pass

