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

from django.conf.urls import url

import community.views
from community.api import CheckDeleteUserFromCommunityView, CommunityFavoriteView, CommunityGroupAddView, \
    CommunityGroupDelView, CommunityGroupView, CommunityLeaveView, CommunityManageGroupView, CommunityManageQSetsView, \
    CommunityManageUserGroupView, CommunityUnfavoriteView

urlpatterns = [
    # page to create/ask for new community
    url(r'^create$', community.views.create),
    url(r'^join/(?P<community>[\w]+)$', community.views.join, name='join-community'),

    #description, users, components, settings, communication

    url(r'^manage/(?P<community>[\w]+)/description$', community.views.manage_descriptions, name='manage-community-description'),
    url(r'^manage/(?P<community>[\w]+)/users$', community.views.manage_users, name='manage-community-users'),
    url(r'^manage/(?P<community>[\w]+)/drafts/(?P<page>[-]{0,1}\d+)?$', community.views.manage_drafts, name='manage-community-drafts'),
    url(r'^manage/(?P<community>[\w]+)/drafts/accept/(?P<fingerprint>[^/]+)$', community.views.manage_drafts_accept, name='manage-community-drafts-accept'),
    url(r'^manage/(?P<community>[\w]+)/drafts/deny/(?P<fingerprint>[^/]+)$', community.views.manage_drafts_deny, name='manage-community-drafts-deny'),
    url(r'^manage/(?P<community>[\w]+)/components$', community.views.manage_components, name='manage-community-components'),
    url(r'^manage/(?P<community>[\w]+)/q/(?P<questionnaire>[-\w]+)/settings$', community.views.manage_views, name='manage-community-views'),
    url(r'^manage/(?P<community>[\w]+)/settings$', community.views.manage_settings,
        name='manage-community-settings'),

    url(r'^(?P<community>[\w]+)/api/check_delete/(?P<comm_user>[0-9]+)$', CheckDeleteUserFromCommunityView.as_view()),

    url(r'^manage/(?P<community>[\w]+)/communication$', community.views.manage_communication, name='manage-community-communication'),

    url(r'^manage/(?P<community>[\w]+)/joinform$', community.views.manage_community_join_form, name='manage-community-join-form'),
    url(r'^manage/(?P<community>[\w]+)/groups$', community.views.manage_groups, name='manage-community-groups'),
    url(r'^manage/(?P<community>[\w]+)/plugins$', community.views.manage_plugins, name='manage-community-plugins'),
    url(r'^manage/(?P<community>[\w]+)/qsets/(?P<questionnaire>[-\w]+)?$', community.views.manage_qsets, name='manage-community-qsets'),


    url(r'^activate/(?P<hash>[\w]+)$', community.views.activate, name='activate-user-community'),
    url(r'^activate_confirmed/(?P<hash>[\w]+)$', community.views.activate_confirmed, name='activate-user-community-complete'),
    url(r'^dontactivate/(?P<hash>[\w]+)$', community.views.dontactivate, name='dontactivate-user-community'),
    url(r'^block/(?P<hash>[\w]+)$', community.views.block, name='block-user-community'),

    url(r'^leave/(?P<community>[\w]+)$', CommunityLeaveView.as_view(), name='leave-community'),
    url(r'^favorite/(?P<community>[\w]+)$', CommunityFavoriteView.as_view(), name='favorite-community'),
    url(r'^unfavorite/(?P<community>[\w]+)$', CommunityUnfavoriteView.as_view(), name='favorite-community'),

    url(r'^list/(?P<community>[\w]+)/(?P<group>[\w]+)$', CommunityGroupView.as_view(), name='group-community'),

    # API for Manage the Groups.
    url(r'^(?P<community>[\w]+)/api/groups$', CommunityManageGroupView.as_view(), name='manage-groups-community'),
    url(r'^(?P<community>[\w]+)/api/user/groups$', CommunityManageUserGroupView.as_view(), name='manage-user-groups-community'),
    url(r'^(?P<community>[\w]+)/api/qsets$', CommunityManageQSetsView.as_view(), name='manage-groups-qsets'),
    
    # Views 
    
    # url(r'^manage/(?P<community>[\w]+)/statistics$', community.views.manage_statistics_view, name='manage-statistics'),
    # url(r'^manage/view/statistics$', community.views.manage_statistics_view, name='manage-statistics-view'),
    
    url(r'^listadd/(?P<community>[\w]+)/(?P<group>[\w]+)/(?P<email>[^/]+)$', CommunityGroupAddView.as_view(), name='groupadd-community'),

    url(r'^listdel/(?P<community>[\w]+)/(?P<group>[\w]+)/(?P<email>[^/]+)$', CommunityGroupDelView.as_view(), name='groupdel-community'),

    #Select available questionnaire
    url(r'^(?P<community>[\w]+)/questionnaires$', community.views.select_questionnaire_view, name='community-select-questionnaire-view'),
]
