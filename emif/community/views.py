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
import json
import logging
import operator

import pymongo
from Bio import Entrez
from constance import config
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_POST

from accounts.models import EmifProfile
from developer.models import Plugin
from emif.context_processors import belongcomms
from emif.settings import MONGOD_ONLINE, pubmed_feed_collection
from emif.settings import PUBMED_EMAIL
from emif.tasks import send_custom_mail
from fingerprint.listings import database_listing
from fingerprint.models import Fingerprint
from fingerprint.tasks import indexFingerprintCelery
from notifications.models import Notification
from questionnaire.models import Question, QuestionSet, Questionnaire
from tag.models import Tag
from .forms import HeaderForm
from .models import Community, CommunityActivation, CommunityActivationMessage, CommunityExcludedExtraFields, \
    CommunityFields, \
    CommunityGroup, CommunityJoinForm, \
    CommunityJoinFormReply, \
    CommunityPlugins, CommunityUser, \
    ExternalCommunity, PluginPermission, QuestionSetAccessGroups
from .utils import getComm

logger = logging.getLogger(__name__)


def manage_statistics_view(request, community=None, template_name='manage_community_statistics.html'):
    return render(request, template_name)

def splash(request, template_name='community_splash.html'):

    if not request.user.is_authenticated() and not config.login_bypass:
        return redirect('home')

    # if the number scales up (or we eventually open community creation to everyone, this will have to be replaced by a paginator)
    communities = belongcomms(request) 
    user_comms = communities['user_comms']
    other_comms = communities['other_comms']
    disabled_comms = communities['disabled_comms']

    external_communities = ExternalCommunity.objects.all()

    comlen = 3

    comms = [str(item) for item in user_comms.values_list('slug', flat=True)]

    if MONGOD_ONLINE:
        
        publications = pubmed_feed_collection.find({
            'slug': {
                '$in': comms
            }
        }, limit=30).sort("pmid", pymongo.DESCENDING)
        publications = list(publications)
    else:
        publications = []

    return render(request, template_name, {
            'activemenu': 'home',
            'request': request,
            'hide_add': True,
            'breadcrumb': True,
            'user_comms': user_comms,
            "other_comms": other_comms,
            'disabled_comms': disabled_comms,
            'number_comms': len(user_comms) + len(other_comms),
            'external_comms': external_communities,
            'comlen': comlen,
            'publications': publications,
            'single_community': settings.SINGLE_COMMUNITY,
        })

@transaction.atomic
def create(request, template_name='create_community.html'):
    if request.method == 'POST':
        data = request.POST
        emails = []
        adict = dict(settings.ADMINS)
        for admin in adict:
            emails.append(adict[admin])


        send_custom_mail.delay('%s: Request for community %s creation' % (settings.GLOBALS['BRAND'],data['name']),
            """Dear Administrator,\n
                    A new community creation request has been submitted by %s. The details can be seen below
                    \n
                    <strong>Name</strong>: %s
                    <strong>Description</strong>: %s
                    <strong>Motivation</strong>: %s

                    \nSincerely,\n%s
            """ %(request.user.get_full_name(), data['name'], data['description'], data['motivation'], settings.GLOBALS['BRAND']), settings.DEFAULT_FROM_EMAIL, emails)

        return render(request, template_name, {
            'request': request,
            'hide_add': True,
            'requested': True,
            'breadcrumb': True,
        })
    else:
        return render(request, template_name, {
            'request': request,
            'hide_add': True,
            'breadcrumb': True,
        })

@transaction.atomic
def join(request, community=None, template_name='join_community.html'):
    
    try:
        comm = Community.objects.get(slug=community)
    except Community.DoesNotExist:
        raise Http404

    cu = None
    try:
        cu = CommunityUser.objects.get(community=comm, user=request.user)
    except CommunityUser.DoesNotExist:
        pass

    if cu:
        if cu.status == CommunityUser.ENABLED or cu.status == CommunityUser.RESTRICTED:
            return HttpResponseRedirect("/c/" + community + "/databases")
            
    join_form = None
    if cu is None:
        join_form = CommunityJoinForm.objects.filter(community=comm)

    success = None
    if request.method == 'POST' and cu is None:
        missing = []
        answers = []
        for question in CommunityJoinForm.objects.filter(community=comm):
            field = forms.CharField(required=question.required)
            answer = field.to_python(request.POST.get("jform{}".format(question.id)))
            try:
                field.validate(answer)
            except forms.ValidationError:
                missing.append(question.question_text)
            else:
                if answer != field.empty_value:
                    answers.append((question, answer))

        if not missing:
            if comm.membership == Community.MEMBERSHIP_PUBLIC:
                # on open communities you don't need to perform a join
                #  but if somebody does it set its status to ENABLED
                cu = CommunityUser.objects.create(community=comm, user=request.user, status=CommunityUser.ENABLED)
                CommunityGroup.put_on_pre_existing_group(CommunityGroup.DEFAULT_GROUP, comm, cu)
            else:
                cu = CommunityUser.objects.create(community=comm, user=request.user, status=CommunityUser.DISABLED)
                CommunityActivation.objects.create(community=comm, user=request.user, commuser=cu)

            CommunityJoinFormReply.objects.bulk_create(
                CommunityJoinFormReply(commuser=cu, join_form=question, reply_text=answer)
                for question, answer in answers
            )

            success = True
        else:
            # assuming that the users doesn't change any html, this should never happen
            #  so I don't bother displaying "required field" messages. HTML5 forms errors
            #  should deal with that.
            success = False

    return render(request, template_name, {
        'comm': comm,
        'comm_user': cu,
        'join_form': join_form,
        'success': success,
        'request': request,
        'breadcrumb': True,
    })


