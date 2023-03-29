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
##
#   See user history of queries
##
from django.core.paginator import PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from community.models import QuestionSetAccessGroups
from community.utils import getComm
from emif.models import AdvancedQuery, AdvancedQueryAnswer
from emif.models import QueryLog
from fingerprint.listings import results_diff
from fingerprint.views import fingerprint_page_access_denied, render_one_questionset, show_fingerprint_page_read_only
from questionnaire.models import Questionnaire


def advanced_search(request, questionnaire_id, question_set, aqid):
    return advanced_search_comm(request, None, questionnaire_id, question_set, aqid)

def advanced_search_comm(request, community, questionnaire_id, question_set, aqid):
    try:
        del request.session['isAdvanced']
        del request.session['query']
        del request.session['serialized_query']
    except:
        pass

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    return show_fingerprint_page_read_only(request, questionnaire_id, question_set, True, aqid, comm=comm)


def database_search_qs(request, questionnaire_id, sortid, aqid):
    return database_search_qs_comm(request, None, questionnaire_id, sortid, aqid)

def database_search_qs_comm(request, community, questionnaire_id, sortid, aqid):
    
    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    if comm != None:
        qs_list = Questionnaire.objects.get(id=questionnaire_id).questionsets()
        question_set = qs_list.get(sortid=sortid)

        allow_qset_read = QuestionSetAccessGroups.checkAccess("R", comm, None, request.user, question_set)

        if allow_qset_read:
            response = render_one_questionset(request, questionnaire_id, sortid, community, advancedquery_id=aqid, is_new=False, advanced_search=True,
                                                template_name='fingerprint_search_qs.html')
        else:
            return fingerprint_page_access_denied(request, template_name='access_denied.html')

    else:
        response = render_one_questionset(request, questionnaire_id, sortid, community=None, advancedquery_id=aqid, is_new=False, advanced_search=True,
                                               template_name='fingerprint_search_qs.html')

    return response

def history_defer(request, template_name='history.html'):
    return history(request, '0', 1)

def history_defer_advanced(request, template_name='history.html'):
    return history(request, '1', 1)

def history(request, source, page, page_rows=10, template_name='history.html'):

    if not request.user.is_authenticated():
        return HttpResponse( "Must be logged in to see query history", status=403)

    queries = AdvancedQuery.objects.filter(user=request.user, removed=False, title__isnull=False).order_by('-date')

        ## Paginator ##
    if(request.method == 'POST'):
        try:
            page_rows = int(request.POST.get('paginator_rows', 10))

            request.session['paginator_rows'] = page_rows
        except:
            pass
    else:
        try:
            page_rows = int(request.session['paginator_rows'])
        except:
            pass

    simple_queries = QueryLog.objects.filter(user=request.user, removed = False).order_by('-created_date')

    myPaginator = Paginator(simple_queries, page_rows)

    myadvancedPaginator = Paginator(queries, page_rows)

    if source == '0':
        try:
            pager_simple =  myPaginator.page(page)
        except PageNotAnInteger, e:
            pager_simple =  myPaginator.page(1)

        pager = myadvancedPaginator.page(1)

    else:

        try:
            pager =  myadvancedPaginator.page(page)
        except PageNotAnInteger, e:
            pager =  myadvancedPaginator.page(1)

        pager_simple = myPaginator.page(1)

    return render(request, template_name, {'request': request, 'source': source, 'breadcrumb': True, 'queries_simple': pager_simple, 'queries': pager, 'page_rows':page_rows})


def resultsdiff_history(request, query_id):
    query = get_object_or_404(AdvancedQuery, id=query_id)

    this_answers = AdvancedQueryAnswer.objects.filter(refquery=query)

    request.POST = request.POST.copy()
    request.POST['qid'] = str(query.qid.id)
    request.POST['boolrelwidget-boolean-serialization'] = query.serialized_query

    for answer in this_answers:
        request.POST[answer.question] = answer.answer

    return results_diff(request, opening_saved=True)


def resultsdiff_historysimple(request, query_id):
    query = get_object_or_404(QueryLog, id=query_id)

    request.POST = request.POST.copy()
    request.POST["query"] = query.query

    return results_diff(request, opening_saved=True)


def remove(request, query_id):
    if not request.user.is_authenticated():
        raise Http404

    try:
        query = AdvancedQuery.objects.get(id=query_id)

        query.removed = True

        query.save()

    except:
        print '-- Error: Cant find advanced query with id '+str(query_id)
        pass

    request.session['deleted_query_id'] = True
    return redirect('advancedsearch.views.history_defer_advanced')

def removesimple(request, query_id):
    if not request.user.is_authenticated():
        raise Http404

    try:
        query = QueryLog.objects.get(id=query_id)

        query.removed = True

        query.save()

    except:
        print '-- Error: Cant find free text query with id '+str(query_id)
        pass

    request.session['deleted_query_id'] = True
    return redirect('advancedsearch.views.history_defer')

def remove_all(request):
    if not request.user.is_authenticated():
        raise Http404

    queries = AdvancedQuery.objects.filter(user=request.user)

    queries.update(removed=True)

    '''for query in queries:
        query.removed = True

        query.save()'''

    request.session['deleted_query_id'] = True
    return redirect('advancedsearch.views.history_defer_advanced')

def remove_allsimple(request):
    if not request.user.is_authenticated():
        raise Http404

    queries = QueryLog.objects.filter(user=request.user)

    for query in queries:
        query.removed = True

        query.save()

    request.session['deleted_query_id'] = True
    return redirect('advancedsearch.views.history_defer')
