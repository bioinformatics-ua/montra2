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
"""A module for Python index

.. moduleauthor:: Luís A. Bastião Silva <bastiao@ua.pt>
"""
import datetime
import json
import logging
import re

import pysolr
from django.conf import settings
from django.template.defaultfilters import slugify

from questionnaire import Fingerprint_Index
from questionnaire.models import Question, Questionnaire

logger = logging.getLogger()


class CoreEngine:
    """It is responsible for index the documents and search over them
    It also connects to SOLR
    """

    SOLR_CORE = settings.SOLR_CORE
    CONNECTION_TIMEOUT_DEFAULT = 10
    def __init__(self, timeout=CONNECTION_TIMEOUT_DEFAULT, core=SOLR_CORE):
        # Setup a Solr instance. The timeout is optional.
        self.solr = pysolr.Solr('http://' +settings.SOLR_HOST+ ':'+ settings.SOLR_PORT+settings.SOLR_PATH+'/'+core, timeout=timeout)


    def reindex_quest_solr(self):
        p = re.compile("(\\d{1,2})(\.\\d{2})*$", re.L)

        #qsets = QuestionSet.objects.all()
        slugs = []
        questionaires = Questionnaire.objects.filter(disable=False)

        solr = pysolr.Solr('http://' +settings.SOLR_HOST+ ':'+ settings.SOLR_PORT+settings.SOLR_PATH)
        start=0
        rows=100
        fl=''

        for quest in questionaires:
            id = quest.id
            obj = {"id":"questionaire_"+str(id)}
            qsets = quest.questionsets()
            for qs in qsets:
                questions = qs.questions()
                for q in questions:
                    x = q.slug_fk
                    key = str(x.slug1) + "_qs"
                    obj[key] = q.text
            slugs.append(obj)


        for quest in questionaires:
            solr.delete(id='questionaire_'+str(id))

        solr.add(slugs)

    def index_fingerprint(self, doc):
        """Index fingerprint
        """
        # index document
        self.index_fingerprint_as_json(doc)


    def index_fingerprints(self, docs):
        """Index fingerprint
        """
        # index document
        self.index_fingerprint_as_json(docs, several = True)

    def index_fingerprint_as_json(self, d, several=False):
        """Index fingerprint as json
        """
        # index document
        xml_answer = None
        if several:
            xml_answer = self.solr.add(d)
        else:
            xml_answer = self.solr.add([d])

        self.optimize()

    def optimize(self):
        """This function optimize the index. It improvement the search and retrieve documents subprocess.
        However, it is a hard tasks, and call it for every index document might not be a good idea.
        """
        self.solr.optimize()

    def update(self, doc):
        """Update the document
        """
        # Search  and identify the document id

        self.solr.add([doc])


    def delete(self, id_doc):


        """Delete the document
        """
        self.solr.delete(id=id_doc, softCommit=True)

    def deleteQuery(self, q):
        """Delete the document
        """
        self.solr.delete(q=q)

    def search_fingerprint(self, query, start=0, rows=100, fl='*,score', sort='', facet="off", fq='', qop='AND'):
        """search the fingerprint
        """
        # Later, searching is easy. In the simple case, just a plain Lucene-style
        # query is fine.
        results = self.solr.search(query,**{'facet': facet,'rows': rows,'start': start,'fl': fl,'fq': fq,'sort': sort,'q.op': qop,})
        return results

    def search_highlight(self, query, start=0, rows=100, fl='*,score', sort='', hlfl="", qop='AND', fq='', multivalue_fields=tuple()):
        """search the fingerprint
        """
        #hl=true&hl.fl=text_txt

        kwargs = {
            'start': start,
            'rows': rows,
            'fl': fl,
            'q.op': qop,
            'sort': sort,
            'hl': "true",
            'hl.fl': hlfl,
            "hl.fragsize": 0,
            'fq': fq,
        }

        # for multivalue fields add this config so all values are returned and not only the highlighted ones
        for field in multivalue_fields:
            kwargs["f.{}_txt.hl.preserveMulti".format(field)] = "true"

        results = self.solr.search(
            query,
            **kwargs
        )
        return results

    def highlight_questions(self, query, start=0, rows=1000, fl='id', sort='', hlfl="*"):
        """search the fingerprint
        """
        #hl=true&hl.fl=text_txt
        #query = "qs_all:%s~10" % query
        
        query = "qs_all:%s" % query

        results = self.solr.search(query,**{
                'rows': rows,
                'start': start,
                'fl': fl,
                'q.op': 'AND',
                'sort': sort,
                'hl.fragsize': 0,
                #'hl.maxAlternateFieldLength': 500
                'hl':"true",
                'hl.fl': hlfl
                })
        return results

    def more_like_this(self, id_doc, type, start=0, fl='id, score', maxx=100):
        similar = self.solr.more_like_this(q='id:'+id_doc, fq='type_t:'+type,
            start=start, rows=maxx, mltcount=maxx, mltfl='mlt_t', mltmintf=2, mltmindf=2, mltminwl=4, fl=fl)
        return similar


