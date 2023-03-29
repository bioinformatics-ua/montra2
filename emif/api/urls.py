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

from django.conf.urls import include, url
from rest_framework_nested import routers
from rest_framework.urlpatterns import format_suffix_patterns


from api.views import *

from dashboard.api import *

from public.api import *

from statistics.api import *

from questionnaire.api import *

from community.api import *

urlpatterns = [
    url(r'^root/$', api_root),
    url(r'^emailcheck$', EmailCheckView.as_view(), name='emailcheck'),
    url(r'^removePermissions$', RemovePermissionsView.as_view(), name='removepermissions'),
    url(r'^passOwnership$', PassOwnershipView.as_view(), name='passownership'),
    url(r'^populationcheck$', PopulationCheckView.as_view(), name='populationcheck'),
    url(r'^getfile$', GetFileView.as_view(), name='getfile'),
    url(r'^getcommunityfile$', GetCommunityFileView.as_view(), name='getcommunityfile'),
    url(r'^deletefile$', DeleteFileView.as_view(), name='deletefile'),
    url(r'^deletecommunityfile$', DeleteCommunityFileView.as_view(), name='deletecommunityfile'),
    url(r'^deletecommunityfolder$', DeleteCommunityFolderView.as_view(), name='deletecommunityfolder'),
    url(r'^search$', SearchView.as_view(), name='search'),
    url(r'^metadata', MetaDataView.as_view(), name='metadata'),
    url(r'^stats$', StatsView.as_view(), name='stats'),
    url(r'^validate$', ValidateView.as_view(), name='validate'),
    url(r'^pubmed$', PublicationsView.as_view(), name='pubmed'),
    url(r'^population$', PopulationView.as_view(), name='population'),
    url(r'^notify_owner$', NotifyOwnerView.as_view(), name='notify_owner'),
    url(r'^addpubliclink$', AddPublicLinkView.as_view(), name='addpubliclink'),
    url(r'^deletepubliclink$', DeletePublicLinkView.as_view(), name='addpubliclink'),
    url(r'^searchsuggestions$', SearchSuggestionsView.as_view(), name='searchsuggestions'),

    url(r'^notifications$', NotificationsView.as_view(), name='notifications'),
    url(r'^readnotification$', ReadNotificationView.as_view(), name='readnotification'),
    url(r'^removenotification$', RemoveNotificationView.as_view(), name='removenotification'),
    url(r'^requestanswer$', RequestAnswerView.as_view(), name='requestanswer'),

    url(r'^togglesubscription$', ToggleSubscriptionView.as_view(), name='togglesubscription'),

    # search databases services
    url(r'^searchdatabases$', SearchDatabasesView.as_view(), name='searchdatabases'),

    # dashboard widgets services
    url(r'^dbtypes/(?P<community>[\w]+)?$', DatabaseTypesView.as_view(), name='dbtypes'),
    url(r'^userstats/(?P<community>[\w]+)?$', UserStatsView.as_view(), name='userstats'),
    url(r'^mostviewed/(?P<community>[\w]+)?$', MostViewedView.as_view(), name='mostviewed'),
    url(r'^mostviewedfingerprint/(?P<community>[\w]+)?$', MostViewedFingerprintView.as_view(), name='mostviewedfingerprint'),
    url(r'^lastusers$', LastUsersView.as_view(), name='lastusers'),
    url(r'^feed/(?P<community>[\w]+)?$', FeedView.as_view(), name='feed'),
    url(r'^tagcloud/(?P<community>[\w]+)?$', TagCloudView.as_view(), name='tagcloud'),

    # private links api services
    url(r'^plinkemails$', PrivateLinkEmailView.as_view(), name='plinkemails'),

    url(r'^topusers$', TopUsersView.as_view(), name='topusers'),
    url(r'^recommendations/(?P<community>[\w]+)?$', RecommendationsView.as_view(), name='recommendations'),

    url(r'^topnavigators$', TopNavigatorsView.as_view(), name='topnavigators'),

    url(r'statistics/(?P<fingerprint_schema_id>[^/]+)/(?P<operation>[^/]+)/(?P<ttype>[^/]+)/(?P<ttype2>[^/]+)/$', \
        FingerprintSchemas.as_view(), name='databasesglobal'),

    url(r'statistics/portal/(?P<community>[^/]+)/(?P<operation>[^/]+)/(?P<dateStart>[^/]+)/(?P<dateEnd>[^/]+)$', \
        PortalStats.as_view(), name='statistics'),    

    # questionnaire api services
    url(r'^wizards$', QuestionnaireWizardView.as_view(), name='wizards'),

    # questionnaire import webservice
    url(r'^importquestionnaire$', QuestionnaireImportView.as_view(), name='importquestionnaire'),

    url(r'^free_slug/(?P<slug>[a-z0-9]+)$', CommunityFreeSlugView.as_view(), name='communityfreeslug'),

    url(r'^questionnaire-import-status/(?P<id>[0-9]+)$', QuestionnaireImportStatusView.as_view()),
    url(r'^manage-questionnaire-preview/(?P<fingerprint_hash>[^/]+)', ManageQuestionnairePreviewView.as_view()),
]

# I did this here, because I don't have time now to migrate all the services
# to here and organize this code. Thus, new services must be declared here, 
# following the README instructios. 
from api.community_api.views import CommunityViewSet, CommunitySettingsView, CommunityQuestionnairesView
from api.fingerprint_api.views import FingerprintViewSet, AnswerViewSet, FingerprintView
from api.questionnaire_api.views import QuestionnaireViewSet

router = routers.SimpleRouter()
router.register(r'communities', CommunityViewSet, base_name='communitiesview')
router.register(r'questionnaires', QuestionnaireViewSet, base_name='questionnairesview')
router.register(r'fingerprints', FingerprintViewSet)

fingerprints_router = routers.NestedSimpleRouter(router, r'fingerprints', lookup='fingerprint')
fingerprints_router.register(r'answers', AnswerViewSet, base_name='fingerprint-answer')

urlpatterns += [
    url(r'^', include(router.urls)),
    url(r'^', include(fingerprints_router.urls)),
    url(r'^fingerprint-cslug-fslug/(?P<community_slug>[\w]+)/(?P<db_name>[^/]+)/?$', FingerprintView.as_view(), name='fingerprintview'),
    url(r'^community/(?P<community_slug>[-\w]+)/questionnaire/(?P<questionnaire_slug>[-\w]+)/settings/$', CommunitySettingsView.as_view(), name='communitysettings'),
    url(r'^community/(?P<community_slug>[-\w]+)/questionnaires/$', CommunityQuestionnairesView.as_view(), name='communityquestionnaires'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
