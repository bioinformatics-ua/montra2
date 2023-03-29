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
from __future__ import print_function

import json
import logging
import os
import zipfile

from constance import config
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import EmifProfile
from community.models import Community, CommunityGroup, CommunityUser, PluginPermission, QuestionSetAccessGroups
from community.utils import getComm
from community.views import buildPermissionsMatrix
from developer.models import Plugin, PluginFingeprint, PluginVersion
from emif.models import AdvancedQuery, AdvancedQueryAnswer
from emif.utils import generate_hash
from emif.views import get_api_info
from geolocation.services import add_city
from population_characteristics.models import Characteristic
from public.models import PublicFingerprintShare
from public.utils import hasFingerprintPermissions
from questionnaire import QuestionProcessors
from questionnaire.models import Question, Questionnaire
from questionnaire.services import createqset, createqsets
from questionnaire.utils import split_numal
from questionnaire.views import r2r
from taskqueue.models import QueueJob
from .listings import get_databases_from_solr
from .models import Answer, AnswerRequest, Fingerprint, FingerprintImportFile, \
    FingerprintSubscription, QuestionSetCompletion
from .services import attachPermissions, create_database_montra_file, create_database_pdf_file, deleteFingerprint, \
    extract_answers, saveFingerprintAnswers, \
    save_answers_to_csv, setNewPermissions
from .tasks import importFingerprint

logger = logging.getLogger(__name__)


def export_bd_answers(request, runcode, template_name='exporting_message.html'):
    """
    Method to export answers of a specific database to a csv file
    :param request:
    :param runcode:
    """


    try:
        this_fingerprint = Fingerprint.objects.get(fingerprint_hash=runcode)

        list_databases = get_databases_from_solr(request, "id:" + runcode)

        qj = QueueJob(
                title = 'Database %s answers - %s' % (this_fingerprint.findName(), timezone.now().strftime('%B %d, %Y, %I:%M %p')),
                runner = request.user
            )
        qj.save()

        args = [list_databases, 'MyDB']

        qj.execute(save_answers_to_csv, args)

        #return save_answers_to_csv(list_databases, 'MyDB')

    except Fingerprint.DoesNotExist:
        pass

    return render(request, template_name, {
        'request': request,
        'message': ('Database %s answers have been scheduled to be exported.' % (this_fingerprint.findName())),
        "job_queue_menu": config.jobQueueMenu,
    })


def export_database_pdf_file(request, fingerprint_hash):
    fingerprint = get_object_or_404(Fingerprint, fingerprint_hash=fingerprint_hash)
    fingerprint_name = fingerprint.findName()

    qj = QueueJob(
        title='Export database {} answers in pdf format - {}'.format(fingerprint_name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user,
    )
    qj.save()

    qj.execute(create_database_pdf_file, (fingerprint_hash,))

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'Database {} answers in pdf format have been scheduled to be exported.'.format(fingerprint_name),
            "job_queue_menu": config.jobQueueMenu,
        },
    )


def export_database_montra_file(request, fingerprint_hash):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    fingerprint = get_object_or_404(Fingerprint, fingerprint_hash=fingerprint_hash)
    fingerprint_name = fingerprint.findName()

    qj = QueueJob(
        title='Export database {} answers in montra format - {}'.format(fingerprint_name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user,
    )
    qj.save()

    qj.execute(create_database_montra_file, (fingerprint_hash,))

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'Database {} answers in montra format have been scheduled to be exported.'.format(fingerprint_name),
            "job_queue_menu": config.jobQueueMenu,
        },
    )


def database_add(request, questionnaire_id, sortid):
    return database_add_comm(request, None ,questionnaire_id, sortid)

def database_add_comm(request, community, questionnaire_id, sortid):

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    response = show_fingerprint_page_read_only(request, questionnaire_id, sortid,
                                               template_name='database_add.html', comm=comm)

    return response

def delete_fingerprint(request, id, community):
    try:
        # get fingerprint questionnaire 
        f = Fingerprint.objects.get(fingerprint_hash=id)
        questionnaire = f.questionnaire
    except Fingerprint.DoesNotExist:
        raise Http404

    deleteFingerprint(id, request.user, community)

    return redirect('fingerprint.listings.database_listing_by_community_questionnaire', community=community, questionnaire=questionnaire.slug)


def database_edit_dl(request, fingerprint_id, questionnaire_id, community=None, sort_id=0):
    """
    detailed view with direct linking to questionset
    """
    return database_edit(request, fingerprint_id, questionnaire_id, community, sort_id=sort_id)


