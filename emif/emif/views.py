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
# import the logging library
import logging
import os.path
import sys
import traceback

from allauth.socialaccount.models import SocialApp
from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError, EmailMultiAlternatives, send_mail
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

import developer
from accounts.models import TermsConditions
from api.models import FingerprintAPI
from community.models import Community
from fingerprint.listings import get_databases_from_solr, get_databases_from_solr_v2
from fingerprint.models import Fingerprint
from fingerprint.services import create_multimontra, save_answers_to_csv
from notifications.models import Notification
from questionnaire.models import Question, Questionnaire
from searchengine.models import Slugs
from security.recaptcha import Recaptcha
from taskqueue.models import QueueJob
from .models import ContactForm, InvitePending, SharePending
from .utils import activate_user, generate_hash, send_custom_mail

logger = logging.getLogger(__name__)


def documentation(request, template_name='documentation.html'):

    md = None

    with open (os.path.abspath("emif/static/markdown/README.md"), "r") as myfile:
        md=''.join(myfile.readlines())

    comm = None
    if settings.SINGLE_COMMUNITY:
        comm = Community.objects.all()[:1].get()

    return render(request, template_name, {
            'request': request,
            'breadcrumb': True,
            'activemenu': 'documentation',
            'docs': md,
            'comm': comm
        })



def get_api_info(fingerprint_id):
    """This is an auxiliar method to get the API Info
    """
    result = {}


    results = FingerprintAPI.objects.filter(fingerprintID=fingerprint_id)
    result = {}
    for r in results:
        result[r.field] = r.value
    return result



def index(request, template_name='index_new.html'):
    referal = request.GET.get('ref', None)

    if request.user.is_authenticated():
        if referal != None:
            return HttpResponseRedirect(settings.BASE_URL + referal)
        else:
            return HttpResponseRedirect(reverse ('community-splash'))
    else:
        if config.login_bypass:
            return HttpResponseRedirect(reverse ('community-splash'))

    return HttpResponseRedirect(reverse ('login_emif'))

def login_emif(request, template_name='index_new.html'):
    referal = request.GET.get('ref', None)

    try:
        availableTerms = True
        all_enabled_terms = TermsConditions.objects.filter(enabled=True)
        if all_enabled_terms:
            terms = all_enabled_terms[0]
    except:
        traceback.print_exc(file=sys.stdout)
        availableTerms = False

    tags = ','.join(filter(None,set(Community.objects.all().values_list('tags__slug', flat=True))))

    providers = SocialApp.objects.values_list('provider', flat=True)

    return render(request, template_name, {
        'request': request, 
        'availableTerms': availableTerms,
        'referal': referal,
        'tags': tags,
        'providers': providers
    })

def index_beta(request, template_name='index_beta.html'):
    return index(request, template_name=template_name)

def about(request, template_name='about.html'):
    return render(request, template_name, {'request': request, 'breadcrumb': True, 'activemenu': 'about'})

def bootstrap_ie_compatibility(request, template_name='bootstrap_ie_compatibility.css'):
    return render(request, template_name, {'request': request, 'breadcrumb': False})

def statistics(request, questionnaire_id, question_set, template_name='statistics.html'):
    try:
        quest = Questionnaire.objects.get(id=questionnaire_id)

        qs_list = quest.questionsets()

        if int(question_set) == 99:
            question_set = len(qs_list) - 1
        question_set = qs_list[int(question_set)]

        questions = Question.objects.filter(questionset=question_set)

        return render(request, template_name, {'request': request, 'questionset': question_set,
                                               'breadcrumb': True, 'questions_list': questions,
                                               'questionnaire_id': questionnaire_id})

    except Questionnaire.DoesNotExist:
        raise Exception("The questionnaire %s does not exist. Cant get statistics view")

    return None


