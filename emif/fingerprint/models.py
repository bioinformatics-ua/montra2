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
import logging

from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from newsletter.models import Newsletter, Subscription

from questionnaire.models import Question, QuestionSet, QuestionSetPermissions, Questionnaire, fileHash
from searchengine.search_indexes import CoreEngine, generateFreeText, generateMltText, setProperFields

logger = logging.getLogger(__name__)


class Database:
    id = ''
    name = ''
    date = ''
    date_modification = ''
    institution = ''
    location = ''
    email_contact = ''
    number_patients = ''
    ttype = ''
    type_name = ''
    logo = ''
    last_activity = ''

    admin_name = ''
    admin_address = ''
    admin_email = ''
    admin_phone = ''

    scien_name = ''
    scien_address = ''
    scien_email = ''
    scien_phone = ''

    tec_name = ''
    tec_address = ''
    tec_email = ''
    tec_phone = ''

    percentage = 0

    communities = []

    fields = {}

    draft = ''

    score = ''

    def __eq__(self, other):
        return other.id == self.id

    def __str__(self):
        print id

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'draft': self.draft,
            'fields': self.fields,
            'institution': self.institution,
            'last_activity': self.last_activity,
            'location': self.location,
            'name': self.name,
            'number_patients': self.number_patients,
            'percentage': self.percentage,
            'score': self.score,
            'type_name': self.type_name,
        }


class FingerprintManager(models.Manager):
    def valid(self, questionnaire=None, owner=None, include_drafts=False, community=None):
        tmp = self.get_queryset().filter(removed=False)
        if questionnaire is not None:
            tmp = tmp.filter(questionnaire=questionnaire)

        if owner is not None:
            tmp = tmp.filter(Q(owner=owner) | Q(shared=owner))

        if community is not None:
            tmp = tmp.filter(community=community)

        if not include_drafts:
            tmp = tmp.filter(draft=False)

        return tmp