def getHighlightedList(request, highlightMap, questionnaire_id, fingerprint_id):

    h = None
    rHighlights = None
    qhighlights = None

    if "query" in request.session and "highlight_results" in request.session:
        h = request.session["highlight_results"]

    if h != None:
        quest = Questionnaire.objects.get(id=questionnaire_id)
        qsids = quest.questionsets_ids()

        if "results" in h and fingerprint_id in h["results"]:

            rHighlights = h["results"][fingerprint_id]

            for tag in rHighlights:
                type_separator_index = tag.rfind("_")
                if type_separator_index == -1:
                    type_separator_index = len(tag)
                try:
                    q = Question.objects.get(slug_fk__slug1=tag[:type_separator_index], questionset__in=qsids)

                    highlightMap[q.questionset.id] = True
                except Question.DoesNotExist:
                    pass

        if "questions" in h and 'questionaire_%s' % str(questionnaire_id) in h["questions"]:
            qhighlights = h["questions"]['questionaire_%s' % str(questionnaire_id)]

            for qh in qhighlights:

                q = Question.objects.filter(slug_fk__slug1=qh[:-3], questionset__in=qsids)

                if q.count() > 0:
                    q = q[0]

                    highlightMap[q.questionset.id] = True

    return highlightMap


def _get_question_set_list(qs_list, fingerprint, comm, user, answer_requests, highlight_map):
    """
    aux func to create the list of context to create the side list of question sets on the fingerprint view
    """
    qreturned = []

    for questionset in qs_list:
        try:
            qsc = QuestionSetCompletion.objects.get(fingerprint=fingerprint, questionset=questionset)
        except QuestionSetCompletion.DoesNotExist:
            answered = 0
            possible = 0
            fill = 0
        else:
            answered = qsc.answered
            possible = qsc.possible
            fill = qsc.fill

        qreturned.append(
            [
                questionset,
                answered,
                possible,
                int(fill),
                answer_requests.filter(question__questionset=questionset),
                highlight_map[questionset.id],
                QuestionSetAccessGroups.checkAccess("R", comm, fingerprint, user, questionset),
                QuestionSetAccessGroups.checkAccess("W", comm, fingerprint, user, questionset),
            ]
        )

    return qreturned


def database_edit(request, fingerprint_id, questionnaire_id, community=None, sort_id=1, readonly=False):
    """
    fingerprint full detailed view - showing by default the first question set (as this url does not specify it)
    however, this is also called by other functions which pass the sort_id
    """

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    try:
        this_fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)

        users_db = this_fingerprint.unique_users_string()
        created_date = this_fingerprint.created
        owner_fingerprint = this_fingerprint.community.is_owner(request.user)

        qs_list = this_fingerprint.questionnaire.questionsets().order_by('sortid')

        question_set = get_object_or_404(qs_list, sortid=sort_id)

        # well this doesnt scale well, we should have the database name on the fingerprint
        # it probably will be mitigated by using the descriptor that should be updated on save...
        fingerprint_name = this_fingerprint.findName()

        # mark questionsets that have questions request by other users
        requests = AnswerRequest.objects.filter(fingerprint = this_fingerprint, removed=False)

        highlightMap = {questionset.id: False for questionset in qs_list}
        if readonly:
            highlightMap = getHighlightedList(request, highlightMap, questionnaire_id, fingerprint_id)

        # count questionset filled answers
        qreturned = _get_question_set_list(qs_list, this_fingerprint, comm, request.user, requests, highlightMap)

        if comm.auto_accept:
            draft_checkbox_status = this_fingerprint.draft
        else:
            if hasattr(this_fingerprint, "fingerprintpending"):
                draft_checkbox_status = False
            else:
                draft_checkbox_status = this_fingerprint.draft

        r = r2r("database_edit.html", request,
                questionnaire=this_fingerprint.questionnaire,
                questionset=question_set,
                questionsets=qreturned,
                globalprogress = this_fingerprint.fill,
                runinfo=None,
                errors=None,
                progress=None,
                fingerprint_id=fingerprint_id,
                fingerprint=this_fingerprint,
                draft_checkbox_status=draft_checkbox_status,
                hits=this_fingerprint.hits,
                q_id = questionnaire_id,
                sort_id = sort_id,
                async_progress=None,
                async_url=None,
                qs_list=qs_list,
                breadcrumb=True,
                name=fingerprint_name.encode('utf-8'),
                id=fingerprint_id,
                users_db=users_db,
                owner_fingerprint=owner_fingerprint,
                usrs=this_fingerprint.unique_users(),
                created_date=created_date,
                hide_add=True,
                readonly=readonly,
                comm=comm
        )
        r['Cache-Control'] = 'no-cache'
        r['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"

        return r

    except Fingerprint.DoesNotExist:
        print("-- Error obtaining fingerprint", fingerprint_id)

    # Something is really wrong if we get here...
    return HttpResponse('Error open edit for fingerprint '+str(fingerprint_id), status=500)


def database_detailed_view(request, fingerprint_id, questionnaire_id, community=None):
    return database_edit(request, fingerprint_id, questionnaire_id, community, readonly=True)


def database_detailed_view_dl(request, fingerprint_id, questionnaire_id, sort_id, community=None):
    """
    detailed view with direct linking to questionset
    """
    return database_edit(request, fingerprint_id, questionnaire_id, community, sort_id=sort_id, readonly=True)


def database_detailed_qs(request, fingerprint_id, questionnaire_id, sort_id):
    if not hasFingerprintPermissions(request, fingerprint_id):
        raise PermissionDenied

    this_fp = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)

    qs_list = this_fp.questionnaire.questionsets()
    question_set = qs_list.get(sortid=sort_id)

    allow_qset_read = QuestionSetAccessGroups.checkAccess("R", this_fp.community, this_fp, request.user, question_set)

    if allow_qset_read:
        response = render_one_questionset(
            request,
            questionnaire_id,
            sort_id,
            community=this_fp.community.slug if this_fp.community else None,
            fingerprint_id=fingerprint_id,
            is_new=False,
            readonly=True,
            template_name='fingerprint_add_qs.html')
    else:
        return fingerprint_page_access_denied(request, template_name='access_denied.html')

    logger.debug("database_detailed_qs ... ");
    return response


