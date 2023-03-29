from rest_framework import serializers

from questionnaire.models import Questionnaire, Question, QuestionSet
from fingerprint.models import Fingerprint
from emif.utils import removehs
from api.fingerprint_api.serializers import FingerprintSerializer
from django.db.models import Q

class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    
    def get_text(self, obj):
        return removehs(obj.text)

    class Meta:
        model = Question
        fields = ['text', 'id', 'type', 'number', 'show_advanced']

class QuestionsetSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    text = serializers.SerializerMethodField()
    
    def get_text(self, obj):
        return removehs(obj.text)

    class Meta:
        model = QuestionSet
        fields = ['id', 'sortid', 'text', 'questions']

class QuestionnaireSerializer(serializers.ModelSerializer):   
    fingerprint_set = serializers.SerializerMethodField(required=False, read_only=True)
    questionsets = QuestionsetSerializer(many=True)

    def get_fingerprint_set(self, questionnaire):
        
        query = Q(questionnaire=questionnaire, removed=False)

        request = self.context.get('request', None)
        if request:
            query.add(Q(owner=request.user), Q.AND)    

        community = self.context.get('community', None)
        if community:
            query.add(Q(community=community), Q.AND)
        
        fingerprints = Fingerprint.objects.filter(query)

        return FingerprintSerializer(fingerprints, many=True).data

    class Meta:
        model = Questionnaire
        fields = ['id', 'name', 'slug', 'fingerprint_set', 'questionsets', 'short_description', 'long_description', 'logo']

