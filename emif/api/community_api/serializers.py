from rest_framework import serializers

from community.models import Community, CommunityPermissions, CommunityFields
from questionnaire.models import Questionnaire
from api.questionnaire_api.serializers import QuestionnaireSerializer, QuestionSerializer


class CommunitySerializer(serializers.ModelSerializer):
    questionnaires = QuestionnaireSerializer(many=True)

    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'slug', 'questionnaires', 'dblist_sortid']


class CommunityPermissionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommunityPermissions
        fields = ['export_dblist', 'export_fingerprint', 'export_datatable']

class CommunityFieldsSerializer(serializers.ModelSerializer):
    field = QuestionSerializer()

    class Meta:
        model = CommunityFields
        fields = ['section', 'show_label', 'apply_formatting', 'icon', 'view', 'sortid', 'community', 'field']


