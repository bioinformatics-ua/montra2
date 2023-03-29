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
from github3 import login
from github3.null import NullObject

from django.shortcuts import render
from django.conf import settings
from emif.utils import send_custom_mail
from community.models import Community

from . import forms, models


def feedback_thankyou(request, template_name='feedback_thankyou.html'):
    return render(request, template_name, {'request': request, 'breadcrumb': True})


def report_bug(request):

    if request.method == 'POST':  # If the form has been submitted...
        form = forms.BugReportForm(request.POST)
        if form.is_valid():  # All validation rules pass

            title = request.POST.get('title', '').encode('ascii', 'ignore')
            name = request.user.get_full_name()

            description = "<strong>Description: </strong>"+request.POST.get('description', '').encode('ascii', 'ignore')
            ''' description += "\n<strong>Steps to reproduce: </strong>"+request.POST.get('steps', '').encode('ascii', 'ignore')
            description += "\n<strong>Expected result: </strong>"+request.POST.get('expected', '').encode('ascii', 'ignore')
            description += "\n<strong>Priority: </strong>"+request.POST.get('priority', '').encode('ascii', 'ignore')'''

            from_email = request.user.email
            browser = request.META.get('HTTP_USER_AGENT', "")

            description = description + "\n\nReported by %s, email: %s with: %s" % (name, from_email, browser)

            if settings.GITHUB_USERNAME and settings.GITHUB_PASSWD:
                issue = IssueManager()
                newissue = issue.create(title, description)

                if not isinstance(newissue, NullObject):
                    models.BugReport.objects.create(issue=newissue.number, requester=request.user, report=description)

            emails_to_feedback = [from_email]
            for k, v in settings.ADMINS:
                emails_to_feedback.append(v)

            try:
                send_custom_mail(title, description, settings.DEFAULT_FROM_EMAIL, emails_to_feedback)
            except:
                pass
            return feedback_thankyou(request)

    else:
        form = forms.BugReportForm()  # An unbound form

    comm = None
    if settings.SINGLE_COMMUNITY:
        comm = Community.objects.all()[:1].get()

    return render(request, 'bugreport.html', {
        'form': form, 'request': request, 'breadcrumb': True,
        'activemenu': 'contact', 'activesubmenu': 'bugreport',
        'comm': comm
    })


def issues_handler(request):
    issue = IssueManager()

    try:
        issues_open = issue.list('open', None)
    except:
        issues_open = []

    try:
        issues_closed = issue.list('closed', None)
    except:
        issues_closed = []

    milestones = issue.list_milestones()

    return render(
        request,
        'list_issues.html',
        {
            'request': request,
            'breadcrumb': True,
            'activemenu': 'history',
            'issues_open': issues_open,
            'issues_closed': issues_closed,
            'milestones': milestones
        }
    )


class IssueManager(object):
    def __init__(self):
        self.gh = login(settings.GITHUB_USERNAME, settings.GITHUB_PASSWD)

    def create(self, title, body):
        return self.gh.create_issue(settings.GITHUB_ACCOUNT,settings.GITHUB_REPO, title, body, labels=['bugreport'])

    def list(self, state_of, labels_of):
        """
        should do:
        for i in issuemanager.list(state='open'):
            print i.created_at
            print i.body_text
            print i.title

        """
        return self.gh.issues_on(settings.GITHUB_ACCOUNT,settings.GITHUB_REPO, state=state_of, labels=labels_of, number=30)

    def list_labels(self):
        # I'm adding this shit statically due to the use case of the EMIF Catalogue
        # It's the only way that this will make sense.
        return ['Use Case 1', 'Use Case 2', 'Use Case 3', 'Use Case 4', 'Use Case 5', 'Use Case 6']

    def list_milestones(self):
        repo = self.gh.repository(settings.GITHUB_ACCOUNT,settings.GITHUB_REPO)

        # for some reason i couldnt find out,
        # milestones iterator only returns open milestones when used without state parameter
        # so i join them up myself...
        milestones = []
        miles_open = repo.milestones()
        miles_closed = repo.milestones(state='closed')

        for mile in miles_closed:
            milestones.append(mile)

        for mile in miles_open:
            milestones.append(mile)

        return milestones[::-1]