def fingerprint_page_access_denied(request, template_name):
    r = r2r(template_name, request, access_denied=True)
    r['Cache-Control'] = 'no-cache'
    r['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"
    return r
    
def show_fingerprint_page_read_only(request, q_id, qs_id, SouMesmoReadOnly=False, aqid=None, errors={}, template_name='advanced_search.html', comm=None):

    """
    Return the QuestionSet template

    Also add the javascript dependency code.
    """
    # Getting first timestamp

    activemenu = ''
    activesubmenu = ''

    if template_name == "database_add.html" :
        hide_add = True
        activemenu = 'add'

    else:
        hide_add = False
        activesubmenu=''
        activemenu = ''

    serialized_query = None

    if template_name == 'advanced_search.html' and aqid != None:
        this_query = AdvancedQuery.objects.get(id=aqid)
        serialized_query = this_query.serialized_query
    try:
        quest = Questionnaire.objects.get(id=q_id)

        activesubmenu = quest.id

        qs_list = quest.questionsets()

        if (int(qs_id) == 99):
            qs_id = len(qs_list) - 1
            
        question_set = qs_list[int(qs_id)]

        questions = question_set.questions()

        questions_list = {}
        for qset_aux in qs_list:
            questions_list[qset_aux.id] = qset_aux.questions()

        fingerprint_id = generate_hash()

        #### Find out about the number of answers serverside
        qreturned = []
        for x in qs_list:
            ttct = x.total_count()
            ans = 0
            percentage = 0
            allow_qset_reading = QuestionSetAccessGroups.checkAccess("R", comm, None, request.user, x)
            qreturned.append([x, ans, ttct, percentage, allow_qset_reading])
        #### End of finding out about the number of answers serverside

        if template_name == "database_add.html" and comm and comm.questionnaires.all().count() == 1:
            activemenu = 'databases'
            activesubmenu = 'add'

        if template_name == "advanced_search.html":
            activemenu = 'databases'
            activesubmenu = 'search-{}'.format(quest.slug)

        r = r2r(template_name, request,
                        questionset=question_set,
                        questionnaire=quest,
                        globalprogress = 0,
                        questionsets=qreturned,
                        runinfo=None,
                        progress=None,
                        async_progress=None,
                        async_url=None,
                        qs_list=qs_list,
                        fingerprint_id=fingerprint_id,
                        breadcrumb=True,
                        hide_add=hide_add,
                        q_id=q_id,
                        aqid=aqid,
                        comm=comm,
                        activemenu=activemenu,
                        activesubmenu=activesubmenu,
                        serialized_query=serialized_query)
        r['Cache-Control'] = 'no-cache'

        r['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"


    except:
        raise

    return r

def database_add_qs(request, fingerprint_id, questionnaire_id, sortid, community=None):

    response = render_one_questionset(request, questionnaire_id, sortid, community=community, fingerprint_id= fingerprint_id,
                                               template_name='fingerprint_add_qs.html')

    return response

def database_edit_qs(request, fingerprint_id, questionnaire_id, sort_id):
    if not hasFingerprintPermissions(request, fingerprint_id):
        raise PermissionDenied

    this_fp = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)
    

    qs_list = this_fp.questionnaire.questionsets()
    question_set = qs_list.get(sortid=sort_id)

    allow_qset_write = QuestionSetAccessGroups.checkAccess("W", this_fp.community, this_fp, request.user, question_set)

    if allow_qset_write:
        response = render_one_questionset(
            request,
            questionnaire_id,
            sort_id,
            community=this_fp.community.slug if this_fp.community else None,
            fingerprint_id=fingerprint_id,
            is_new=False,
            template_name='fingerprint_add_qs.html')
    else:
        return fingerprint_page_access_denied(request, template_name='access_denied.html')

    return response

def render_one_questionset(request, questionnaire_id, questionset_id, community=None, errors={}, advancedquery_id=None, fingerprint_id=None, is_new=True, readonly = False, advanced_search=False, template_name='fingerprint_add_qs.html'):
    """
    Return the QuestionSet template

    Also add the javascript dependency code.
    """
    this_fingerprint = None
    is_advanced_query_result_page = False

    comm = None
    if not request.user.is_anonymous():
        if community is not None:
            comm = getComm(community, request.user)

    # In case we should be getting an advancedquery
    if advancedquery_id != None:
        this_query = AdvancedQuery.objects.get(id=advancedquery_id)
        this_answers = AdvancedQueryAnswer.objects.filter(refquery=this_query)

        request.POST = request.POST.copy()
        for answer in this_answers:
            request.POST[answer.question] = answer.answer

    if fingerprint_id != None and not is_new:
        
        try:
            this_fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)

            this_answers = Answer.objects.filter(fingerprint_id=this_fingerprint)

            request.POST = request.POST.copy()

            h = None
            rHighlights = None
            qhighlights = None

            if "query" in request.session and "highlight_results" in request.session:
                h = request.session["highlight_results"]
                is_advanced_query_result_page = True

            if h != None:
                if "results" in h and fingerprint_id in h["results"]:
                    rHighlights = h["results"][fingerprint_id]
                if "questions" in h:
                    qhighlights = h["questions"]

            qhid_general = "questionaire_"+str(this_fingerprint.questionnaire.pk)
            for answer in this_answers:
                this_q  = answer.question
                value   = answer.data

                if "[" in str(value):
                    value = str(value).replace("]", "").replace("[", "")

                slug = this_q.slug_fk.slug1

                if readonly:
                    if this_q.type == "publication":
                        if rHighlights is not None and slug+"_txt" in rHighlights:
                            value = [pub.encode('utf-8')for pub in rHighlights[slug+"_txt"]]
                            value = [
                                dict(zip(
                                    ("pmid", "title", "authors", "year", "journal", "link"),
                                    pub.split("$$$")
                                ))
                                for pub in value
                            ]
                            value = json.dumps(value)
                    else:
                        if rHighlights is not None and slug+"_s" in rHighlights:
                            value = rHighlights[slug+"_s"][0].encode('utf-8')

                    qhid = "questionaire_"+str(this_fingerprint.questionnaire.pk)
                    qhslug = "%s_qs"%slug

                    if qhighlights != None and qhid in qhighlights and qhslug in qhighlights[qhid]:
                        request.POST['qhighlight_question_%s' % this_q.number] = qhighlights[qhid][qhslug][0].encode('utf-8')

                request.POST['question_%s' % this_q.number] = value

                if answer.comment != None:
                    request.POST['comment_question_%s' % this_q.number] = answer.comment

                # This "extra" field was on the old solr version, i will admit, i have no clue wth this does...
                # it doesn't seem to make any difference as far as i could check, anyway i left it here commented
                # in case we need it after all
                #extra[this_q] = ans = extra.get(this_q, {})
                #ans['ANSWER'] = value
                #extra[this_q] = ans

        except Fingerprint.DoesNotExist:
            print("-Error fingerprint", fingerprint_id, "does not exist but we think it does.")
    
    try:
        quest = Questionnaire.objects.get(id=questionnaire_id)
        qs_list = quest.questionsets().filter(sortid=questionset_id).order_by('sortid')

        if (int(questionset_id) == 99):
            questionset_id = len(qs_list) - 1
        question_set = qs_list[0]
        #questions = Question.objects.filter(questionset=questionset_id)

        questions = question_set.questions()

        questions_list = {}
        for qset_aux in qs_list:
            #questions_aux = Question.objects.filter(questionset=qset_aux)
            questions_list[qset_aux.id] = qset_aux.questions()

        qlist = []
        jsinclude = []      # js files to include
        cssinclude = []     # css files to include
        jstriggers = []
        qvalues = {}

        qlist_general = []

        for k in qs_list:
            qlist = []
            qs_aux = None
            for question in questions_list[k.id]:
                qs_aux = question.questionset

                Type = question.get_type()
                _qnum, _qalpha = split_numal(question.number)

                qdict = {
                    'template': 'questionnaire/%s.html' % (Type),
                    'qnum': _qnum,
                    'qalpha': _qalpha,
                    'qtype': Type,
                    'qnum_class': (_qnum % 2 == 0) and " qeven" or " qodd",
                    'qalpha_class': _qalpha and (ord(_qalpha[-1]) % 2 \
                                                     and ' alodd' or ' aleven') or '',
                }

                # add javascript dependency checks
                cd = question.getcheckdict()
                depon = cd.get('requiredif', None) or cd.get('dependent', None)
                if depon:
                    #It allows only 1 dependency
                    #The line above allows multiple dependencies but it has a bug when is parsing white spaces
                    qdict['checkstring'] = ' checks="dep_check(\'question_%s\')"' % depon

                    qdict['depon_class'] = ' depon_class'
                    jstriggers.append('qc_%s' % question.number)
                    if question.text[:2] == 'h1':
                        jstriggers.append('acc_qc_%s' % question.number)
                if 'default' in cd and not question.number in cookiedict:
                    qvalues[question.number] = cd['default']
                if Type in QuestionProcessors:
                    qdict.update(QuestionProcessors[Type](request, question))
                    if 'jsinclude' in qdict:
                        if qdict['jsinclude'] not in jsinclude:
                            jsinclude.extend(qdict['jsinclude'])
                    if 'cssinclude' in qdict:
                        if qdict['cssinclude'] not in cssinclude:
                            cssinclude.extend(qdict['jsinclude'])
                    if 'jstriggers' in qdict:
                        jstriggers.extend(qdict['jstriggers'])
                        #if 'qvalue' in qdict and not question.number in cookiedict:
                        #    qvalues[question.number] = qdict['qvalue']

                qlist.append((question, qdict))
            if qs_aux == None:
                qs_aux = k
            qlist_general.append((qs_aux, qlist))

        errors = {}

            # extracting answers
            #-- (removed unnecessary code) --
        if fingerprint_id != None and not is_new or advancedquery_id != None:
            (qlist_general, qlist, jstriggers, qvalues, jsinclude, cssinclude, extra_fields, hasErrors) = extract_answers(request, questionnaire_id, question_set, qs_list)

        permissions = None
        if this_fingerprint != None:
            permissions = this_fingerprint.getPermissions(question_set)

        if template_name == 'fingerprint_search_qs.html':
            advanced_search = True

        ansrequests = []
        if is_new == False and readonly == False:
            ansrequests = AnswerRequest.objects.filter(fingerprint = this_fingerprint, question__questionset__sortid=questionset_id, removed = False)

        # check if is a new fingerprint that is being added, else it is a view/edit of an existing one
        if is_new:
            prevAccessibleQuestionSet = question_set.prev()
            nextAccessibleQuestionSet = question_set.next()
        else:
            accessMode = "R" if readonly else "W"
            accessMode = "R" if advanced_search else accessMode
            prevAccessibleQuestionSet = QuestionSetAccessGroups.getPreviousAccessibleQuestionSet(accessMode, comm, this_fingerprint, request.user, question_set)
            nextAccessibleQuestionSet = QuestionSetAccessGroups.getNextAccessibleQuestionSet(accessMode, comm, this_fingerprint, request.user, question_set)

        r = r2r(template_name, request,
                community=community,
                questionnaire=quest,
                questionset=question_set,
                depmap = json.dumps(question_set.dependency_tree()),
                questionsets=question_set.questionnaire.questionsets,
                runinfo=None,
                errors=errors,
                qlist=qlist,
                progress=None,
                triggers=jstriggers,
                qvalues=qvalues,
                jsinclude=jsinclude,
                cssinclude=cssinclude,
                async_progress=None,
                async_url=None,
                qs_list=qs_list,
                advanced_search = advanced_search,
                questions_list=qlist_general,
                fingerprint_id=fingerprint_id,
                breadcrumb=True,
                permissions=permissions,
                readonly=readonly,
                aqid = advancedquery_id,
                answer_requests = ansrequests,
                is_advanced_query_result_page=is_advanced_query_result_page,
                prevAccessibleQuestionSet=prevAccessibleQuestionSet,
                nextAccessibleQuestionSet=nextAccessibleQuestionSet
        )

        r['Cache-Control'] = 'no-cache'
        r['Expires'] = "Thu, 24 Jan 1980 00:00:00 GMT"

    except:

        raise
    return r

