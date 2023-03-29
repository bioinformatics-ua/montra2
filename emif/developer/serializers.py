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
from __future__ import absolute_import

from django.contrib.auth.models import Group, User
from django_comments.models import Comment
from rest_framework import serializers

from accounts.models import EmifProfile, Profile
from api.models import FingerprintAPI
from community.models import Community, CommunityFields, CommunityPlugins
from docs_manager.models import Document
from emif.utils import removehs
from fingerprint.models import Answer, Fingerprint
from questionnaire.models import Choice, Question, QuestionSet, Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):

    questions_count = serializers.SerializerMethodField()
    fingerprints_count = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ['slug','name', 'logo', 'short_description', 'questions_count', 'fingerprints_count']

    def get_questions_count(self, obj):
        return obj.qsets.count()
    
    def get_fingerprints_count(self, obj):
        c = self.context.get("community")
        if c:
            return Fingerprint.objects.filter(community=c, questionnaire=obj, removed=False).count()
        return False

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model = User
        exclude = ['id', 'password', 'username',
        'user_permissions', 'is_superuser', 'is_staff', 'is_active']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id', 'description']

class EmifProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    interests = QuestionnaireSerializer(many=True)
    profiles = ProfileSerializer(many=True)

    class Meta:
        model = EmifProfile
        exclude = ['id', 'privacy']

class FingerprintSerializer(serializers.ModelSerializer):
    questionnaire = QuestionnaireSerializer()
    owner = serializers.SerializerMethodField()
    shared = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.email

    def get_shared(self, obj):
        return obj.shared.values_list('email', 'first_name', 'last_name', 'id')

    def get_name(self, obj):
        return obj.findName()

    class Meta:
        model = Fingerprint
        exclude = ['id', 'removed', 'description']

class QuestionSerializer(serializers.ModelSerializer):
    disposition = serializers.SerializerMethodField(method_name='getDisp')
    questionset = serializers.SerializerMethodField(method_name='getQuestionset')

    def getDisp(self, obj):
        return dict(Question.DISPOSITION_TYPES)[obj.disposition]

    def getQuestionset(self, obj):
        return obj.questionset.text


    class Meta:
        model = Question
        exclude = ['id', 'checks', 'extra_en',
        'footer_en', 'slug_fk', 'stats',
        'metadata', 'mlt_ignore', 'tooltip']

class QuestionSetSerializer(serializers.ModelSerializer):
    def getQuestionset(self, obj):
        return obj.text

    class Meta:
        model = QuestionSet
        exclude = ['id', 'checks', 'extra_en', 'tooltip']

class ChoiceSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField(method_name='getQuestion')

    def getQuestion(self, obj):
        return obj.question.number

    class Meta:
        model = Choice
        exclude = ['id','sortid','text_en']

class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = Answer
        fields = ['question', 'data']

class FingerprintAPISerializer(serializers.ModelSerializer):
    pass
    class Meta:
        model = FingerprintAPI
        exclude = ['id', 'fingerprintID', 'user']

class DocumentSerializer(serializers.ModelSerializer):
    pass
    class Meta:
        model = Document
        exclude = ['id', 'fingerprint_id', 'removed']

class CommentSerializer(serializers.ModelSerializer):
    submit_date = serializers.SerializerMethodField(method_name='getDate')

    def getDate(self, obj):
        return obj.submit_date.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'user_email', 'comment', 'submit_date']

class CommunityPluginSerializer(serializers.ModelSerializer):
    plugin = serializers.SerializerMethodField(method_name='getPlugin')

    def getPlugin(self, obj):
        try:
            if(obj.plugin.icon):
                return { 'name':obj.plugin.name, 'slug':obj.plugin.slug, 'icon': obj.plugin.icon, 'type':obj.plugin.type }
            return { 'name':obj.plugin.name, 'slug':obj.plugin.slug, 'icon': "", 'type':obj.plugin.type }
        except:
            return { 'name':obj.plugin.name, 'slug':obj.plugin.slug, 'icon': "", 'type':obj.plugin.type }

    class Meta:
        model = CommunityPlugins
        fields = ['plugin', 'community', 'sortid']

class CommunitySerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField(method_name='getIcon')
    thumbnail = serializers.SerializerMethodField(method_name='getThumbnail')
    def getIcon(self, obj):
        if(obj.icon):
            return str(obj.icon.name)
        else:
            return ""
    def getThumbnail(self, obj):
        if(obj.thumbnail):
            return str(obj.thumbnail.name)
        else:
            return str(obj.icon.name)
    class Meta:
        model = Community
        fields = ['name','slug','icon', 'thumbnail', 'dblist_sortid']


class CommunityFieldsSerializer(serializers.ModelSerializer):
    field = serializers.SerializerMethodField()
    community = serializers.SerializerMethodField()
    sortid = serializers.SerializerMethodField()

    def get_field(self, obj):
        return {
                'slug': obj.field.slug,
                'text': removehs(obj.field.text), 
                'type': obj.field.type  
            }

    def get_community(self, obj):
        return {
            'slug': obj.community.slug,
            'dblist_sortid': obj.community.dblist_sortid
        }

    def get_sortid(self, obj):
        return obj.sortid

    class Meta:
        model = CommunityFields
        fields = ['field','community','sortid']
