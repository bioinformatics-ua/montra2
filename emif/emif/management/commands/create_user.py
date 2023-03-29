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
from userena.models import UserenaSignup

from emif.models import add_invited


class Command(BaseCommand):
    help = 'Creates a new user, with an EmifProfile'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('password')
        parser.add_argument(
            '--superuser', default=False, action="store_true", help="Make the created user a super user"
        )
        parser.add_argument(
            '--not-active', default=True, action="store_false", help="Creates an user with is_active=False"
        )
        parser.add_argument(
            '--send-email', default=False, action="store_true", help="Send an email with an activation link"
        )

    def handle(self, username, email, password, **options):
        if options["not_active"] and options["send_email"]:
            raise CommandError(
                "Must not send an activation email for active users, it will contain an invalid activation link."
            )
        elif not options["not_active"] and not options["send_email"]:
            self.stderr.write("WARNING: Creating a not active user and not sending an activation mail.")

        user = UserenaSignup.objects.create_user(
            username,
            email,
            password,
            active=options["not_active"],
            send_email=options["send_email"],
        )

        if options["superuser"]:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        add_invited(user)
