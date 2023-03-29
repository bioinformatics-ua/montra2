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

import hashlib
import json
import logging

from constance import config
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, Paginator
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework.authtoken.models import Token

from accounts.models import EmifProfile, RestrictedGroup, RestrictedUserDbs
from community.models import Community, CommunityGroup, CommunityUser
from community.utils import getComm
from developer.serializers import CommunityFieldsSerializer, CommunitySerializer
from emif.models import AdvancedQuery, AdvancedQueryAnswer, QueryLog
from emif.utils import convert_query_from_boolean_widget, escapeSolrArg
from emif.utils import get_community_field_from_entry, removehs
from questionnaire.models import Question, Questionnaire
from searchengine.search_indexes import CoreEngine
from .models import Database, Fingerprint
from .models import FingerprintPending
from .services import define_rows, merge_highlight_results
from .tasks import anotateshowonresults

logger = logging.getLogger(__name__)


def query_solr(request, page=1):
    return query_solr_comm(request, None, page)

def query_solr_comm(request, community, page=1):
    if not request.POST:
        return Http404

    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    # Get the list of databases for a specific user
    _filter = request.POST["filter"].replace('&quot;', '"');

    qop = 'AND'

    if _filter.startswith('id:('):
        qop = 'OR'

    rows = 5
    if page == None:
        page = 1

    if comm:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows, extraFields=comm.list_fields.all())
    else:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows)

    if len(filterString) > 0:
        if len(_filter) > 0:
            _filter += " AND "

        _filter += filterString

    if comm != None:

        _filter = _addSolrSlugsToStr(comm, _filter)


    (list_databases,hits) = get_databases_from_solr_v2(request, _filter, sort=sortString, rows=rows, start=range, qop=qop)

    list_databases = paginator_process_list(list_databases, hits, range)

    ret = {}
    ret["Hits"] = hits
    ret["Start"] = range
    ret["Rows"] = rows
    ret["Filter"] = filterString
    if range > hits:
        ret["Rec_Page"] = 1
    else:
        ret["Rec_Page"] = page

    return JsonResponse(ret)

def _addSolrSlugsToStr(comm, filter):
    comm_slugs = comm.getSolrSlugs()
    
    if comm_slugs:
        if len(filter) > 0 :
            filter += " AND "

        filter += comm_slugs
    
    return filter

def get_searchfield(user):
    try:
        stype = user.emif_profile.search_type
        if stype == 'all':
            return 'all_txt:'

        elif stype == 'questions':
            return 'questions_txt:'

    except:
        pass


    return 'text_txt:'


def results_fulltext(request, page=1, full_text=True,template_name='results.html', isAdvanced=False, query_reference=None, advparams=None, comm=None, questionnaire=None, default_mode=None):
    query = ""
    in_post = True
    fq = ''

    (rows, search_type) = define_rows(request)
    try:
        query = request.POST['query']
        request.session['query'] = query
    except:
        in_post = False

    if not in_post:
        query = request.session.get("query","")

    if isAdvanced == False:
        #query = '%s"%s"~10' % (get_searchfield(request.user), escapeSolrArg(query))
        if ' ' in query:
            query = '%s"%s"' % (get_searchfield(request.user), query)
        else:
            query = '%s%s' % (get_searchfield(request.user), query)
        logger.info("Query: "+ query)

    if comm != None:
        fq += comm.getSolrSlugs()

    else:
        cus = CommunityUser.objects.filter(Q(status=CommunityUser.ENABLED) | Q(status=CommunityUser.RESTRICTED), user=request.user)
        # TODO: Here, we should also consider the Open communities.
        if cus.count() > 0:
            cs  = Community.objects.filter(communityuser__in=cus) | Community.objects.filter(public=True)
            cs = cs.distinct()
            first = True
            for com in cs:
                if not first:
                    fq += ' OR '
                else:
                    first=False
                fq += com.getSolrSlugs()


        else:
            if in_post:
                try:
                    query_old = request.POST['query']
                except:
                    query_old = ""
            else:
                query_old = ""
            return render(request, "results.html", {
                'request': request,
                'comm': comm,
                'questionnaire': questionnaire,
                'paginator_view_name': resolve(request.path_info).url_name,
                'breadcrumb': True,  
                'isSearch': True,
                'results': True, 
                'search_old': query_old, 
                'hide_add': True,
                'num_results': 0, 
                'page_obj': None
                })

    if default_mode is None:
        default_mode = {"database_name_t": "asc"}

    return results_fulltext_aux(request, query, page, template_name, isAdvanced=isAdvanced, query_reference=query_reference, advparams=advparams, comm=comm, questionnaire=questionnaire, default_mode=default_mode, fq=fq)


