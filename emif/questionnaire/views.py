#!/usr/bin/python
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

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.db import transaction
from django.conf import settings
import datetime
from django.views.generic import TemplateView

import django_tables2 as tables

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from questionnaire import QuestionProcessors
from questionnaire import Fingerprint_Summary
from questionnaire import questionnaire_done
from questionnaire import questionset_done
from questionnaire import AnswerException
from questionnaire import Processors
from questionnaire.models import *
from questionnaire.parsers import *

from questionnaire.utils import *
from questionnaire.request_cache import request_cache
from questionnaire import profiler

from searchengine.search_indexes import convert_text_to_slug
from searchengine.models import Slugs

import logging
import random
import md5
import re

from openpyxl import load_workbook

from django.template.defaultfilters import slugify
from questionnaire.export import ExportQuestionnaire
import tempfile, csv, cStringIO, codecs
from wsgiref.util import FileWrapper

from tasks import importQuest

from community.models import Community

def r2r(tpl, request, **contextdict):
    "Shortcut to use RequestContext instead of Context in templates"
    contextdict['request'] = request
    return render(request, tpl, contextdict)

#def get_runinfo(random):
#    "Return the RunInfo entry with the provided random key"
#    res = RunInfo.objects.filter(random=random.lower())
#    return res and res[0] or None

def get_question(number, questionnaire):
    "Return the specified Question (by number) from the specified Questionnaire"
    res = Question.objects.filter(number=number, questionset__in=questionnaire.questionsets_ids())
    return res and res[0] or None

def _table_headers(questions):
    """
    Return the header labels for a set of questions as a list of strings.

    This will create separate columns for each multiple-choice possiblity
    and freeform options, to avoid mixing data types and make charting easier.
    """
    ql = list(questions.distinct('number'))
    ql.sort(lambda x, y: numal_sort(x.number, y.number))
    columns = []
    for q in ql:
        if q.type == 'choice-yesnocomment':
            columns.extend([q.number, q.number + "-freeform"])
        elif q.type == 'choice-freeform':
            columns.extend([q.number, q.number + "-freeform"])
        elif q.type.startswith('choice-multiple'):
            cl = [c.value for c in q.choice_set.all()]
            cl.sort(numal_sort)
            columns.extend([q.number + '-' + value for value in cl])
            if q.type == 'choice-multiple-freeform':
                columns.append(q.number + '-freeform')
        else:
            columns.append(q.number)
    return columns



@permission_required("questionnaire.export")
def export_csv(request, qid): # questionnaire_id
    """
    For a first_name questionnaire id, generaete a CSV containing all the
    answers for all subjects.
    """
    #print "export_csv"

    #print qid
    class UnicodeWriter:
        """
        COPIED from http://docs.python.org/library/csv.html example:

        A CSV writer which will write rows to CSV file "f",
        which is encoded in the first_name encoding.
        """

        def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
            # Redirect output to a queue
            self.queue = cStringIO.StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

        def writerow(self, row):
            self.writer.writerow([s.encode("utf-8") for s in row])
            # Fetch UTF-8 output from the queue ...
            data = self.queue.getvalue()
            data = data.decode("utf-8")
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the target stream
            self.stream.write(data)
            # empty queue
            self.queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)

    fd = tempfile.TemporaryFile()

    questionnaire = get_object_or_404(Questionnaire, pk=int(qid))
    headings, answers = answer_export(questionnaire)

    writer = UnicodeWriter(fd)
    writer.writerow([u'subject', u'runid'] + headings)
    for subject, runid, answer_row in answers:
        row = ["%s/%s" % (subject.id, subject.state), runid] + [
            a if a else '--' for a in answer_row]
        writer.writerow(row)

    contentLength = fd.tell()
    response = HttpResponse(FileWrapper(fd), content_type="text/csv")
    response['Content-Length'] = contentLength
    response['Content-Disposition'] = 'attachment; filename="export-%s.csv"' % qid
    return response