class Fingerprint(models.Model):
    fingerprint_hash =  models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(blank=True, null=True, validators=[MaxLengthValidator(600)])
    questionnaire = models.ForeignKey(Questionnaire, null=True)

    community = models.ForeignKey('community.Community', null=True)

    last_modification = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    owner = models.ForeignKey(User, related_name="fingerprint_owner_fk")
    shared = models.ManyToManyField(User, related_name="fingerprint_shared_fk")
    hits = models.IntegerField(default=0, help_text="Hit count for this fingerprint")
    removed = models.BooleanField(default=False, help_text="Remove logically the fingerprint")

    fill = models.FloatField(default=0, help_text="Database Questionset")

    draft = models.BooleanField(default=True)

    objects = FingerprintManager()

    def __unicode__(self):
        return self.fingerprint_hash

    def __len__(self):
        return Answer.objects.filter(fingerprint_id=self.id).count()

    def __getitem__(self, key):
        #answers = self.get_answers()
        a = None
        try:
            a = Answer.objects.filter(fingerprint_id=self.id, next_answer__isnull=True).filter(question__slug_fk__slug1=key).get()
        except Exception, e:
            raise IndexError

        if a == None:
            raise KeyError
        return a

    ''' This breaks django-rest-framework serialization.
        In all true, a fingerprint iterator shouldnt iterate
        the answers at all, at least that is my opinion

    def __iter__(self):
        #answers = self.get_answers()
        anss = Answer.objects.filter(fingerprint_id=self.id).all()
        for a in anss:
            yield a
    '''

    def keys(self):
        keys = Answer.objects.filter(fingerprint_id=self.id, next_answer__isnull=True).all().values_list("question__slug_fk__slug1", flat=True)
        return keys

    def iterkeys(self):
        for x in keys:
            yield x

    def __contains__(self, key):
        try:
            a = Answer.objects.filter(fingerprint_id=self.id, next_answer__isnull=True).filter(question__slug_fk__slug1=key).get()
        except Exception, e:
            return False
        return a != None

    def setSubscription(self, user, value):

        try:
            subscription = FingerprintSubscription.objects.get(user = user, fingerprint = self)
            subscription.removed = not value
            subscription.save()

        except FingerprintSubscription.DoesNotExist:


            # we dont create in case its false it doesnt exist, pointless work
            if value:
                subscription = FingerprintSubscription(user = user, fingerprint = self)
                subscription.save()

    def findName(self):
        name = ""
        try:
            name_ans = Answer.objects.get(question__slug_fk__slug1='database_name', fingerprint_id=self, next_answer__isnull=True)

            name = name_ans.data

        except Answer.DoesNotExist:
            name ="Unnamed"

        return name

    def updateFillFromCache(self):
        qsets = QuestionSetCompletion.objects.filter(fingerprint=self)

        total = 0
        count = 0

        for qset in qsets:
            total+=qset.fill
            count+=1

        total_fill = 0
        try:
            total_fill = (total/count)
        except ZeroDivisionError:
            pass

        self.fill = total_fill
        self.save()


    def updateFillPercentage(self, reset=False):
        # remove old values

        if reset:
            QuestionSetCompletion.objects.filter(fingerprint=self).delete()

        answers = Answer.objects.filter(fingerprint_id = self, next_answer__isnull=True)

        qsets = self.questionnaire.questionsets()
        for qset in qsets:
            (partial, answered, possible) = qset.findDependantPercentage(answers)

            QuestionSetCompletion.create_or_update(self, qset, partial, answered, possible)

        self.updateFillFromCache()

    # return fingerprint database owners (aka who created the entry and who the entry was shared with)
    def unique_users(self):
        users = set()

        users.add(self.owner)

        for share in self.shared.all():
            users.add(share)

        return users

    def unique_users_string(self):
        users = set()
        users.add(self.owner.username)
        for share in self.shared.all():
            users.add(share.username)

        users = list(users)
        users_string = users[0]

        for i in xrange(1, len(users)):
            users_string+= ' \\ ' + users[i]

        return users_string

    # GET permissions model
    def getPermissions(self, question_set):
        if question_set is None:
            return None

        permissions = QuestionSetPermissions.objects.filter(fingerprint=self, qs=question_set)
        if not permissions.exists():
            return QuestionSetPermissions.objects.create(fingerprint=self, qs=question_set)
        return permissions.get()


    @staticmethod
    def getActiveFingerprints(questionnaire_id):
        return Fingerprint.objects.filter(questionnaire=questionnaire_id, removed=False)

    def answers(self, restriction=None):
        answers = Answer.objects.filter(fingerprint_id=self).order_by('question__number')

        if restriction:
            # if the owner is the user looking at the request, we dont have any restrictions
            if restriction in self.unique_users():
                return answers

            pqs = QuestionSetPermissions \
                .objects.filter(fingerprint=self, visibility=QuestionSetPermissions.VISIBILITY_PUBLIC) \
                .values_list('qs__id', flat=True)

            answers = answers.filter(question__questionset__id__in = pqs)

        return answers

    def indexFingerprint(self, batch_mode=False):
        if hasattr(self, 'preview_questionnaire'):
            return

        def is_if_yes_no(question):
            return question.type in 'choice-yesno' or \
                    question.type in 'choice-yesnocomment' or \
                    question.type in 'choice-yesnodontknow'

        d = {}
        # Get parameters that are only on fingerprint
        # type_t
        d['id']=self.fingerprint_hash
        d['type_t'] = self.questionnaire.slug
        d['date_last_modification_dt'] = self.last_modification.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        d['created_dt'] = self.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        d['user_t'] = self.unique_users_string()
        d['percentage_d'] = self.fill

        comm_slug = ''
        if self.community != None:
            comm_slug = self.community.slug

        d['communities_t'] = comm_slug
        d['draft_t'] = '%s' % self.draft

        # Add answers
        answers = Answer.objects.filter(fingerprint_id=self)

        additional_text = []
        question_txt = []
        for answer in answers:
            question = answer.question

            # We try to get permissions preferences for this question
            permissions = self.getPermissions(question.questionset)

            slug = question.slug_fk.slug1
            if permissions.allow_indexing or slug == 'database_name':

                question_txt.append(question.text)

                setProperFields(d, question, slug, answer.data)
                if is_if_yes_no(question) and 'yes' in answer.data:
                    additional_text.append(question.text)
                elif question.type == "publication" and slug + "_txt" in d:
                    additional_text.extend(d[slug + "_txt"])

                if answer.comment is not None:
                    d['comment_question_'+slug+'_t'] = answer.comment

        d['text_txt'] = generateFreeText(d) + additional_text

        d['text'] = d['text_txt']
        d['mlt_t'] = generateMltText(d)
        d['questions_txt'] = question_txt + additional_text
        logger.info("Indexing Fingerprint..")

        d['all_txt'] = d['text_txt'] + question_txt
        # for facets
        d['text_en'] = d['all_txt']

        if batch_mode:
            return d
        else:
            print "-- Indexing unique fingerprint hash "+str(self.fingerprint_hash)
            c = CoreEngine()

            results = c.search_fingerprint("id:"+self.fingerprint_hash)
            if len(results) == 1:
                # Delete old entry if any
                c.delete(results.docs[0]['id'])

            c.index_fingerprint_as_json(d)


class FingerprintPending(models.Model):
    """
    If a record of this models exists, the associated fingerprint is pending.
    To check that the following could be executed `hasattr(fingerprint, "fingerprintpending")`
    """
    fingerprint = models.OneToOneField(Fingerprint, primary_key=True)