def check_database_add_conditions(request, questionnaire_id, sortid, saveid, community=None,
                                  template_name='database_add.html', users_db=None, created_date=None):
    # -------------------------------------
    # --- Process POST with QuestionSet ---
    # -------------------------------------

    fingerprint_id = request.POST['fingerprint_id']

    questionnaire = qsobjs = None
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        qsobjs = questionnaire.questionsets()

    except Questionnaire.DoesNotExist:
        raise Exception("Can't find questionnaire on check_database_add_conditions")

    question_set = None
    saveqs = None

    try:
        question_set = request.POST['active_qs']
        sortid = request.POST['active_qs_sortid']
    except:
        for qs in qsobjs:
            if qs.sortid == int(sortid):
                question_set = qs.pk
                break

    for qs in qsobjs:
        if qs.sortid == int(saveid):
            saveqs = [qs]
            break

    if (int(sortid) == 99):
            sortid = len(questionnaire.questionsets()) - 1

    qs_index = int(sortid) - 1
    question_set2 = qsobjs[qs_index]

    if request.POST:
        (qlist_general, qlist, jstriggers, qvalues, jsinclude, cssinclude, extra_fields, hasErrors) = extract_answers(request, questionnaire_id, question_set2, saveqs)
    else:
        (qlist_general, qlist, jstriggers, qvalues, jsinclude, cssinclude, extra_fields, hasErrors) = extract_answers(HttpRequest(), questionnaire_id, question_set2, saveqs)

    if fingerprint_id is not None:
        if users_db is None:
            users_db = request.user.username

        if not hasErrors:
            add_city(qlist_general)

            comm = None
            if community is not None:
                comm = getComm(community, request.user)
                if(isinstance(comm, HttpResponseRedirect)):
                    return comm

            success = saveFingerprintAnswers(qlist_general, fingerprint_id, question_set2.questionnaire, users_db, extra_fields=extra_fields, created_date=created_date, community=comm)

            if not success:

                qs = -1
                try :
                    qs = question_set2.questionnaire.findMandatoryQs().sortid
                except:
                    pass
                return JsonResponse({'mandatoryqs': qs})

            if request and request.POST:
                fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)
                # I perform a .get() here since the fingerprint must be already created
                #  after the saveFingerprintAnswers function above
                setNewPermissions(request, fingerprint, sortid)

            # new version that just serializes the created fingerprint object (this eventually can be done using celery)
            #indexFingerprintCelery.delay(fingerprint_id)

    return JsonResponse({'success': 'true'})


