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
from django.core.management.base import BaseCommand, CommandError
import os
import re

from community.models import Community

class Command(BaseCommand):

    args = ''
    help = 'List all communities and respective slugs'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 0:
            comm = None
            try:
                print "Community listing (name: slug)"
                if ( Community.objects.all().count() == 0 ):
                    print "There are no communities"
                else:
                    for comm in Community.objects.all():
                        print "%s:\t%s" % (comm.name, comm.slug)
        
            except:
                print "-- ERROR: Cannot list communities !"

        else:
            self.stdout.write('-- USAGE: \n    '+'python manage.py list_communities'+'\n\n')
