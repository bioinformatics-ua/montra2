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
import django.views
from adminplus.sites import AdminSitePlus
from allauth.account import views as allauth_account_views
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

import advancedsearch.views
import community.views
import cookies.views
import compare.views
import control_version.views
import datatable.views
import emif.views
import fingerprint.views
import geolocation.views
import population_characteristics.documents
import population_characteristics.views
from developer.views import CommunityDeveloperGlobalView, CommunityDeveloperIframeView, DeveloperGlobalView, \
    DeveloperIframeView

admin.site = admin.sites.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = [
    # Comments
    url(r'^comments/', include('django_comments.urls')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Index page
    url(r'^index$', community.views.splash, name="community-splash"),
    url(r'^$', emif.views.index, name="home"),
    #url(r'^index$', 'emif.views.index', name="home"),
    url(r'^indexbeta$', emif.views.index_beta, name="home_beta"),

    url(r'^login$', emif.views.login_emif, name="login_emif"),

    #url(r'^about$', 'emif.views.about'),
    # must do this to be able to use custom paths on this css file
    url(r'^bootstrap_ie_compatibility$', emif.views.bootstrap_ie_compatibility),

    # Cookie Consent
    url(r'^cookiesconsent$', cookies.views.submit_cookies_consent, name='community-developer-iframe'),

    # Terms Consent
    url(r'^termsconsent', include('terms.urls')),

    # Community Plugins
    url(r'^c/(?P<community>[\w]+)/apps/tp/(?P<plugin_hash>[^/]+)$', CommunityDeveloperIframeView.as_view(), name='community-developer-iframe'),
    url(r'^c/(?P<community>[\w]+)/apps/gp/(?P<plugin_hash>[^/]+)$', CommunityDeveloperGlobalView.as_view(), name='community-developer-iframe'),

    # Advanced Search
    url(r'^c/(?P<community>[\w]+)/advancedSearch/(?P<questionnaire_id>[0-9]+)/(?P<question_set>[0-9]+)/(?P<aqid>[0-9]+)?$', advancedsearch.views.advanced_search_comm),
    url(r'^advancedSearch/(?P<questionnaire_id>[0-9]+)/(?P<question_set>[0-9]+)/(?P<aqid>[0-9]+)?$', advancedsearch.views.advanced_search),

    # Database Add
    url(r'^c/(?P<community>[\w]+)/add/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$', fingerprint.views.database_add_comm),
    url(r'^add/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$', fingerprint.views.database_add),
    url(r'^c/(?P<community>[\w]+)/searchqs/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/((?P<aqid>[0-9]+)/)?$', advancedsearch.views.database_search_qs_comm),
    url(r'^searchqs/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/((?P<aqid>[0-9]+)/)?$', advancedsearch.views.database_search_qs),
    url(r'^c/(?P<community>[\w]+)/addqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$', fingerprint.views.database_add_qs),
    url(r'^addqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$', fingerprint.views.database_add_qs),
    url(r'^c/(?P<community>[\w]+)/addPost/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/(?P<saveid>[0-9]+)$', fingerprint.views.check_database_add_conditions),
    url(r'^addPost/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/(?P<saveid>[0-9]+)$', fingerprint.views.check_database_add_conditions),
    url(r'^apps/tp/(?P<plugin_hash>[^/]+)$', DeveloperIframeView.as_view(), name='developer-iframe'),
    url(r'^apps/gp/(?P<plugin_hash>[^/]+)$', DeveloperGlobalView.as_view(), name='developer-global'),

    # Database Edit
    url(r'^c/(?P<community>[\w]+)/dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$', fingerprint.views.database_edit),
    url(r'^c/(?P<community>[\w]+)/dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$', fingerprint.views.database_edit_dl),
    url(r'^c/(?P<community>[\w]+)/dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$', fingerprint.views.database_detailed_view),
    url(r'^c/(?P<community>[\w]+)/dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)$', fingerprint.views.database_detailed_view_dl),
    url(r'^dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$', fingerprint.views.database_edit),
    url(r'^dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$', fingerprint.views.database_edit_dl),
    url(r'^dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$', fingerprint.views.database_detailed_view),
    url(r'^dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)$', fingerprint.views.database_detailed_view_dl),
    url(r'^editqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$', fingerprint.views.database_edit_qs),
    url(r'^detailedqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$', fingerprint.views.database_detailed_qs),
    url(r'^feedback/thankyou/', emif.views.feedback_thankyou),
    url(r'^feedback$', emif.views.feedback, name="feedback"),
    url(r'^bugreport$', control_version.views.bug_report, name="bug_report"),

    # Results
    url(r'^results$', fingerprint.listings.results_fulltext),

    #Statistics
    url(r'^statistics/(?P<questionnaire_id>[0-9]+)/(?P<question_set>[0-9]+)/$', emif.views.statistics),
    # url(r'^statistics$', 'emif.views.statistics'),

    url(r'^c/(?P<community>[\w]+)/geo$', geolocation.views.geo_comm),
    url(r'^geo$', geolocation.views.geo),
    url(r'^c/(?P<community>[\w]+)/resultsdiff/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.results_diff),
    url(r'^resultsdiff/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.results_diff),
    url(r'^c/(?P<community>[\w]+)/resultscomp', compare.views.results_comp_comm),
    url(r'^resultscomp', compare.views.results_comp),

    url(r'^c/(?P<community>[\w]+)/fingerprint/(?P<runcode>[^/]+)/$', fingerprint.views.document_form_view_comm_first_qset),
    url(r'^c/(?P<community>[\w]+)/fingerprint/(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/$', fingerprint.views.document_form_view_comm),
    url(r'^c/(?P<community>[\w]+)/fingerprint/(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/(?P<activetab>[^/]+)/$', fingerprint.views.document_form_view_comm),
    # *** jerboa barebones***
    url(r'^c/(?P<community>[\w]+)/fingerprint/(?P<runcode>[^/]+)/jerboa/(?P<plugin>[^/]+)/$', population_characteristics.documents.jerboa_view),


    url(r'^fingerprint/(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/$', fingerprint.views.document_form_view, name="fingerprint-preview"),
    url(r'^fingerprint/(?P<runcode>[^/]+)/(?P<qs>[-]{0,1}\d+)/(?P<activetab>[^/]+)/$', fingerprint.views.document_form_view),

    # Single qs for load by blocks
    url(r'^c/(?P<community>[\w]+)/fingerprintqs/(?P<runcode>[^/]+)/(?P<qsid>[0-9]+)/$', fingerprint.views.single_qset_view_community),
    url(r'^fingerprintqs/(?P<runcode>[^/]+)/(?P<qsid>[0-9]+)/$', fingerprint.views.single_qset_view),

    # List Databases
    url(r'^c/(?P<community>[\w]+)/query/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.query_solr_comm),
    url(r'^query/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.query_solr),
    
    #database listing by community
    url(r'^c/(?P<community>[\w]+)/databases/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.database_listing, 
        name='fingerprint.listings.database_listing_by_community_first_quest',  
        kwargs={'paginator_view_name': 'fingerprint.listings.database_listing_by_community_questionnaire', 'first_questionnaire': True}),
    url(r'^c/(?P<community>[\w]+)/q/(?P<questionnaire>[-\w]+)/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.database_listing, 
        name='fingerprint.listings.database_listing_by_community_questionnaire'),
    url(r'^c/(?P<community>[\w]+)$', fingerprint.listings.database_listing, name='fingerprint.listings.database_listing_by_community'),
    url(r'^alldatabases/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.database_listing, name="fingerprint.listings.database_listing_all"), 

    #personal databases
    url(r'^databases/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.database_listing, 
        name="fingerprint.listings.personal_database_listing_all", 
        kwargs={'only_personal_databases':True}),
    url(r'^c/(?P<community>[\w]+)/q/(?P<questionnaire>[-\w]+)/databases/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.database_listing, 
        name="fingerprint.listings.personal_database_listing_by_community", 
        kwargs={'only_personal_databases':True}),

    url(r'^c/(?P<community>[\w]+)/q/(?P<questionnaire>[-\w]+)/custom-view$', datatable.views.custom_view_questionnaire_export),
    url(r'^c/(?P<community>[\w]+)/population/compare$', population_characteristics.views.compare_comm),
    url(r'^population/compare$', population_characteristics.views.compare),
    url(r'^alldatabases/data-table$', datatable.views.all_databases_data_table),
    url(r'^qs_data_table$', datatable.views.qs_data_table),
    url(r'^export_datatable$', datatable.views.export_datatable),
    url(r'^export_message$', datatable.views.export_message),
    url(r'^c/(?P<community>[\w]+)/export_all_answers$', emif.views.export_all_answers),
    url(r'^c/(?P<community>[\w]+)/export_selected_answers$', emif.views.export_selected_answers),
    url(r'^c/(?P<community>[\w]+)/export_selected_answers_multimontra$', emif.views.export_selected_answers_multimontra),
    url(r'^c/(?P<community>[\w]+)/export_my_answers$', emif.views.export_my_answers),
    url(r'^export_search_answers$', emif.views.export_search_answers),
    url(r'^export_bd_answers/(?P<runcode>[^/]+)/$', fingerprint.views.export_bd_answers),
    # url(r'^delete-questionnaire/(?P<qId>[0-9]+)/$', utils.delete_questionnaire.delete),
    
    # Documentation
    url(r'^c/(?P<community>[\w]+)/docs/api$', fingerprint.listings.docs_api),
    url(r'^docs/api$', fingerprint.listings.docs_api),
    #more like this

    url(r'^c/(?P<community>[\w]+)/mlt/(?P<doc_id>[^/]+)/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.more_like_that_comm),
    url(r'^mlt/(?P<doc_id>[^/]+)/(?P<page>[-]{0,1}\d+)?$', fingerprint.listings.more_like_that),
    url(r'^rm/(?P<id>[^/]+)/(?P<community>[\w]+)', fingerprint.views.delete_fingerprint),
    url(r'^share/activation/(?P<activation_code>[^/]+)', emif.views.sharedb_activation),
    url(r'^share/(?P<db_id>[^/]+)', emif.views.sharedb),
    url(r'^invite/(?P<db_id>[^/]+)', emif.views.invitedb),
    url(r'^inviteCommunity/(?P<db_id>[^/]+)', emif.views.inviteCommunity),

    # API
    url(r'^api/', include('api.urls')),

    # Control version
    url(r'^controlversion/', include('control_version.urls')),

    # allauth inactive url 
    url(r"^accounts/inactive/$", allauth_account_views.account_inactive, name="account_inactive"),

    # Questionnaire URLs
    #url(r'q/', include('questionnaire.urls')),
    
    # User accounts URLs    
    url(r'^accounts/', include('accounts.urls')),

    # url(r'^api-upload-info/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^c/(?P<community>[\w]+)/api-info/(?P<page>[-]{0,1}\d+)?', fingerprint.listings.create_auth_token, name="api-info-comm"),
    url(r'^api-info/(?P<page>[-]{0,1}\d+)?', fingerprint.listings.create_auth_token, name="api-info"),

    # Population Characteristics URLs
    url(r'population/', include('population_characteristics.urls')),

    # Docs Manager
    url(r'docsmanager/', include('docs_manager.urls',namespace="docsmanager")),

    # Studies
    url(r'studies/', include('studies.urls')),

    # Literature URLs
    url(r'literature/', include('literature.urls')),

    # AdvancedSearch URLs
    url(r'advsearch/', include('advancedsearch.urls')),

    # Public links URLs
    url(r'^c/(?P<community>[\w]+)/public/', include('public.urls')),
    url(r'public/', include('public.urls')),

    # newsletter system
    url(r'^newsletter/', include('newsletter.urls')),

    # Notifications URLs
    url(r'notifications/', include('notifications.urls')),

    # unique views plugin
    url(r'hitcount/', include('hitcount.urls', namespace='hitcount')),

    # Fingerprint
    url('^fingerprint/', include('fingerprint.urls')),

    # DashBoard
    url(r'^c/(?P<community>[\w]+)/dashboard', include('dashboard.urls')),

    # Statistics
    url(r'^statistics', include('statistics.urls')),

    # Developer app urls
    url(r'^developer/', include('developer.urls')),

    # SSO
    url(r'^saml2/', include('djangosaml2.urls')),

    #questionnaires
    url(r'questionnaire/', include('questionnaire.urls')),

    # Achilles
    url(r'achilles/', include('achilles.urls')),

    # Community
    url(r'^community/', include('community.urls')),

    # Tag system
    url(r'^tag/', include('tag.urls')),

    # Queue of Jobs
    url(r'jobs/', include('taskqueue.urls')),

    # Production hard-fix.
    url(r'^mode-javascript.js$', emif.views.serveModeJs, name="serveModeJs"),
    url(r'^theme-github.js$', emif.views.serveThemeGithub, name="serveThemeGithub"),

    #oauth
    url(r'^accounts/', include('allauth.urls')),

    #oauth
    url(r'^accounts/', include('lifescience_aai.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^403/$', TemplateView.as_view(template_name='403.html')),
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