def handle_uploaded_file(f):
    with open(os.path.join(os.path.abspath(settings.PROJECT_DIR_ROOT + 'emif/static/upload_images/'), f.name),
              'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def feedback(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)
        if form.is_valid():  # All validation rules pass
            if config.recaptcha_verification:
                recaptcha = Recaptcha(settings.BASE_URL,  settings.RECAPTCH_PUBLIC_KEY, settings.RECAPTCH_PRIVATE_KEY)
                capchaVerified = recaptcha.verify(request.POST.get('g-recaptcha-response', ''))
                if not capchaVerified: 
                    return HttpResponse('Invalid Recaptcha. Please try again.')
            subject = request.POST.get('topic', '').encode('ascii', 'ignore')
            name = request.POST.get('name', '').encode('ascii', 'ignore')
            message = request.POST.get('message', '').encode('ascii', 'ignore')
            from_email = request.POST.get('email', '')

            emails_to_feedback = []
            for k, v in settings.ADMINS:
                emails_to_feedback.append(v)

            try:
                message_admin = "Name: " + str(name) + "\nEmail: " + from_email + "\n\nMessage:\n" + str(message)
                message = "Dear " + name + ",\n\nThank you for giving us your feedback.\n\nYour message will be analyzed by "+config.brand+" team.\n\nMessage sent:\n" + str(message) + "\n\nSincerely,\n"+config.brand
                # Send email to admins
                send_custom_mail(subject, message_admin, settings.DEFAULT_FROM_EMAIL, emails_to_feedback)
                # Send email to user with the copy of feedback message
                send_custom_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [from_email])

            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return feedback_thankyou(request)

    else:
        form = ContactForm()  # An unbound form
        if request.user.is_authenticated():
            form=ContactForm(initial={'name': request.user.get_full_name(),'email':request.user.email})

    comm = None
    if settings.SINGLE_COMMUNITY:
        comm = Community.objects.all()[:1].get()

    return render(request, "feedback.html", {
        'form': form, 'request': request, 'breadcrumb': True, 'RECAPTCH_PUBLIC_KEY': settings.RECAPTCH_PUBLIC_KEY,
        'activemenu': 'feedback', 'activesubmenu': 'suggestions', 'comm': comm
        })


def feedback_thankyou(request):
    return render(request, "feedback_thankyou.html", {'request': request, 'breadcrumb': True, 'activemenu': 'feedback'})


def inviteCommunity(request, db_id, template_name="sharedb.html"):
    email = request.POST.get('email', '')
    custom_message = request.POST.get('message', '')
    subject = request.POST.get('subject', '')
    base_addr = request.POST.get('base_addr', '')
    comm_name = request.POST.get('comm_name', '')

    
    invite_link = base_addr+"community/join/"+comm_name
    message = '%s\nPlease register in the %s at the link below: \n%s\n\nSincerely,\n%s' % (custom_message, config.brand, invite_link, config.brand)
    result = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    
    msg = EmailMultiAlternatives(subject, message,[settings.DEFAULT_FROM_EMAIL], [email])
#    msg.send()
    REFRESH = '<META HTTP-EQUIV="Refresh" CONTENT="1; URL='+base_addr+'community/manage/'+comm_name+'/users">'
    return HttpResponse("An invitation has been sent to "+email+" "+REFRESH)
# ***


def invitedb(request, db_id, template_name="sharedb.html"):
    email = request.POST.get('email', '')
    message_write = request.POST.get('message', '')
    if (email == None or email==''):
        return HttpResponse('Invalid email address.')

    fingerprint = None
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=db_id)
    except Fingerprint.DoesNotExist:
        print "Fingerprint with id "+db_id+" does not exist."
        return HttpResponse("Service Unavailable")

    subject = config.brand+": A new database is trying to be shared with you."
    link_invite = settings.BASE_URL + "accounts/signup/"

    message = """%s\n
            To have full access to this fingerprint, please register in the %s following the link below: \n\n
            %s
            \n\nSincerely,\n%s
    """ % (message_write, config.brand, link_invite, config.brand)


    send_custom_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


    pend = None

    try:
        pend = InvitePending.objects.get(fingerprint=fingerprint, email=email)
        return HttpResponse("User already has been invited to join catalogue")
    except:
        pass

    pend = InvitePending(fingerprint=fingerprint, email=email)
    pend.save()

    return HttpResponse("An invitation has been sent to the user email so he can signup on catalogue")

