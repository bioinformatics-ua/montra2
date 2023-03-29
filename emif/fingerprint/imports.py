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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.from django.contrib.auth.models import User
from __future__ import absolute_import

import json
import logging
import os
import os.path
import zipfile

from bson import json_util
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import transaction
from django_comments.models import Comment
from hitcount.models import Hit, HitCount

from api.models import FingerprintAPI
from community.models import Community
from docs_manager.models import FingerprintDocuments
from emif.utils import generate_hash
from population_characteristics.models import Characteristic, Comments
from questionnaire.models import Question, QuestionSetPermissions, Questionnaire
from .models import Answer, AnswerChange, Fingerprint, FingerprintHead

PATH_STORE_FILES = settings.MEDIA_ROOT +'popchar/'

IMPOSSIBLE = -1
AS_IS = 0
NEW_IDS = 1

class FingerprintImporter(object):
    def __init__(self, path):
        self.path = path

    @transaction.atomic
    def import_fingerprint(self, force_questionnaire=None):
        raise NotImplementedError("Please Implement this method")

    """This method will build the object according with the type
    of the object to Import.
    """
    @staticmethod
    def getInstance(t_type, path):
        if t_type == "zip":
            return FingerprintZipImporter(path)
        else:
            raise Exception("The supplied format is not supported")


