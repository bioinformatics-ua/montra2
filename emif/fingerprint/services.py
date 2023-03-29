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
import csv
import datetime
import logging
import os
import tempfile
import zipfile
from datetime import timedelta

import six
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File as DjangoFile
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

from community.models import Community
from notifications.services import sendNotification
from questionnaire import AnswerException, Processors, QuestionProcessors
from questionnaire.models import QuestionSet, Questionnaire
from questionnaire.services import createqsets
from questionnaire.utils import split_numal
from questionnaire.views import get_question
from searchengine.search_indexes import CoreEngine
from taskqueue.models import QueueJob
from .export import FingerprintExporter
from .models import Answer, AnswerChange, AnswerRequest, Fingerprint, FingerprintHead


def define_rows(request):

    ttype = 'answers'

    if request.POST and "page_rows" in request.POST and request.user.is_authenticated():
        rows = int(request.POST["page_rows"])

        profile = request.user.emif_profile

        profile.paginator = rows

        profile.save()

    else:
        # Otherwise get number of rows from preferences
        rows = 5

        try:
            profile = request.user.emif_profile

            rows = profile.paginator

        except:
            pass

    if rows == -1:
        rows = 99999

    if request.POST and "t_search" in request.POST and request.user.is_authenticated():
        ttype = request.POST["t_search"]

        profile = request.user.emif_profile

        profile.search_type = ttype

        profile.save()

    return (rows, ttype)

def merge_highlight_results(query, resultHighlights):
    c = CoreEngine()
    h = {}
    h["results"] = resultHighlights

    if query:
        qresults = c.highlight_questions(query)
        h["questions"] = qresults.highlighting

    return h

def saveFingerprintAnswers(qlist_general, fingerprint_id, questionnaire, user, extra_fields=None, created_date=None, community=None):
    # Update or create fingerprint entry
    fingerprint = updateFingerprint(fingerprint_id, questionnaire, user, community)


    def saveChanges(versionhead, fingerprint, this_ans, current_value, value, current_comment, comment):
        # create version head if not any yet
        if versionhead == None:
            # find out if we already have other revisions, if not revision starts at 1
            revision = None

            try:
                last_revision = FingerprintHead.objects.filter(fingerprint_id=fingerprint).order_by('-id')[0]

                revision = last_revision.revision+1
            except:
                revision = 1

            versionhead = FingerprintHead(fingerprint_id=fingerprint, revision=revision)

            versionhead.save()

        # save answerchange
        answerchange = AnswerChange(revision_head=versionhead, answer=this_ans, old_value=current_value, new_value=value, old_comment=current_comment, new_comment=comment)
        answerchange.save()

        return versionhead


    # If no errors on getting the fingerprint, update/add the new questions
    if fingerprint != None:
        # i get them all, instead of a query for each, is probabily faster this way
        answers = Answer.objects.filter(fingerprint_id=fingerprint)

        # TO DO
        # For each response in qlist_general

        versionhead = None

        # we must mark answer requests as solved if any exist when a question is given an response
        answer_requests = AnswerRequest.objects.filter(fingerprint=fingerprint, removed = False)

        for qs_aux, qlist in qlist_general:
            for question, qdict in qlist:
                value = getAnswerValue(question, qdict)
                comment = getComment(question, extra_fields)

                if value != None:
                    if value.strip() != "":
                        markAnswerRequests(user, fingerprint, question, answer_requests)

                    this_ans = None
                    try:
                        this_ans = Answer.objects.get(fingerprint_id=fingerprint, question=question)

                        current_value = this_ans.data
                        current_comment = this_ans.comment

                        # update existing answers
                        this_ans.data=value;

                        #if comment != None:
                        this_ans.comment=comment;

                        this_ans.save()

                        # if value or comment changed
                        if current_value != value or current_comment != comment:
                            versionhead = saveChanges(versionhead, fingerprint, this_ans, current_value, value, current_comment, comment)

                    except Answer.DoesNotExist:
                        # new ,create new answer
                        this_ans = Answer(question=question, data=value, comment=comment, fingerprint_id=fingerprint)
                        this_ans.save()
                        if not ((value == None or value.strip() =='') and (comment == None or comment.strip() == '')):
                            versionhead = saveChanges(versionhead, fingerprint, this_ans, None, value, None, comment)


        fingerprint.save()

        #This is kind of heavy, so we do it on the background
        #because of cyclical dependencies, i just can import it here... i know its bad but i didn't knew of any other way
        from fingerprint.tasks import calculateFillPercentage
        calculateFillPercentage.delay(fingerprint)
        #calculateFillPercentage(fingerprint)

        return checkMandatoryAnswers(fingerprint)
        # format for answers : Answer(question=question, data=data, comment=comment, fingerprint_id=fingerprint_id)

