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
from __future__ import print_function, absolute_import

import json
import zipfile
from copy import deepcopy

from bson import json_util
from django.conf import settings
from django.utils import timezone
from django_comments.models import Comment
from hitcount.models import Hit, HitCount

from api.models import FingerprintAPI
from docs_manager.models import Document
from population_characteristics.models import Characteristic, Comments
from questionnaire.models import QuestionSetPermissions
from .models import Answer, AnswerChange, FingerprintHead


class FingerprintExporter(object):
    def __init__(self, fingerprint, path):
        self.fingerprint = fingerprint
        self.path = path

    def export(self):
        raise NotImplementedError("Please Implement this method")

    """This method will build the object according with the type
    of the object to export.
    """
    @staticmethod
    def getInstance(t_type, fingerprint, path):
        if t_type == "zip":
            return FingerprintZipExporter(fingerprint, path)
        else:
            raise Exception("The supplied format is not supported")


class FingerprintZipExporter(FingerprintExporter):

    def __init__(self, fingerprint, path):
        FingerprintExporter.__init__(self, fingerprint, path)

    def export(self):
        with zipfile.ZipFile(self.path, "w") as zip:

                print("- Writing fingerprint data")
                zip.writestr('fingerprint.json', self.__generateFingerprintJson(self.fingerprint))

                print("- Writing answers")
                zip.writestr('answers.json', self.__generateAnswersJson(self.fingerprint))

                print("-- Writing Fingerprint head revisions")
                zip.writestr('fheads.json', self.__generateFingerprintHeadsJson(self.fingerprint))

                print("-- Writing Answer Changes")
                zip.writestr('fans.json', self.__generateAnswersChangesJson(self.fingerprint))

                print("- Writing extra api information")
                zip.writestr('extra.json', self.__generateExtra(self.fingerprint))

                print("- Writing discussion")
                zip.writestr('discussion.json', self.__generateComment(self.fingerprint))

                print("- Handling documents")
                print("-- Writing documents entries")
                zip.writestr('documents_index.json', self.__generateDocuments(self.fingerprint))

                docs = self.__listDocuments(self.fingerprint)

                print("-- Writing relevant characteristic links")
                zip.writestr('popchar.json', self.__generateCharacteristics(self.fingerprint))

                print("-- Writing files themselves")
                for doc in docs:
                    try:
                        zip.write(doc.path, arcname="documents/"+doc.revision+doc.file_name)
                        print("--- Writing file", doc.file_name)
                    except:
                        print("--- ERROR: Couldn't find file", doc.path)

                print("-- Writing characteristic comments")
                zip.writestr('popcharcomments.json', self.__generatePopCharComments(self.fingerprint))

                print("- Writing hitcount")
                zip.writestr('hitcount.json', self.__generateHitcount(self.fingerprint))
                zip.writestr('hitcount_detail.json', self.__generateHitcountDetail(self.fingerprint))

                print("- Writing qset permissions")
                zip.writestr('qset_permissions.json', self.__generatePermissions(self.fingerprint))

                print("- Writing metadata")
                zip.writestr('metadata.json', self.__generateMeta(self.fingerprint))

    # This is used mainly to ensure some kind of integrity on data imported
    def __generateMeta(self, fingerprint):
        meta = {}

        emails = fingerprint.shared.all().values_list('email', flat=True)

        meta['shared-with'] = [e for e in emails]

        meta['catalogue-version'] = settings.VERSION
        meta['export-date'] = timezone.now().strftime('%B %d, %Y, %I:%M %p')

        meta['questionnaire'] = fingerprint.questionnaire.slug

        return json.dumps(meta, indent=4, default=json_util.default)

    def __generateFingerprintJson(self, fingerprint):
        finger = deepcopy(fingerprint.__dict__)

        del finger['_state']
        if "_community_cache" in finger:
            del finger["_community_cache"]

        finger['slug'] = fingerprint.questionnaire.slug

        return json.dumps(finger, indent=4, default=json_util.default)

    def __generateAnswersJson(self, fingerprint):
        ans = Answer.objects.filter(fingerprint_id=fingerprint)

        return self.__getCleanJson(ans)

    def __generateFingerprintHeadsJson(self, fingerprint):
        fheads = FingerprintHead.objects.filter(fingerprint_id=fingerprint)

        return self.__getCleanJson(fheads)

    def __generateAnswersChangesJson(self, fingerprint):
        fans = AnswerChange.objects.filter(revision_head__fingerprint_id=fingerprint)

        return self.__getCleanJson(fans)

    def __generateExtra(self, fingerprint):
        extra = FingerprintAPI.objects.filter(fingerprintID=fingerprint.fingerprint_hash)

        return self.__getCleanJson(extra)

    def __generateComment(self, fingerprint):
        comments = Comment.objects.filter(object_pk = fingerprint.id)

        return self.__getCleanJson(comments)

    def __generateDocuments(self, fingerprint):
        docs = Document.objects.filter(fingerprint_id=fingerprint.fingerprint_hash)

        return self.__getCleanJson(docs)

    def __generateCharacteristics(self, fingerprint):

        ids = Document.objects.filter(fingerprint_id=fingerprint.fingerprint_hash).values_list('id', flat=True)

        relchar = Characteristic.objects.filter(id__in=ids).values_list('document_ptr', flat=True)

        return json.dumps([e for e in relchar], indent=4, default=json_util.default)

    def __generatePopCharComments(self, fingerprint):
        popcomments = Comments.objects.filter(fingerprint_id=fingerprint.fingerprint_hash)

        return self.__getCleanJson(popcomments)

    def __generateHitcount(self, fingerprint):
        count = HitCount.objects.filter(object_pk=fingerprint.id)

        return self.__getCleanJson(count)

    def __generateHitcountDetail(self, fingerprint):
        count = Hit.objects.filter(hitcount__object_pk=fingerprint.id)

        return self.__getCleanJson(count)

    def __generatePermissions(self, fingerprint):
        count = QuestionSetPermissions.objects.filter(fingerprint=fingerprint)

        return self.__getCleanJson(count)

    def __listDocuments(self, fingerprint):
        docs = Document.objects.filter(fingerprint_id=fingerprint.fingerprint_hash)

        return docs

    def __getCleanJson(self, objects):
        returnable = [] # obj.__dict__ for obj in objects]

        for obj in objects:
            tmp = obj.__dict__.copy()

            if isinstance(obj, Answer):
                tmp['slug'] = obj.question.slug_fk.slug1

            try:
                del tmp['_state']
            except:
                pass

            returnable.append(tmp)

        return json.dumps(returnable, indent=4, default=json_util.default)
