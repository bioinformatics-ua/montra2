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

class Command(BaseCommand):

    args = '<id community> <destination_folder>'
    help = 'Exports all fingerprint objects from a specific community to serializable objects'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 2:
            comm_id=args[0]
            dest_folder=args[1]

            comm = None
            try:
                comm = Community.objects.get(slug=comm_id)
                print "Exporting %s ..." % comm.name
                print "Questionnaire: ", comm.questionnaires.all()[0]
                
                for fp in Fingerprint.objects.all():
                    print fp
                    fp_hash=fp.fingerprint_hash

                    if (fp.questionnaire == comm.questionnaires.all()[0]):
                        try:
                            dest_path=dest_folder+"/"+comm_id+"_"+fp_hash+".montra"
                            print "Exporting fingerprint with hash %s to %s..." % (fp_hash , dest_path)
                            fp_obj = Fingerprint.objects.get(fingerprint_hash=fp_hash)
                            fe = FingerprintExporter.getInstance('zip', fp_obj, dest_path)
                            fe.export()
                        except:
                            print "-- ERROR: Cannot export fingerprint with hash: %s !" % fp_hash
                            
            except:
                print "Community %s not found" % comm_id
                print "Please use one of the following id's : "
                for comm in Community.objects.all():
                    print comm.slug

        else:
            self.stdout.write('-- USAGE: \n    '+
                'python manage.py export_community <slug community> <destination_folder>'+
                '\n\n')