@transaction.atomic
def join_first_auto(request):
    try:
        comm = Community.objects.all()[:1].get()
    except Community.DoesNotExist:
        raise Http404
    
    cu, _ = CommunityUser.objects.get_or_create(community=comm, user=request.user)
    if comm.membership in (Community.MEMBERSHIP_OPEN, Community.MEMBERSHIP_PUBLIC):
        # The only difference between OPEN and PUBLIC communities is that on PUBLIC communities
        #  a user has to accept a set of terms and conditions. On a single community installation
        #  we are assuming that such terms are defined on installation level (on register) instead of
        #  community level.
        cu.status = CommunityUser.ENABLED
        cu.save()

        # I will add them to the default group in case in the future they switch from an open/public
        #  membership to a moderated one, avoiding existing users not having access to databases
        CommunityGroup.put_on_pre_existing_group(CommunityGroup.DEFAULT_GROUP, comm, cu)

        return render(request, 'userena/activation_complete.html')
    else:
        CommunityActivation.objects.create(community=comm, user=request.user, commuser=cu)

    return render(
        request,
        'join_community.html',
        {
            'comm': comm,
            'comm_user': cu,
            'success': True,
            'request': request,
            'breadcrumb': True,
        },
    )

#description, users, components, settings, communication

def get_comm(community, request):
    comm = getComm(community, request.user)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm
    
    try:
        comm.owners.get(id=request.user.id)
    except User.DoesNotExist:
        raise Http404

    return comm


def notify_draft_submission(request, fingerprint):
    user = request.user
    community = fingerprint.community
    name = fingerprint.findName()

    manager_message = """Dear Community Manager,\n
            User '%s' has submitted a request to turn public a draft database:
            \n
            <strong>Email</strong>: <a href="mailto:'%s'">%s</a>
            <strong>Organization</strong>: %s
            <strong>Country</strong>: %s
            <strong>Database</strong>: %s

            \n
            Click <a href="%s">here</a> to proceed to draft management.\n
            
            \n
            Sincerely,\n%s
            """ % (
        user.get_full_name(),
        user.email,
        user.email,
        user.emif_profile.organization,
        user.emif_profile.country,
        name,
        "{}community/manage/{}/drafts".format(settings.BASE_URL, community.slug),
        settings.GLOBALS['BRAND'],
    )

    send_custom_mail.delay(
        '%s: %s wants to publish a draft database' % (settings.GLOBALS['BRAND'], user.get_full_name()),
        manager_message,
        settings.DEFAULT_FROM_EMAIL,
        community.owners.values_list('email', flat=True),
    )

    return 0


def notify_study_submission(community, user, name):

    cg = CommunityGroup.objects.get(community=community, name=CommunityGroup.STUDY_MANAGERS_GROUP)
    study_managers = cg.members.all().values_list("user__email", flat = True)

    manager_message = """Dear Study Manager,\n
            User '%s' has submitted a study request:
            \n
            <strong>Email</strong>: <a href="mailto:'%s'">%s</a>
            <strong>Organization</strong>: %s
            <strong>Country</strong>: %s
            <strong>Study Request</strong>: %s

            \n
            Click <a href="%s">here</a> to proceed to study management.\n
            
            \n
            Sincerely,\n%s
            """ %(user.get_full_name(), user.email, user.email, user.emif_profile.organization,
                    user.emif_profile.country, name, settings.BASE_URL+'c/' + community.slug + '/apps/tp/Study Requests', settings.GLOBALS['BRAND'])

    send_custom_mail.delay('%s: %s submitted a study request' % (settings.GLOBALS['BRAND'], user.get_full_name()),
        manager_message, settings.DEFAULT_FROM_EMAIL, list(study_managers))

    return 0

def __check_pubmed_query(query):
    if query:
        Entrez.email = PUBMED_EMAIL
        handle = Entrez.esearch(db="pubmed", term=query)
        record = Entrez.read(handle)
        return len(record["IdList"])
    return 0

@transaction.atomic
def manage_descriptions(request, community=None, template_name='manage_community_description.html'):
    comm = get_comm(community, request)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    new_logo = request.FILES.get('new_logo', None)
    new_thumb = request.FILES.get('new_thumb', None)

    success = None
    res_number = __check_pubmed_query(comm.query)

    if request.method == 'POST':
        data = request.POST
        
        form = HeaderForm(request.POST)

        if new_logo != None:
            
            comm.icon = new_logo
            if new_thumb!=None:
                comm.thumbnail = new_thumb
            comm.save()

        if 'comm_desc' in data:
            comm.description = data['comm_desc'][:4999]
            comm.short_desc = data['comm_desc_short'][:198]
            comm.save()

        if 'tag_container' in data:
            comm.set_tags(Tag.parse_tags(data['tag_container']))

            comm.save()
        
        if form.is_valid():
            comm.header_display = form.cleaned_data["display"]
            comm.save()


        elif 'query_container' in data:
            new_query = data['query_container'][:200]
            try:
                res_number = __check_pubmed_query(new_query)
                comm.query = new_query
                comm.save()
            except:
                success = False

    form = HeaderForm()
    form.fields['display'].initial = [comm.header_display]

    return render(request, template_name, {
        'comm': comm,
        'success': success,
        'query_results': res_number,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'description',
        'breadcrumb': True,
        'header_choice_form': form
    })