def convert_text_to_slug(text):
    return slugify(text)


def setProperFields(d, question, field, value):
    """
    Set all proper fields for this question (this has in attention question types and such)
    P.e., for dates, it will date *_t and *_dt and for numeric *_t and *_d
    """
    # We always set the text one

    def setField(val):
        d[field+val['key']+"_t"] = val['value']
        d[field+val['key']+"_s"] = val['value']

    if question.type in Fingerprint_Index:
        value = Fingerprint_Index[question.type](value)
    
    #set field sufix according with field type
    if question.type == 'datepicker':
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            d[field+'_dt'] = value
        except ValueError:
            d[field+'_dt'] = ''
    elif question.type == 'numeric':
        d[field+'_d'] = value
    elif question.type == "publication":
        if value:  # check if value has something
            if value.startswith("{"):
                value = "[{}]".format(value)

            value = json.loads(value)

            if value:  # check if the list of publications is empty
                d[field+'_txt'] = [
                    "$$$".join(pub.get(key, "")
                    for key in ("pmid", "title", "authors", "year", "journal", "link"))
                    for pub in value
                ]
    elif isinstance(value, basestring):
        d[field+'_t'] = value
        d[field+'_s'] = value
    else:
        for val in value:
            setField(val)

    # Check and also apply the correct type, if any
    suffix = assert_suffix(str(question.type))

    if suffix != None:
        val = convert_value(value, str(question.type))
        if val != None:
            d[field+suffix] = val

    return d

def assert_suffix(type):
    if type.lower() == "numeric":
        return "_d"
    elif type.lower() == "datepicker":
        return "_dt"
    elif type.lower() == "publication":
        return "_txt"

    return None

def convertDate(value):
    value = re.sub("\"", "", value)

    try:
        # First we try converting to normalized format, yyyy-mm-dd
        date = datetime.datetime.strptime(value, '%Y-%m-%d')
        return date
    except ValueError:
        pass

    try:
        # We try yyyy/mm/dd
        date = datetime.datetime.strptime(value, '%Y/%m/%d')
        return date
    except ValueError:
        pass

    try:
        # We try just the year, yyyy
        date = datetime.datetime.strptime(value, '%Y')
        return date
    except ValueError:
        pass

    # failed conversion
    return None

def replaceDate(m):
    group = m.group(0)

    converted_date = convertDate(group)
    if converted_date == None:
        return '*'
    return converted_date.isoformat()+'T00:00:00Z'


def convert_value(value, type, search=False):
    """
    Convert a value formated in database to the one indexed.
    """
    if type == "numeric":
        # remove separators if they exist on representation
        value = re.sub(r"[^0-9.]", "", value)
        try:
            value = float(value)
        except ValueError:
            pass
        else:
            return value

    elif type == "datepicker":
        if value.startswith('[') and value.endswith(']'):
            temp = value
            temp = re.sub("[0-9/-]+", replaceDate, temp)

            return temp
        else:
            # for some weird reason, single date queries to solr returns error,
            # they must be in a range format always ? wth i just do a range query on the same date
            result = convertDate(value)
            if result is not None:
                iso = result.isoformat()
                if search:
                    end = result + datetime.timedelta(hours=23, minutes=59, seconds=59)
                    return "[{}Z TO {}Z]".format(iso, end.isoformat())
                return iso + "Z"

    return None


def generateFreeText(d):
    """
    Generates the freetext field, from current parameters
    """
    freetext = []
    dont_index = {'text_txt', 'text_en', 'questions_txt', 'all_txt', 'tagcloud', 'created_dt','date_last_modification_dt','type_t', 'user_t', 'mlt_t'}

    for q in d:
        if q.endswith('_t') and q not in dont_index and d[q] is not None and len(d[q]) > 0:
            freetext.append(re.sub('[#_{}]',' ', d[q]))

    return freetext


def generateMltText(d):
    """
    Generates the mlt field, from current parameters
    """
    dont_index = {'text_txt', 'text_en', 'questions_txt', 'all_txt' 'tagcloud', 'created_dt','date_last_modification_dt','type_t', 'user_t', 'database_name_t', 'mlt_t'}

    try:
        quest = Questionnaire.objects.filter(slug=d['type_t'])

        if quest.count() == 0:
            raise Exception('No questionnaire with type_t %s' % d['type_t'])

        quest = quest[0]
        questions = Question.objects.filter(questionset__in=quest.questionsets_ids(), mlt_ignore=True)

        for question in questions:
            dont_index.add(question.slug_fk.slug1+'_t')

    except:
        logger.error("Error retrieving questionnaire ignore mlt slugs")

    freetext = []
    for q in d:
        if q.endswith('_t') and not q.startswith('comment_') and q not in dont_index and d[q] is not None and len(d[q]) > 0:
            freetext.append(re.sub('[#_{}]', ' ', d[q]))

    return freetext
