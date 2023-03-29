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
#
from __future__ import print_function

import csv
import json
import re
import tempfile

from constance import config
from django.contrib.auth.models import User
from django.core.files import File as DjangoFile
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import strip_tags

from accounts.models import EmifProfile, RestrictedGroup, RestrictedUserDbs
from community.models import QuestionSetAccessGroups
from community.utils import getComm
from fingerprint.models import Fingerprint
from questionnaire.models import Question, QuestionSet, Questionnaire
from questionnaire.services import createhollowqsets, creatematrixqsets
from taskqueue.models import QueueJob


def get_matrix_data(db_type, questions_dict, user, selected_databases, flat=False):
    # generate a mumbo jumbo digest for this combination of parameters, to be used as key for caching purposes

    titles = None
    answers = None
    hashed = None  # TODO
    cached = None

    q_dict = json.loads(questions_dict)
    questions = []

    if cached != None:
        (titles, answers) = cached

    else:
        fingerprints = Fingerprint.objects.filter(id__in=selected_databases)

        keys = q_dict.keys()
        keys_parsed = []
        for key in keys:
            key = key.split("_")[1]
            keys_parsed.append(key)

        qsets_ids = list(QuestionSet.objects.filter(id__in=keys_parsed).order_by("sortid").values_list("id", flat=True))

        for qs in qsets_ids:
            # for key, value in sorted(q_dict.iteritems(), key=lambda (k,v): (v,k)):
            k = "qs_" + str(qs)
            question = Question.objects.filter(questionset_id=qs, id__in=q_dict[k]).order_by("number")
            questions.append(question)

        try:
            eprofile = EmifProfile.objects.get(user=user)

            if eprofile.restricted == True:
                hashes = RestrictedGroup.hashes(user)

                others = RestrictedUserDbs.objects.filter(user=user)

                for db in others:
                    hashes.add(db.fingerprint.fingerprint_hash)

                fingerprints = fingerprints.filter(fingerprint_hash__in=hashes)

        except EmifProfile.DoesNotExist:
            print("-- ERROR: Couldn't get emif profile for user")

        (titles, answers) = creatematrixqsets(db_type, fingerprints, questions, flat=flat)

    return (hashed, titles, answers)


def qs_data_table(request, template_name='qs_data_table.html'):
    db_type = int(request.POST.get("db_type"))
    # qset_post = request.POST.getlist("qsets[]")
    selected_databases = request.POST.getlist("selected_databases[]")
    questions_dict = request.POST.get("questions_dict")

    (hashed, titles, answers) = get_matrix_data(db_type, questions_dict, request.user, selected_databases)

    return render(request, template_name,
                  {'request': request, 'hash': hashed, 'export_all_answers': True, 'breadcrumb': False,
                   'collapseall': False, 'geo': False, 'titles': titles, 'answers': answers})


def all_databases_data_table(request, template_name='custom_view_export.html'):
    return custom_view_questionnaire_export(request, None, None, template_name)


def custom_view_questionnaire_export(request, community, questionnaire, template_name='custom_view_export.html'):
    if not config.datatable:
        raise Http404

    comm = getComm(community, request.user)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    questionnaire = comm.questionnaires.get(slug=questionnaire)

    qsets_truncated = questionnaire.questionsets().exclude(sortid__in=[0, 99])

    databases = {}
    fingerprints = Fingerprint.objects.filter(community=comm, questionnaire=questionnaire, removed=False, draft=False)

    for fingerprint in fingerprints:
        databases[fingerprint.id] = fingerprint.findName()

    quest_qsets = {questionnaire: createhollowqsets(questionnaire.id).ordered_items()}

    for qset_i in qsets_truncated:
        if comm:
            allow_qset_reading = QuestionSetAccessGroups.checkAccess("R", comm, None, request.user, qset_i)
        else:
            allow_qset_reading = True
        qset_i.readPermission = allow_qset_reading

    return render(request, template_name, {'request': request, 'export_datatable': True,
                                           'breadcrumb': True, 'collapseall': False, 'geo': True,
                                           'dict_qsets': quest_qsets,
                                           'comm': comm,
                                           'activemenu': 'databases',
                                           'activesubmenu': 'datatable-{}'.format(questionnaire.slug),
                                           'questionnaire': questionnaire,
                                           'comm_databases': databases,
                                           'qst': qsets_truncated,
                                           })


def export_message(request):
    return render(request, 'exporting_message.html', {
        'request': request,
        'message': 'An export of this datatable view has been scheduled to be exported.',
        "job_queue_menu": config.jobQueueMenu,
    })


def export_datatable(request, template_name='exporting_message.html'):
    db_type = int(request.POST.get("db_type"))
    selected_databases = request.POST.getlist("selected_databases[]")
    questions_dict = request.POST.get("questions_dict")
    user = User.objects.get(username=request.user.username)
    qj = QueueJob(
        title='Export of datatable view - %s' % (timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=user
    )
    qj.save()

    args = [db_type, questions_dict, selected_databases]
    qj.execute(handle_table_export, args)

    return render(request, template_name, {
        'request': request,
        'message': 'An export of this datatable view has been scheduled to be exported.',
        "job_queue_menu": config.jobQueueMenu,
    })


def handle_table_export(db_type, questions_dict, selected_databases, job=None, user=None):
    """
    Method to export all databases answers to a csv file
    """

    def clean_str_exp(s):
        s2 = s.replace("\n", "|").replace(";", ",").replace("\t", "    ").replace("\r", "").replace("^M", "").replace(
            "|", "")

        return re.sub("\s\s+", " ", s2)

    (hashed, titles, answers) = get_matrix_data(db_type, questions_dict, user, selected_databases, flat=True)

    response = None
    with tempfile.NamedTemporaryFile() as tmp:

        if job:
            job = QueueJob.objects.get(id=job)
            job.output_name = '%s.csv' % (hashed)
            job.save()

            response = tmp
        else:

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="' + str(hashed) + '.csv"'

        writer = csv.writer(response)

        titles_clean = []
        for title in titles:
            titles_clean.append(
                title.replace('h0. ', '').replace('h1. ', '').replace('h2. ', '').replace('h3. ', '').replace('h4. ',
                                                                                                              '').replace(
                    'h5. ', '').replace('h6. ', '').replace('h7. ', ''))

        writer.writerow(titles_clean)

        total_ans = len(answers)
        i = 0

        for title, ans in answers:
            i += 1

            line = [title]
            for a in ans:
                if a != '':
                    line.append(clean_str_exp(strip_tags(a[0])))
                else:
                    line.append('')
            writer.writerow(line)

            job.progress = (100 * i) / total_ans
            job.save()

        if job:
            job.output = DjangoFile(response)
            job.save()

        return response

        # list_databases = get_databases_from_solr(request, "*:*")
        # return save_answers_to_csv(list_databases, "DBs")
