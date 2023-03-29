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

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Administration'),
            column=2,
            collapsible=False,
            models=('django.contrib.*',),
            css_classes=('g-d-8',),
        ))

        custom_links = [{'url': '/admin/{0}'.format(x[0]),
                         'title': x[1],
                         'external': False} for x in context.get('custom_list')]
        self.children.append(modules.LinkList(
            _('Custom Views'),
            column=2,
            collapsible=False,
            children=custom_links,
            css_classes=('g-d-8',),
        ))


        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            collapsible=False,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))



        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=10,
            collapsible=False,
            column=2,
            css_classes=('g-d-8',),
        ))