class FingerprintZipImporter(FingerprintImporter):

    def __init__(self, path):
        FingerprintImporter.__init__(self, path)

    def __checkForce(self, new_fingerprint, force_questionnaire, force_community):
        if force_questionnaire:
            try:
                #questionnaire
                q = Questionnaire.objects.get(slug=force_questionnaire)
                new_fingerprint.questionnaire=q
            except Questionnaire.DoesNotExist:
                raise Exception('CANNOT IMPORT fingerprint into the invalid questionnaire %s' % force_questionnaire)

            try:
                #community
                logging.debug("----community SLUG----")
                logging.debug(force_community)
                c = Community.objects.get(slug=force_community)
                new_fingerprint.community = c
            except Community.DoesNotExist:
                raise Exception('CANNOT IMPORT fingerprint into the invalid community %s' % force_community)

        return new_fingerprint

    @transaction.atomic
    def import_fingerprint(self, force_questionnaire=None, force_community=None):
        with zipfile.ZipFile(self.path, "r") as zip:
            meta = json.loads(zip.read('metadata.json'),object_hook=json_util.object_hook)
            fdict = json.loads(zip.read('fingerprint.json'),object_hook=json_util.object_hook)

            new_fingerprint = Fingerprint()
            new_hash =None

            level = self.__checkFeasibility(meta, fdict, force_questionnaire, force_community)

            if level == AS_IS:
                logging.info('-- Hash/fingerprint_id are free, import as is on exported file.\n')

                new_fingerprint.__dict__.update(fdict)

                new_fingerprint = self.__checkForce(new_fingerprint, force_questionnaire=force_questionnaire, force_community=force_community)

                new_fingerprint.save()

                self.__import(zip, self.path, new_fingerprint, force_questionnaire=force_questionnaire, force_community=force_community)

                return new_fingerprint

            elif level == NEW_IDS:
                logging.info('-- Hash/fingerprint_id are occupied, importing with a new id.\n')
                new_hash = generate_hash()

                fdict['fingerprint_hash'] = new_hash
                del fdict['id']
                new_fingerprint.__dict__.update(fdict)

                new_fingerprint = self.__checkForce(new_fingerprint, force_questionnaire, force_community)

                new_fingerprint.save()

                self.__addShares(meta, new_fingerprint)

                self.__import(zip, self.path, new_fingerprint, replacing=True, force_questionnaire=force_questionnaire, force_community=force_community)

                return new_fingerprint

            else: # impossible
                logging.critical('-- ERROR: Impossible to import fingerprint, the questionnaire doesnt exist, or doesnt match the slug.')

        return None
    # There's a need to check a couple of things. First we must ensure the owner of the database exists in the system.
    # Second, we need to check if the questionnaire also exists in the system. Without those two the import is pointless
    # After this, we must check if the shared users exist, while this are not mandatory, we can only add users available
    # We must also check if the fingerprint_hash is taken, or if the primary key that was used to export is taken, to see
    # if we must make new ones
    def __checkFeasibility(self, meta, fdict, force_questionnaire, force_community):
        try:
            
            logging.debug("----community SLUG----")
            logging.debug(force_community)

            #questionaire exists?
            if force_questionnaire!=None:
                quest = Questionnaire.objects.get(slug=force_questionnaire)
            else:
                quest = Questionnaire.objects.get(id=fdict['questionnaire_id'])

            #community exists?
            if force_community!=None:
                comm = Community.objects.get(slug=force_community)
            else:
                comm = Community.objects.get(id=fdict['community_id'])

            try:
                finger = Fingerprint.objects.get(id = fdict['id'])

                return NEW_IDS

            except Fingerprint.DoesNotExist:
                return AS_IS

        except (Questionnaire.DoesNotExist, Community.DoesNotExist):
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
            return IMPOSSIBLE

    def __import(self, zip, old, fingerprint, replacing=False, force_questionnaire=None, force_community=None):

        logging.debug("- Saved fingerprint model")

        self.__writeFiles(zip)

        logging.debug("- Saved all files to static files folder")

        answers_map = self.__importAnswers(zip, fingerprint, replacing)

        logging.debug("- Saved all answers to models")

        if not force_questionnaire and not force_community:
            fheads_map = self.__importFHeads(zip, fingerprint, replacing)

            logging.debug("- Saved fingerprint head revisions to models")

            self.__importFans(zip, fingerprint, answers_map, fheads_map,replacing)

            logging.debug("- Saved fingerprint answer changes to models")

            self.__importQsetPermissions(zip, fingerprint, replacing)

            logging.debug("- Saved Qset Permissions to models")

        self.__importDiscussion(zip, fingerprint, replacing)

        logging.debug("- Saved Discussion to models")

        hitmap = self.__importHitCount(zip, fingerprint, replacing)

        self.__importHitCountDetails(zip, fingerprint, hitmap, replacing)

        logging.debug("- Saved hitcount to models")

        self.__importAPI(zip, fingerprint, replacing)

        logging.debug("- Saved extra API data to models")

        self.__importDocumentReferences(zip, fingerprint, replacing)

        logging.debug("- Saved Document References (except pop char.) to models")


        charmap = self.__importCharacteristicReferences(zip, fingerprint, replacing)

        logging.debug("- Saved PopChar Documents References to models")

        self.__importPopCharComments(zip, fingerprint, charmap, replacing)

        logging.debug("- Saved PopChar comments to models")

        fingerprint.indexFingerprint()

        logging.debug("- Indexed the imported fingerprint on solr ")

        fingerprint.updateFillPercentage()

        logging.debug("- Updating fill percentage on new database")

        call_command('index_mongod')

        logging.debug("- Ran mongod indexing and aggregation")

        logging.debug("---- Finished importing %s with fingerprint hash %s", str(old), fingerprint.fingerprint_hash)

    # Since we  can be changing references, i have to map the changes...
    def __importAnswers(self, zip ,fingerprint , replacing):
        answers = json.loads(zip.read('answers.json'), object_hook=json_util.object_hook)
        tmap = None
        before = None

        if replacing:
            tmap = {}

        fquestions = fingerprint.questionnaire.questions()

        for ans in answers:

            try:
                question = fquestions.get(slug_fk__slug1=ans['slug'])

                this_ans = Answer()

                if replacing:
                    ans['fingerprint_id_id'] = fingerprint.id

                    before = ans['id']
                    del ans['id']

                this_ans.__dict__.update(ans)

                this_ans.__dict__['question_id'] = question.id

                this_ans.save()

                if replacing:
                    tmap[before] = this_ans.id

            except Question.DoesNotExist:
                pass


        return tmap

    # Since we  can be changing references, i have to map the changes...
    def __importFHeads(self, zip ,fingerprint , replacing):
        fheads = json.loads(zip.read('fheads.json'), object_hook=json_util.object_hook)
        tmap = None
        before = None

        if replacing:
            tmap = {}

        for head in fheads:

            this_head = FingerprintHead()

            if replacing:
                head['fingerprint_id_id'] = fingerprint.id

                before = head['id']
                del head['id']

            this_head.__dict__.update(head)

            this_head.save()

            if replacing:
                tmap[before] = this_head.id


        return tmap

    def __importFans(self, zip, fingerprint, answers_map, fheads_map, replacing):
        fans = json.loads(zip.read('fans.json'), object_hook=json_util.object_hook)

        for fan in fans:

            this_fan = AnswerChange()

            if replacing:
                fan['revision_head_id'] = fheads_map[fan['revision_head_id']]
                fan['answer_id'] = answers_map[fan['answer_id']]

                del fan['id']

            this_fan.__dict__.update(fan)

            this_fan.save()

    def __importQsetPermissions(self, zip, fingerprint, replacing):
        qperms = json.loads(zip.read('qset_permissions.json'), object_hook=json_util.object_hook)

        for qperm in qperms:

            this_qperm = QuestionSetPermissions()

            if replacing:
                qperm['fingerprint_id'] = fingerprint.id
                del qperm['id']

            this_qperm.__dict__.update(qperm)

            this_qperm.save()

    def __importDiscussion(self, zip, fingerprint, replacing):
        comments = json.loads(zip.read('discussion.json'), object_hook=json_util.object_hook)

        for comment in comments:

            this_comment = Comment()

            if replacing:
                comment['object_pk'] = fingerprint.id
                del comment['id']

            # Here we also have to check if user exists, otherwise we set it to anonymous
            try:
                this_user = User.objects.get(id=comment['user_id'])
            except:
                comment['user_id'] = -1

            this_comment.__dict__.update(comment)

            this_comment.save()

    # Since we  can be changing references, i have to map the changes...
    def __importHitCount(self, zip , fingerprint , replacing):
        hits = json.loads(zip.read('hitcount.json'), object_hook=json_util.object_hook)
        tmap = None
        before = None

        if replacing:
            tmap = {}

        for hit in hits:

            this_hit = HitCount()

            if replacing:
                hit['object_pk'] = fingerprint.id

                before = hit['id']
                del hit['id']

            this_hit.__dict__.update(hit)

            this_hit.save()

            if replacing:
                tmap[before] = this_hit.id


        return tmap

    def __importHitCountDetails(self, zip, fingerprint, hitmap, replacing):
        hitdetails = json.loads(zip.read('hitcount_detail.json'), object_hook=json_util.object_hook)

        for hitdetail in hitdetails:

            this_hitdetail = Hit()

            if replacing:
                hitdetail['hitcount_id'] = hitmap[hitdetail['hitcount_id']]

                del hitdetail['id']

            try:
                this_user = User.objects.get(id=hitdetail['user_id'])
            except:
                hitdetail['user_id'] = -1

            this_hitdetail.__dict__.update(hitdetail)

            this_hitdetail.save()

    def __importAPI(self, zip, fingerprint, replacing):
        extra = json.loads(zip.read('extra.json'), object_hook=json_util.object_hook)

        for ex in extra:

            this_extra = FingerprintAPI()

            if replacing:
                ex['fingerprintID'] = fingerprint.fingerprint_hash
                del ex['id']

            this_extra.__dict__.update(ex)

            this_extra.save()

    # Since we  can be changing references, i have to map the changes...
    def __importDocumentReferences(self, zip ,fingerprint , replacing):
        docs = json.loads(zip.read('documents_index.json'), object_hook=json_util.object_hook)
        popcharlist = json.loads(zip.read('popchar.json'), object_hook=json_util.object_hook)

        for doc in docs:
            # PopChar dont pass through here. Are added using Characteristic model
            if doc['id'] not in popcharlist:
                this_doc = FingerprintDocuments()

                if replacing:
                    doc['fingerprint_id'] = fingerprint.fingerprint_hash

                    del doc['id']

                # update absolute paths, since they are relative to static file folder in every setup
                doc['path'] = os.path.abspath(PATH_STORE_FILES)+"/"+doc['revision']+doc['file_name']

                this_doc.__dict__.update(doc)

                this_doc.save()

    # Since we  can be changing references, i have to map the changes...
    def __importCharacteristicReferences(self, zip ,fingerprint , replacing):
        docs = json.loads(zip.read('documents_index.json'), object_hook=json_util.object_hook)
        popcharlist = json.loads(zip.read('popchar.json'), object_hook=json_util.object_hook)
        tmap = None
        before = None

        if replacing:
            tmap = {}

        for doc in docs:
            # PopChar dont pass through here. Are added using Characteristic model
            if doc['id'] in popcharlist:
                this_doc = Characteristic()

                if replacing:
                    doc['fingerprint_id'] = fingerprint.fingerprint_hash

                    before = doc['id']
                    del doc['id']

                # update absolute paths, since they are relative to static file folder in every setup
                doc['path'] = os.path.abspath(PATH_STORE_FILES)+"/"+doc['revision']+doc['file_name']

                this_doc.__dict__.update(doc)

                this_doc.save()

                if replacing:
                    tmap[before] = this_doc.id

        return tmap

    def __importPopCharComments(self, zip, fingerprint, charmap, replacing):
        comments = json.loads(zip.read('popcharcomments.json'), object_hook=json_util.object_hook)

        for comment in comments:

            this_comment = Comments()

            if replacing:
                comment['fingerprint_id'] = fingerprint.fingerprint_hash
                del comment['id']

            # Here we also have to check if user exists, otherwise we set it to anonymous
            try:
                this_user = User.objects.get(id=comment['user_id'])
            except:
                comment['user_id'] = -1

            this_comment.__dict__.update(comment)

            this_comment.save()

    def __addShares(self, meta, fingerprint):
        for m in meta['shared-with']:
            share = User.objects.filter(email=m)

            if share.count() > 0:
                fingerprint.shared.add(share[0])
            else:
                logging.info("User with email %s doesn't exist.", str(m))

        fingerprint.save()

    def __writeFiles(self, zip):
        for file in zip.namelist():
            if file.startswith('documents/'):
                name = file[10:]
                f = zip.read(file)
                with open(os.path.join(os.path.abspath(PATH_STORE_FILES), name), 'wb+') as destination:
                    destination.write(f)
                logging.info("Wrote file %s", str(name))
