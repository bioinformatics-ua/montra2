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

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods

from cookies.models import CookieConsent

import logging

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def submit_cookies_consent(request):

    if not request.user.is_authenticated():
        logging.error("Non-authenticated user '%s' attempted to consent to cookie disclaimer" % request.user)
        return Http404

    user = request.user

    try:
        CookieConsent.objects.get(user=user)
    except CookieConsent.DoesNotExist:
        new_consent = CookieConsent(user=user)
        new_consent.save()

        logging.debug("User %s consented to cookie disclaimer." % request.user)
        return HttpResponse()
    else:
        raise Exception("User %s already gave their cookie usage consent" % user)