def answer_export(questionnaire, answers=None):
    """
    questionnaire -- questionnaire model for export
    answers -- query set of answers to include in export, defaults to all

    Return a flat dump of column headings and all the answers for a
    questionnaire (in query set answers) in the form (headings, answers)
    where headings is:
        ['question1 number', ...]
    and answers is:
        [(subject1, 'runid1', ['answer1.1', ...]), ... ]

    The headings list might include items with labels like
    'questionnumber-freeform'.  Those columns will contain all the freeform
    answers for that question (separated from the other answer data).

    Multiple choice questions will have one column for each choice with
    labels like 'questionnumber-choice'.

    The items in the answers list are unicode strings or empty strings
    if no answer was first_name.  The number of elements in each answer list will
    always match the number of headings.
    """
    if answers is None:
        answers = Answer.objects.all()

    qsids = questionnaire.questionsets_ids()

    answers = answers.filter(question__questionset__in=qsids).order_by(
        'subject', 'runid', 'question__questionset__sortid', 'question__number')

    answers = answers.select_related()
    questions = Question.objects.filter(questionset__in=qsids)
    headings = _table_headers(questions)

    coldict = {}
    for num, col in enumerate(headings): # use coldict to find column indexes
        coldict[col] = num
    # collect choices for each question
    qchoicedict = {}
    for q in questions:
        qchoicedict[q.id] = [x[0] for x in q.choice_set.values_list('value')]

    runid = subject = None
    out = []
    row = []
    for answer in answers:
        if answer.runid != runid or answer.subject != subject:
            if row:
                out.append((subject, runid, row))
            runid = answer.runid
            subject = answer.subject
            row = [""] * len(headings)
        ans = answer.split_answer()
        if type(ans) == int:
            ans = str(ans)
        for choice in ans:
            col = None
            if type(choice) == list:
                # freeform choice
                choice = choice[0]
                col = coldict.get(answer.question.number + '-freeform', None)
            if col is None: # look for enumerated choice column (multiple-choice)
                col = coldict.get(answer.question.number + '-' + choice, None)
            if col is None: # single-choice items
                if ((not qchoicedict[answer.question.id]) or
                    choice in qchoicedict[answer.question.id]):
                    col = coldict.get(answer.question.number, None)
            if col is None: # last ditch, if not found throw it in a freeform column
                col = coldict.get(answer.question.number + '-freeform', None)
            if col is not None:
                row[col] = choice
    # and don't forget about the last one
    if row:
        out.append((subject, runid, row))
    return headings, out


class QuestionnareImportFileTable(tables.Table):
    filename = tables.Column(accessor='filename')
    status = tables.TemplateColumn(template_name='status_column.html')

    class Meta:
        template_name = 'django_tables2_bootstrap_override.html'


class ImportQuestionnaireView(TemplateView):
    template_name = "questionnaire_import.html"

    def get(self, request, success_message=None, error_message=None):
        if(not (request.user.is_superuser or request.user.groups.filter(name='importers').exists())):
            return HttpResponse('Forbidden', 403)

        quploads = QuestionnareImportFile.objects.filter(uploader=request.user)#.order_by('-id')[:10]

        table = QuestionnareImportFileTable(quploads)
        tables.RequestConfig(request, paginate={'per_page': 10}).configure(table)

        comm = None
        if settings.SINGLE_COMMUNITY:
            comm = Community.objects.all()[:1].get()
        
        questionnaires = Questionnaire.objects.filter(disable=False)

        return render(request, self.template_name,
            {
                'request': request,
                'activemenu': 'import',
                'quploads': quploads,
                'activesubmenu': 'import_questionnaire',
                'success_message': success_message,
                'error_message': error_message,
                'breadcrumb': True,
                'table': table,
                'comm': comm,
                'questionnaires': questionnaires
            })

    def post(self, request):
        try:
            try:
                uploaded_file = request.FILES['file']
            except:
                return self.get(request, error_message="Error importing questionnaire. Select a xlsx file with a questionnaire schema before importing.")
            try:
                qid_to_merge = request.POST["qid"]
            except:
                raise
                qid_to_merge = None


            qi = QuestionnareImportFile(file=uploaded_file, uploader=request.user, filename=uploaded_file.name)
            qi.save()

            preview = request.POST['action'] == 'Preview'

            importQuest.apply_async(args=[qi.id, preview, request.user, qid_to_merge])
            importQuest.apply_async(args=["", preview, request.user])

            if preview:
                return redirect('questionnaire-preview-loading', questionnaire_id=qi.id)

            return self.get(request, success_message="Questionnaire importing asyncronously, will be briefly available. To import another questionnaire please add it below.")
        except:
            raise
            return self.get(request, error_message="Error importing questionnaire. Make sure you are importing a xlsx file with a questionnaire schema. If the problem persists please try again later, or contact the administrator.")

class ExportQuestionnaireView(TemplateView):
    template_name = "questionnaire_export.html"

    def get(self, request):
        if(not (request.user.is_superuser or request.user.groups.filter(name='importers').exists())):
            return HttpResponse('Forbidden', 403)

        comm = None
        if settings.SINGLE_COMMUNITY:
            comm = Community.objects.all()[:1].get()

        return render(request, self.template_name,
            {
                'request': request,
                'activemenu': 'export',
                'activesubmenu': 'export_questionnaire',
                'schemas': Questionnaire.objects.all(),
                'breadcrumb': True,
                'comm': comm
            })


class ExportQuestionnaireAttachView(TemplateView):
    template_name = "questionnaire_export.html"

    def get(self, request, questionnaire_id):
        if(not (request.user.is_superuser or request.user.groups.filter(name='importers').exists())):
            return HttpResponse('Forbidden', 403)

        fd = tempfile.NamedTemporaryFile()

        questionnaire = get_object_or_404(Questionnaire, pk=int(questionnaire_id))

        exporter = ExportQuestionnaire.factory("excel", questionnaire, fd)
        exporter.export()

        contentLength = fd.tell()
        response = HttpResponse(open(fd.name, 'rb'), content_type="application/vnd.ms-excel")
        response['Content-Length'] = contentLength
        response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % questionnaire.name
        return response


class QuestionnairePreviewLoadingView(TemplateView):
    template_name = 'questionnaire_preview_loading.html'