@transaction.atomic
def manage_users(request, community=None):
    comm = get_comm(community, request)

    if isinstance(comm, HttpResponseRedirect):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'comm_user_approval' in data and comm.membership != Community.MEMBERSHIP_OPEN:
            # handle users waiting for approavel to enter the community

            cu = comm.communityuser_set.get(id=int(data['comm_user_approval']))
            ca = CommunityActivation.objects.get(commuser=cu, used=False)
            next_status = int(data['status'])

            if next_status in (CommunityUser.ENABLED, CommunityUser.RESTRICTED):
                ca.activate(next_status)
                if next_status == CommunityUser.ENABLED:
                    CommunityGroup.put_on_pre_existing_group(CommunityGroup.DEFAULT_GROUP, comm, cu)
                    CommunityGroup.put_on_pre_existing_group(CommunityGroup.EDITORS_GROUP, comm, cu)
            elif next_status == CommunityUser.BLOCKED:
                ca.block()
            elif next_status == CommunityUser.REJECTED:
                ca.dontactivate()

        elif 'comm_user_status' in data and comm.membership != Community.MEMBERSHIP_OPEN:
            # change existing community user status

            # if in the future restrictions are allowed on open communities, note that user might not have a
            #  CommunityUser record and the line below will fail
            cu = CommunityUser.objects.get(id=int(data['comm_user_status']))
            next_status = int(data['status'])
            if next_status not in (CommunityUser.ENABLED, CommunityUser.RESTRICTED, CommunityUser.BLOCKED, CommunityUser.REMOVED):
                return HttpResponseBadRequest("Invalid CommunityUser status {}".format(next_status))

            if next_status == CommunityUser.REMOVED:
                all_fps = comm\
                    .fingerprint_set\
                    .valid(include_drafts=True)\
                    .filter(questionnaire__in=comm.questionnaires.all())
                owned_fingerprints = all_fps.filter(owner=cu.user)
                if not owned_fingerprints.filter(shared=None).exists():  # only perform this if the user doesn't own fingerprints where he is the single owner
                    # transfer ownership to one of the shared owners
                    for fp in owned_fingerprints:
                        fp.owner = fp.shared.first()
                        fp.save()
                        fp.shared.remove(fp.owner)
                        indexFingerprintCelery.delay(fp.fingerprint_hash)

                    # remove user from shared owner of other fingerprints
                    for fp in all_fps.filter(shared=cu.user):
                        fp.shared.remove(cu.user)
                        indexFingerprintCelery.delay(fp.fingerprint_hash)

                    if settings.SINGLE_COMMUNITY:
                        cu.user.is_active = False
                        cu.user.save()

                    cu.delete()

            else:
                cu.status = next_status
                cu.save()

        elif 'make_comm_user' in data:
            # promote community user to community manager

            if comm.membership == Community.MEMBERSHIP_OPEN:
                user = User.objects.get(id=int(data['make_comm_user']))
                try:
                    cu = comm.communityuser_set.get(user=user)
                except CommunityUser.DoesNotExist:
                    cu = CommunityUser.objects.create(
                        community=comm,
                        user=User.objects.get(id=int(data['make_comm_user'])),
                        status=CommunityUser.ENABLED,
                    )
                    CommunityGroup.put_on_pre_existing_group(
                        CommunityGroup.DEFAULT_GROUP,
                        comm,
                        cu,
                    )
            else:
                cu = comm.communityuser_set.get(id=int(data['make_comm_user']))

                # if we make a user community manager he must be enabled!
                cu.status = CommunityUser.ENABLED
                cu.save()

            comm.owners.add(cu.user)

        elif 'rm_user' in data:
            # demote community user from community manager

            # if we make a user community manager he must be enabled!
            user = User.objects.get(id=int(data['rm_user']))
            comm.owners.remove(user)
            comm.invisible_owners.remove(user)

            comm.save()
            try:
                cu = user.community_users.get(community=comm)
            except CommunityUser.DoesNotExist:
                pass
            else:
                if cu.communitygroup_set.count() == 1 and cu.communitygroup_set.get().name == CommunityGroup.DEFAULT_GROUP:
                    cu.delete()

        elif 'invisible_user' in data:
            # make the community manager position of a community user invisible to other users

            mdata = data['invisible_user'].split('_')
            set_invisible = (int(mdata[1]) == 1)
            # if we make a user community manager he must be enabled!
            user = User.objects.get(id=int(mdata[0]))

            if set_invisible:
                comm.invisible_owners.add(user)
            else:
                comm.invisible_owners.remove(user)

        elif 'pct' in data:
            # change community membership

            mvar = data.get('membership', None)

            comm.public = False

            if mvar == "open":
                comm.membership = "open"
                comm.public = True
            elif mvar == "public":
                comm.membership = "public"
            elif mvar == "invitation":
                comm.membership = "invitation"
            else:
                comm.membership = "moderated"                

            disclaimer_text = data.get('disclaimer', "")
            comm.disclaimer = disclaimer_text

            comm.save()

        # avoid refreshing the page sending the same POST request which could lead to 500
        return redirect("manage-community-users", comm.slug)

    owners = comm.owners.all()

    if comm.membership == Community.MEMBERSHIP_OPEN:
        users = [
            ep.user
            for ep in EmifProfile.objects
            .filter(user__is_active=True)
            .exclude(user__id=-1)
            .exclude(user__in=owners)
            .select_related("user")
        ]
    else:
        users = comm.communityuser_set.filter(user__is_active=True).exclude(user__id=-1).exclude(user__in=owners)

    join_form_questions = CommunityJoinForm.objects.filter(community=comm)

    join_form_replies = {}
    if join_form_questions.exists():
        for comm_user in users:
            form_replies = []
            if not isinstance(comm_user, User):
                replies = {
                    reply.join_form.id: reply.reply_text
                    for reply in CommunityJoinFormReply.objects.filter(commuser=comm_user)
                }

                for question in join_form_questions:
                    form_replies.append(
                        (
                            question.question_text,
                            replies.get(question.id, "")
                        )
                    )

            # Add user join form replies
            join_form_replies[comm_user.id] = form_replies

    if comm.membership == Community.MEMBERSHIP_OPEN:
        new_users = None
        comm_users = [(user, user) for user in users]
    else:
        new_users = users.filter(status=CommunityUser.DISABLED)
        comm_users = [(comm_user, comm_user.user) for comm_user in users.exclude(status=CommunityUser.DISABLED)]

    # comm_users is an array of tuples. each tuple has as two values, the first can be either the django user object or
    #  the community user object. the second value is always the django user object.
    # We do this because on an open community some users dont have a CommunityUser associated, so instead of
    #  using the id of the community_user, the id of the django user object is used.

    return render(request, "manage_community_users.html", {
        'comm': comm,
        'success': success,
        'request': request,
        'owners': owners,
        'new_users': new_users,
        'comm_users': comm_users,
        'comm_has_join_form': join_form_questions.exists(),
        'join_form_replies': json.dumps(join_form_replies),
        'activemenu': 'mancomm',
        'activesubmenu': 'users',
        'breadcrumb': True,
    })


