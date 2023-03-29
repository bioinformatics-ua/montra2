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
import hashlib
import logging
import random
import re
import time
from datetime import datetime

from constance import config
from django.conf import settings
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from fingerprint.models import Fingerprint
from questionnaire.models import Question, Questionnaire
from searchengine.models import Nomenclature
from searchengine.models import Slugs
from searchengine.search_indexes import CoreEngine, assert_suffix, convert_value
from .models import SharePending

# Get an instance of a logger
logger = logging.getLogger(__name__)


def generate_hash():
    hash = hashlib.md5()
    hash.update("".join(chr(random.randint(0, 255)) for _ in range(16)))
    hash.update(settings.SECRET_KEY)
    key = hash.hexdigest()
    return key


def convert_text_to_slug(text):
    #TODO: optimize
    return text.replace(' ', '_').replace('?','').replace('.', '').replace(',','')


def clean_value(v):
    if isinstance(v, str):
        logging.debug("Value: " + v)

        v = re.sub(r"\[|\]", "", v)
        logging.debug("Value after clean: " + v)
    elif isinstance(v, list):
        for v_aux in v:
            v += v_aux + " "
    return v

def convert_date(d):
    new_date = datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f')
    return new_date.strftime("%Y-%m-%d %H:%M")


def get_nomenclature(institution_name, database_name):
    """
    Get the nomenclature to the database based on institution name
    """
    value = clean_value(institution_name+"_"+database_name)
    slug = convert_text_to_slug(value)
    return slug



def database_exists(database_name):
    """
    Verify if the nomenclature database name already exists
    """
    results = Nomenclature.objects.filter(name=database_name)
    if len(results)==0:
        return False
    else:
        return True

class ordered_dict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._order = self.keys()

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._order.remove(key)

    def order(self):
        return self._order[:]

    def ordered_items(self):
        return [(key,self[key]) for key in self._order]



class Tag:

        def __init__(self):
            self.id = -1
            self.tag = ''
            self.value = ''
            self.extra = ''
            self.number = ''
            self.comment = ''
            self.ttype = ''


        def __eq__(self, other):
            return other.id == self.id


        def __cmp__(self, other):
            return cmp(other.id, self.id)

        def __lt__ (self, other):
            return self.number < other.number

        def __gt__ (self, other):
            return other.__lt__(self)

        def __str__(self):
            return self.tag + ", " + self.value

class QuestionGroup:

    def __init__(self):
        self.list_ordered_tags = []
        self.name = ""
        self.sortid = ""
        self.qsid = ""
        self.highlights = False
        #self.qsid = -1

        self.info = False

    def __eq__(self, other):
        return other.name == self.name

    def __lt__ (self, other):

        return self.sortid < other.sortid

    def __gt__ (self, other):
        return other.__lt__(self)

    def __str__(self):
        return self.name


def get_database_from_id_with_tlv(db):
    c = CoreEngine()
    results = c.search_fingerprint('id:'+db.id)
    class Tag:
        tag = ''
        value = ''

    list_values = []
    blacklist = ['created_dt', 'type_t', '_version_']

    for result in results:
        questionnaire_slug = result['type_t']
        q_main = Questionnaire.objects.filter(slug=questionnaire_slug)[0]

        for k in result:
            if k in blacklist:
                continue
            t = Tag()
            results = Slugs.objects.filter(slug1=k, question__questionset__in=q_main.questionsets_ids())
            if len(results)>0:
                text = results[0].description
            else:
                text = k
            info = text[:75] + (text[75:] and '..')

            t.tag = info

            value = clean_value(str(result[k]))
            value = value[:75] + (value[75:] and '..')
            t.value = value

            list_values.append(t)
        break
    db.fields = list_values
    return db


def convert_dict_to_query2(params):
    query = ""
    i = 0
    size_params = len(params)
    for key in params:
        query += key+"_t:" + params[key]+"*"
        i = i + 1
        if (size_params != i ):
            query += " AND "

    return query

def is_only_space(s):
    return s == len(s) * ' '

