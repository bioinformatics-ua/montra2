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
import os.path

from django.core.management.base import BaseCommand, CommandError

from fingerprint.export import FingerprintExporter
from fingerprint.models import Fingerprint


class Command(BaseCommand):

    help = 'Exports a fingerprint object to a serializable object'

    def add_arguments(self, parser):
        parser.add_argument("fingerprint_hash")
        parser.add_argument("dir_file", help="directory to save the exported file")

    def handle(self, *args, **options):
        self.stdout.write("- Finding fingerprint with hash ", ending="")
        self.stdout.write(options["fingerprint_hash"])

        finger = Fingerprint.objects.filter(fingerprint_hash=options["fingerprint_hash"])
        if not finger.exists():
            raise CommandError("-- ERROR: Fingerprint with hash {} doesn't exist on the system".format(options["fingerprint_hash"]))

        finger = finger.get()

        fe = FingerprintExporter.getInstance('zip', finger, os.path.join(options["dir_file"], "{}.montra".format(options["fingerprint_hash"])))
        fe.export()
