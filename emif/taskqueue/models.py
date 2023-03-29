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

from django.db import models

from django.contrib.auth.models import User

from .tasks import async_job

from django.conf import settings

def inputHash(instance, filename):
    ''' Callable to be called by the FileField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return '.{0}queue_inputs/{1}_{2}'.format(settings.MEDIA_URL, instance.id, instance.output_name)

def outputHash(instance, filename):
    ''' Callable to be called by the FileField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return '.{0}queue_outputs/{1}_{2}'.format(settings.MEDIA_URL, instance.id, instance.output_name)


# Generic Task Queue
# Lamba functions should respect a few principles, such as being autocontained in data retrieval and updating
class QueueJob(models.Model):
    START = 0
    PROCESSING = 1
    FINISHED = 2
    FAILED = -1

    STATUS_TYPES = (
        (START, 'Job has started'),
        (PROCESSING, 'Job is being processed'),
        (FINISHED, 'Job has finished'),
        (FAILED, 'Job has failed execution')
    )
    input = models.FileField(upload_to=inputHash, null=True, blank=True, max_length=1000)
    output = models.FileField(upload_to=outputHash, null=True, blank=True, max_length=1000)
    output_name = models.CharField(max_length=300, null=True, blank=True)
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=2000, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    runner = models.ForeignKey(User)
    status = models.IntegerField(default=START, choices=STATUS_TYPES)
    progress = models.IntegerField(default=0)

    def get_status(self):
        if self.status == QueueJob.START:
            return 'Waiting to start'
        elif self.status == QueueJob.PROCESSING:
            return 'Processing'
        elif self.status == QueueJob.FINISHED:
            return 'Finished'

        return 'Error'

    def execute(self, lambda_funct, args):
        async_job.delay(self, lambda_funct, args)

    class Meta:
        ordering = ['-id']