def getComment(question, extra_fields):

    try:
        comment = extra_fields['comment_question_'+question.slug_fk.slug1+"_t"].strip()

        return comment
    except:
        pass


    return None

# Checks if all mandatory answers have been answered, namely fingerprint name
def checkMandatoryAnswers(fingerprint):
    try:
        name = Answer.objects.get(fingerprint_id=fingerprint, question__slug_fk__slug1="database_name", next_answer__isnull = True)

        if name.data.strip() == "":
            return False

    except Answer.DoesNotExist:
        return False

    return True

def getAnswerValue(question, qdict):

    try:
        choices = None
        value = None
        choices_txt = None

        if qdict.has_key('timeperiods'):
            value = qdict['value']

            for key, repres, used in qdict['timeperiods']:
                if used==True:
                    value += '#%s'%key
        elif qdict.has_key('value'):
            value = qdict['value']

        elif qdict.has_key('current'):
            value = qdict['current']

        elif qdict.has_key('choices'):
            choices = qdict['choices']

            qv = ""
            try:
                qv = qdict['qvalue']

                if qv == '_entry_':
                    qv += ' ' + str(qdict['opt'])

            except:
                pass

            value = ""
        
            do_again = False
            try:
                if len(choices[0])==3:
                    for choice, unk, checked  in choices:
                        if checked != "":
                            value = value + "#" + choice.value

                elif len(choices[0])==4:
                    # Have to ignore the first choice, since it's been saved before
                    for choice, unk, checked, _aux  in choices:
                        if checked != "":
                            if _aux != "":
                                value = value + "#" + choice.value + "{" + _aux +"}"
                            else:
                                value = value + "#" + choice.value

                elif len(choices[0])==2:
                    for checked, choice  in choices:
                        if checked:
                            value = value + "#" + choice.value

            except:
                do_again = True

            if do_again:
                for checked, choice  in choices:
                    if checked:
                        value = value + "#" + choice.value

            if len(value) > 0:
                value = value[1:]
            '''
            TO-DO
            Verify if symbols || (separator) is compatible with solr
            '''
            #Save in case of extra field is filled
            if qdict.has_key('extras'):
                extras = qdict['extras']
                for q, val in extras:
                    if val:
                        value = value + "||" + val


        else:
            pass

        slug = question.slug_fk.slug1

        return value
    except:
        pass

    return None

def updateFingerprint(fingerprint_id, questionnaire, user, community=None):

    def getUser(user):
        try:
            user = User.objects.get(username=user)

            return user

        except User.DoesNotExist:
            logging.error("Couldnt find user %s", user)
            return None

    fingerprint = None

    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)

        # In case already exists, update latest modification time
        fingerprint.last_modification = timezone.now()
        fingerprint.save()
        #fingerprint.indexFingerprint()

    # In case is a new one, create it
    except Fingerprint.DoesNotExist:

        user_fk = getUser(user)

        if user_fk is None:
            logging.error("-- ERROR: Could not save fingerprint because user '%s' does not exist.", user)
        elif questionnaire is None or not isinstance(questionnaire, Questionnaire):
            logging.error("-- ERROR: You must pass a valid questionnaire object to save a fingerprint.")
        else:
            # At this point the description isnt being used (since there's no way to add descriptions to a fingerprint on the gui)
            fingerprint = Fingerprint(fingerprint_hash=fingerprint_id,
                description="",
                questionnaire=questionnaire,
                community=community,
                last_modification=timezone.now(),
                created=timezone.now(),
                owner=user_fk)
            fingerprint.save()

    return fingerprint

def deleteFingerprint(fingerprint_id, username, community=None):
    user= str(username.email)

    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_id)
        
        # Check permissions
        comm = None  
        if community!=None:
            comm = Community.objects.get(slug=community)
        should_delete = belongsUser(fingerprint, user) or\
                                  (comm!=None and comm.is_owner(username))
        if username.is_superuser or should_delete == True:
            fingerprint.removed=True
            fingerprint.save()
            unindexFingerprint(fingerprint_id)

    except Fingerprint.DoesNotExist:
        logging.error("Tried to delete fingerprint who doesnt exist")

def belongsUser(fingerprint, email):
    if fingerprint.owner.email == email:
        return True

    for share in fingerprint.shared.all():
        if share.email == email:
            return True

    return False

def unindexFingerprint(fingerprint_id):
    c = CoreEngine()
    c.delete(fingerprint_id)