@require_GET
def manage_drafts(request, community=None, page=1):
    comm = get_comm(community, request)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    if comm.auto_accept:
        raise Http404()

    return database_listing(request, community, page=page, template_name='manage_community_drafts.html', drafts=True)


def _validate_fingerprint_draft(fingerprint, validate):
    if hasattr(fingerprint, "fingerprintpending"):
        if validate:
            fingerprint.draft = False
            fingerprint.save()
            fingerprint.indexFingerprint()
        fingerprint.fingerprintpending.delete()


@require_POST
@transaction.atomic
def manage_drafts_accept(request, community=None, fingerprint=None):
    comm = get_comm(community, request)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    if comm.auto_accept:
        raise Http404()

    _validate_fingerprint_draft(get_object_or_404(Fingerprint, fingerprint_hash=fingerprint), True)

    return JsonResponse({"msg": "Done"})


@require_POST
@transaction.atomic
def manage_drafts_deny(request, community=None, fingerprint=None):
    comm = get_comm(community, request)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    if comm.auto_accept:
        raise Http404()

    _validate_fingerprint_draft(get_object_or_404(Fingerprint, fingerprint_hash=fingerprint), False)

    return JsonResponse({"msg": "Done"})


@transaction.atomic
def manage_components(request, community=None, template_name='manage_community_components.html'):
    comm = get_comm(community, request)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm
        
    possible_pgs = Plugin.objects.filter(Q(type=Plugin.DATABASE) | Q(type=Plugin.THIRD_PARTY) | Q(type=Plugin.FULL_FLEDGED))
    
    success = None
    if request.method == 'POST':
        data = request.POST

        if 'from[]' in data:

            existent_db_plugins = CommunityPlugins.objects.filter(community=comm, plugin__type=Plugin.DATABASE).delete()
    

            pgs = json.loads(data.get('from[]'))['from']  
                
            #pgs = data.getlist('from[]')

            #*********** JERBOA FIX #1287
            #comm.show_popchar = False
            comm.show_popchar = True

            comm.show_docs = False
            i=1
            for pg in pgs:

                if pg['id'] == 'db':
                    comm.db_sortid = i
                #elif pg['id'] == 'pc':
                #    comm.popchar_sortid = i
                #    comm.show_popchar = True

                elif pg['id'] == 'dcs':
                    comm.docs_sortid = i
                    comm.show_docs = True

                else:

                    try:
                        plugin_exists = CommunityPlugins.objects.get(plugin_id = pg['id'], community_id=comm.id)
                    except CommunityPlugins.DoesNotExist:
                        try:
                        #comm.plugins.add()
                            CommunityPlugins.objects.create(plugin=possible_pgs.get(id=int(pg['id'])), community=comm, sortid=i)
                        except Plugin.DoesNotExist:
                            logger.error("Cannot add plugin with id %d", pg['id'])

                i+=1

            comm.save()


        if 'fromc[]' in data:
            pgs = json.loads(data.get('fromc[]'))['from']
            #pgs = data.getlist('from[]')

            #*********** JERBOA FIX #1287
            #comm.show_popchar = False
            comm.show_popchar = True

            #comm.show_docs = False
            #comm.plugins.clear()
            existent_db_plugins = CommunityPlugins.objects.filter(Q(community=comm) & Q(Q(plugin__type=Plugin.THIRD_PARTY) | Q(plugin__type=Plugin.FULL_FLEDGED))).delete()

            i=1
            for pg in pgs:

                if pg['id'] == 'db':
                    comm.db_sortid = i

                else:

                    try:
                        plugin_exists = CommunityPlugins.objects.get(plugin_id = pg['id'], community_id=comm.id)
                        
                    except CommunityPlugins.DoesNotExist:
                        try:
                        #comm.plugins.add()
                            CommunityPlugins.objects.create(plugin=possible_pgs.get(id=int(pg['id'])), community=comm, sortid=i)
                            
                        except Plugin.DoesNotExist:
                            logger.error("Cannot add plugin with id %d", pg['id'])

                i+=1

            comm.save()

    other_plugins = possible_pgs.exclude(id__in=comm.plugins.all().values_list('id', flat=True))
    other_plugins = other_plugins.filter(type=Plugin.DATABASE, removed=False)

    other_plugins_comm = possible_pgs.exclude(id__in=comm.plugins.all().values_list('id', flat=True))
    other_plugins_comm = other_plugins_comm.filter(Q(type=Plugin.THIRD_PARTY) | Q(type=Plugin.FULL_FLEDGED), removed=False)

    return render(request, template_name, {
        'comm': comm,
        'db_plugins': CommunityPlugins.objects.filter(community=comm, plugin__type=Plugin.DATABASE, plugin__removed=False).order_by('sortid'),
        'comm_plugins': CommunityPlugins.objects.filter(Q(plugin__type=Plugin.THIRD_PARTY) | Q(plugin__type=Plugin.FULL_FLEDGED), community=comm, plugin__removed=False).order_by('sortid'),
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'other_db_plugins': other_plugins,
        'other_comm_plugins': other_plugins_comm,
        'activesubmenu': 'components',
        'breadcrumb': True,
    })