def results_fulltext_aux(request, query, page=1, template_name='results.html', isAdvanced=False, force=False, query_reference=None, advparams=None, comm=None, questionnaire=None, default_mode=None, fq=''):
    (rows, search_type) = define_rows(request)
    if request.POST and "page" in request.POST and not force:
        page = request.POST["page"]

    if page is None:
        page = 1

    if query == "" or query == "text_txt:" or "text_txt: AND" in query or query.strip() == "text_txt:*":
        return render(request, "results.html", {
            'request': request,
            'comm': comm,
            'questionnaire': questionnaire,
            'paginator_view_name': resolve(request.path_info).url_name,
            'breadcrumb': True,  
            'isSearch': True,
            'results': True, 
            'hide_add': True,
            'num_results': 0, 
            'page_obj': None
        })

    #query = query # + " AND " + typeFilter(request.user)

    if default_mode is None:
        default_mode = {"database_name_t": "asc"}

    if comm:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows, extraFields=comm.list_fields.all(), default_mode=default_mode)
    else:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows, default_mode=default_mode)

    sort_params["base_filter"] = query
    query_filtered = query

    if len(filterString) > 0:
        query_filtered += " AND " + filterString

    try:
        hlfl = ",".join(advparams)
    except:
        hlfl = None

    # we need to know the slug of multivalue fields to apply special highlighting configs
    if questionnaire is None:
        if comm is None:
            multivalue_fields = Question.objects.filter(type="publication").values_list("slug", flat=True)
        else:
            multivalue_fields = Question.objects.filter(
                questionset__questionnaire__in=comm.questionnaires.all(),
                type="publication",
            ).values_list("slug", flat=True)
    else:
        multivalue_fields = Question.objects.filter(
            questionset__questionnaire=questionnaire,
            type="publication",
        ).values_list("slug", flat=True)

    if isAdvanced:
        (list_databases, hits, hi) = get_databases_from_solr_with_highlight(request, query_filtered, sort=sortString, rows=rows, start=range, hlfl=hlfl, fq=fq, multivalue_fields=multivalue_fields)
    else:
        (list_databases, hits, hi) = get_databases_from_solr_with_highlight(request, query_filtered, sort=sortString, rows=rows, start=range, fq=fq, multivalue_fields=multivalue_fields)

    if not isAdvanced:
        hi = merge_highlight_results('"{}"'.format(escapeSolrArg(request.session["query"])), hi)
    else:
        hi = merge_highlight_results(None, hi)

    if range > hits and not force:
        return results_fulltext_aux(request, query, 1, isAdvanced=isAdvanced, force=True)

    request.session["highlight_results"] = hi

    community = None
    if comm:
        community = comm.slug

    extra_comm = {'community': community}

    if len(list_databases) == 0:
        query_old = request.session.get('query', "")

        if isAdvanced:
            return render(request, "results.html", {'request': request, 'breadcrumb': True,  'isSearch': True,
                                                'results': True, 'hide_add': True,
                                                'comm': comm,
                                                'questionnaire': questionnaire,
                                                'paginator_view_name': resolve(request.path_info).url_name,
                                                'paginator_extra_view_args': extra_comm,
                                                'extra_comm': extra_comm,
                                                'num_results': 0, 'page_obj': None, 'isAdvanced': True})
        else:
            return render(request, "results.html", {'request': request, 'breadcrumb': True, 'isSearch': True,
                                                'results': True, 'hide_add': True,
                                                'comm': comm,
                                                'questionnaire': questionnaire,
                                                'paginator_view_name': resolve(request.path_info).url_name,
                                                'paginator_extra_view_args': extra_comm,
                                                'extra_comm': extra_comm,
                                                'num_results': 0, 'page_obj': None, 'search_old': query_old, 'isAdvanced': False})

    list_databases = paginator_process_list(list_databases, hits, range)

    # only execute if this if we are not posting back, we dont want to do this on changing page or applying filters
    if request.POST.get('page') is None and query_reference is not None:
        # anotate the databases appearing on results
        anotateshowonresults.delay(query_filtered, request.user, isAdvanced, query_reference)

    myPaginator = Paginator(list_databases, rows)
    try:
        pager = myPaginator.page(page)
    except PageNotAnInteger:
        pager = myPaginator.page(page)

    query_old = request.session.get('query', "")

    if isAdvanced:
        return render(request, template_name, {'request': request,
                                           'num_results': hits, 'page_obj': pager, 'page_rows': rows, 'isSearch': True,
                                           'results': True, 'hide_add': True,
                                           'comm': comm,
                                           'questionnaire': questionnaire,
                                           'paginator_view_name': resolve(request.path_info).url_name,
                                           'paginator_extra_view_args': extra_comm,
                                           'extra_comm': extra_comm,
                                           'breadcrumb': True, 'isAdvanced': True, "sort_params": sort_params, "page":page})
    else:
        return render(request, template_name, {'request': request, 'isSearch': True,
                                           'results': True, 'hide_add': True,
                                           'comm': comm,
                                           'questionnaire': questionnaire,
                                           'paginator_view_name': resolve(request.path_info).url_name,
                                           'paginator_extra_view_args': extra_comm,
                                           'extra_comm':extra_comm,
                                           'num_results': hits, 'page_obj': pager, 'page_rows': rows,'breadcrumb': True, 'search_old': query_old, 'isAdvanced': False, "sort_params": sort_params, "page":page})


def typeFilter(user):
    emifprofile = user.emif_profile
    interests = emifprofile.interests.all()

    type_t_list = ""
    if interests:
        for i in interests:
            type_t = i.slug.replace(" ", "").lower()
            type_t_list+=(type_t + ",")

        type_t_list = type_t_list[:-1]

        return "type_t:" + type_t_list


def store_query(user_request, query_executed):
    query = QueryLog()
    if user_request.user.is_authenticated():
        query.user = user_request.user
    else:
        query.user = None

    query.query = query_executed

    query.save()

    return query


