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
import json
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from transmeta import TransMeta

from parsers import ParseException, parse_checks
from questionnaire import QuestionChoices
from searchengine.models import Slugs
from utils import split_numal


def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

_numre = re.compile("(\d+)([a-z]+)", re.I)

class DepQuestion:
    answers = {}
    def __init__(self):
        self.answers = {}

    def add_answer(self, answer, number):
        if answer not in self.answers:
            self.answers[answer] = [number]
        else:
            self.answers[answer].append(number)

    def lengths(self):
        lengths = {}

        for key in self.answers:
            lengths[key] = len(self.answers[key])

        return lengths

class DepList:
    dep_map = {}
    question_counts = {}

    def __separateCond(self, dep):
        depl = dep.split(',')

        if len(depl) == 2:
            return (depl[0], depl[1])

        return (None, None)

    def __init__(self, questionset):
        self.dep_map={}
        self.question_counts = {}

        questions = questionset.questions()

        for question in questions:
            if question.type != 'comment':
                dep=questionset.getDependency(question)
                if dep != None:
                    (depnumber, answer) = self.__separateCond(dep)

                    if depnumber not in self.dep_map:
                        self.dep_map[depnumber] = DepQuestion()

                    self.dep_map[depnumber].add_answer(answer, question.number)

        # must do two rounds, because i dont know the full map until i go through them all since this i cant supose dependency order
        for question in questions:
            if question.type != 'comment':
                self.question_counts[question.number] = 1

                if question.number in self.dep_map:
                    self.question_counts[question.number] = self.dep_map[question.number].lengths()

                else:
                    self.question_counts[question.number] = 1

    def get(self):
        return self.question_counts


def questionnaire_logo_directory_path(instance, filename):
    return 'questionnaire/logos/{0}/{1}'.format(instance.id, filename)

class Questionnaire(models.Model):
    name                = models.CharField(max_length=128)
    short_description   = models.CharField(max_length=128, default='', blank=True)
    long_description    = models.CharField(max_length=512, default='', blank=True)
    logo                = models.ImageField(upload_to=questionnaire_logo_directory_path, default='', blank=True)
    redirect_url        = models.CharField(max_length=128, help_text="URL to redirect to when Questionnaire is complete. Macros: $SUBJECTID, $RUNID, $LANG", default="/static/complete.html")
    slug                = models.CharField(max_length=128, unique=True)
    disable             = models.CharField(max_length=128)
    qsets               = models.ManyToManyField('QuestionSet', related_name='qs_list')
    in_preview = models.BooleanField(default=False)
    preview_fingerprint = models.OneToOneField(
        'fingerprint.Fingerprint',
        on_delete=models.SET_NULL,
        related_name='preview_questionnaire',
        null=True)

    def __unicode__(self):
        return self.name

    def questionsets(self):
        if not hasattr(self, "__qscache"):
            self.__qscache = self.qsets.all().order_by('sortid')
        return self.__qscache

    def questionsets_ids(self):
        if not hasattr(self, "__qsidscache"):
            self.__qsidscache = self.questionsets().values_list('id', flat=True)
        return self.__qsidscache

    def questions(self):
        if not hasattr(self, "__questionscache"):
            questions = Question.objects.none()

            qsets = self.questionsets()

            for qset in qsets:
                questions = questions | qset.questions()

            #self.__questionscache = sorted(questions, key=lambda x: natural_key(x.number))
            self.__questionscache = questions # sorted(questions, key=lambda x: natural_key(x.number))
            
        return self.__questionscache

    def questions_choices(self,questions):
        choices = Choice.objects.none()
        
        for quest in questions:
            choices = choices | quest.choices()
            
        return choices

    def findMandatoryQs(self):
        if not hasattr(self, "__mandatoryqscache"):
            self.__mandatoryqscache = None
            try:
                name = Question.objects.get(questionset__in=self.questionsets_ids(), slug_fk__slug1="database_name")

                self.__mandatoryqscache = name.questionset

            except Question.DoesNotExist:
                logging.error("does not exist question database_name")
        return self.__mandatoryqscache

    def get_database_field(self):
        question = self.questions().filter(slug_fk__slug1="database_name")
        if question.count() > 0:
            return question[0].text

        return None

    def copy(self):
        def __firstSlugFree(slug):
            i=2
            # if there's more than 100 copies, there's probably something wrong...
            while i < 100:
                try:
                    quest = Questionnaire.objects.get(slug=(slug+str(i)))
                except Questionnaire.DoesNotExist:
                        return str(i)
                i+=1

            return None

        clone = Questionnaire()

        clone.__dict__ = self.__dict__.copy()

        new_slug = __firstSlugFree(clone.slug)

        if new_slug != None:
            clone.id = None

            clone.slug = clone.slug+new_slug
            clone.name = clone.name+" "+new_slug
            clone.save()

            for questionset in self.questionsets():
                questionset.copy(clone)

            return clone

        else:
            logging.error("-- Can't clone questionnaire safely.")
            return None

    class Meta:
        permissions = (
            ("export", "Can export questionnaire answers"),
            ("management", "Management Tools")
        )