def markAnswerRequests(user, fingerprint, question, answer_requests):

    this_requests = answer_requests.filter(question=question)

    for req in this_requests:
        # We set the request as fullfilled
        req.removed = True
        req.save()

        message = "User "+str(fingerprint.owner.get_full_name())+" answered some questions you requested on database "+str(fingerprint.findName())+"."

        sendNotification(timedelta(hours=12), req.requester, fingerprint.owner,
            "c/"+fingerprint.community.slug+"/fingerprint/"+fingerprint.fingerprint_hash+"/"+str(question.questionset.sortid), message)

def intersect(answers, questionset):

    # i know, this would be simpler if we just had the __in query, but we could only do this
    # if we deleted entries on Answer, and i don't want to do that because of the versioning
    # (on field can be empty, be filled, be empty and be filled again), the version has a pointer to the answer
    # we can't go around deleting entries... is preferable to do the process of checking for emptyness in this query

    non_empty = []
    for ans in answers.filter(question__in=questionset.questions()):
        if ans.data != None and ans.data != '':
            non_empty.append(ans)

    return non_empty


def setNewPermissions(request, fingerprint, identification):
    """
    Set new permissions for a questionset, based on a post request
    """
    identification = request.POST.get('_qs_perm', None)

    this_permissions                = fingerprint.getPermissions(QuestionSet.objects.get(id=identification))

    this_permissions.visibility     = int(request.POST.get('_qs_visibility', '0'))
    this_permissions.allow_indexing = (request.POST.get('_qs_indexing', 'true') == 'true')
    this_permissions.allow_exporting= (request.POST.get('_qs_exporting', 'true') == 'true')

    this_permissions.save()


def extract_answers(request2, questionnaire_id, question_set, qs_list):

    question_set2 = question_set
    request = request2
    items = request.POST.items()

    logging.debug('Extract answers....')

    # Extract files if they exits
    uploaded_paths = uploadfiles(request)

    logging.debug('upload paths')
    logging.debug(uploaded_paths)

    questionnaire = qsobjs = None
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        qsobjs = questionnaire.questionsets()

    except Questionnaire.DoesNotExist:
        raise Exception("The questionnaire %s does not exist. Cant extract_answers")

    sortid = 0

    if request.POST:
        try:
            question_set = request.POST['active_qs']
            sortid = request.POST['active_qs_sortid']
            fingerprint_id = request.POST['fingerprint_id']
        except:
            for qs in qsobjs:
                if qs.sortid == int(sortid):
                    question_set = qs.pk
                    break

    expected = []
    for qset in qsobjs:
        questions = qset.questions()
        for q in questions:
            expected.append(q)

    extra = {} # question_object => { "ANSWER" : "123", ... }
    extra_comments = {}
    extra_qhighlight = {}
    extra_fields = {}
    # this will ensure that each question will be processed, even if we did not receive
    # any fields for it. Also works to ensure the user doesn't add extra fields in
    '''for x in expected:
        items.append((u'question_%s_Trigger953' % x.number, None))
    '''
    # generate the answer_dict for each question, and place in extra
    for item in items:
        key, value = item[0], item[1]
        if key.startswith('comment_question_') or key.endswith('_ignoreme_') or key.startswith('qhighlight_question_'):
            continue
        if key.startswith('question_'):
            answer = key.split("_", 2)
            question = get_question(answer[1], questionnaire)
            if not question:
                logging.warn("Unknown question when processing: %s" % answer[1])
                continue
            extra[question] = ans = extra.get(question, {})
            if (len(answer) == 2):
                ans['ANSWER'] = value
            elif (len(answer) == 3):
                ans[key] = value
            else:
                logging.warn("Poorly formed form element name: %r" % answer)
                continue
            extra[question] = ans



            comment_id = "comment_question_"+question.number#.replace(".", "")
            qhighlight_id = "qhighlight_question_"+question.number

            try:
                if request.POST and request.POST[comment_id]!='':
                    #comment_id_index = "comment_question_"+question.slug
                    comment_id_index = "comment_question_"+question.slug_fk.slug1
                    extra_comments[question] = request.POST[comment_id]
                    extra_fields[comment_id_index+'_t'] = request.POST[comment_id]
            except KeyError:
                pass

            try:
                if request.POST and request.POST[qhighlight_id]!='':
                    #comment_id_index = "comment_question_"+question.slug
                    qh_id_index = "qhighlight_question_"+question.slug_fk.slug1
                    extra_qhighlight[question] = request.POST[qhighlight_id]
            except KeyError:
                pass

    errors = {}

    # Verification of qprocessor answers
    def verify_answer(question, answer_dict):

        type = question.get_type()

        if "ANSWER" not in answer_dict:
            answer_dict['ANSWER'] = None
        answer = None
        if type in Processors:
            answer = Processors[type](question, answer_dict) or ''

        return True

    active_qs_with_errors = False

    for question, ans in extra.items():

        try:
            cd = question.getcheckdict()

            depon = cd.get('requiredif', None) or cd.get('dependent', None)

            verify_answer(question, ans)

        except AnswerException as e:
            errors[question.number] = e
            logging.exception("AnswerException")
        except Exception:
            logging.exception("Unexpected Exception")
            raise

    try:
        questions = question_set2.questions()

        questions_list = {}
        for qset_aux in qs_list:
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
                    key = "question_%s" % question.number

                    if(uploaded_paths.has_key(key)):
                        qdict.update(QuestionProcessors[Type](request2, question, uploaded_paths[key]))
                    else:
                        qdict.update(QuestionProcessors[Type](request2, question))
                        
                    try:
                        qdict['comment'] = extra_comments[question]
                    except KeyError:
                        pass

                    try:
                        qdict['qhighlight'] = extra_qhighlight[question]
                    except KeyError:
                        pass

                    if question.number in errors:
                        qdict["qprocessor_errors"] = errors[question.number].message

                    if 'jsinclude' in qdict:
                        if qdict['jsinclude'] not in jsinclude:
                            jsinclude.extend(qdict['jsinclude'])
                    if 'cssinclude' in qdict:
                        if qdict['cssinclude'] not in cssinclude:
                            cssinclude.extend(qdict['jsinclude'])
                    if 'jstriggers' in qdict:
                        jstriggers.extend(qdict['jstriggers'])
                qlist.append((question, qdict))

            if qs_aux == None:
                qs_aux = k
            qlist_general.append((qs_aux, qlist))
    except:
        raise

        ## HOT FIX for qvalues to work properly, THIS SHOULD BE FIXED IN THE CODE ABOVE

    qvalues = {}
    for question, qdict in qlist_general:
        for k, v in qdict:
            try:
                qval = v['qvalue']

                if qval != None and qval != '':

                    try:
                        cutzone = qval.index('#');
                        qvalues[k.number] = qval[0:cutzone]
                    except ValueError:
                        qvalues[k.number] = qval

            except KeyError:
                pass

    return (qlist_general, qlist, jstriggers, qvalues, jsinclude, cssinclude, extra_fields, len(errors)!=0)


