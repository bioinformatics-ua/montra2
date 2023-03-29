import re

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers

from fingerprint.models import Fingerprint, Question, Answer


class FingerprintSerializer(serializers.ModelSerializer):
    database_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Fingerprint
        exclude = ['id']
        read_only_fields = ['fingerprint_hash', 'last_modification', 'created', 'hits', 'removed', 'fill', 'owner', 'shared']

    def get_database_name(self, obj):
        return obj.findName()


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    class Meta:
        model = Answer
        fields = ['question', 'data']

    def validate_data(self, value):
        question = self.instance.question
        method = getattr(self,
                         'type_{}'.format(question.type.replace('-', '_')),
                         None)
        if method is None:
            raise serializers.ValidationError('Unsupported question type')
        method(value)
        return value

    def type_comment(self, value):
        pass

    def type_email(self, value):
        if not re.match(r'.+@.+\..+', value):
            raise serializers.ValidationError('Invalid email')

    def type_numeric(self, value):
        try:
            float(value)
        except ValueError:
            raise serializers.ValidationError('Value must be numeric')

    def type_choice(self, value):
        pass

    def type_choice_multiple(self, value):
        if not re.match(r"[\w\d\s\-]+#?", value):
            raise serializers.ValidationError('Invalid multiple choice answer. Should be separated by \'#\' if multiple (example: Option A#Option B')

    def type_choice_multiple_freeform(self,value):
        if not re.match(r"([\w\d\s\-_]+#?)+(\|\|[\w\d\s\-_]+)?", value):
            raise serializers.ValidationError('Invalid multiple choice freeform answer. Should be separated by \'#\' if multiple (example: Option A#Option B||freeform answer')

    def type_open(self, value):
        pass

    def type_open_button(self, value):
        pass

    def type_open_textfield(self, value):
        pass

    def type_url(self, value):
        validate = URLValidator()
        try:
            validate(value)
        except ValidationError:
            raise serializers.ValidationError('Invalid url')