class QuestionSet(models.Model):
    __metaclass__ = TransMeta

    "Which questions to display on a question page"
    questionnaire = models.ForeignKey(Questionnaire)
    # TODO
    # questionnaire = models.ManyToManyField(Questionnaire)
    sortid = models.IntegerField() # used to decide which order to display in
    heading = models.CharField(max_length=255)
    checks = models.CharField(max_length=128, blank=True,
    help_text = """Current options are 'femaleonly' or 'maleonly' and shownif="QuestionNumber,Answer" which takes the same format as <tt>requiredif</tt> for questions.""")
    text = models.TextField(help_text="This is interpreted as Textile: <a href='http://hobix.com/textile/quick.html'>http://hobix.com/textile/quick.html</a>")
    help_text = models.CharField(max_length=2255, blank=True, null=True)
    tooltip = models.BooleanField(default=False, help_text="If help text appears in a tooltip")
    show_advanced = models.BooleanField(default=True, help_text='If questionset appears in advanced search')

    def questions(self):
        if not hasattr(self, "__qcache"):
            self.__qcache = Question.objects.filter(questionset=self).order_by('number')
            #self.__qcache.sort()
        return self.__qcache

    # Returns the serverside total and filled count for this questionset
    def total_count(self):
        if not hasattr(self, "__qtotal_count"):
            self.__qtotal_count = len(Question.objects.filter(questionset=self).exclude(checks__contains='dependent').order_by('number'))

        return self.__qtotal_count

    def next(self):
        qs = self.questionnaire.questionsets()
        retnext = False
        for q in qs:
            if retnext:
                return q
            if q == self:
                retnext = True
        return None

    def prev(self):
        qs = self.questionnaire.questionsets()
        last = None
        for q in qs:
            if q == self:
                return last
            last = q

    def is_last(self):
        try:
            return self.questionnaire.questionsets()[-1] == self
        except NameError:
            # should only occur if not yet saved
            return True

    def is_first(self):
        try:
            return self.questionnaire.questionsets()[0] == self
        except NameError:
            # should only occur if not yet saved
            return True
    def copy(self, questionnaire):
        clone = QuestionSet()

        clone.__dict__ = self.__dict__.copy()

        clone.id = None

        clone.save()

        for question in self.questions():
            question.copy(clone)

        return clone

    def dependency_tree(self):
        dl = DepList(self)

        return dl.get()

        if not hasattr(self, "__questionstreecache"):
            questions = self.questions()

            dl = DepList(questions)

            self.__questionstreecache = dl.get()

        return self.__questionstreecache

    def getDependency(self, question):
        checks = ""
        try:
            checks = question.checks.strip()
        except:
            pass

        # not dependant in anyone
        if len(checks) == 0:
            return None
        else:

            extra = checks.split(" ")

            for ex in extra:
                if ex.startswith('dependent="'):
                    return ex[11:-1]

            return None

    def findDependantPercentage(self, answers):
        from fingerprint.models import Answer

        ref_cache = {}
        total = 0
        filled = 0

        def __fills_condition(dep):
            depl = dep.split(',')

            if len(depl) == 2:
                answer = None
                try:
                    answer = ref_cache[depl[0]]
                except:
                    try:
                        answer = answers.get(question__number=depl[0], next_answer__isnull=True)
                        ref_cache[depl[0]] = answer

                    except Answer.DoesNotExist:
                        return False

                if depl[1].lower() == answer.data.lower():
                    return True

            return False

        def __count(total, filled, question):
            if question.type == 'comment':
                return (total, filled)

            total+=1
            try:
                ans = answers.get(question=question, next_answer__isnull=True)
                if len(ans.data.strip()) != 0:
                    filled += 1
            except Answer.DoesNotExist:
                pass

            return (total, filled)

        for question in self.questions():
            dep = self.getDependency(question)

            # has dependency
            if dep == None:
                (total, filled) = __count(total, filled, question)

            else:
                if __fills_condition(dep):
                    (total, filled) = __count(total, filled, question)

        try:
            return ((filled * 100) / total, filled, total)
        except:
            return (0,filled,total)

    def __unicode__(self):
        return u'%s: %s' % (self.questionnaire.name, self.heading)
    class Meta:
        translate = ('text',)