class Answer(models.Model):
    """
    Answer of the Fingerprint
    """

    question        = models.ForeignKey(Question)
    data            = models.TextField() # Structure question
    comment         = models.TextField(null=True) # Comment
    fingerprint_id  = models.ForeignKey(Fingerprint)

    date_of_capture = models.DateTimeField(auto_now_add=True, null=True)
    previous_answer = models.ForeignKey('Answer', related_name='prev_ans', null=True)
    next_answer     = models.ForeignKey('Answer', related_name='next_ans', null=True)

    def get_slug():
        return question.slug_fk.slug1

    def __str__(self):
        return "ANSWER{id="+str(self.id)+", question_slug="+self.question.slug_fk.slug1+", data="+self.data+", comment="+str(self.comment)+"}"



'''
    Fingerprint answers tracked change - a simple revision system

        Each time a already existing fingerprint has answers modified, there's a new object
        from this model, and one answer change for each answer change
'''
class FingerprintHead(models.Model):
    fingerprint_id = models.ForeignKey(Fingerprint)
    revision       = models.IntegerField()
    date           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "FINGERPRINT_ID:"+str(self.fingerprint_id)+" REVISION: "+str(self.revision) + " DATE: "+ str(self.date)

    def changes(self):
        return AnswerChange.objects.filter(revision_head=self)

    @staticmethod
    def mergeChanges(fingerprintheads):
        answermap = {}
        for head in fingerprintheads.order_by('date'):
            for change in head.changes():
                answermap[change.answer] = change

        return answermap.values()



class AnswerChange(models.Model):
    revision_head = models.ForeignKey(FingerprintHead)
    answer        = models.ForeignKey(Answer)
    old_value     = models.TextField(null=True)
    new_value     = models.TextField(null=True)
    old_comment   = models.TextField(null=True)
    new_comment   = models.TextField(null=True)

    def __str__(self):
        return "QUESTION: "+str(self.answer.question.number)

''' The idea is showing the number of times the db is returned over time
'''
class FingerprintReturnedSimple(models.Model):
    fingerprint = models.ForeignKey(Fingerprint)
    searcher    = models.ForeignKey(User)
    date        = models.DateTimeField(auto_now_add=True)
    query_reference = models.ForeignKey('emif.QueryLog')

class FingerprintReturnedAdvanced(models.Model):
    fingerprint = models.ForeignKey(Fingerprint)
    searcher    = models.ForeignKey(User)
    date        = models.DateTimeField(auto_now_add=True)
    query_reference = models.ForeignKey('emif.AdvancedQuery')

class AnswerRequest(models.Model):
    fingerprint = models.ForeignKey(Fingerprint)
    question    = models.ForeignKey(Question)
    requester   = models.ForeignKey(User)
    date        = models.DateTimeField(auto_now=True)
    comment     = models.CharField(max_length=1000, default='')
    removed     = models.BooleanField(default=False)

"""
This class wraps the Description of the Fingerprint.
It will be used to list fingerprints, for instance.
It is useful to centralized the code.
Developed in first EMIF Hackthon.
"""
class FingerprintDescriptor(object):
    static_attr = ["id", "date", "date_modification", "last_activity", "ttype", "type_name"]
    slug_dict = {"name":"database_name",
                    "institution" : 'institution_name',
                    "email_contact" : 'contact_administrative',
                    "number_patients" : 'number_active_patients_jan2012',
                    "logo" : 'upload-image',
            }
    observational_spec = {
        "admin_name" : 'institution_name',
        "admin_address" : 'Administrative_contact_address',
        "admin_email" : 'Administrative_contact_email',
        "admin_phone" : 'Administrative_contact_phone',

        "scien_name" : 'Scientific_contact_name',
        "scien_address" : 'Scientific_contact_address',
        "scien_email" : 'Scientific_contact_email',
        "scien_phone" : 'Scientific_contact_phone',

        "tec_name" : 'Technical_contact_/_data_manager_contact_name',
        "tec_address" : 'Technical_contact_/_data_manager_contact_address',
        "tec_email" : 'Technical_contact_/_data_manager_contact_email',
        "tec_phone" : 'Technical_contact_/_data_manager_contact_phone',
    }
    ad_spec = {
        "admin_name" : 'Administrative_Contact__AC___Name',
        "admin_address" : 'AC__Address',
        "admin_email" : 'AC__email',
        "admin_phone" : 'AC__phone',

        "scien_name" : 'Scientific_Contact__SC___Name',
        "scien_address" : 'SC__Address',
        "scien_email" : 'SC__email',
        "scien_phone" : 'SC__phone',

        "tec_name" : 'Technical_Contact_Data_manager__TC___Name',
        "tec_address" : 'TC__Address',
        "tec_email" : 'TC__email',
        "tec_phone" : 'TC__phone',
    }

    spec = ["location"]
    def __init__(self, fingerprint):
        self.obj = fingerprint

    def __getattr__(self, name):
        try:
            #print name
            if name in self.static_attr:
                return self.parse_static_args(name)
            elif name in self.slug_dict:
                return self.obj[self.slug_dict[name]].data
            elif name in self.spec:
                return self.parse_specific(name).data
            elif name in self.observational_spec:
                return self.parse_type_spec(name).data
        except Exception, e:
            pass
        return ""

    def parse_type_spec(self, name):
        if self.type_name == "Observational Data Sources":
            return self.obj[self.observational_spec[name]]
        elif "AD Cohort" in self.type_name:
            return self.obj[self.ad_spec[name]]
    def parse_static_args(self,name):
        print "FOUND STATIC ARG"
        if name == "id":
            print "FOUND ID"
            return self.obj.fingerprint_hash

        if name == "date":
            return self.obj.created

        if name == "date_last_modification" or name == "last_activity":
            return self.obj.last_modification

        if name == "ttype":
            return self.obj.questionnaire.slug

        if name == "type_name":
            return self.obj.questionnaire.name

    def parse_specific(self,name):
        if name == "location":
            if "city" in self.obj:
                return self.obj['city']
            if "location" in self.obj:
                return self.obj['location']
            if "PI:_Address" in self.obj:
                return self.obj['PI:_Address']

