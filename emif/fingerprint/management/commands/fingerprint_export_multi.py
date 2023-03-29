# -*- coding: utf-8 -*-
# Copyright (C) 2022 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
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
import os

from django.core.management.base import BaseCommand, CommandError

from community.models import Community
from fingerprint.models import Fingerprint
from fingerprint.services import create_multimontra


class Command(BaseCommand):

    help = 'Exports several fingerprint objects to a serializable object'

    def add_arguments(self, parser):
        parser.add_argument("dir_file")
        parser.add_argument(
            "-c", "--community", dest="communities", action="append", default=[],
            help="slug of the community to export all its fingerprints",
        )
        parser.add_argument(
            "-f", "--fingerprint", dest="fingerprints", action="append", default=[],
            help="fingerpritn hash to expot",
        )
        parser.add_argument("-l", "--list-file", help="file with a fingeprint hash per line to export")

    def get_fingerprint(self, fingerprint_hash):
        fingerprint = Fingerprint.objects.filter(fingerprint_hash=fingerprint_hash)
        if not fingerprint.exists():
            raise CommandError("-- ERROR: Fingerprint with hash {} doesn't exist on the system".format(fingerprint_hash))

        self.to_export |= fingerprint

    def handle(self, *args, **options):
        self.to_export = Fingerprint.objects.none()

        if options["communities"]:
            for community in options["communities"]:
                comm = Community.objects.filter(slug=community)
                if not comm.exists():
                    raise CommandError("-- ERROR: Community with slug {} does not exist".format(options["community"]))

                self.to_export |= comm.get().fingerprint_set.all()

        if options["fingerprints"]:
            for fingerprint_hash in options["fingerprints"]:
                self.get_fingerprint(fingerprint_hash)

        if options["list_file"]:
            with open(options["list_file"]) as f:
                for fingerprint_hash in f:
                    self.get_fingerprint(fingerprint_hash.strip())

        filename = create_multimontra(self.to_export, dir=options["dir_file"])

        os.rename(filename, filename + ".multimontra")

        self.stdout.write("Exported fingerprints to file {}.multimontra".format(filename))