def uploadfiles(request):

    logging.debug('Upload files....')

    uploaded_paths = {}
    try:
        if request.FILES:
            logging.debug('Files....')
            for name, f in request.FILES.items():
                file_path = handle_uploaded_file(f, request.POST['fingerprint_id'])
                target_key = name.split('_image')
                if file_path:
                    uploaded_paths[target_key[0]] = file_path
                else:
                    uploaded_paths[target_key[0]] = None
    except:
        pass
    return uploaded_paths


def handle_uploaded_file(f, fingerprint_id):

    logging.debug('Uploading file....')

    file_path = 'files/' + fingerprint_id + '/' + f.name
    folder_path = os.path.join(os.path.abspath(settings.MEDIA_ROOT), 'files/' + fingerprint_id)

    #if directory doesnt exists create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(os.path.join(os.path.abspath(settings.MEDIA_ROOT), file_path),
              'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    return file_path


def save_answers_to_csv(list_databases, filename, job=None, user=None):
    """
    Method to export answers of a given database to a csv file
    """
    response = None
    with tempfile.NamedTemporaryFile() as tmp:

        if job:
            job = QueueJob.objects.get(id=job)
            job.output_name = '%s_%s_%s.csv' % (settings.SITE_NAME.replace(' ', '_'), filename, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            job.save()

            response = tmp
        else:
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s_%s_%s.csv"' % (settings.SITE_NAME.replace(' ', '_'), filename, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

        if list_databases:
            writer = csv.writer(response, delimiter = '\t')
            writer.writerow(['DB_ID', 'DB_name', 'Questionset', 'Question', 'QuestionNumber', 'Answer', 'Date Last Modification'])
            i = 0

            percentage = 0
            total_databases = len(list_databases)

            for t in list_databases:

                i+=1
                id = t.id

                qsets, name, db_owners, fingerprint_ttype = createqsets(id, clean=False, changeSearch=True, noprocessing=False, validateAccessPermission=True, user=user)

                qsets = attachPermissions(id, qsets)

                for (k, qs), permissions in qsets:
                    if permissions.visibility == 0 and permissions.allow_exporting == True:
                        writeGroup(id, k, qs, writer, name, t)

                writer.writerow([id, name, "System", "Date", "99.0", t.date])
                writer.writerow([id, name, "System", "Date Modification", "99.1", t.date_modification])
                writer.writerow([id, name, "System", "Type", "99.2", t.type_name])
                writer.writerow([id, name, "System", "Type Identifier", "99.3", t.ttype])

                job.progress = (100 * i) / total_databases
                job.save()

        if job:
            job.output = DjangoFile(response)
            job.save()

    return response


def create_multimontra(fingerprints, dir=None, job=None, user=None):
    if job:
        job = QueueJob.objects.get(id=job)
        job.output_name = "{}_{}.multimontra".format("SelectedDBsMultimontra", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        job.save()

    # create multimontra main file
    with tempfile.NamedTemporaryFile(delete=False, dir=dir) as ft_main:

        # build multimontra file
        with zipfile.ZipFile(ft_main, "w", zipfile.ZIP_DEFLATED) as zip:
            for i, fingerprint_hash in enumerate(fingerprints):
                # create montra file
                ft = tempfile.NamedTemporaryFile()

                if isinstance(fingerprint_hash, six.string_types):
                    fp = Fingerprint.objects.filter(fingerprint_hash=fingerprint_hash)
                    if not fp.exists():
                        continue
                    fp = fp.get()
                else:
                    fp = fingerprint_hash

                fe = FingerprintExporter.getInstance('zip', fp, ft)
                fe.export()

                # reset file pointer
                ft.seek(0)
                # load file bytes
                file_bytes = ft.read()
                # write montra file inside multimontra
                zip.writestr('%s.montra' % fp.fingerprint_hash, file_bytes)

                if job:
                    job.progress = (i + 1) / len(fingerprints) * 100
                    job.save()

        # reset main file pointer
        ft_main.seek(0)

        if job:
            job.output = DjangoFile(ft_main)
            job.save()
        else:
            return ft_main.name


def create_database_pdf_file(fingerprint_hash, job=None, user=None):
    if job:
        job = QueueJob.objects.get(id=job)
        job.output_name = "{}_{}.pdf".format(fingerprint_hash, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        job.save()

    fp = Fingerprint.objects.get(fingerprint_hash=fingerprint_hash)

    qsets, name, db_owners, fingerprint_ttype = createqsets(fp.fingerprint_hash, validateAccessPermission=True, user=user)

    fingerprint = render_to_string(
        'pdf/fingerprint.html',
        {
            'STATIC_URL': settings.STATIC_URL,
            'name': name,
            'qsets': qsets.ordered_items(),
            'db_owners': db_owners,
            'ttype': fingerprint_ttype,
        },
    )

    with tempfile.NamedTemporaryFile(delete=False) as ft:
        pisa.CreatePDF(fingerprint, ft)

        if job:
            job.progress = 100
            job.output = DjangoFile(ft)
            job.save()


def create_database_montra_file(fingerprint_hash, job=None, user=None):
    if job:
        job = QueueJob.objects.get(id=job)
        job.output_name = "{}_{}.montra".format(fingerprint_hash, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        job.save()

    with tempfile.NamedTemporaryFile(delete=False) as ft:
        fp = Fingerprint.objects.get(fingerprint_hash=fingerprint_hash)
        fe = FingerprintExporter.getInstance('zip', fp, ft)
        fe.export()

        if job:
            job.progress = 100
            job.output = DjangoFile(ft)
            job.save()


def attachPermissions(fingerprint_hash, qsets):
    zipper = qsets
    zipee = []
    fingerprint = None
    try:
        fingerprint = Fingerprint.objects.get(fingerprint_hash=fingerprint_hash)


        for q, v in zipper.ordered_items():
            qpermissions = fingerprint.getPermissions(QuestionSet.objects.get(id=v.qsid))
            zipee.append(qpermissions)

        merged = zip(zipper.ordered_items(), zipee)

        return merged

    except Fingerprint.DoesNotExist:
        logging.error("-- ERROR: Fingerprint with id fingerprint_hash %s doesn't exist", fingerprint_hash)

    return None

def clean_str_exp(s):
    return s.replace("\n", "|").replace(";", ",").replace("\t", "    ").replace("\r","").replace("^M","")

def writeGroup(id, k, qs, writer, name, t):
    if (qs!=None and qs.list_ordered_tags!= None):
        list_aux = sorted(qs.list_ordered_tags)

        for q in list_aux:
            _answer = clean_str_exp(str(q.value))
            if (_answer == "" and q.ttype=='comment'):
                _answer = "-"
            writer.writerow([id, name, k.replace('h1. ', ''), clean_str_exp(str(q.tag)), str(q.number), _answer, q.lastChange])
