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
from __future__ import print_function

import multiprocessing

from django.core.management.base import BaseCommand

from fingerprint.models import Fingerprint
from searchengine.search_indexes import CoreEngine


def worker(fingerprint_id):
    fingerprint = Fingerprint.objects.get(id=fingerprint_id)
    print("-- Indexing fingerprint hash ", fingerprint.fingerprint_hash)
    return fingerprint.indexFingerprint(batch_mode=True)


class Command(BaseCommand):
    help = 'Indexes all Fingerprints in SOLR'

    def add_arguments(self, parser):
        parser.add_argument(
            "-p", "--processes",
            type=int, default=4, help="Number of processes to use to index fingerprints",
        )

    def handle(self, *args, **options):
        fingerprints = Fingerprint.objects.valid(include_drafts=True).filter(preview_questionnaire__isnull=True)

        p = multiprocessing.Pool(processes=options["processes"])
        try:
            indexes = p.map(worker, (fp.id for fp in fingerprints))
        finally:
            p.close()

        self.stdout.write("-- Committing to solr")

        c = CoreEngine()
        c.deleteQuery('type_t:*')
        c.index_fingerprints(indexes)

        self.stdout.write('-- Finished indexing all fingerprints in SOLR.\n')