def results_diff(request, community=None, page=1, opening_saved=False):

    # in case the request come's from a advanced search
    comm = getComm(community, request.user)
    quest = None
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    if community:
        request.session['search_origin'] = community
    else:
        request.session['search_origin'] = 'all'

    if request.POST.get("qid") != None:

        request.session['isAdvanced'] = True
        qlist = []
        jsinclude = []      # js files to include
        cssinclude = []     # css files to include
        jstriggers = []
        qvalues = {}
        qexpression = None  # boolean expression
        qserialization = None   # boolean expression serialization to show on results
        qid = None  #questionary id
        if request.POST:
            contador=-1

            for k, v in request.POST.items():
                
                if (len(v)==0):
                    continue
                if k.startswith("question_"):
                    s = k.split("_")
                    if len(s) == 4:
                        if (qvalues.has_key(s[1])):
                            qvalues[s[1]] += " " + v # evaluates true in JS
                        else:
                            
                            qvalues[s[1]] = v # evaluates true in JS
                    elif len(s) == 3 and s[2] == 'comment':
                        qvalues[s[1] + '_' + s[2]] = v
                    else:
                        if (qvalues.has_key(s[1])):
                            qvalues[s[1]] += " " + v
                        else:
                            qvalues[s[1]] = v                            
                elif k == "boolrelwidget-boolean-representation":
                    qexpression = v
                elif k == "boolrelwidget-boolean-serialization":
                    request.session['serialization_query'] = v
                    qserialization = v
                elif k == "qid":
                    qid = v

            if qexpression == None or qserialization == None or qexpression.strip()=="" or qserialization.strip() == "":
                response = HttpResponse()
                response.status_code = 500
                return response

            (query, advparams) = convert_query_from_boolean_widget(qexpression, qid)
            request.session['query'] = query
            request.session['advparams'] = advparams

            # We will be saving the query on to the serverside to be able to pull it all together at a later date
            try:
                # we get the current user
                this_user = User.objects.get(username = request.user)

                this_query = None

                this_query_hash = hashlib.sha1(qserialization).hexdigest()

                try:
                    quest = Questionnaire.objects.get(id = qid)
                except Questionnaire.DoesNotExist:
                    logger.error("Questionnaire doesnt exist...")

                this_query = AdvancedQuery(user=this_user,name=("Query on "+timezone.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                    serialized_query_hash=this_query_hash,
                    serialized_query=qserialization, qid=quest)
                this_query.save()
                # and we all so insert the answers in a specific table exactly as they were on the post request to be able to put it back at a later time
                for k, v in request.POST.items():
                    if k.startswith("question_") and len(v) > 0:
                        aqa = AdvancedQueryAnswer(refquery=this_query,question=k, answer=v)
                        aqa.save()

                serialization_a = AdvancedQueryAnswer(refquery=this_query, question="boolrelwidget-boolean-representation", answer=qexpression)
                serialization_a.save()

                ttl = this_query.title

                if not ttl:
                    ttl = this_query.name

                request.session['query_id'] = this_query.id
                request.session['query_type'] = this_query.qid.id
                request.session['query_title'] = ttl

            except User.DoesNotExist:
                return HttpResponse("Invalid username")

            return results_fulltext_aux(request, query, isAdvanced=True, query_reference=this_query, advparams=advparams, comm=comm, questionnaire=quest)

    query = ""
    advparams=None
    simple_query=None
    in_post = True
    try:
        query = request.POST['query']
        #t_search = request.POST['t_search']

        # must save only on post, and without the escaping so it doesnt encadeate escapes on queries remade
        if query != "" and request.POST.get('page') is None and not opening_saved:
            simple_query = store_query(request, query)

        escaped_query = escapeSolrArg(query)
        query = escaped_query

        if comm != None:

            query = _addSolrSlugsToStr(comm, query)

        request.session['query'] = escaped_query

        request.session['isAdvanced'] = False
        request.session['query_id'] = -1
        request.session['query_type'] = -1
    except:
        in_post = False

    if not in_post:
        query = request.session.get('query', "")
        advparams=request.session.get('advparams', None)

    if query == "":
        return render(request, "results.html", {'request': request,
                                                'paginator_view_name': resolve(request.path_info).url_name,
                                                'num_results': 0, 'page_obj': None, 'breadcrumb': True})
    try:
        # Store query by the user
        if 'search_full' in request.POST:
            search_full = request.POST['search_full']
            request.session['search_full'] = 'search_full'
        else:
            search_full = request.session.get('search_full', "")
        if search_full == "search_full":
            return results_fulltext(request, page, full_text=True, isAdvanced=request.session['isAdvanced'], query_reference=simple_query, advparams=advparams, comm=comm, questionnaire=quest, default_mode={"score": "desc"})
    except:
        raise

    return results_fulltext(request, page, full_text=False, isAdvanced=request.session['isAdvanced'], query_reference=simple_query, advparams=advparams, comm=comm, questionnaire=quest ,default_mode={"score": "desc"})


def get_databases_from_solr(request, query="*:*"):

    (list_databases, hits) = get_databases_from_solr_v2(request, query=query)

    return list_databases

def __get_scientific_contact(db, db_solr, type_name):
    if type_name == "Observational Data":
        if (db_solr.has_key('institution_name_t')):
            db.admin_name = db_solr['institution_name_t']
        if (db_solr.has_key('Administrative_contact_address_t')):
            db.admin_address = db_solr['Administrative_contact_address_t']
        if (db_solr.has_key('Administrative_contact_email_t')):
            db.admin_email = db_solr['Administrative_contact_email_t']
        if (db_solr.has_key('Administrative_contact_phone_t')):
            db.admin_phone = db_solr['Administrative_contact_phone_t']


        if (db_solr.has_key('Scientific_contact_name_t')):
            db.scien_name = db_solr['Scientific_contact_name_t']

        if (db_solr.has_key('Scientific_contact_address_t')):
            db.scien_address = db_solr['Scientific_contact_address_t']

        if (db_solr.has_key('Scientific_contact_email_t')):
            db.scien_email = db_solr['Scientific_contact_email_t']
        if (db_solr.has_key('Scientific_contact_phone_t')):
            db.scien_phone = db_solr['Scientific_contact_phone_t']


        if (db_solr.has_key('Technical_contact___data_manager_contact_name_t')):
            db.tec_name = db_solr['Technical_contact___data_manager_contact_name_t']
        if (db_solr.has_key('Technical_contact___data_manager_contact_address_t')):
            db.tec_address = db_solr['Technical_contact___data_manager_contact_address_t']
        if (db_solr.has_key('Technical_contact___data_manager_contact_email_t')):
            db.tec_email = db_solr['Technical_contact___data_manager_contact_email_t']
        if (db_solr.has_key('Technical_contact___data_manager_contact_phone_t')):
            db.tec_phone = db_solr['Technical_contact___data_manager_contact_phone_t']

    elif "AD Cohort" in type_name or "EPAD" in type_name:

        if (db_solr.has_key('Administrative_Contact__AC___Name_t')):
            db.admin_name = db_solr['Administrative_Contact__AC___Name_t']
        if (db_solr.has_key('AC__Address_t')):
            db.admin_address = db_solr['AC__Address_t']
        if (db_solr.has_key('AC__email_t')):
            db.admin_email = db_solr['AC__email_t']
        if (db_solr.has_key('AC__phone_t')):
            db.admin_phone = db_solr['AC__phone_t']

        if (db_solr.has_key('Scientific_Contact__SC___Name_t')):
            db.scien_name = db_solr['Scientific_Contact__SC___Name_t']
        if (db_solr.has_key('SC__Address_t')):
            db.scien_address = db_solr['SC__Address_t']
        if (db_solr.has_key('SC__email_t')):
            db.scien_email = db_solr['SC__email_t']
        if (db_solr.has_key('SC__phone_t')):
            db.scien_phone = db_solr['SC__phone_t']

        if (db_solr.has_key('Technical_Contact_Data_manager__TC___Name_t')):
            db.tec_name = db_solr['Technical_Contact_Data_manager__TC___Name_t']
        if (db_solr.has_key('TC__Address_t')):
            db.tec_address = db_solr['TC__Address_t']
        if (db_solr.has_key('TC__email_t')):
            db.tec_email = db_solr['TC__email_t']
        if (db_solr.has_key('TC__phone_t')):
            db.tec_phone = db_solr['TC__phone_t']

    return db


def get_databases_process_results(results):
    list_databases = []
    questionnaires_ids = {}
    qqs = Questionnaire.objects.all()
    for q in qqs:
        questionnaires_ids[q.slug] = (q.pk, q.name)

    for r in results:
        try:
            database_aux = Database()

            database_aux.fields = r

            database_aux.id = r['id']

            database_aux.score = round(float(r['score']), 2)

            try:
                database_aux.percentage = r['percentage_d']
            except KeyError:
                pass

            if (not r.has_key('created_dt')):
                database_aux.date = ''
            else:

                try:
                    database_aux.date = r['created_dt']
                except:
                    database_aux.date = ''


            if (not r.has_key('date_last_modification_dt')):
                database_aux.date_modification = r['created_dt']
            else:

                try:
                    database_aux.date_modification = r['date_last_modification_dt']
                except:
                    database_aux.date_modification = r['created_dt']

            if (not r.has_key('database_name_t')):
                database_aux.name = '(Unnamed)'
            else:
                database_aux.name = r['database_name_t']

            #database_aux.localtion = ''
            # localtion ?!?! -> "No English, no Babes !" 
            database_aux.location = ''


            if(r.has_key('city_t')):
                database_aux.location = r['city_t']
            if (r.has_key('PI:_Address_t')):
                database_aux.location = r['PI:_Address_t']
            if (r.has_key('AC__Address_t')):
                database_aux.location = r['AC__Address_t']
            if (r.has_key('TC__Address_t')):
                database_aux.location = r['TC__Address_t']
            if (r.has_key('location_t')):
                database_aux.location = r['location_t']

            if (not r.has_key('institution_name_t')):
                database_aux.institution = ''
            else:
                database_aux.institution = r['institution_name_t']

            if (not r.has_key('contact_administrative_t')):
                database_aux.email_contact = ''
            else:
                database_aux.email_contact = r['contact_administrative_t']

            if (not r.has_key('number_active_patients_jan2012_d')):
                database_aux.number_patients = ''
            else:
                database_aux.number_patients = r['number_active_patients_jan2012_d']

            if (not r.has_key('date_last_modification_dt')):
                database_aux.last_activity = ''
            else:
                database_aux.last_activity = r['date_last_modification_dt']

            if (not r.has_key('upload_image_t')):
                database_aux.logo = 'nopic_db.png'
            else:
                database_aux.logo = r['upload_image_t']

            (ttype, type_name) = questionnaires_ids[r['type_t']]
            database_aux.ttype = ttype
            database_aux.type_name = type_name
            database_aux = __get_scientific_contact(database_aux, r, database_aux.type_name)

            database_aux.communities = r.get('communities_t', '').split('#')

            database_aux.draft = (r.get('draft_t', 'False') == 'True')

            list_databases.append(database_aux)
        except Exception as e:
            logger.exception("--An Exception occured while processing database --")
            pass
    
    return list_databases

def restriction(user):
    dbs = RestrictedUserDbs.objects.filter(user=user)
    rest = None
    i = 0

    def add_condition(i, rest, hash):

        if rest == None:
            rest = " AND (id:"+hash
        else:
            rest += " OR id:"+hash

        i += 1

        return (i, rest)

    # The main principle is avoid iterations, since usually this number will be very restricted in comparison with the real value
    for db in dbs:
        (i, rest) = add_condition(i, rest, db.fingerprint.fingerprint_hash)

    dbs = RestrictedGroup.hashes(user)

    for hash in dbs:
        (i, rest) = add_condition(i, rest, hash)

    if i>0:
        rest += ")"

    return rest

def get_databases_from_solr_v2(request, query="*:*", sort="", rows=10000, start=0, fl='*,score', post_process=None, qop='AND', comm_manager = False):
    
    if request.user.is_authenticated():
        try:
            eprofile = EmifProfile.objects.get(user=request.user)
            
            if eprofile.restricted == True:
                query += restriction(request.user)

        except EmifProfile.DoesNotExist:
            logger.error("Couldn't get emif profile for user")

    if not request.user.is_staff and not comm_manager:
        if query:
            query += ' AND '
        query += '(draft_t:False OR user_t:"'+request.user.username+'")'
        #query += ' AND (draft_t:False OR user_t:"'+request.user.email+'")'
    
    c = CoreEngine()
    results = c.search_fingerprint(query, sort=sort, rows=rows, start=start, fl=fl, qop=qop)
    list_databases = get_databases_process_results(results)

    if post_process:
        list_databases = post_process(results, list_databases)

    return (list_databases, results.hits)

def get_query_from_more_like_this(request, doc_id, type, maxx=100):
    try:
        eprofile = EmifProfile.objects.get(user=request.user)
    except EmifProfile.DoesNotExist:
        logger.error("Couldn't get emif profile for user")
    if eprofile.restricted == True:
        query = restriction(request.user)

    c = CoreEngine()
    #results = c.search_fingerprint(query, sort=sort, rows=rows, start=start)
    results = c.more_like_this(doc_id, type, maxx=maxx)


    if len(results)>0:
        queryString = "id:("
        for r in results:
            if "id" in r:
                queryString = queryString + r["id"]+"^"+str(r["score"])+ " "

        queryString = queryString + ")"
    else:
        queryString = None

    ## PY SOLR IS STUPID, OTHERWISE THIS WOULD BE AVOIDED
    database_name = ""
    results = c.search_fingerprint("id:"+doc_id , start=0, rows=1, fl="score", qop='OR')

    for r in results:
        if "database_name_t" in r:
            database_name = r["database_name_t"]

    return (queryString, database_name)

def get_databases_from_solr_with_highlight(request, query="*:*", sort="", rows=100, start=0, hlfl="*", fq="", multivalue_fields=tuple()):
    try:
        eprofile = EmifProfile.objects.get(user=request.user)
    except EmifProfile.DoesNotExist:
        logger.error("Couldn't get emif profile for user")
    if eprofile.restricted == True:
        query += restriction(request.user)

    c = CoreEngine()

    if not request.user.is_staff:
        query += ' AND (draft_t:False OR user_t:"'+request.user.username+'")'
        #query += ' AND (draft_t:False OR user_t:"'+request.user.email+'")'

    results = c.search_highlight(query, sort=sort, rows=rows, start=start, hlfl=hlfl, fq=fq, multivalue_fields=multivalue_fields)

    list_databases = get_databases_process_results(results)

    return (list_databases,results.hits, results.highlighting)


def database_listing(request, community, questionnaire=None, page=1, template_name='community_fingerprint_listing.html', drafts=False, only_personal_databases=False, paginator_view_name=None, first_questionnaire=False):
    """
    List databases by executing a solr query

    Keyword arguments:

    request                 -- http request object
    community               -- Community slug
    questionnaire           -- Questionnaire slug
    page                    -- Results page number                                  (default 1)
    template                -- Template file name                                   (default 'community_fingerprint_listing.html')
    drafts                  -- List databases that are waitting for approval        (default False)
    only_personal_databases -- Show only personal databases                         (default False)
    paginator_view_name     -- View name to be used on the paginator object         (default view name is extracted from current request)
    first_questionnaire     -- Get community first questionnaire if not defined     (default False)

    """

    # get community
    comm = getComm(community, request.user)
    # getComm may return a redirect object when the user 
    # doesnt has access to the required community
    if isinstance(comm, HttpResponseRedirect):
        return comm

    # get questionnaire
    questionnaire_obj = None
    if questionnaire is not None:
        try:
            questionnaire_obj = Questionnaire.objects.get(slug=questionnaire)
        except Questionnaire.DoesNotExist:
            raise Http404
    elif first_questionnaire:
        comm_quests = comm.questionnaires.all()
        if comm_quests:
            questionnaire_obj = comm_quests[0]

    #questionnaire slug
    questionnaire_slug = '' if questionnaire_obj is None else questionnaire_obj.slug

    paginator_extra_view_args = {
                                    'community': community,
                                    'questionnaire': questionnaire_slug
                                }
    # is owner?
    try:
        comm_manager = comm.is_owner(request.user)
    except:
        comm_manager = False

    # paginator 
    (rows, search_type) = define_rows(request)
    if request.POST:
        page = request.POST["page"]
    if page is None:
        page = 1

    # lets clear the geolocation session search filter (if any)
    try:
        del request.session['query']
        del request.session['advparams']
        del request.session['isAdvanced']
        del request.session['serialized_query']
    except KeyError:
        pass

    # define session vars
    if only_personal_databases:
        request.session['list_origin'] = 'personal'
    else:
        request.session['list_origin'] = 'all'

    # get extra filters
    if comm:
        (sortString, filterString, sort_params, start) = paginator_process_params(request, page, rows, extraFields=comm.list_fields.all(), community=comm)
    else:
        (sortString, filterString, sort_params, start) = paginator_process_params(request, page, rows)
    
    # build solr search query
    query = build_solr_base_query(request.user, only_personal_databases, comm, questionnaire)
    sort_params["base_filter"] = query  
    if len(filterString) > 0:
        query = add_to_solr_query(query, filterString)

    # Get drafts (used to list fingerprints on Manage > Drafts option )
    if drafts:
        query = build_solr_draft_query(comm)
        paginator_extra_view_args = {'community': community}

        activemenu = 'mancomm'
        activesubmenu = 'drafts'
    else:
        activemenu = 'databases'
        if only_personal_databases:
            activesubmenu = 'personal-' + questionnaire_slug
        else:
            activesubmenu = 'questionnaire-' + questionnaire_slug

    try:
        selected_databases = json.loads(sort_params["extraObjects"])["selectedList"]
    except (ValueError, KeyError):
        selected_databases = set()
    else:
        selected_databases = set(selected_databases)

    #Execute query
    if query != "":
        if selected_databases:
            # if the user has databases selected we have to remove from the selection those that do not meet the
            #  filtering criteria defined by the user.
            # for that we retrieve all databases ...
            (list_databases, hits) = get_databases_from_solr_v2(request, query, sort=sortString, comm_manager=comm_manager)

            selected_databases.intersection_update(d.id for d in list_databases)
            # ... and only after filtering the selection, we restrict to the required ones for the current page.
            list_databases = list_databases[start:start + rows]

            # update extraObjects in sort_params, which contains the selectedList
            extraObjects = json.loads(sort_params["extraObjects"])
            extraObjects["selectedList"] = list(selected_databases)
            sort_params["extraObjects"] = json.dumps(extraObjects)
        else:
            (list_databases, hits) = get_databases_from_solr_v2(request, query, sort=sortString, rows=rows, start=start, comm_manager=comm_manager)
    else:
        list_databases = []
        hits = 0

    #init paginator
    list_databases = paginator_process_list(list_databases, hits, start)

    ## Paginator ##
    myPaginator = Paginator(list_databases, rows)
    try:
        pager = myPaginator.page(page)
    except PageNotAnInteger:
        pager = myPaginator.page(1)
    ## End Paginator ##
    
    #data view
    if 'view' in request.POST and request.POST['view'] in ('list', 'table', 'card'):
        view = request.POST['view']
    else:
        view = config.table_view.lower()  # Use constance's table view variable

    returnObj = {
        'request': request,
        'paginator_view_name': (resolve(request.path_info).url_name, paginator_view_name)[
            paginator_view_name is not None],
        'paginator_extra_view_args': paginator_extra_view_args,
        'view': view,  # list, card or table
        'list_databases': list_databases,
        'breadcrumb': True,
        'collapseall': False,
        'geo': True,
        'page_obj': pager,
        'page_rows': rows,
        'alldatabases': True,
        'comm': comm,
        'questionnaire': questionnaire_obj,
        'extra_comm': {
            'community': community,
            'questionnaire': questionnaire_slug
        },
        'activemenu': activemenu,
        'activesubmenu': activesubmenu,
        'add_databases': True,
        'sort_params': sort_params,
        'page': page,
        'hits': hits,
        'selected_databases': selected_databases,
    }
    
    if only_personal_databases:
        returnObj['export_my_answers'] = True
        returnObj['api_token'] = True
        returnObj['owner_fingerprint'] = True
        returnObj['databases'] = True
    else:
        returnObj['data_table'] = True
        returnObj['export_all_answers'] = True

    return render(request, template_name, returnObj)


def build_solr_draft_query(comm):
    query = ""

    for quest in comm.questionnaires.all():
        dbs = FingerprintPending.objects.filter(
            fingerprint__questionnaire=quest,
            fingerprint__community=comm,
        )
        for db in dbs:
            db = db.fingerprint
            query = add_to_solr_query(query, 'id:' + db.fingerprint_hash, 'OR')

    return query


def build_solr_base_query(user, only_personal_databases, comm, questionnaire):
    query = ""

    # personal databases?
    if only_personal_databases == True:
        query = add_to_solr_query(query, "user_t:" + '"' + user.username + '"')
        if user.is_superuser:
            query = add_to_solr_query(query, "user_t:*")

    if comm != None:
        # add community
        query = add_to_solr_query(query, 'communities_t: ' + comm.slug)
        # add questionnaire slugs to solr query
        if questionnaire is not None:
            solr_slugs = 'type_t: ' + questionnaire
        else:
            #add all questionnaires slugs that are associated with the community
            solr_slugs = comm.getSolrSlugs()

        if solr_slugs:
            query = add_to_solr_query(query, solr_slugs)
    else:
        #show all user's databases
        ids = CommunityUser.objects.filter(user=request.user).values_list('community', flat=True)
        comms = Community.objects.filter(id__in=ids)
        tmp = ""
        first = True
        for community in comms:
            if first:
                tmp = add_to_solr_query(tmp, community.getSolrSlugs())
                first=False
            else:
                tmp = add_to_solr_query(tmp, community.getSolrSlugs(), 'OR')
        
        query = add_to_solr_query(query, tmp)

    return query

def add_to_solr_query(query, condition, operator="AND"):
    if query:
        query += " " + operator + " " + condition
    else:
        query = condition

    return query

def is_filter_active(field_slug, sort_params):
    """
    Verifies if the a certain field slug has an active filter on sort_params
    field_slug - string
    sort_params - dict
    returns boolean
    """
    if sort_params.has_key(field_slug) and sort_params[field_slug].has_key('filter'):
        return True

    return False

def get_filter_value(field_slug, sort_params):
    """
    Fills the filter values
    filter_dict - dict
    field_slug - string
    sort_params - dict with all parameters for sorrting and filtering
    """
    if is_filter_active(field_slug, sort_params):
        return sort_params[field_slug]['filter']
    
    return None



# Documentation
def docs_api(request, community=None):
    comm = getComm(community, request.user)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    cu = CommunityUser.objects.filter(community=comm, user=request.user)
    if not request.user.is_superuser and not comm.is_owner(request.user) and (not cu.exists() or not CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu.get())):
        return HttpResponseForbidden()

    return render(
        request,
        'docs/api.html',
        {
            'request': request,
            'comm': comm,
            'activemenu': 'apiinfo',
            'breadcrumb': True,
        }
    )


