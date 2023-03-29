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

from __future__ import absolute_import


from django.conf import settings
from celery import shared_task
import time

from datetime import timedelta

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from community.feed import PubMedFeed

@periodic_task(run_every=crontab(minute=settings.PUBMED_MIN, hour=settings.PUBMED_HOUR, day_of_week=settings.PUBMED_DAY))
def update_pubmed_feed():
    pmf = PubMedFeed(retmax=10)
    pmf.index_communities()
