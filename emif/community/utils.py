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

from django.http import Http404
from django.shortcuts import redirect

from django.conf import settings
from constance import config

from community.models import Community, CommunityUser

def getComm(community, user, force=False):
    comm = None
    if community != None:
        try:
            comm = Community.objects.get(slug=community)
        except Community.DoesNotExist:
            raise Http404

    if force or (comm and comm.public) == True:
        return comm

    if settings.SINGLE_COMMUNITY and config.login_bypass:
        return comm

    if not user.is_authenticated():
        return redirect('join-community', community=comm.slug)

    try:

        cu = CommunityUser.objects.get(community=comm, user=user)

        if cu.status in [CommunityUser.ENABLED, CommunityUser.RESTRICTED]:
            return comm

    except CommunityUser.DoesNotExist:
        pass

    if not comm:
        return None

    return redirect('join-community', community=comm.slug)
    
