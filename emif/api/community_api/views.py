import django_filters

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from community.models import Community, CommunityFields, CommunityGroup, CommunityUser
from api.community_api import serializers
from api.questionnaire_api.serializers import QuestionSerializer, QuestionnaireSerializer


class CommunityAPIPermission(BasePermission):
    message = "You are not allowed to this community's API"

    def has_object_permission(self, request, view, obj):
        user = request.user
        cu = obj.belongs(user=request.user)
        if cu is None:
            return False
        
        return CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, obj, cu)\
            or CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, obj, cu)\
            or obj.is_owner(user)

class CommunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Community.objects.all()
    serializer_class = serializers.CommunitySerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend,)
    search_fields = ('name',)
    filter_fields = ('name',)
    lookup_field = "name"
    permission_classes = (IsAuthenticated, CommunityAPIPermission,)

class CommunitySettingsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community_slug, questionnaire_slug):
        user = request.user
        if not user.is_authenticated():
            return Response({}, status=status.HTTP_403_FORBIDDEN)
    
        # get community
        try:
            comm = Community.objects.get(slug=community_slug)
        except Community.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if user belongs to this community
        cu = comm.belongs(user=request.user)
        if cu is None:
            return  Response({}, status=status.HTTP_403_FORBIDDEN)

        cu = CommunityUser.objects.get(user=user, community=comm)
        if CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu)\
            or CommunityGroup.verify_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, comm, cu)\
            or comm.is_owner(user):
            # question sets 
            questionnaire = comm.questionnaires.filter(slug=questionnaire_slug).first()
            if questionnaire is None:
                return  Response({}, status=status.HTTP_403_FORBIDDEN)              

            # possible fields
            possible_fields = questionnaire.questions().filter(type__in = ['open', 'open-validated', 'email', 'url', 'open-textfield',
                    'open-button', 'open-location', 'numeric', 'datepicker', 'location', 'choice-multiple', 'choice', 'choice-yesno']).exclude(slug_fk__slug1='database_name')
                

            # comm fields
            comm_fields = CommunityFields.objects.filter(community=comm, questionnaire=questionnaire).order_by('sortid')

            # comm permissions
            comm_permissions = comm.get_permissions()
            
            return  Response({ 
                    'result': 
                        {
                            'questionnaire': QuestionnaireSerializer(questionnaire).data,
                            'possible_fields': QuestionSerializer(possible_fields, many=True).data,
                            'comm_permissions': serializers.CommunityPermissionsSerializer(comm_permissions).data,
                            'comm_fields': serializers.CommunityFieldsSerializer(comm_fields, many=True).data,
                            'comm': serializers.CommunitySerializer(comm).data
                        }
                }, status=status.HTTP_200_OK)
                
        return  Response({}, status=status.HTTP_403_FORBIDDEN)


    def post(self, request, community):
        pass
    

class CommunityQuestionnairesView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, community_slug):
        user = request.user
        if not user.is_authenticated():
            return Response({}, status=status.HTTP_403_FORBIDDEN)
    
        # get community
        try:
            comm = Community.objects.get(slug=community_slug)
        except Community.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        # check if user belongs to this community
        cu = comm.belongs(user=request.user)
        if cu is None:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

        questionnaires = comm.questionnaires.all()

        return Response(
            {
                'result': QuestionnaireSerializer(questionnaires, many=True, context={'community': comm}).data
            },
            status=status.HTTP_200_OK
        )
                


    def post(self, request, community):
        pass
