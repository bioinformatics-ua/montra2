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
import json

from constance import config
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .github import issues_handler, report_bug
from .models import BugReport


# Bug Report
def bug_report(request):
    if not config.bug_report:
        raise Http404()

    return report_bug(request)


def list_issues(request):
    if not (settings.GITHUB_USERNAME and settings.GITHUB_PASSWD):
        raise Http404()

    return issues_handler(request)


@csrf_exempt
def github_event(request):
    body = json.loads(request.body)

    try:
        action = body.get('action')

        if action == 'closed':
            issue = body.get('issue')
            number = issue['number']

            BugReport.close(number, send_mail=True)

    except KeyError:
        return HttpResponse('Forbidden', status=403)

    return HttpResponse('')
