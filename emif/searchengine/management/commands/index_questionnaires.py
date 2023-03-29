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

from django.core.management.base import BaseCommand, CommandError


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
import sys
import re

from django.conf import settings
import pysolr

from django.core.cache import cache

class Command(BaseCommand):
    args = ''
    help = 'Indexes all Questionnaires in SOLR'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        self.stdout.write("Reindexing questionnaires on solr")

        c = CoreEngine()

        c.reindex_quest_solr()

        cache.delete('reindexingQuestionnaires')
        self.stdout.write('-- Finished indexing all questionnairs in SOLR.\n')

