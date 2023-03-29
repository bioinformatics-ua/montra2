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
from __future__ import absolute_import

from datetime import timedelta

from celery import shared_task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template import Context
from django.template.loader import render_to_string
from django.utils import timezone
from django_comments.models import Comment
from newsletter.models import Article, Message, Newsletter, Site, Submission, Subscription

from emif.utils import send_custom_mail
from population_characteristics.models import Characteristic
from searchengine.search_indexes import CoreEngine
from .models import Fingerprint, FingerprintReturnedAdvanced, FingerprintReturnedSimple
from .models import FingerprintHead, FingerprintImportFile
from .services import unindexFingerprint


# This indexes the fingerprint using the celery, so the interface doesn't have to block
@shared_task
def indexFingerprintCelery(fingerprint_hash):
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_hash)

        fingerprint.indexFingerprint()

    except Fingerprint.DoesNotExist:
        print "-- ERROR: Can't index fingerprint, because fingerprint wasn't found."


@shared_task
def anotateshowonresults(query_filtered, user, isadvanced, query_reference):
    # Operations
    print "start annotating database appearing on results"

    c = CoreEngine()
    results = c.search_fingerprint(query_filtered)
    for result in results:
        fingerprint_id = result['id']

        if not fingerprint_id.startswith("questionaire_"):
            try:
                fp = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)
                print "processing "+str(fp)

                if isadvanced:
                    fingerprintreturn = FingerprintReturnedAdvanced(fingerprint=fp, searcher=user, query_reference=query_reference)
                    fingerprintreturn.save()
                else:
                    fingerprintreturn = FingerprintReturnedSimple(fingerprint=fp, searcher=user, query_reference=query_reference)
                    fingerprintreturn.save()

            except Fingerprint.DoesNotExist:
                print fingerprint_id + ' doesnt exist on db'

    print "ends annotation of databases appearing on results"
    return 0

@periodic_task(run_every=crontab(minute=settings.NEWSLETTER_MIN, hour=settings.NEWSLETTER_HOUR, day_of_week=settings.NEWSLETTER_DAY))
def very_long_drafts():
    print " Going around, checking for old draft databases"
    fingerprints = Fingerprint.objects.filter(draft=True, fingerprint_hash='6abcccf8c478f82cc4d29c671671ad08')

    for fingerprint in fingerprints:
        since_update = timezone.now() - fingerprint.last_modification

        uu = fingerprint.unique_users()
        dcs = []

        for u in uu:
            dcs.append(u.email)

        if since_update.days > 30:
            # if there is been 30 days since last update, and the database is draft, double check if user didnt forget the database.
            send_custom_mail('%s: %s has not been updated recently' % (settings.GLOBALS['BRAND'], fingerprint.findName()),
            """Dear Database Custodian,\n
                    We noticed your %s database has not been updated in the last month, and still is in a draft stage.\n

                    Draft databases will not appear for other users. \n

                    If you desire to mark your database as a available database,
                    please disable draft mode <a href="%sfingerprint/%s/1/">here</a>.

                    \nSincerely,\n%s
            """ %(fingerprint.findName(),
             settings.BASE_URL,fingerprint.fingerprint_hash,
             settings.GLOBALS['BRAND']), settings.DEFAULT_FROM_EMAIL, dcs)


@periodic_task(run_every=crontab(minute=settings.NEWSLETTER_MIN, hour=settings.NEWSLETTER_HOUR, day_of_week=settings.NEWSLETTER_DAY))
def generate_newsmessages():
    # Operations
    print "start generating weekly newsletters messages"

    if not config.newsletter:
        print 'Ignored, newsletter is disabled'

    elif not settings.DEBUG:
        fingerprints = Fingerprint.objects.valid()

        newsletters = Newsletter.objects.all().exclude(slug='emif-catalogue-newsletter')

        for fingerprint in fingerprints:
            try:
                print "Generating for "+fingerprint.fingerprint_hash
                newsletter = newsletters.get(slug=fingerprint.fingerprint_hash)

                report = generateWeekReport(fingerprint, newsletter)

                putWeekReport(report, newsletter)

            except Newsletter.DoesNotExist:
                print "-- Error: Found hash not existent on newsletters: "+fingerprint.fingerprint_hash

        print "ends generation"

        print "start sending emails"

        aggregate_emails()

        print "finished sending emails"

        print "--"
        return 0
    else:
        print 'Aborted since we are on DEBUG mode'

