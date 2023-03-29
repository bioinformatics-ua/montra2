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
import logging
from re import compile

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from constance import config

from terms.models import TermsAccept
from accounts.models import TermsConditions

logger = logging.getLogger(__name__)


class TermsAcceptMiddleware:
    """
    Middleware that requires a user to accept the terms and conditions, should these exist.
    Will not forward the user to the terms page if this user has already accepted the terms.
    """

    def process_request(self, request):
        assert hasattr(request, 'user'), "The Terms Accept middleware\
 requires authentication middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
 work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
 'django.core.context_processors.auth'."

        path = request.path_info.lstrip('/')
        if config.terms_of_use_redirect and \
                not any(m.match(path) for m in [compile("termsconsent")]) and \
                request.user.is_authenticated():
            terms = TermsConditions.objects.filter(enabled=True, name="default")

            if terms.exists():
                try:
                    terms_accept = TermsAccept.objects.get(user=request.user)
                except TermsAccept.DoesNotExist:
                    logging.debug("%s being forwarded to accept current terms and conditions." % request.user)
                    return HttpResponseRedirect(
                        "/termsconsent"
                    )
                else:
                    if config.terms_of_use_redirect_on_update and \
                            terms[0].last_updated_on > terms_accept.date_accepted:
                        logging.debug("%s being forwarded to accept new terms and conditions." % request.user)
                        return HttpResponseRedirect(
                            "/termsconsent"
                        )