def convert_dict_to_query(params):
    query = ""
    i = 0
    size_params = len(params)
    for key in params:
        if (params[key]!="" or not is_only_space(params[key])):
            query += key+"_t:" + params[key]+"*"
            i = i + 1
            if (size_params != i ):
                query += " AND "

    return query


def convert_query_from_boolean_widget(query, q_id):
    """
    Receives query in Advanced Search format and convert to Solr format.
    # Example to test the funcion:

    #a = "question_nr_1.01: 'sadsa' AND question_nr_1.02: 'dsadsadsa' AND question_nr_1.04: 'asdsaa'"
    #print convert_query_from_boolean_widget(a, 49)
    """
    try:
        questionnarie = Questionnaire.objects.get(id=q_id)

        advparams = []
        ttype = questionnarie.slug

        questionsets = questionnarie.questionsets()
        # I cant remove the symbol
        query = re.sub("_____[a-zA-Z0-9._()\[\]\/\-\+?!'@#$%&*=~^|\\<>;,\.\" ]+_____", "", query)

        def __check(m):
            logger.debug("-- CHECK")

            question_id = m.group(1)

            question_id = question_id.replace('question_nr_', '')
            question_answer = m.group(5)

            logger.debug("T:"+m.group(0))
            logger.debug("Q: "+question_id + " A:"+question_answer)

            q = Question.objects.filter(number=question_id, questionset__in=questionsets)

            suffix = assert_suffix(q[0].type)
            temp = q[0].slug

            if m.group(2):
                temp += '_%s'% m.group(2)[5:-5]

            if suffix != None:
                temp += suffix
            else:
                # This is a fix, for search in index time by strings 
                # In SOLR 
                temp += '_s'

            advparams.append(temp)

            convert = convert_value(question_answer, q[0].type, True)
            if q[0].type == 'numeric' and question_answer.startswith('[') and question_answer.endswith(']'):
                    question_answer = question_answer
                    return escapeSolrArg(temp)+":"+question_answer
            #elif q[0].type == 'datepicker' and question_answer.startswith('[') and question_answer.endswith(']'):
            #        question_answer = question_answer
            #        return escapeSolrArg(temp)+":"+question_answer    

            # setting name as literal, and after escaping the literal definer
            if convert == None:
                if question_answer.startswith('[') and question_answer.endswith(']'):
                    question_answer = question_answer
                    return escapeSolrArg(temp)+":"+question_answer
                else:
                    convert = question_answer
            
            return escapeSolrArg(temp)+":"+str(convert)

        # how to escape everything but unescaped single quotes, very nice ref from :
        # http://stackoverflow.com/questions/249791/regex-for-quoted-string-with-escaping-quotes
        # this is non-greedy, giving the smallest match possible (as we want)
        r = re.sub("(question_nr_[10-9\\.]+)(\*\*\*\*\*[a-z0-9_]+\*\*\*\*\*)?(:)( )?(\"(\\\.|[^\"])*\"|\[[0-9\.,\-a-zA-Z\* ]*\])", __check, query)
        #r = re.sub('(question_nr_[10-9\\.]+)', check, query)

        r = r + " AND type_t:"+ttype

        return (r, advparams)

    except Questionnaire.DoesNotExist:
        raise Exception("The questionnaire %s does not exist. Cant convert qvalues to query")

    return (None, None)

## Reference on how to escape this efficiently from:
# - http://www.opensourceconnections.com/2013/01/17/escaping-solr-query-characters-in-python/
# These rules all independent, order of
# escaping doesn't matter
escapeRules = {'+': r'\+',
               '-': r'\-',
               '&': r'\&',
               '|': r'\|',
               '!': r'\!',
               '(': r'\(',
               ')': r'\)',
               '{': r'\{',
               '}': r'\}',
               '[': r'\[',
               ']': r'\]',
               '^': r'\^',
               '~': r'\~',
               '*': r'\*',
               '?': r'\?',
               ':': r'\:',
               #'"': r'\"',
               ';': r'\;',
               ' ': r'\ ',
               '"': r'\"'}