def sharedb(request, db_id, template_name="sharedb.html"):
    if not request.method == 'POST':
        return HttpResponse("Service Unavailable")

    # Verify if it is a valid email
    email = request.POST.get('email', '')
    message = request.POST.get('message', '')
    if (email == None or email==''):
        return HttpResponse('Invalid email address.')

    # Verify if it is a valid user name
    username_to_share = None
    try:
        username_to_share = User.objects.get(email__exact=email)
    except Exception, e:
        pass

    if not username_to_share:
        return HttpResponse("Invalid email address.")


    # Verify if it is a valid database
    if (db_id == None or db_id==''):
        return HttpResponse('Service Unavailable')

    fingerprint = None
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=db_id)
    except Fingerprint.DoesNotExist:
        return HttpResponse("Service Unavailable")

    subject = config.brand+": A new database has been shared with you."
    name = username_to_share.get_full_name()
    message = request.POST.get('message', '')
    from_email = request.POST.get('email', '')

    __objs = SharePending.objects.filter(db_id=db_id, pending=True, user=username_to_share)
    if (len(__objs)>0):
        share_pending = __objs[0]
        success_msg = "You have already invited this user to start collaborating in your database. The invitation email was re-sent to his address."
    else:
        share_pending = SharePending()
        share_pending.user = username_to_share
        share_pending.db_id = db_id
        share_pending.activation_code = generate_hash()
        share_pending.pending = True
        share_pending.user_invite = request.user
        share_pending.save()
        success_msg = "An invitation has been sent to your co-worker start collaboration in your database. If you need further assistance, please do not hesitate to contact "+config.brand+" team."

    link_activation = settings.BASE_URL + "share/activation/"+share_pending.activation_code

    new_notification = Notification(destiny=username_to_share ,origin=request.user,
        notification=(fingerprint.findName()+" has been shared with you, please click here to activate it."), type=Notification.SYSTEM, href=link_activation)

    new_notification.save()

    emails_to_feedback = []
    for k, v in settings.ADMINS:
        emails_to_feedback.append(v)

    try:

        message = """%s

            Now you're able to edit and manage the database. \n\n
            To activate the database in your account, please open this link:
            %s
            \n\nSincerely,\n%s
        """ % (message, link_activation, config.brand)
        # Send email to admins
        #send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails_to_feedback)
        # Send email to user with the copy of feedback message
        send_custom_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [from_email])

    except BadHeaderError:
        return HttpResponse('Service Unavailable')

    return HttpResponse(success_msg)

def sharedb_activation(request, activation_code, template_name="sharedb_invited.html"):

    return activate_user(activation_code, request.user, context = request, template_name=template_name)


def export_all_answers(request, community):
    """
    Method to export all databases answers to a csv file
    """
    comm = get_object_or_404(Community, slug=community)

    if not comm.belongs(request.user):
        raise Http404

    list_databases = get_databases_from_solr(request, "communities_t:"+comm.slug)

    qj = QueueJob(
        title='Export of all database answers in %s - %s' % (comm.name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user,
    )
    qj.save()

    args = [list_databases, 'DBs']

    qj.execute(save_answers_to_csv, args)

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'An export of all databases has been scheduled to be exported.',
            "job_queue_menu": config.jobQueueMenu,
        },
    )