@transaction.atomic
def manage_views(request, community=None, questionnaire=None, template_name='manage_community_views.html'):
    comm = get_comm(community, request)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    qst = comm.questionnaires.filter(slug = questionnaire).first()
    #qst = None
    # This is hardcoded and very very bad, we structuraly allow many questionnaires but since we will not make sure
    # they have common fields we use the fields from the first... i dont like it, but since is a requirement to specify other fields
    # theres nothing i can do about it
    possible_fields = None
    if qst:
        possible_fields = qst.questions().filter(type__in =['open', 'open-validated', 'email', 'url', 'open-textfield',
        'open-button', 'open-location', 'numeric', 'datepicker', 'location', 'choice-multiple', 'choice', 'choice-yesno']).exclude(slug_fk__slug1='database_name')

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'view' in data:
            
            #extract view and sections fields from request
            view = data.get('view')
            sections = []
            if 'section-0' in data:
                flds = json.loads(data.get('section-0'))['from']
                sections.append({'section': 0, 'flds': flds})
            if 'section-1' in data:
                flds = json.loads(data.get('section-1'))['from']
                sections.append({'section': 1, 'flds': flds})
            if 'section-2' in data:
                flds = json.loads(data.get('section-2'))['from']
                sections.append({'section': 2, 'flds': flds})
            
            #delete all settings
            CommunityFields.objects.filter(community=comm, questionnaire=qst, view=view).delete()
            CommunityExcludedExtraFields.objects.filter(community=comm, questionnaire=qst, view=view).delete()

            #save new settings
            for section in sections:
                i = 1
                for fld in section.get('flds'):
                    if fld['id'] == 'db':
                        comm.dblist_sortid = i
                    else:
                        try:
                            #comm.list_fields.add(possible_fields.get(id=int(fld['id'])))
                            CommunityFields.objects.create(
                                field=possible_fields.get(id=int(fld['id'])), 
                                community=comm, 
                                questionnaire=qst, 
                                view=view, 
                                section=section.get('section'),
                                icon=fld['icon'],
                                show_label=fld['label'],
                                apply_formatting=fld['formatting'],
                                sortid=i
                            )
                        except Question.DoesNotExist:
                            logger.error("Cannot add question with id %d", fld['id'])
                    i+=1

            possible_extra_fields = list(CommunityExcludedExtraFields.POSSIBLE_FIELDS[view])
            for key in data:
                if not key.startswith("extra_"):
                    continue

                field = key[6:]
                try:
                    possible_extra_fields.remove(field)
                except ValueError:
                    pass  # ignore unknown extra fields

            for field in possible_extra_fields:
                CommunityExcludedExtraFields.objects.create(
                    community=comm, questionnaire=qst, view=view, name=field
                )

            comm.save()

        if 'adv_change' in data:
            flds = json.loads(data.get('adv_change'))
            questions = qst.questions()
            questions.update(show_advanced=False)
            questionsets = qst.questionsets()
            questionsets.update(show_advanced=False)

            for fld in flds:
                if 'qs_' in fld:
                    questionsets.filter(id=int(fld[3:])).update(show_advanced=True)
                elif 'q_' in fld:
                    q = questions.filter(id=int(fld[2:]))
                    if q.count() > 0:
                        qset = q[0].questionset
                        qset.show_advanced=True
                        qset.save()
                        q.update(show_advanced=True)

    comm_fields = None
    if qst:
        comm_fields = CommunityFields.objects.filter(community=comm, questionnaire=qst).order_by('sortid')

    return render(request, template_name, {
        'comm': comm,
        'questionnaire': qst,
        'qst': qst,
        'comm_permissions': comm.get_permissions(),
        "comm_fields_class": CommunityFields,  # to avoid having view values hardcoded
        'comm_fields': comm_fields,
        "comm_extra_fields": CommunityExcludedExtraFields.POSSIBLE_FIELDS,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'views-{}'.format(qst.slug),
        'breadcrumb': True,
    })


@transaction.atomic
def manage_settings(request, community=None, questionnaire=None, template_name='manage_community_settings.html'):
    comm = get_comm(community, request)

    if (isinstance(comm, HttpResponseRedirect)):
        return comm

    qst = comm.questionnaires.filter(slug=questionnaire).first()

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'permissions_change' in data:
            cp = comm.get_permissions()
            cp.export_dblist = data.get('export_dblist', False) != False
            cp.export_fingerprint = data.get('export_fingerprint', False) != False
            cp.export_datatable = data.get('export_datatable', False) != False
            comm.auto_accept = data.get('auto_accept', False) != False
            cp.save()
            comm.save()

        if 'questionnaires_display' in data:
            comm.questionnaires_display = data["questionnaires_display"]
            comm.save()


    comm_fields = None
    if qst:
        comm_fields = CommunityFields.objects.filter(community=comm, questionnaire=qst).order_by('sortid')

    return render(request, template_name, {
        'comm': comm,
        'questionnaire': qst,
        'qst': qst,
        'comm_permissions': comm.get_permissions(),
        'comm_fields': comm_fields,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'settings-{}'.format(comm.slug),
        'breadcrumb': True,
    })

