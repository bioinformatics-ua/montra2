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
from fingerprint.models import Fingerprint
from public.models import PublicFingerprintShare

def hasFingerprintPermissions(request, fingerprint_id):

    if request.user.is_authenticated():
        return True
    else:
        public_key = None
        if 'publickey' in request.POST:
            public_key = request.POST.get('publickey')

        else:
            public_key = request.GET.get('publickey')

        print public_key
        try:
            public_link = PublicFingerprintShare.objects.get(hash=public_key)

            if public_link.fingerprint.fingerprint_hash == fingerprint_id:
                return True

        except PublicFingerprintShare.DoesNotExist:
            pass


    return False