def more_like_that(request, doc_id, mlt_query=None, page=1, template_name='more_like_this.html', force=False):
    return more_like_that_comm(request, None, doc_id, mlt_query, page, template_name, force)

def more_like_that_comm(request, community, doc_id, mlt_query=None, page=1, template_name='more_like_this.html', force=False):
    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    if not config.more_like_this:
        raise Http404
    #first lets clean the query session log
    if 'query' in request.session:
        del request.session['query']

    if 'advparams' in request.session:
        del request.session['advparams']

    if 'isAdvanced' in request.session:
        del request.session['isAdvanced']

    if 'query_id' in request.session:
        del request.session['query_id']
    if 'query_type' in request.session:
        del request.session['query_type']

    if 'query_title' in request.session:
        del request.session['query_title']

    database_name = ""

    fingerprint = Fingerprint.objects.get(fingerprint_hash=doc_id)

    if mlt_query == None:
        (_filter, database_name) = get_query_from_more_like_this(request, doc_id, fingerprint.questionnaire.slug)
    else:
        _filter = mlt_query

    extra_comm = {
                    'community': community
                 }

    if not _filter:
        return render(request, template_name, {'request': request,
                                       'paginator_view_name': resolve(request.path_info).url_name,
                                       'paginator_extra_view_args': extra_comm,
                                       'num_results': 0, 'page_obj': None,
                                       'page_rows': 0,'breadcrumb': True,
                                       "breadcrumb_text": "More Like - "+database_name,
                                       "fingerprint_id": doc_id,
                                       'database_name': database_name, 'isAdvanced': False,
                                       'hide_add': True, 'more_like_this': True,
                                       'comm': comm,
                                       'extra_comm': extra_comm,
                                       "sort_params": None, "page":None})

    (rows, search_type) = define_rows(request)
    if request.POST and not force:
        page = request.POST["page"]

    if page == None:
        page = 1

    if comm:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows, extraFields=comm.list_fields.all())
    else:
        (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows)
    sort_params["base_filter"] = _filter;

    if len(filterString) > 0:
        _filter += " AND " + filterString

    if comm != None:

        _filter = _addSolrSlugsToStr(comm, _filter)

    def fn(res, lst):
        m = {}
        for r in res:
            if "id" in r and "score" in r:
                m[r["id"]] = r

        for d in lst:
            if d.id in m:
                d.score = str(round(float( m[d.id]["score"]), 3) )
        return lst

    (list_databases,hits) = get_databases_from_solr_v2(request, _filter, sort=sortString, rows=rows, start=range, fl="*, score", post_process=fn, qop='OR')
    if range > hits and force < 2:
        return databases(request, page=1, force=True)

    list_databases = paginator_process_list(list_databases, hits, range)

    ## Paginator ##
    myPaginator = Paginator(list_databases, rows)
    try:
        pager =  myPaginator.page(page)
    except PageNotAnInteger:
        pager =  myPaginator.page(page)
    ## End Paginator ##

    return render(request, template_name, {'request': request,
                                           'num_results': hits, 'page_obj': pager,
                                           'page_rows': rows,'breadcrumb': True,
                                           "breadcrumb_text": "More Like - "+database_name,
                                           "fingerprint_id": doc_id,
                                           'database_name': database_name, 'isAdvanced': False,
                                           'hide_add': True, 'more_like_this': True,
                                           'comm': comm,
                                           'extra_comm': {
                                            'community': community
                                           },
                                           "sort_params": sort_params, "page":page})


