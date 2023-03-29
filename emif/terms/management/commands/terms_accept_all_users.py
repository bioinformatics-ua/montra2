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
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from terms.models import TermsAccept


@transaction.atomic
def recreate_terms_accept(context):
    try:
        TermsAccept.objects.all().delete()
        TermsAccept.objects.bulk_create([
            TermsAccept(user=u) for u in User.objects.all()
        ])
    except Exception as e:
        transaction.set_rollback(True)

        context.stdout.write(e)
        return False
    return True


class Command(BaseCommand):
    help = 'Create TermsAccept entries for all users (auto accept terms)'

    def handle(self, *args, **options):
        self.stdout.write('Recreating all TermsAccept objects...')
        if recreate_terms_accept(self):
            self.stdout.write('Successfully recreated TermsAccept objects')
        else:
            self.stdout.write('Error during TermsAccept recreation. Rolling back...')


