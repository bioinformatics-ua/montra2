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
from django.core.management.base import BaseCommand, CommandError
from fingerprint.imports import FingerprintImporter

class Command(BaseCommand):

    args = '<path>'
    help = 'Imports a fingerprint object to a serializable object'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 1:

            fi = FingerprintImporter.getInstance('zip', args[0])
            fi.import_fingerprint()

        elif len(args) == 2:

            print '''
                ###################################################################
                # ATTENTION: ENTERING DANGEROUS GROUND, FORCE QUESTIONNAIRE TYPE  #
                # WILL SEVERELY LIMIT THE CAPACITY TO IMPORT DATA, ONLY COMMON    #
                # SLUGGED QUESTIONS WILL BE IMPORTED.                             #
                #
                # ALL QUESTION REVISIONS AND QUESTIONSET PERMISSIONS WILL BE LOST #
                ###################################################################
            '''
            tt = raw_input('Do you want to proceed ? (y/n):')

            if tt == 'y':
                fi = FingerprintImporter.getInstance('zip', args[0])
                fi.import_fingerprint(force_questionnaire=args[1])

        else:
            self.stdout.write('-- USAGE: \n    '+
                'python manage.py fingerprint_import <path_file> [<forced_questionnaire>]?'+
                '\n\n')