class QuestionSetCompletion(models.Model):
    fingerprint     = models.ForeignKey(Fingerprint)
    questionset     = models.ForeignKey(QuestionSet)
    latest_update   = models.DateTimeField(auto_now=True)
    fill            = models.FloatField(default=0)
    answered        = models.IntegerField(default=0)
    possible        = models.IntegerField(default=0)

    @staticmethod
    def create_or_update(fingerprint, questionset, fill, answered, possible):
        qcompletion = None
        try:
            qcompletion = QuestionSetCompletion.objects.get(fingerprint=fingerprint, questionset=questionset)
            qcompletion.fill = fill
            qcompletion.answered = answered
            qcompletion.possible = possible

            qcompletion.save()

        except QuestionSetCompletion.DoesNotExist:
            qcompletion = QuestionSetCompletion(fingerprint=fingerprint, questionset=questionset, fill=fill, answered=answered, possible=possible)
            qcompletion.save()

        return qcompletion

class FingerprintSubscription(models.Model):
    fingerprint     = models.ForeignKey(Fingerprint)
    user            = models.ForeignKey(User)
    date            = models.DateTimeField(auto_now_add=True)
    latest_update   = models.DateTimeField(auto_now=True)
    removed         = models.BooleanField(default=False)

    @staticmethod
    def active():
        return FingerprintSubscription.objects.filter(removed=False)

    def isSubscribed(self):
        return not self.removed

    def getNewsletter(self):
        newsl = None


        try:
            newsl = Newsletter.objects.get(slug=self.fingerprint.fingerprint_hash)

        except Newsletter.DoesNotExist:

            newsl, created = Newsletter.objects.get_or_create( title=self.fingerprint.findName()+' Updates',
                            slug=self.fingerprint.fingerprint_hash,
                            email=settings.DEFAULT_FROM_EMAIL,
                            message_template=EmailTemplate.objects.get(subject='aggregate'),
                            sender=config.brand)
        return newsl

    def setNewsletterSubs(self, new_status):
        newsl = self.getNewsletter()

        newsl_sub = None
        try:
            newsl_sub = Subscription.objects.get(user=self.user,  newsletter=newsl)
        except Subscription.DoesNotExist:
            newsl_sub = Subscription(user=self.user, newsletter = newsl)

        if(new_status):
            newsl_sub.update('subscribe')
        else:
            newsl_sub.update('unsubscribe')

        newsl_sub.save()


class FingerprintImportFile(models.Model):
    START = 0
    PROCESSING = 1
    FINISHED = 2

    STATUS_TYPES = (
        (START, 'Fingerprint import started'),
        (PROCESSING, 'Fingerprint is being imported'),
        (FINISHED, 'Fingerprint finished importing')
    )

    file = models.FileField(upload_to=fileHash, null=True, blank=True)
    filename = models.CharField(max_length=3000, blank=True, null=True)
    uploader = models.ForeignKey(User)
    status = models.IntegerField(default=START, choices=STATUS_TYPES)

    def get_status(self):
        if self.status == FingerprintImportFile.START:
            return 'Waiting to start'
        elif self.status == FingerprintImportFile.PROCESSING:
            return 'Processing'
        elif self.status == FingerprintImportFile.FINISHED:
            return 'Finished'

        return 'Error'