@transaction.atomic
def manage_communication(request, community=None, template_name='manage_community_communication.html'):
    comm = get_comm(community, request)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'broadcast' in data:
            for cu in comm.communityuser_set.all():
                href = data.get('broadcast_url', None)
                message = data.get('broadcast', None)

                if message:
                    clean_message = message.strip()[:200]
                    if len(clean_message) > 0:
                        nt = Notification(
                            destiny=cu.user,
                            origin=request.user,
                            type=Notification.SYSTEM,
                            href=href,
                            notification=clean_message
                        )

                        nt.save()

    return render(request, template_name, {
        'comm': comm,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'communication',
        'breadcrumb': True,
    })


def buildPermissionsMatrix(comm, ugroup):
    ugroup = sorted(ugroup, key=operator.attrgetter('pk'))

    if comm:
        valid_plugins = comm.plugins.filter(Q(type=Plugin.DATABASE) | Q(type=Plugin.THIRD_PARTY) | Q(type=Plugin.FULL_FLEDGED))
    else:
        valid_plugins = []

    matrix = []
    first_liner = ['Plugin'] + [group.name for group in ugroup]
    matrix.append(first_liner)

    for plugin in valid_plugins:
        line = []
        for group in ugroup:
            # ********************************************************************
            # *** to be deleted/ignored ?
            # ********************************************************************
            """
            if database:
                try:
                    cp = CommunityDatabasePermission.objects.get(communitygroup=group, plugin=plugin, database=database)
                    created = False

                except CommunityDatabasePermission.DoesNotExist:
                    logger.debug("-- No comm database permission, defaulting to community permission")
                    cp = PluginPermission.objects.filter(communitygroup=group, plugin=plugin)[0]

                    cdp = CommunityDatabasePermission(communitygroup=cp.communitygroup, plugin=cp.plugin, database=database)
                    cdp.save()
            else:
                cp = PluginPermission.objects.filter(communitygroup=group, plugin=plugin, allow=True)[0]
                print("*** get_or_create: created?"+str(created)+" *** -> "+cp.communitygroup.name+".allow:"+str(cp.allow))
            """
            # ***
            # ********************************************************************
            # ********************************************************************

            cp = PluginPermission.objects.filter(communitygroup=group, plugin=plugin)
            if cp.exists():
                cp.get()
            else:
                cp = PluginPermission.objects.create(communitygroup=group, plugin=plugin, allow=False)

            line.append(cp)
        pname = [plugin.name] + line
        matrix.append(pname)

    return matrix


def buildGroupPluginPermissionsMatrix(comm, ugroup):
    valid_plugins = comm.plugins.filter(Q(type=Plugin.DATABASE) | Q(type=Plugin.THIRD_PARTY) | Q(type=Plugin.FULL_FLEDGED))

    grouppluginmatrix = []
    first_liner = ['Group'] + [plugin.name for plugin in valid_plugins]
    grouppluginmatrix.append(first_liner)
    
    for group in ugroup:
        line = [group]
        for plugin in valid_plugins:
            cps = PluginPermission.objects.filter(communitygroup__community=comm, communitygroup=group, plugin=plugin)
            if cps.exists():
                cps = cps.get()
            else:
                cps = PluginPermission.objects.create(communitygroup=group, plugin=plugin, allow=False)
            line.append(cps)

        grouppluginmatrix.append(line)

    return grouppluginmatrix


# Builds ( First+Last Name, email, Institution, Group-checked or not for that member )
def buildUserPermissionsMatrix(comm, ugroup):
    usermatrix = []
    
    first_liner = ['Name'] + ['Email'] + ['Institution'] + [group.name for group in ugroup]
    usermatrix.append(first_liner)

    if comm.membership == Community.MEMBERSHIP_OPEN:
        cusers = [ep.user for ep in EmifProfile.objects.filter(user__is_active=True).exclude(user__id=-1).select_related("user")]
    else:
        cusers = comm.communityuser_set.all().exclude(user__id=-1)
    
    for cuser in cusers:
        if comm.membership == Community.MEMBERSHIP_OPEN or cuser.status == CommunityUser.ENABLED:
            if isinstance(cuser, CommunityUser):
                user = cuser.user
            else:  # if isinstance(cuser, User):
                user = cuser

            line = ["{} {}".format(user.first_name, user.last_name), user.email]

            try:
                institution = user.emif_profile.organization
            except:
                institution = "undefined"
            line.append(institution)

            # for each user... check each group...
            for group in ugroup:

                if group.name == "default" and comm.membership == Community.MEMBERSHIP_OPEN:
                    ingroup = True
                else:
                    ingroup = group.members.filter(user=user)

                if ingroup:
                    line.append((group.id, user.email, True))
                else:
                    line.append((group.id, user.email, False))

            usermatrix.append(line)
    return usermatrix


def buildGroupQSetPermissionsMatrix(comm, ugroup, questionnaire_id, database=None):
    valid_qsets = []
    #valid_qsets = QuestionSet.all(questionnaire=questionnaire_id).filter(id__in=comm.questionnaires.all().values_list('id', flat=True))
    #valid_qsets = QuestionSet.objects.all(questionnaire=questionnaire_id).filter(id__in=[1,2])

    valid_qsets = QuestionSet.objects.all().order_by('sortid').filter(questionnaire=questionnaire_id)

    # questionnaire == questionnaire_id, obter os qsets do questionnaire_id
    
    groupmatrix = []
    first_liner = ['Group/Question Set'] + [qset.text.replace('h1. ', '') for qset in valid_qsets]
    groupmatrix.append(first_liner)
    
    for group in ugroup:
        line = []
        line.append(group)
        for qset in valid_qsets:
            qsetPermission = None
            try:
                qsetPermission = QuestionSetAccessGroups.objects.filter(communitygroup=group, qset=qset)
                line.append(qsetPermission[0])
            except:
                (qsetPermission, created) = QuestionSetAccessGroups.objects.get_or_create(communitygroup=group, qset=qset, can_read=True, can_write=False)
                line.append(qsetPermission)
        groupmatrix.append(line)


    return groupmatrix