class ImportFingerprintView(TemplateView):
    template_name = "fingerprint_import.html"

    def __importFingerprintFromFile(self, upfile, user, filename, force_qtype, qtype, force_community) :
        qi = FingerprintImportFile(file=upfile, uploader=user, filename=filename)
        qi.save()
        importFingerprint.apply_async([qi.id, force_qtype, qtype, force_community])

    def get(self, request, success_message=None, error_message=None):
        if(not (request.user.is_superuser or request.user.groups.filter(name='importers').exists())):
            return HttpResponse('Forbidden', 403)

        qsts = Questionnaire.objects.filter(disable=False)
        communities = Community.objects.all()
        communityOutputArray = []
        for community in communities :
            questionnaireStrSlugs = "|".join( o.slug for o in community.questionnaires.all() )
            communityOutputArray.append({
                "name" : community.name,
                "slug" : community.slug,
                "questionnaireStrSlugs" : questionnaireStrSlugs
            })

        quploads = FingerprintImportFile.objects.filter(uploader=request.user).order_by('-id')[:10]

        comm = None
        if settings.SINGLE_COMMUNITY:
            comm = Community.objects.all()[:1].get()

        return render(request, self.template_name,
            {
                'request': request,
                'activemenu': 'import',
                'activesubmenu': 'fingerprint',
                'success_message': success_message,
                'error_message': error_message,
                'questionnaires': qsts,
                'communities': communityOutputArray,
                'breadcrumb': True,
                'quploads': quploads,
                'comm': comm
            })

    def post(self, request):
        try:
            uploaded_file = request.FILES['file']
            name_array = uploaded_file.name.split(".")
            extension = name_array[len(name_array) - 1]
            force_qtype = "on"
            qtype = request.POST.get('questionnaire', None)
            force_community = request.POST.get('community', None)

            if extension not in [ "montra", "multimontra" ]:
                return self.get(request, error_message="Error importing Fingerprint. File extension must be .montra or .multimontra.")

            if extension == "multimontra":

                with zipfile.ZipFile(uploaded_file) as zip_file:                  
                    for zip_file_child_info in zip_file.infolist():                   
                        zip_file_child = zip_file.extract(zip_file_child_info)
                        file_child = open(zip_file_child)
                        self.__importFingerprintFromFile(File(file_child), request.user, zip_file_child_info.filename, force_qtype, qtype, force_community)
                        os.remove(zip_file_child)

            else:
                self.__importFingerprintFromFile(uploaded_file, request.user, uploaded_file.name, force_qtype, qtype, force_community)

            return self.get(request, success_message="Fingerprint importing asynchrounsly and will be briefly available. To import another fingerprint please add it below.")
            
        except:
            return self.get(request, error_message="Error importing Fingerprint. Make sure you are importing a .montra or .multimontra file with a fingerprint export. If the problem persists please try again later, or contact the administrator.")



