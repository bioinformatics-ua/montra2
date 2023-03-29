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

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from accounts.models import TermsConditions
from .models import TermsAccept

import logging

logger = logging.getLogger(__name__)


def submit_terms_page(request, template_name='terms_accept.html'):

    if not request.user.is_authenticated():
        logging.warn("Non-authenticated user '%s' attempted to consent to website terms" % request.user)
        return Http404

    user = request.user

    if request.POST:
        try:
            terms_accept = TermsAccept.objects.get(user=user)
        except TermsAccept.DoesNotExist:
            new_consent = TermsAccept(user=user)
            new_consent.save()
        else:
            terms_accept.date_accepted = timezone.now()
            terms_accept.save()
        logging.debug("User %s consented to terms of use. Redirecting..." % user)
        return HttpResponseRedirect("/index")

    terms = TermsConditions.objects.filter(name="default", enabled=True)
    if terms.exists():
        return render(request, template_name, {
            'terms': terms.first()
        })

    return HttpResponseRedirect("/")
