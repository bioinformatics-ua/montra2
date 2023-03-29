# -*- coding: utf-8 -*-
# Copyright (C) 2016 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
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
from django.core.management.base import BaseCommand, CommandError
import os
import re

from community.models import Community
from fingerprint.models import Fingerprint
from fingerprint.export import FingerprintExporter
from questionnaire.models import Question

class Command(BaseCommand):

    args = '<id community>'
    help = 'convert numbers in fingerprints from a specific community [script only for migrate purposes of release 4.4]'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 1:
            comm_id=args[0]

            comm = None
            try:
                comm = Community.objects.get(slug=comm_id)
                print "Converting %s ..." % comm.name

                for f in Fingerprint.objects.all():
                    if not f.removed:
                        if f.questionnaire == comm.questionnaires.all()[0]:
                            #print f.questionnaire.name
                            for a in f.answers():
                                if a.question.type=="numeric":
                                    val=a.data;
                                    print "original: "+val
                                    update_val = False

                                    if isinstance(val, basestring):
                                        try:
                                            if val.index('.'):
                                                #print "has ."
                                                val=val.replace('.', '')
                                                update_val=True
                                        except: 
                                            #print "no ."
                                            pass

                                        try:
                                            if val.index(','):
                                                #print "has ,"
                                                val=val.replace(',', '.')
                                                update_val=True
                                        except: 
                                            #print "no ,"
                                            pass
       
                                    if (update_val):
                                       #print a
                                       print "converted: "+val
                                       a.data=val
                                       a.save()
                                       #print a


            except:
                print "Community %s not found" % comm_id
                print "Please use one of the following id's : "
                for comm in Community.objects.all():
                    print comm.slug

        else:
            self.stdout.write('-- USAGE: \n    '+
                'python manage.py convert_numbers_community <slug community>'+
                '\n\n')
