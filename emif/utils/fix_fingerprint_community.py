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
from fingerprint.models import Fingerprint, Answer
from fingerprint.tasks import *
from community.models import Community

def addCommunitiesToEachFingerprint():
    fingerprints = Fingerprint.objects.all()

    for fingerprint in fingerprints:
        coms = Community.objects.filter(questionnaires=fingerprint.questionnaire)
        if coms:
            com = coms[0]
            fingerprint.community_id = com.id
            fingerprint.save()
            print "associated community '"+ str(com) +"' with fingerprint: '" + fingerprint.fingerprint_hash + "'"
        else:
            print "fingerprint '" + fingerprint.fingerprint_hash + "' has no community."

    print "-- Done !"

addCommunitiesToEachFingerprint()