def paginator_process_params(request, page, rows, default_mode=None, extraFields=None, community=None):
    sortFieldsLookup = {
        "database_name": "database_name_t",
        "last_update": "date_last_modification_dt",

        "institution": "institution_sort",
        "nrpatients": "nrpatients_sort",
        "score": "score",
    }

    all_fields = ["database_name", "last_update", "type", "institution", "location", "nrpatients", "score"]

    if extraFields is None:
        extraFields = tuple()

    for field in extraFields:
        if field.type == 'numeric':
            sortFieldsLookup[field.slug] = field.slug+"_d"
        else:
            sortFieldsLookup[field.slug] = field.slug+"_t"

    filterFieldsLookup = {
        "database_name_filter": "database_name_s",
        "last_update_filter": "date_last_modification_dt",

        "institution_filter": "institution_name_s",
        "nrpatients_filter": "number_active_patients_jan2012_d",

        "draft_filter": "draft_t",
    }

    for field in extraFields:
        sufix = "_s"
        
        if field.type == 'numeric':
            sufix = "_d"
        
        filterFieldsLookup['%s_filter' % field.slug] = field.slug + sufix

    for field in extraFields:
        all_fields.append(field.slug)

    openTextFilters = ["database_name_filter", "institution_filter", "location_filter"]

    for field in extraFields:
        openTextFilters.append('%s_filter' % field.slug)

    sortString = ""
    filterString = ""
    sort_params= {}

    if "s" in request.POST:
        mode = json.loads(request.POST["s"])
    else:
        mode = default_mode if default_mode is not None else {"database_name": "asc"}

    for x in mode:
        if mode[x] == 'undefined':
            continue
        if x in sortFieldsLookup:
            if mode[x] == "asc" or mode[x] == "desc":
                sortString += "{} {}".format(sortFieldsLookup[x], mode[x])
                if x not in sort_params:
                    sort_params[x] = {}
                sort_params[x]["name"] = mode[x]
        elif len(mode[x]) > 0 and x in filterFieldsLookup:
            if x == "last_update_filter":
                filterString += "(created_dt:{} OR date_last_modification_dt:{}) AND ".format(
                    filter_value_to_string(mode[x]), filter_value_to_string(mode[x]),
                )
            elif x == "draft_filter" and (request.user.is_staff or (community and community.is_owner(request.user))):
                if mode[x] == "yes":
                    converted_value = "true"
                elif mode[x] == "no":
                    converted_value = "false"
                else:
                    converted_value = None

                if converted_value:
                    filterString += "draft_t: {} AND ".format(converted_value)

                    sort_params["draft"] = {
                        "filter": converted_value,
                    }
            elif x in openTextFilters:
                # all aditional filters applied at the results view are inserted at openTextFilters
                filterString += "({}:{}) AND ".format(
                    filterFieldsLookup[x], filter_value_to_string(mode[x]),
                )
            else:
                filterString += "{}:'{}' AND ".format(
                    filterFieldsLookup[x], mode[x],
                )
            if x[:-7] not in sort_params:
                sort_params[x[:-7]] = {}
            sort_params[x[:-7]]["filter"] = mode[x]

    if len(filterString) > 0:
        filterString = filterString[:-4]

    for x in all_fields:
        if (x in sort_params) and ("name" in sort_params[x]):
            sort_params["selected_name"] = x
            sort_params["selected_value"] = sort_params[x]["name"]
            if sort_params[x]["name"] == "asc":
                new_fields = {
                    "click_url": '?s={{"{}":"desc"}}'.format(x),
                    "next": 'desc',
                    "icon": "fas fa-fw fa-chevron-up",
                }
                sort_params[x].update(new_fields)
            elif sort_params[x]["name"] == "desc":
                new_fields = {
                    "click_url": '?s={{"{}":"asc"}}'.format(x),
                    "next": 'asc',
                    "icon": "fas fa-fw fa-chevron-down",
                }
                sort_params[x].update(new_fields)
        else:
            new_fields = {
                "click_url": '?s={{"{}":"asc"}}'.format(x),
                "next": 'asc',
                "icon": "fas fa-fw fa-minus",
            }
            if x not in sort_params:
                sort_params[x] = new_fields
            else:
                sort_params[x].update(new_fields)

    start = (int(page) - 1) * rows

    if "extraObjects" in mode:
        extraObjects = mode["extraObjects"]
    else:
        extraObjects = {}
    sort_params["extraObjects"] = json.dumps(extraObjects)

    return sortString, filterString, sort_params, start