@transaction.atomic
def manage_qsets(request, community=None, questionnaire=None, template_name='manage_community_qsets.html'):
    comm = get_comm(community, request)

    if questionnaire == None:
        try:
            quests = None
            if comm:
                quests = comm.questionnaires.filter(disable=False)
            else:
                quests = Questionnaire.objects.filter(disable=False)
        except:
            pass
        if quests == None:
            raise Http404
        for q in quests:
            qset = q
    else:
        qset = comm.questionnaires.filter(slug = questionnaire).first()


    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'medit' in data:
            qSetAGs = QuestionSetAccessGroups.objects.filter(communitygroup__community=comm)
            
            for qsAG in qSetAGs:
                qsAG.can_read=False
                qsAG.can_write=False
                qsAG.save()

            for elem in data:
                if elem.startswith('elem_'):
                    r_or_w = elem[5:]
                    kid = int(r_or_w[2:])

                    if r_or_w.startswith('r_'):
                        try:
                            qsAG = qSetAGs.get(id=kid)
                            qsAG.can_read=True
                            qsAG.save()
                            #duplicate_cps = cps.filter(communitygroup=cp.communitygroup, plugin=cp.plugin)

                        except QuestionSetAccessGroups.DoesNotExist:
                            logger.error("*** QuestionSetAccessGroups.DoesNotExist ***")

                    elif r_or_w.startswith('w_'):
                        try:
                            qsAG = qSetAGs.get(id=kid)
                            qsAG.can_write=True
                            qsAG.save()
                            #duplicate_cps = cps.filter(communitygroup=cp.communitygroup, plugin=cp.plugin)

                        except QuestionSetAccessGroups.DoesNotExist:
                            logger.error("*** QuestionSetAccessGroups.DoesNotExist ***")

    # get the active groups
    ugroup = CommunityGroup.valid(community = comm)

    plugins = Plugin.all(type=Plugin.DATABASE)
    groupqsetmatrix = buildGroupQSetPermissionsMatrix(comm, ugroup, qset)
    # *** end ***

    return render(request, template_name, {
        'ugroup': ugroup,
        'groupmatrix': groupqsetmatrix,
        'comm': comm,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'qset-'+questionnaire,
        'breadcrumb': True
    })


@transaction.atomic
def manage_groups(request, community=None, template_name='manage_community_groups.html'):
    comm = get_comm(community, request)

    if isinstance(comm, HttpResponseRedirect):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'gadd' in data and len(data['gadd']) > 0:
            # Add group only if group name is unique
            ts=data['gadd'].strip()
            try:
                CommunityGroup.valid(community=comm).get(name=ts)
            except CommunityGroup.DoesNotExist:
                CommunityGroup.objects.create(community=comm, name=ts)

        elif 'gdel' in data:
            gid = int(data['gdel'])
            try:
                cg = CommunityGroup.valid(community=comm).get(id=gid)
                if cg.name not in CommunityGroup.PRE_EXISTING_GROUPS:  # dont allow deletion of pre existing groups
                    cg.removed = True
                    cg.members.clear()
                    cg.save()
                    cg.delete()
            except CommunityGroup.DoesNotExist:
                pass

        elif 'medit' in data:
            cps = PluginPermission.objects.filter(communitygroup__community=comm)
            #cps.update(allow=False)
            for cp in cps:
                cp.allow=False
                cp.save()

            for key in data:
                if key.startswith('elem_'):
                    kid = int(key[5:])
                    try:
                        cp = cps.get(id=kid)
                        cp.allow=True   # só entra aqui se o checkbox estiver activo, logo -> =True
                        cp.save()
                        #duplicate_cps = cps.filter(communitygroup=cp.communitygroup, plugin=cp.plugin)
                    except PluginPermission.DoesNotExist:
                        logger.error("*** PluginPermission.DoesNotExist ***")

    # get the active groups
    ugroup = CommunityGroup.valid(community=comm)

    matrix = buildPermissionsMatrix(comm, ugroup)
    groupmatrix = buildGroupPluginPermissionsMatrix(comm, ugroup)
    usermatrix = buildUserPermissionsMatrix(
        comm, ugroup.exclude(name=CommunityGroup.DATABASE_OWNERS_GROUP)
    )
    # *** end ***

    return render(request, template_name, {
        'ugroup': ugroup,
        'matrix': matrix,
        'usermatrix': usermatrix,
        'groupmatrix': groupmatrix,
        'comm': comm,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'groups',
        'breadcrumb': True
    })

@transaction.atomic
def manage_plugins(request, community=None, template_name='manage_community_plugins.html'):
    comm = get_comm(community, request)

    if(isinstance(comm, HttpResponseRedirect)):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'medit' in data:
            cps = PluginPermission.objects.filter(communitygroup__community=comm)
            #cps.update(allow=False)
            for cp in cps:
                cp.allow=False
                cp.save()

            for key in data:
                if key.startswith('elem_'):
                    kid = int(key[5:])
                    try:
                        cp = cps.get(id=kid)
                        cp.allow=True   # só entra aqui se o checkbox estiver activo, logo -> =True
                        cp.save()
                        #duplicate_cps = cps.filter(communitygroup=cp.communitygroup, plugin=cp.plugin)

                    except PluginPermission.DoesNotExist:
                        logger.error("*** PluginPermission.DoesNotExist ***")

    # get the active groups
    ugroup = CommunityGroup.valid(community = comm)

    grouppluginmatrix = buildGroupPluginPermissionsMatrix(comm, ugroup)
    # *** end ***

    return render(request, template_name, {
        'ugroup': ugroup,
        'groupmatrix': grouppluginmatrix,
        'comm': comm,
        'success': success,
        'request': request,
        'activemenu': 'mancomm',
        'activesubmenu': 'plugins',
        'breadcrumb': True
    })