@require_http_methods(["GET"])
def export_selected_answers(request, community):
    """
    Method to export selected databases answers to a csv file
    """
    comm = get_object_or_404(Community, slug=community)

    if not comm.belongs(request.user):
        raise Http404

    fingerprints = request.GET.get('fingerprints')
    if fingerprints is None or not fingerprints:
        return HttpResponseBadRequest()

    fingerprints = fingerprints.split(",")
    if not fingerprints:
        return HttpResponseBadRequest()

    list_databases, hits = get_databases_from_solr_v2(
        request,
        'communities_t:{} AND id:({})'.format(comm.slug, ' OR '.join(f.strip() for f in fingerprints))
    )

    if not hits:
        return HttpResponseNotFound()

    qj = QueueJob(
        title='Export of selected database answers in %s - %s' % (comm.name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user,
    )
    qj.save()

    args = [list_databases, 'SelectedDBs']

    qj.execute(save_answers_to_csv, args)

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'An export of selected databases has been scheduled to be exported.',
            "job_queue_menu": config.jobQueueMenu,
        },
    )


@require_http_methods(["GET"])
def export_selected_answers_multimontra(request, community):
    """
    Method to export selected databases answers to a montra file
    """
    if not request.user.is_staff:
        return HttpResponseForbidden()

    comm = get_object_or_404(Community, slug=community)

    fingerprints = request.GET.get('fingerprints')
    if fingerprints is None or not fingerprints:
        return HttpResponseBadRequest()

    fingerprints = fingerprints.split(",")
    if not fingerprints:
        return HttpResponseBadRequest()

    list_databases, hits = get_databases_from_solr_v2(
        request,
        'communities_t:{} AND id:({})'.format(comm.slug, ' OR '.join(f.strip() for f in fingerprints))
    )

    if not hits:
        return HttpResponseNotFound()

    qj = QueueJob(
        title='Export of selected database answers in multimontra format in %s - %s' % (comm.name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user,
    )
    qj.save()

    list_databases = [db.id for db in list_databases]

    qj.execute(create_multimontra, (list_databases,))

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'An export of selected databases in multimontra format has been scheduled to be exported.',
            "job_queue_menu": config.jobQueueMenu,
        },
    )


def export_my_answers(request, community):
    """
    Method to export my databases answers to a csv file
    """
    comm = get_object_or_404(Community, slug=community)

    if not comm.belongs(request.user):
        raise Http404

    user = request.user
    list_databases = get_databases_from_solr(request, "user_t:" + '"' + user.username + '" AND communities_t:'+comm.slug)

    qj = QueueJob(
        title='Export of my databases in %s - %s' % (comm.name, timezone.now().strftime('%B %d, %Y, %I:%M %p')),
        runner=request.user
    )
    qj.save()

    args = [list_databases, 'MyDBs']

    qj.execute(save_answers_to_csv, args)

    return render(
        request,
        'exporting_message.html',
        {
            'request': request,
            'message': 'An export of your databases has been scheduled to be exported.',
            "job_queue_menu": config.jobQueueMenu,
        },
    )


def export_search_answers(request, template_name='exporting_message.html'):
    """
    Method to export search databases answers to a csv file
    """

    user = request.user

    query = None
    isadvanced = request.session.get('isAdvanced')
    value = request.session.get('query')

    if(isadvanced):
        query = value
    else:
        query = "text_txt:"+str(value)

    list_databases = get_databases_from_solr(request, query)



    qj = QueueJob(
            title = 'Export of search result databases - %s' % (timezone.now().strftime('%B %d, %Y, %I:%M %p')),
            runner = request.user
        )
    qj.save()

    args = [list_databases, 'Search Results']

    qj.execute(save_answers_to_csv, args)

    return render(request, template_name, {
        'request': request,
        'message': 'An export of current search results has been scheduled.',
        "job_queue_menu": config.jobQueueMenu,
    })


# Auxiliar Implementation
def serveStatic(filePath):

    fsock = open(filePath, "r")
    return HttpResponse(fsock)

# Patch for production
def serveThemeGithub(request):
    
    
    pth = os.path.dirname(developer.__file__)
    return serveStatic(pth+'/static/js/vendor/theme-github.js')
    
# Patch for production

def serveModeJs(request):

    pth = os.path.dirname(developer.__file__)
    return serveStatic(pth+'/static/js/vendor/mode-javascript.js')
    
