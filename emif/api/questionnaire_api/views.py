from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from questionnaire.models import Questionnaire
from api.questionnaire_api import serializers


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = serializers.QuestionnaireSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', 'slug')
    lookup_field = "slug"
    permission_classes = (IsAuthenticated,)
