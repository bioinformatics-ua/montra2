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
from django.conf import settings

from accounts.models import EmifProfile, Profile
from developer.models import Plugin, PluginVersion

from community.models import CommunityUser, Community, CommunitiesFavorited
from django.db.models import Q

def debug(context):
  return {'DEBUG': settings.DEBUG}

def baseurl(request):
    """
    Return a BASE_URL template context for the current request.
    """
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'

    burl = None
    if settings.DEBUG:
        burl = scheme + request.get_host() + settings.BASE_URL
    else:
        burl = settings.BASE_URL

    return {
        'BASE_URL': burl,
    }

# make user personal profiles available everywhere
'''def profiles_processor(request):
    profiles = []

    if request.user.is_authenticated():
        try:

            user_profile = EmifProfile.objects.get(user = request.user)

            profiles = user_profile.profiles.all()

        except EmifProfile.DoesNotExist:
            pass

    return { 'profiles': profiles }
'''
# making certain globals like brand and footer available everywhere

def globals(request):
    return settings.GLOBALS

def singlecommunity(request):
    return {
        'singlecommunity': settings.SINGLE_COMMUNITY
    }

def eprofile(request):
    eprofile = None

    if request.user.is_authenticated():
        try:
            eprofile = EmifProfile.objects.get(user = request.user)

        except EmifProfile.DoesNotExist:
            pass

    return {
        'eprofile': eprofile
    }

def thirdparty(request):
    return {
        'thirdparty': PluginVersion.all_valid(type=Plugin.THIRD_PARTY),
        'globalwidgets': PluginVersion.all_valid(type=Plugin.FULL_FLEDGED)
        }

def belongcomms(request):
    if request.user.is_authenticated():
        cus = CommunityUser.objects.filter(Q(status=CommunityUser.ENABLED) | Q(status=CommunityUser.RESTRICTED), user=request.user)

        cf = CommunitiesFavorited.objects.filter(user=request.user)

        cus_disabled = CommunityUser.objects.filter(Q(status=CommunityUser.DISABLED), user=request.user)

        # In CommunityUser | In CommunitiesFavorited
        cs = Community.objects.filter(Q(communityuser__in=cus) | Q(communitiesfavorited__in=cf)).distinct()


        disabled_cs = Community.objects.filter(Q(communityuser__in=cus_disabled)).distinct()

        other_cs = Community.objects.filter(~Q(communityuser__in=cus) & ~Q(communitiesfavorited__in=cf) & ~Q(communityuser__in=cus_disabled)).distinct()

        return {
            "user_comms": cs,
            "other_comms": other_cs,
            "disabled_comms": disabled_cs
        }

    return {
            "user_comms": Community.objects.none(),
            "other_comms": Community.objects.none(),
            "disabled_comms": Community.objects.none()
        }
