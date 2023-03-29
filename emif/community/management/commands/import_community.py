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
import glob


from community.models import Community
from fingerprint.models import Fingerprint
from fingerprint.imports import FingerprintImporter

class Command(BaseCommand):

    args = '<slug community> <input_folder>'
    help = 'Import all fingerprint objects to a specific community from serializable objects'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 2:
            comm_id=args[0]
            input_folder=args[1]
            comm = None
            try:
                comm = Community.objects.get(slug=comm_id)
                print("Import to %s ..." % comm.name)
                questionnaire = comm.questionnaires.all()[0]
                
                list_files = glob.glob(input_folder + "*.montra")
                for f in list_files: 
                    try:
                        fi = FingerprintImporter.getInstance('zip', f)
                        fi.import_fingerprint(force_questionnaire=questionnaire.slug)
                    except: 
                        import sys, traceback
                        traceback.print_exc(file=sys.stdout)
                        print("ERROR: while importing %s" % f )
            except:
                print("Problem while importing fingerprint. Check if the input arguments are correct.")
        else:
            self.stdout.write('-- USAGE: \n    '+
                'python manage.py import_community <slug community> <destination_folder>'+
                '\n\n')
