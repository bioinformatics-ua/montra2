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

import uuid

from celery import shared_task
import time

from searchengine.search_indexes import CoreEngine

from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from questionnaire.models import *
from searchengine.models import *
from searchengine.search_indexes import CoreEngine
from django.shortcuts import render_to_response, get_object_or_404
import re

from django.conf import settings
import pysolr

from django.core.cache import cache
from questionnaire.imports import ImportQuestionnaire
from questionnaire.models import QuestionnareImportFile

@shared_task
def reindexQuestionnaires():
    print "Reindexing questionnaires on solr"

    c = CoreEngine()

    c.reindex_quest_solr()

    cache.delete('reindexingQuestionnaires')

@shared_task
def importQuest(uploaded_file, preview, user, qid_to_merge=None):
    if uploaded_file=="":
        return  
        
    print "Importing questionnaire async"
    qi = QuestionnareImportFile.objects.get(id=uploaded_file)

    qi.status = QuestionnareImportFile.PROCESSING
    qi.save()
    iq = ImportQuestionnaire.factory('excel', qi.file)
    try:
        if(qid_to_merge):
            questionnaire = iq.import_questionnaire(preview, merge=qid_to_merge)
            ## Set previous questionnaire to null
            old_qimportfile = QuestionnareImportFile.objects.get(questionnaire=qid_to_merge)
            old_qimportfile.questionnaire = None
            old_qimportfile.save()
        else:
            questionnaire = iq.import_questionnaire(preview)
    except ValueError as e:
        qi.status = QuestionnareImportFile.ABORTED
        qi.error_message = str(e)
        qi.save()
        return "Not Unique Slug"
    except Exception as e:
        qi.status = QuestionnareImportFile.ABORTED
        qi.error_message = str(e)
        qi.save()
        return "Invalid Schema"

    qi.status = QuestionnareImportFile.FINISHED
    # If we pass `preview`, then we generate an unfilled fingerprint with no
    # community association.
    if preview:
        # Importing these in the right place leads to some import issue which I
        # couldn't figure out. Let's just import them here, for now.
        from fingerprint.services import saveFingerprintAnswers
        from fingerprint.models import Fingerprint
        
        fingerprint_hash = uuid.uuid4().hex
        saveFingerprintAnswers(
            qlist_general=[],
            fingerprint_id=fingerprint_hash,
            questionnaire=questionnaire,
            user=user)
        questionnaire.preview_fingerprint = Fingerprint.objects.get(
            fingerprint_hash=fingerprint_hash)
        questionnaire.save()
        qi.status = QuestionnareImportFile.PREVIEW
        qi.questionnaire = questionnaire
        print 'Generated preview fingerprint: {}'.format(fingerprint_hash)
    qi.save()

    return "Success"