class QuestionSetPermissions(models.Model):
    """
    This models, keeps the permissions for a questionset, relative to a fingerprint
    """

    VISIBILITY_PUBLIC = 0
    VISIBILITY_PRIVATE = 1
    VISIBILITY_CHOICES = (
        (VISIBILITY_PUBLIC, 'public'),
        (VISIBILITY_PRIVATE, 'private')
    )

    fingerprint = models.ForeignKey("fingerprint.Fingerprint", on_delete=models.CASCADE)
    qs = models.ForeignKey(QuestionSet)
    visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=VISIBILITY_PUBLIC)
    allow_indexing = models.BooleanField(default=True)
    allow_exporting = models.BooleanField(default=True)

    class Meta:
        unique_together = ("fingerprint", "qs")


class Question(models.Model):
    __metaclass__ = TransMeta
    VERTICAL = 0
    HORIZONTAL = 1
    DROPDOWN = 2

    DISPOSITION_TYPES = (
        (VERTICAL, 'Vertical'),
        (HORIZONTAL, 'Horizontal'),
        (DROPDOWN, 'Dropdown')
    )

    questionset = models.ForeignKey(QuestionSet)
    number = models.CharField(max_length=255, help_text=
        "eg. <tt>1</tt>, <tt>2a</tt>, <tt>2b</tt>, <tt>3c</tt><br /> "
        "Number is also used for ordering questions.")
    text = models.TextField(blank=True)
    type = models.CharField(u"Type of question", max_length=32,
        choices = sorted(QuestionChoices, key=lambda t: t[0]),
        help_text = u"Determines the means of answering the question. " \
        "An open question gives the user a single-line textfield, " \
        "multiple-choice gives the user a number of choices he/she can " \
        "choose from. If a question is multiple-choice, enter the choices " \
        "this user can choose from below'.")
    extra = models.CharField(u"Extra information", max_length=128, blank=True, null=True, help_text=u"Extra information (use  on question type)")
    checks = models.CharField(u"Additional checks", max_length=128, blank=True,
        null=True, help_text="Additional checks to be performed for this "
        "value (space separated)  <br /><br />"
        "For text fields, <tt>required</tt> is a valid check.<br />"
        "For yes/no choice, <tt>required</tt>, <tt>required-yes</tt>, "
        "and <tt>required-no</tt> are valid.<br /><br />"
        "If this question is required only if another question's answer is "
        'something specific, use <tt>requiredif="QuestionNumber,Value"</tt> '
        'or <tt>requiredif="QuestionNumber,!Value"</tt> for anything but '
        "a specific value.  "
        "You may also combine tests appearing in <tt>requiredif</tt> "
        "by joining them with the words <tt>and</tt> or <tt>or</tt>, "
        'eg. <tt>requiredif="Q1,A or Q2,B"</tt>'
        " <br /><br /> If it is a location type question, "
        " reach level can be defined by typing <tt>country</tt>, <tt>adm1</tt>"
        " or <tt>adm2</tt>")
    footer = models.TextField(u"Footer", help_text="Footer rendered below the question interpreted as textile", blank=True)
    slug = models.CharField(max_length=128)
    slug_fk = models.ForeignKey(Slugs, blank=True, null=True)
    help_text = models.CharField(max_length=2255, blank=True, null=True)
    stats = models.BooleanField(default=False)
    category = models.BooleanField(default=False)
    tooltip = models.BooleanField(default=False, help_text="If help text appears in a tooltip")
    visible_default = models.BooleanField(u"Comments visible by default", default=False)
    mlt_ignore = models.BooleanField(u"Ignore on More Like This", default=False)
    disposition = models.IntegerField(default=VERTICAL, choices=DISPOSITION_TYPES)

    metadata = models.TextField(blank=True, null=True)
    show_advanced = models.BooleanField(default=True, help_text='If question appears in advanced search')

    '''
    TO SOLVE
    class Meta:
        unique_together = ('questionset', 'slug_fk',)
    '''

    def meta(self):
        if not hasattr(self, "__metadict"):
            try:
                self.__metadict = json.loads(self.metadata)
            except:
                self.__metadict = {}

        return self.__metadict

    def questionnaire(self):
        return self.questionset.questionnaire

    def getcheckdict(self):
        """getcheckdict returns a dictionary of the values in self.checks"""
        if(hasattr(self, '__checkdict_cached')):
            return self.__checkdict_cached
        try:
            self.__checkdict_cached = d = parse_checks(self.sameas().checks or '')
        except ParseException:
            raise Exception("Error Parsing Checks for Question %s: %s" % (
                self.number, self.sameas().checks))
        return d

    def __unicode__(self):
        return u'{%s} (%s) %s' % (unicode(self.questionset), self.number, self.text)

    def sameas(self):
        if self.type == 'sameas':
            try:
                # sameas must become questionset dependant, because now qsets are not bound to a certain questionnaire
                self.__sameas = res = getattr(self, "__sameas",
                    Question.objects.get(number=self.checks, questionset=self.questionset)
                )
                return res
            except Question.DoesNotExist:
                return Question(type='comment') # replace with something benign
        return self

    def display_number(self):
        "Return either the number alone or the non-number part of the question number indented"
        # m = _numre.match(self.number)
        # if m:
        #     sub = m.group(2)
        #     return "&nbsp;&nbsp;&nbsp;" + sub
        return self.number

    def choices(self):
        if self.type == 'sameas':
            return self.sameas().choices()
        res = Choice.objects.filter(question=self).order_by('sortid')
        return res

    def is_custom(self):
        return "custom" == self.sameas().type

    def get_type(self):
        "Get the type name, treating sameas and custom specially"
        t = self.sameas().type
        if t == 'custom':
            cd = self.sameas().getcheckdict()
            if 'type' not in cd:
                raise Exception("When using custom types, you must have type=<name> in the additional checks field")
            return cd.get('type')
        return t

    def questioninclude(self):
        return "questionnaire/" + self.get_type() + ".html"

    def copy(self, questionset):
        clone = Question()

        clone.__dict__ = self.__dict__.copy()

        clone.id = None
        clone.questionset = questionset

        clone.save()

        return clone

    def __cmp__(a, b):
        anum, astr = split_numal(a.number)
        bnum, bstr = split_numal(b.number)
        cmpnum = cmp(anum, bnum)
        return cmpnum or cmp(astr, bstr)

    class Meta:
        translate = ('text', 'extra', 'footer')