#####################################################################################################
#### Fingerprint Readonly methods 
#####################################################################################################



def single_qset_view(request, runcode, qsid, template_name='fingerprint_qs.html'):
    return single_qset_view_community(request, None, runcode, qsid, template_name)

def single_qset_view_community(request, community, runcode, qsid, template_name='fingerprint_qs.html'):

    if not hasFingerprintPermissions(request, runcode):
        raise PermissionDenied

    h = None
    if "query" in request.session and "highlight_results" in request.session:
        h = request.session["highlight_results"]
    #if "query" in request.session and "highlight_results" in request.session and runcode in request.session["highlight_results"]:
    #    h =  merge_highlight_results(request.session["query"] , request.session["highlight_results"][runcode])

    qset, name, db_owners, fingerprint_ttype = createqset(runcode, qsid, highlights=h)

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm
    this_fingerprint = Fingerprint.objects.get(fingerprint_hash=runcode)
    qs_list = this_fingerprint.questionnaire.questionsets()
    question_set = qs_list.get(sortid=qsid)

    allow_qset_read = QuestionSetAccessGroups.checkAccess("R", comm, this_fingerprint, request.user, question_set)
    
    if allow_qset_read:
        return render(request, template_name,{'request': request, 'qset': qset, 'fingerprint_id': runcode})
    else:
        return fingerprint_page_access_denied(request, template_name='access_denied.html')