def activate(request, hash):
    ca = get_object_or_404(CommunityActivation, hash=hash, used=False)

    community = ca.community
    if not request.user.is_superuser and not community.is_owner(request.user):
        raise Http404

    last_messages = CommunityActivationMessage \
        .objects.filter(community=community) \
        .values_list("message", flat=True)
    cu = ca.commuser

    user_info = []

    # Add user basic info
    full_name = cu.user.first_name + " " + cu.user.last_name
    user_info = [
        ('Full Name', full_name),
        ('Email', cu.user.email),
        ('Organization', cu.user.emif_profile.organization),
        ('Country', cu.user.emif_profile.country.code),
    ]

    # Add user replies
    replies = CommunityJoinFormReply.objects.filter(commuser=cu)

    for reply in replies:
        reply_tuple = reply.join_form.question_text, reply.reply_text
        user_info.append(reply_tuple)
    
    return render(
        request,
        'community_activate.html',
        {
            'hide_add': True,
            'breadcrumb': True,
            'hash': hash,
            'cu': cu,
            'user_info': user_info,
            "last_messages": last_messages,
        }
    )


def activate_confirmed(request, hash):
    ca = get_object_or_404(CommunityActivation, hash=hash, used=False)

    community = ca.community
    if not request.user.is_superuser and not community.is_owner(request.user):
        raise Http404

    ca.activate()

    cu = ca.commuser

    # if the default group does not exist, then create it.
    try:
        cg = CommunityGroup.valid(community=community).get(name=CommunityGroup.DEFAULT_GROUP)
    except CommunityGroup.DoesNotExist:
        cg = CommunityGroup.objects.create(community=community, name=CommunityGroup.DEFAULT_GROUP)

    # Add (new)user to default group.
    cg.members.add(cu)
    cg.save()

    return render(
        request,
        'community_activate_complete.html',
        {
            'request': request,
            'hide_add': True,
            'breadcrumb': True,
            'cu': cu
        },
    )


@require_GET
def dontactivate(request, hash):
    ca = get_object_or_404(CommunityActivation, hash=hash, used=False)

    community = ca.community
    if not request.user.is_superuser and not community.is_owner(request.user):
        raise Http404

    msg2user = request.GET.get("msg2user")
    ca.dontactivate(msg2user)
    community_name = community.name

    if msg2user:
        cam, _ = CommunityActivationMessage.objects.get_or_create(community=community, message=msg2user)
        ca.msg2user = cam
        ca.save()

    return render(
        request,
        "community_dontactivate.html",
        {
            'request': request,
            'hide_add': True,
            'breadcrumb': True,
            'community_name': community_name,
        },
    )


@require_GET
def block(request, hash):
    ca = get_object_or_404(CommunityActivation, hash=hash, used=False)

    community = ca.community
    if not request.user.is_superuser and not community.is_owner(request.user):
        raise Http404

    msg2user = request.GET.get("msg2user")
    ca.block(msg2user)
    cu = ca.commuser

    if msg2user:
        cam, _ = CommunityActivationMessage.objects.get_or_create(community=community, message=msg2user)
        ca.msg2user = cam
        ca.save()

    return render(
        request,
        'community_block.html',
        {
            'request': request,
            'hide_add': True,
            'breadcrumb': True,
            'cu': cu,
        },
    )


####################################### 
# Select Community Questionnaire 
#######################################

#Initial view
def select_questionnaire_view(request, community=None, template_name='community_select_questionnaire.html'):
    comm = getComm(community, request.user)
    if(isinstance(comm, HttpResponseRedirect)):
        return comm


    #if theres just one questionnaire redirect to results table
    questionnaires = comm.questionnaires.all()
    if( len(questionnaires) == 1 ):
        return redirect('fingerprint.listings.database_listing_by_community_questionnaire', community=comm.slug, questionnaire = questionnaires[0].slug)

    #show view to select questionnaire
    args = {}
    args['comm'] = comm
    args['breadcrumb'] = True
    args['activesubmenu'] = 'all'
    return TemplateResponse(request, template_name, args)


@transaction.atomic
def manage_community_join_form(request, community=None):
    comm = get_comm(community, request)

    if isinstance(comm, HttpResponseRedirect):
        return comm

    success = None
    if request.method == 'POST':
        data = request.POST

        if 'qadd' in data and len(data['qadd']) > 0:
            question_text = forms.CharField().to_python(data['qadd'])

            required_arg = {}
            if "qrequired" in data:
                converted = data["qrequired"].strip().lower()
                if converted == "yes":
                    required_arg["required"] = True
                elif converted == "no":
                    required_arg["required"] = False
                # if the value is not one of [yes, no] use model's default
            # if the required field value is not provided use model's default

            CommunityJoinForm.objects.create(community=comm, question_text=question_text, **required_arg)

        elif 'qdel' in data:
            qid = int(data['qdel'])
            try:
                cjf = CommunityJoinForm.objects.get(id=qid)
                cjf.removed = True
                cjf.save()
                cjf.delete()
            except CommunityJoinForm.DoesNotExist:
                pass

    join_form = CommunityJoinForm.objects.filter(community=comm)

    return render(request, "manage_community_join_form.html", {
        'comm': comm,
        'success': success,
        'request': request,
        'join_form': join_form,
        'activemenu': 'mancomm',
        'activesubmenu': 'join form',
        'breadcrumb': True,
    })