def aggregate_emails():
    submissions_waiting = Submission.objects.filter(prepared=True, sent=False)

    if len(submissions_waiting) > 0:
        subscribed_users = Subscription.objects.filter(~Q(newsletter__slug = 'emif-catalogue-newsletter'), subscribed=True).values('user').distinct()

        for user in subscribed_users:
            this_user = User.objects.get(id=user['user'])

            if not this_user.is_active:
                continue

            related_submissions = submissions_waiting.filter(subscriptions__user=this_user)

            if this_user.emif_profile.mail_news == True and len(related_submissions) > 0:
                htmlcache = []
                textcache = []

                for submission in related_submissions:
                    subs=submission.subscriptions.get(user=this_user)
                    variable_dict = {
                        'subscription': subs,
                        'site': Site.objects.get_current(),
                        'submission': submission,
                        'message': submission.message,
                        'newsletter': submission.newsletter,
                        'date': submission.publish_date,
                        'STATIC_URL': settings.STATIC_URL,
                        'MEDIA_URL': settings.MEDIA_URL
                    }

                    (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', submission.message.newsletter)

                    unescaped_context = Context(variable_dict, autoescape=False)

                    subject = subject_template.render(unescaped_context).strip()
                    textcache.append(text_template.render(unescaped_context))

                    escaped_context = Context(variable_dict)
                    htmlcache.append(html_template.render(escaped_context))

                html = render_to_string("updates_email.html", {'content': ''.join(htmlcache)})


                message = EmailMultiAlternatives(config.brand+' Newsletter - Database Updates on '+str(timezone.now().strftime('%d/%m/%Y %H:%M')),
                ''.join(textcache),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subs.get_recipient()]
                )

                message.attach_alternative(html,"text/html")
                message.send()

        for submission in submissions_waiting:
            submission.sent=True
            submission.save()

def generateWeekReport(fingerprint, newsletter):

    returnable = {}

    latest_check = timezone.now() - timedelta(days=7)

    fh = FingerprintHead.objects.filter(fingerprint_id = fingerprint, date__gte = latest_check)

    if len(fh) == 0:
        returnable['db_changes'] = None
    else:
        returnable['db_changes'] = render_to_string('subscriptions/fingerprint_changes.html', {
                                        'base_url': settings.BASE_URL,
                                        'changes': FingerprintHead.mergeChanges(fh),
                                        'fingerprint': fingerprint.fingerprint_hash
                                    })

    discussion = Comment.objects.filter(object_pk = fingerprint.id, submit_date__gte = latest_check)
    if not config.discussion or len(discussion) == 0:
        returnable['discussion'] = None
    else:
        returnable['discussion'] = render_to_string('subscriptions/discussion_changes.html', {
                                        'base_url': settings.BASE_URL,
                                        'discussions': discussion,
                                        'fingerprint': fingerprint.fingerprint_hash
                                    })

    characteristic = Characteristic.objects.filter(created_date__gte = latest_check).order_by('-created_date')
    if not config.population_characteristics or len(characteristic) == 0:
        returnable['characteristic'] = None
    else:
        returnable['characteristic'] = render_to_string('subscriptions/pop_changes.html', {
                                        'base_url': settings.BASE_URL,
                                        'pop': characteristic
                                    })

    return returnable

def putWeekReport(report, newsletter):

    # if nothing changed, nothing to report, moving on.
    if report['db_changes'] == None and report['discussion'] == None and report['characteristic'] == None:
        return

    now = timezone.now()

    mess = Message(title=newsletter.title+" - Recent Changes - "+now.strftime("%Y-%m-%d %H:%M"),slug=newsletter.slug+'_'+now.strftime("%Y%m%d%H%M%S"), newsletter=newsletter)
    mess.save()

    if report['db_changes'] != None:
        art = Article(title="Changes on Database:", text=report['db_changes'], post=mess)
        art.save()

    if report['discussion'] != None:
        art2 = Article(title="New Discussion:", text=report['discussion'], post=mess)
        art2.save()

    if report['characteristic'] != None:
        art3 = Article(title="New Population Characteristic Data:", text=report['characteristic'], post=mess)
        art3.save()

    subm = Submission.from_message(mess)

    subm.prepared = True

    subm.save()


@shared_task
def calculateFillPercentage(fingerprint):
    fingerprint.updateFillPercentage()
    fingerprint.indexFingerprint()

@periodic_task(run_every=crontab(minute=0, hour=3))
def remove_orphans():
    # Operations
    print "start removing old orphans databases"

    time = timezone.now() - timedelta(days=1)

    fingers = Fingerprint.objects.filter(last_modification__lte = time)

    for finger in fingers:

        name = finger.findName()

        if name == 'Unnamed':
            print "-- Removing orphan "+str(finger.fingerprint_hash)
            finger.removed=True
            finger.save()
            unindexFingerprint(finger.fingerprint_hash)


    print "ends removing old orphans databases"
    return 0


@shared_task
def importFingerprint(uploaded_file, force_qtype, qtype, force_community):
    from fingerprint.imports import FingerprintImporter

    print "Importing fingerprint async"
    qi = FingerprintImportFile.objects.get(id=uploaded_file)

    qi.status = FingerprintImportFile.PROCESSING
    qi.save()

    iq = FingerprintImporter.getInstance('zip', qi.file)

    if force_qtype and qtype:
        iq.import_fingerprint(force_questionnaire=qtype, force_community=force_community)

    else:
        iq.import_fingerprint()

    qi.status = FingerprintImportFile.FINISHED
    qi.save()


@shared_task
def update_fill_percentages_of_questionnaire(questionnaire_id):
    fps_docs = []
    for fp in Fingerprint.objects.filter(questionnaire__id=questionnaire_id):
        fp.updateFillPercentage(reset=True)
        fps_docs.append(fp.indexFingerprint(batch_mode=True))

    c = CoreEngine()
    c.index_fingerprints(fps_docs)