class Choice(models.Model):
    __metaclass__ = TransMeta

    question = models.ForeignKey(Question)
    sortid = models.IntegerField()
    value = models.CharField(u"Short Value", max_length=1000)
    text = models.CharField(u"Choice Text", max_length=2000)
    opt = models.BooleanField(u"Has Optional text ?", default=True)

    def __unicode__(self):
        return u'(%s) %d. %s' % (self.question.number, self.sortid, self.text)

    class Meta:
        ordering = ('sortid',)
        translate = ('text',)

class QuestionnaireWizard(models.Model):
    questionnaire = models.ForeignKey(Questionnaire)
    user = models.ForeignKey(User)
    removed = models.BooleanField(default=False)

    @staticmethod
    def all(user=None):
        tmp = QuestionnaireWizard.objects.filter(removed=False)

        if user != None:
            tmp=tmp.filter(user=user)

        return tmp

    def remove(self):
        self.removed=True
        self.save()

    def interest(self, interested):
        if interested:
            prof = self.user.emif_profile

            prof.interests.add(self.questionnaire)
            prof.save()

        self.remove()


def fileHash(instance, filename):
    ''' Callable to be called by the FileField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return '.{0}qimports/{1}'.format(settings.MEDIA_URL, instance.id)


# used as a reference to serve as access point for celery to communicate progress on questionnaire import status
class QuestionnareImportFile(models.Model):
    START = 0
    PROCESSING = 1
    FINISHED = 2
    ABORTED = 3
    PREVIEW = 4

    STATUS_TYPES = (
        (START, 'Questionnaire import started'),
        (PROCESSING, 'Questionnaire is being imported'),
        (FINISHED, 'Questionnaire finished importing'),
        (ABORTED,'Questionnaire import aborted'),
        (PREVIEW, 'Questionnaire is currently in preview')
    )

    file = models.FileField(upload_to=fileHash, null=True, blank=True)
    filename = models.CharField(max_length=3000, blank=True, null=True)
    uploader = models.ForeignKey(User)
    status = models.IntegerField(default=START, choices=STATUS_TYPES)
    error_message = models.TextField(
        null=True,
        help_text=('None if the import succeeded with status FINISHED. '
                   'An error message if it failed with status ABORTED.'))

    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.SET_NULL,
        null=True)

    def get_status(self):
        if self.status == QuestionnareImportFile.START:
            return 'Waiting to start'
        elif self.status == QuestionnareImportFile.PROCESSING:
            return 'Processing'
        elif self.status == QuestionnareImportFile.FINISHED:
            return 'Finished'
        elif self.status == QuestionnareImportFile.ABORTED:
            return 'Aborted'
        elif self.status == QuestionnareImportFile.PREVIEW:
            return 'Preview'
        return 'Error'

    def status_name(self):
        if self.status == QuestionnareImportFile.START:
            return 'START'
        elif self.status == QuestionnareImportFile.PROCESSING:
            return 'PROCESSING'
        elif self.status == QuestionnareImportFile.FINISHED:
            return 'FINISHED'
        elif self.status == QuestionnareImportFile.ABORTED:
            return 'ABORTED'
        elif self.status == QuestionnareImportFile.PREVIEW:
            return 'PREVIEW'
        return 'INTERNAL_ERROR'

''' Wizards make no sense anymore, since interests disappeared, in favor of communities
@receiver(post_save, sender=Questionnaire)
def __create_wizards(sender, instance, created, *args, **kwargs):
    #This method uses the post_save signal on Questionnaire to generate wizards to existing users
    if created:
        for user in User.objects.all():
            try:
                qw = QuestionnaireWizard(questionnaire=instance, user=user)
                qw.save()
            except EmifProfile.DoesNotExist:
                pass
'''
