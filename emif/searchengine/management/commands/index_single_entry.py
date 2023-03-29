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

from fingerprint.models import Fingerprint


class Command(BaseCommand):
    help = 'Indexes a Fingerprint in SOLR '

    def add_arguments(self, parser):
        parser.add_argument('fingerprint_hash')

    def handle(self, fingerprint_hash, *args, **options):
        try:
            f = Fingerprint.objects.get(fingerprint_hash=fingerprint_hash)
        except Fingerprint.DoesNotExist:
            raise CommandError("Fingerprint not found")

        f.indexFingerprint()

        self.stdout.write('-- Finished indexing fingerprint in SOLR.\n')