def escapedSeq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escapeRules.keys():
            yield escapeRules[char]
        else:
            yield char
def escapeSolrArg(term):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = term.replace('\\', r'\\')   # escape \ first
    return "".join([nextStr for nextStr in escapedSeq(term)])

def send_custom_mail(title, description, from_mail, to_mail):

    email = render_to_string('email_template.html', {
            'title': title,
            'description': description.replace('\n','<br />'),
            'from_mail': from_mail,
            'to_mail': to_mail,
            'current_date': time.strftime("%d/%m/%Y %H:%M:%S")
        })

    msg = EmailMultiAlternatives(title, description, from_mail, to_mail)
    msg.attach_alternative(email, "text/html")

    msg.send()

def removehs(value):
    value = value.replace('h0. ','')
    value = value.replace('h1. ','')
    value = value.replace('h2. ','')
    value = value.replace('h3. ','')
    value = value.replace('h4. ','')
    value = value.replace('h5. ','')
    value = value.replace('h6. ','')
    value = value.replace('h7. ','')

    return value

def activate_user(activation_code, user, context = None, template_name=None):
    if (user==None or not user.is_authenticated()):
        if context != None:
            return HttpResponse('You need to be authenticated.')
        else:
            logger.info('You need to be authenticated.')
            return False

    __objs = SharePending.objects.filter(activation_code=activation_code, pending=True, user=user)
    if (len(__objs)==0):
        if context != None:
            return HttpResponse('It is already activated or does the item has been expired.')
        else:
            logger.info('It is already activated or does the item has been expired.')
            return False


    if (len(__objs)>1):
        if context != None:
            return HttpResponse('An error has occurred. Contact the '+config.brand+' Team.')

        else:
            logging.info('Multiple objects. An error has occurred. Contact the %s Team.', config.brand)
            return False

    sp = __objs[0]

    fingerprint = None
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=sp.db_id)

    except:
        if context != None:
            return HttpResponse("An error has occurred. Contact the "+config.brand+" Team.")
        else:
            logging.info("No fingerprint found. An error has occurred. Contact the %s Team.", config.brand)
            return False

    fingerprint.shared.add(user)

    fingerprint.save()

    fingerprint.indexFingerprint()

    sp.pending = False
    sp.save()
    finger_name = fingerprint.findName()
    try:
        subject = config.brand+": Accepted database shared"
        message = """Dear %s,\n\n
            \n\n
            %s has been activated. You can access the new database in "Databases" -> Personal".
            \n\nSincerely,\n%s
        """ % (user.get_full_name(), finger_name, config.brand)


        message_to_inviter = """Dear %s,\n\n
            \n\n
            %s has accepted to work with you in database %s.

            \n\nSincerely,\n%s
        """ % (sp.user_invite.get_full_name(), user.get_full_name(), finger_name, config.brand)

        # Send email to admins
        send_custom_mail(subject, message_to_inviter, settings.DEFAULT_FROM_EMAIL, [sp.user_invite.email])
        # Send email to user with the copy of feedback message
        send_custom_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [sp.user.email])

    except BadHeaderError:
        if context != None:
            return HttpResponse('Invalid header found.')
        else:
            logging.info('Invalid header found.')
            return False

    if context != None:
        return render(context, template_name, {'request': context, 'breadcrumb': True})
    else:
        return True


def get_community_field_from_entry(database, slug):
    """
    function to look for a field that was configured for a community
    inside a database entry (also known by fingerprint). This is needed 
    to show only the database entry's fields configured on the community.

    Note: this method was previously implemented also on extra_tags.py with the name 'find_field_value'
    
    database - dict object of Database class
    slug - slug that identifies the configured field on community
    returns dictionary of the database entry field that has a corresponding slug
    """

    if slug == 'start_data_collection':
        try:
            fields = database['fields'].get("%s_t" % slug, '')
            if "/" in fields:
                fields_year = fields.split("/")[2]
                return fields_year
            else:
                return database['fields'].get("%s_t" % slug, '')[:-6]
        except:
            return ''

    return database['fields'].get("%s_t" % slug, '')

