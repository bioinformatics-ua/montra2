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

from celery import shared_task
from django.utils import timezone


@shared_task
def async_job(job, lambda_funct, args):
    from .models import QueueJob

    print "Executing async job"
    job.status = QueueJob.PROCESSING
    job.save()

    try:
        lambda_funct(*args, job=job.id, user=job.runner)

        # refreshing, after job execution, before status update
        job = QueueJob.objects.get(id=job.id)

        job.status = QueueJob.FINISHED
        job.end_date = timezone.now()
        job.save()

    except:
        # refreshing, after job execution, before status update
        job = QueueJob.objects.get(id=job.id)

        job.status = QueueJob.FAILED
        job.end_date = timezone.now()
        job.save()
        raise