def filter_value_to_string(filter_value):
    #is it a range?
    if isinstance(filter_value, list) and len(filter_value) == 2:
        return "[" + filter_value[0] +" TO "+ filter_value[1] + "]"
    else:
        return '"' + filter_value + '"'


def paginator_process_list(list_databases, hits, start):
    nList = []

    for x in xrange(0,start):
        nList.append(None)
    nList.extend(list_databases)
    while len(nList)<hits:
        nList.append(None)

    return nList


def create_auth_token(request, community=None, page=1, force=False):
    """
    Method to create token to authenticate when calls REST API
    """

    if not config.extra_information:
        raise Http404

    comm = getComm(community, request.user)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    cu = CommunityUser.objects.filter(community=comm, user=request.user)
    if not request.user.is_superuser and not comm.is_owner(request.user) and (not cu.exists() or not CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu.get())):
        return HttpResponseForbidden()

    (rows, search_type) = define_rows(request)
    if request.POST and not force:
        page = request.POST["page"]

    if page is None:
        page = 1

    user = request.user
    if not Token.objects.filter(user=user).exists():
        token = Token.objects.create(user=request.user)
    else:
        token = Token.objects.get(user=user)

    _filter = 'user_t:"{}"'.format(user.username)

    (sortString, filterString, sort_params, range) = paginator_process_params(request, page, rows)

    sort_params["base_filter"] = _filter

    if len(filterString) > 0:
        if len(_filter) > 0:
            _filter += " AND "

        _filter += filterString

    if comm is not None:
        _filter = _addSolrSlugsToStr(comm, _filter)

    (list_databases,hits) = get_databases_from_solr_v2(request, _filter, sort=sortString, rows=rows, start=range)
    if range > hits and force < 2:
        return create_auth_token(request, page=1, force=True)

    list_databases = paginator_process_list(list_databases, hits, range)

    myPaginator = Paginator(list_databases, rows)
    try:
        pager = myPaginator.page(page)
    except PageNotAnInteger:
        pager = myPaginator.page(1)
    ## End Paginator ##

    extra_comm = {
        'community': community
    }

    return render(
        request,
        "api-key.html",
        {
            'list_databases': list_databases,
            'paginator_view_name': resolve(request.path_info).url_name,
            'paginator_extra_view_args': extra_comm,
            'token': token,
            'user': user,
            'request': request,
            'breadcrumb': True,
            'page_obj': pager,
            'page_rows': rows,
            "sort_params": sort_params,
            "page": page,
            'comm': comm,
            'extra_comm': extra_comm,
            'activemenu': 'apiinfo',
        },
    )