def document_form_view(request, runcode, qs, activetab='summary', readOnly=False, public_key = None):

    return document_form_view_comm(request, None, runcode, qs, activetab, readOnly, public_key)


def document_form_view_comm_first_qset(request, community, runcode=None, activetab='summary', readOnly=False, public_key = None, force=False):
    comm = getComm(community, request.user, force=force)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm
    
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=runcode)
        # go to the user's first allowed questionnaire section
        firstReadableQuestionSet = QuestionSetAccessGroups.getFirstAccessibleQuestionSet("R", comm, fingerprint, request.user)
    except Exception as e:
        logger.error("Problem while openning fingerprint (not found) " + runcode);
        raise Http404

    # by default send user to second questionnaire section, (index 1)
    # since is the first section with questions
    firstReadableQuestionSet_sortid = 1
    
    if firstReadableQuestionSet != None:
        firstReadableQuestionSet_sortid = firstReadableQuestionSet.sortid

    return document_form_view_comm(request, community, runcode, firstReadableQuestionSet_sortid, activetab, readOnly, public_key)


def document_form_view_comm(request, community, runcode, qs, activetab='summary', readOnly=False, public_key = None, force=False):

    comm = getComm(community, request.user, force=force)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    # ********************************************************************
    # ** Manage/Edit CommunityDatabasePermission popup form processor
    # ********************************************************************
    '''
    if 'medit' in request.POST:
        print "&&& -> Manage/Edit permissions &&&"
        cps = CommunityDatabasePermission.objects.filter(communitygroup__community=comm)

        cps.update(allow=False)

        for key in request.POST:
            if key.startswith('elem_'):
                kid = int(key[5:])

                try:
                    cp = cps.get(id=kid)

                    cp.allow=True
                    cp.save()

                except CommunityDatabasePermission.DoesNotExist:
                    pass
    '''
    # ********************************************************************

    h = None

    if "query" in request.session and "highlight_results" in request.session:
        h = request.session["highlight_results"]

    # GET fingerprint primary key (for comments)
    fingerprint = None
    
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=runcode)
        fingerprint_pk = fingerprint.id
        questionnaire = fingerprint.questionnaire
    except:
        logger.error("Problem while openning fingerprint (not found) " + runcode);
        fingerprint_pk = 0
        raise Http404

    qsets, name, db_owners, fingerprint_ttype = createqsets(runcode, highlights=h)

    if fingerprint_ttype == "":
        raise "There is a missing type of questionnarie, something is really wrong"

    try:
        if (not request.user.is_anonymous()):
            eprofile = EmifProfile.objects.get(user=request.user)

            if eprofile.restricted == True:
                if not eprofile.has_permission(runcode):
                    raise PermissionDenied


    except EmifProfile.DoesNotExist:
        raise "-- ERROR: Couldn't get emif profile for user"


    apiinfo = json.dumps(get_api_info(runcode))
    owner_fingerprint = False

    for owner in db_owners.split(" "):
        if (owner == request.user.username):
            owner_fingerprint = True

    query_old = None
    try:
        query_old = request.session.get('query', "")
    except:
        query_old = None

    name_bc = name
    try:
        name_bc = name.encode('utf-8')
    except:
        pass

    isAdvanced = None

    if(request.session.get('isAdvanced') == True):
        isAdvanced = True
    else:
        isAdvanced = False

    qsets = attachPermissions(runcode, qsets)
    
    jerboa_files = Characteristic.objects.filter(fingerprint_id=runcode).order_by('-latest_date')


    contains_population = False
    latest_pop = None
    if len(jerboa_files)!=0:
        contains_population = True
        latest_pop = jerboa_files[0]



    # Find if user has public links for this db.

    public_links = None

    if (owner_fingerprint or request.user.is_staff) and fingerprint != None:
        public_links = PublicFingerprintShare.objects.filter(user=request.user, fingerprint=fingerprint)

    # increase database hits
    hits = 0
    if fingerprint != None:
        hits = fingerprint.hits+1
        fingerprint.hits = hits
        fingerprint.save()

    subscription = False

    try:
        if (not request.user.is_anonymous()):
            subs = FingerprintSubscription.objects.get(user = request.user, fingerprint = fingerprint)

            subscription = not subs.removed

    except FingerprintSubscription.DoesNotExist:
        pass

    plugins = []
    if comm and public_key is None:
        plugins = [
            plugin
            for plugin in PluginVersion
                            .all_valid(type=Plugin.DATABASE)
                            .filter(plugin__in=comm.plugins.all())
                            .order_by('plugin__id')
            if PluginPermission.check_permission(comm, request.user, plugin, fingerprint)
        ]

    logger.debug("authorized plugins: " + str(plugins))

    users_db = fingerprint.unique_users_string()
    created_date = fingerprint.created

    qs_list = fingerprint.questionnaire.questionsets().order_by('sortid')
    
    try:
        question_set = qs_list.get(sortid=qs)
    except Exception as e:
        logger.error("Problem while openning fingerprint (not found) " + runcode + " questionsets was not found ");
        logger.error(e, exc_info=True)
        raise Http404

    # mark questionsets that have questions request by other users
    requests = AnswerRequest.objects.filter(fingerprint = fingerprint, removed=False)

    highlightMap = {questionset.id: False for questionset in qs_list}
    highlightMap = getHighlightedList(request, highlightMap, fingerprint.questionnaire.id, runcode)

    # count questionset filled answers
    qreturned = _get_question_set_list(qs_list, fingerprint, comm, request.user, requests, highlightMap)

    if query_old:
        asm = 'search'
    elif request.session.get('list_origin', None) == 'personal':
        asm = 'personal'
    else:
        asm = 'all'

    cgroups = []
    matrix = None
    if owner_fingerprint or request.user.is_staff:
        cgroups = CommunityGroup.valid(community = comm)
        matrix = buildPermissionsMatrix(comm, cgroups)

    filled_plugins = PluginFingeprint.objects.filter(fingerprint=fingerprint,empty=False).values_list('plugin__slug', flat=True)
    empty_plugins = PluginFingeprint.objects.filter(fingerprint=fingerprint,empty=True).values_list('plugin__slug', flat=True)
    
    if len(filled_plugins)>0:
        filled_plugins = [str(x) for x in filled_plugins]
    if len(empty_plugins)>0:
        empty_plugins = [str(x) for x in empty_plugins]
    
    cu = None
    try:
        cu = CommunityUser.objects.get(community=comm, user=request.user)
    except CommunityUser.DoesNotExist:
        pass
    except: 
        # Anonymous user - it is a public link
        pass 
    
    is_preview = request.GET.get('preview')
    if not hasattr(fingerprint, 'preview_questionnaire'):
        # It's a regular fingerprint
        is_preview = False
    else:
        if not fingerprint.preview_questionnaire.in_preview:
            # It's a preview fingerprint but it has already been accepted so we
            # don't need to display the management buttons.
            is_preview = False

    pageResult = render(request, 'database_info.html',
        {   'request': request,
            'qsets': qsets,
            'export_bd_answers': True,
            'apiinfo': apiinfo,
            'fingerprint_id': runcode,
            'ugroup': cgroups,
            'matrix': matrix,
            'fingerprint': fingerprint,
            'fingerprint_pk': fingerprint_pk,
            'fingerprint_fill': int(round(fingerprint.fill)),
            'breadcrumb': True, 'breadcrumb_name': name_bc.decode('utf-8'),
            'style': qs, 'collapseall': False,
            'owner_fingerprint':owner_fingerprint,
            'owners': db_owners,
            'owner_obj': fingerprint.owner,
            'shared_obj': fingerprint.shared,
            'fingerprint_dump': True,
            'contains_population': contains_population,
            'latest_pop': latest_pop,
            'hide_add': True,
            'fingerprint_ttype': fingerprint_ttype,
            'search_old': query_old,
            'isAdvanced': isAdvanced,
            'activetab': activetab,
            'readOnly': readOnly,
            'public_link': public_links,
            'public_key': public_key,
            'hits': hits,
            'subscription': subscription,
            'plugins': plugins,
            'comm': comm,
            'questionnaire': questionnaire,
            'comm_user': cu,
            'user': request.user,
            'questionset': question_set,
            'activemenu': 'databases',
            'activesubmenu': asm,
            'questionsets': qreturned,
            'globalprogress': fingerprint.fill,
            'q_id': fingerprint.questionnaire.id,
            'sort_id': qs,
            'qs_list': qs_list,
            'id': runcode,
            'users_db': users_db,
            'created_date': created_date,
            'filled_plugins': filled_plugins,
            'empty_plugins': empty_plugins,
            'is_preview': is_preview,
        })
    return pageResult
