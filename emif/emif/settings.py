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
# Django settings for emif project.
import os.path

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from os import path
from saml2 import saml
import saml2


# well i need to do this trick to be able to refere above project root so i can have config files outside the project
BASEDIR = os.path.abspath(os.path.join(path.dirname(path.abspath(__file__)), '../../'))

DEBUG = True

SITE_NAME = "EMIF Catalogue"

GLOBALS = {
    'BRAND': "EMIF Catalogue",
    'PROJECT_NAME': "EMIF",
    # url based upon STATIC_URL
    'BRAND_LOGO': "img/emif_logo_trans.png",
    'COPYRIGHT': "© Bioinformatics.UA, UA",
    'FOOTER_EXTRA': """
                    <!-- EXTRA HTML FOOTER CODE HERE -->
                    <small id="supportability">This website is optimised to Safari, Chrome, Firefox, Opera and IE9+.
                    <!--It runs in IE7-IE8, but it has low performance and no enhanced features.--></small>
                   """,
    'GOOGLE_ANALYTICS': [
        ['_setAccount', 'UA-38876251-1'],
        ['_trackPageview']
    ],
    'ACTIVATION_REQUIRED': True,
    'ADMIN_MODERATION': False,
    'LOGO': ''
}
# Header and Footer Settings

#TODO: need may be changed.
PUBLIC_HOST='localhost' 

#BASE_URL = '/emif-dev/'
# Note: When changing this to something not /, all is automatically changed on the links (except for links inside css files)
# for this files we must change it manually (or serve them as dinamic files), this problem only ocurrs on IE
# so if changing to something that not /, we should also change on file /static/css/bootstrap_ie_compatibility.css all relative # paths. This is necessary because i cant use django template variables inside a considered static file.
BASE_URL = '/'
SINGLE_COMMUNITY = False
VERSION = '5.5.0'
VERSION_DATE = '2018.March.19 - 15:41UTC'
PROJECT_DIR_ROOT = '/projects/emif-dev/'

XMLSEC_BIN = '/usr/bin/xmlsec1'
IDP_SERVICES = [
    path.join(BASEDIR, 'confs/sso/idps/openidp.xml'),
    path.join(BASEDIR, 'confs/sso/idps/testshib.xml')
]

if DEBUG:
    PROJECT_DIR_ROOT = "./"
    MIDDLE_DIR = ""
    IDP_URL = "http://localhost:8000/"
else:
    MIDDLE_DIR = "/emif/"
    IDP_URL = BASE_URL


ADMINS = (
    ('Luis A. Bastiao Silva', 'bastiao@ua.pt'),
    ('José Luis Oliveira', 'jlo@ua.pt'),
    ('João Rafael Almeida', 'joao.rafael.almeida@ua.pt'),
)

# Only for debug 
if DEBUG:
    ADMINS = (
        ('Luis A. Bastiao Silva', 'bastiao@ua.pt'),
        ('José Luis Oliveira', 'jlo@ua.pt'),
        ('João Rafael Almeida', 'joao.rafael.almeida@ua.pt'),
    )


SOLR_HOST = os.getenv("SOLR_HOST")
SOLR_PORT = os.getenv("SOLR_PORT")
SOLR_PATH = "/solr"
SOLR_CORE = "collection1"

BROKER_CELERY = 'amqp://guest@{}//'.format(os.getenv("RABBITMQ_HOST"))

MANAGERS = ADMINS

DATABASE_PATH_SQLITE3 = "emif.db"

if not DEBUG:
    DATABASE_PATH_SQLITE3 = PROJECT_DIR_ROOT + "emif/" + DATABASE_PATH_SQLITE3

DATABASES = {
    'default': {
        #        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'emif_testing', # Or path to database file if using sqlite3.
        'USER': 'postgres', # Not used with sqlite3.
        'PASSWORD': '12345', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    },
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Lisbon'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"



# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    #'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_JS_FILTERS = (
    'compressor.filters.jsmin.JSMinFilter',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j*zdirg7yy9@q1k=c*q!*kovfsd#$FDFfsdfkae#id04pyta=yz@w34m6rvwfe'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'questionnaire.request_cache.RequestCacheMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'emif.middleware.LoginRequiredMiddleware',
    'emif.middleware.ProfileRequiredMiddleware',
    'terms.middleware.TermsAcceptMiddleware',
    'emif.interceptor.NavigationInterceptor',
)

ROOT_URLCONF = 'emif.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'emif.wsgi.application'

GRAPPELLI_ADMIN_TITLE = "%s Admin" % GLOBALS['BRAND']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'markup_deprecated',
    # 'django.contrib.sites',
    'django_comments',
    'django.contrib.flatpages',

    # Admin area
    #'django_admin_bootstrapped',
    # dashboard
    'dashboard',
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.admindocs',

    'django_premailer',

    # Reverse URL modules for Django and Javascript Framework 
    'django_js_reverse',

    # Questionnaires
    'transmeta',
    'questionnaire',
    #'questionnaire.page',

    # User signup/signin/management
    'userena',
    'guardian',
    'easy_thumbnails',
    'accounts',

    # Django Rest Framework
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    # Bootstrap layouts and forms
    'crispy_forms',
    'emif',

    'searchengine',
    "developer",
    'api',
    'fingerprint',
    'control_version',
    'docs_manager',
    'population_characteristics',
    'literature',
    'django_bootstrap_breadcrumbs',
    'bootstrap_pagination',


    'djcelery',
    #'djangobower',
    'advancedsearch',

    # public links
    'public',
    
    'studies',

    # newsletters
    'django_extensions',
    'newsletter',

    # Utility to hook custom view admin pages easily
    'adminplus',

    # unique views counter
    'hitcount',

    # notifications
    'notifications',
    # Django-Compressor
    "compressor",

    # django-constance
    'constance.backends.database',
    "constance",

    'django_ace',
    "djangosaml2",


    # achilles
    "achilles",

    #community
    'community',

    # cookies
    'cookies',

    # terms
    'terms',

    # TAG
    'tag',

    #generic async task queue
    'taskqueue',

    #OAUTH SSO
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    #enabled providers for SSO
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.orcid',
    'lifescience_aai',

    'sslserver',
    'django_tables2',

    'webpack_loader',

    'selenium'
)

# Exclude Javasscript route from administration pages
# Developers: More apps could be included here.
JS_REVERSE_EXCLUDE_NAMESPACES = ['admin']


GRAPPELLI_INDEX_DASHBOARD = 'accounts.grapelli.CustomIndexDashboard'

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ADDITIONAL_FIELDS = {
    'view_selector': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (("Table", "Table"), ("List", "List"), ("Card", "Card"))
    }],
}

CONSTANCE_CONFIG = {
    'show_fingerprint_number': (True, 'Show the numbers of the questions on the fingerprint.'),
    'table_view': ('Table', 'Select the default view', 'view_selector'),
    'Request_Answer': (True, 'Controls whether we activate/deactivate the request answer functionality.'),
    'population_characteristics': (True, 'Controls whether we activate/deactivate the Population Characteristics functionality.'),
    'compare_populations': (True, 'Controls whether we activate/deactivate the comparison of population characteristics.'),
    'documents': (True, 'Controls whether we activate/deactivate the Documents functionality.'),
    'literature': (True, 'Controls whether we activate/deactivate the Literature functionality.'),
    'extra_information': (True, 'Controls whether we activate/deactivate the Extra Information functionality.'),
    'discussion': (True, 'Controls whether we activate/deactivate the discussion functionality.'),
    'newsletter': (True, 'Controls whether we activate/deactivate the newsletter functionality.'),
    'more_like_this': (True, 'Controls whether we activate/deactivate the more like this functionality.'),
    'geolocation': (True, 'Controls whether we activate/deactivate the map functionality.'),
    'datatable': (True, 'Controls whether we activate/deactivate the datatable functionality.'),
    'login_bypass': (False, 'Controls whether we activate/deactivate the login bypass functionality.'),
    'bug_report': (
        True,
        'Controls whether we activate/deactivate the Bug Report functionality. '
        'If this is deactivated, the feedback left menu button will redirect to the Suggestions page.',
    ),
    'copyright': (GLOBALS['COPYRIGHT'], 'Text to show as copyright'),
    'copyrightsplash': ('<a target="_blank" href="http://bioinformatics.ua.pt/">Bioinformatics, UA.</a>', 'Text to show as copyright on splash screen'),
    'footer_extra': (GLOBALS['FOOTER_EXTRA'], 'Extra HTML to be shown besides the footer'),
    'brand': (GLOBALS['BRAND'], 'Text to be shown as the brand'),
    'project_name': (GLOBALS['PROJECT_NAME'], 'Text to be shown as the brand'),
    'useCommunityList': (True, 'Use the community list '),
    'useFingerprintList': (True, 'Show a list for in-place fingerprint switching '),
    'useQuestionSetRBAC': (True, 'Enable RBAC for access management of each questionnaire section'),
    'logo': (GLOBALS['LOGO'], 'Landing page logo'),
    'title': ('The European Health Data & Evidence Portal', 'Landing page title'),
    'applicationTitle': ('Applications available', 'Applications available section title'),
    'applicationSectionDescription': ('The EHDEN Portal has several applications available to support the research in healthcare studies.', 'Applications available section description'),
    'country_slug': ('location', 'Slug to reference the country in the questionnaire'),
    'population_slug': ('population_size', 'Slug to reference the population size in the questionnaire'),
    'portal_installation':(False, 'Changes the layout of the lateral right menu (EHDEN Portal request)'),
    'map_questionnaire_id': (4, 'Questionnaire to use to fill the map view'),
    'client_wrapper_name':('', 'Client wrapper name for pip install '),
    'recaptcha_verification':(False, 'Activate recaptcha verification on new user registrations'),
    'showSummary':(False, 'Show the summary in the landing page'),
    'homeBanner': ('The European Health Data & Evidence Network (EHDEN) project aspires to be the trusted observational research ecosystem to enable better health decisions, outcomes and care. Its mission is to provide a new paradigm for the discovery and analysis of health data in Europe, by building a large-scale, federated network of data sources standardized to the OMOP common data model.', 'The text shown in the first banner.'),
    'footerBanner': ('Central to EHDEN is the standardisation of health data to the OMOP common data model and the adoption of analytical tools developed by the international Observational Health Data Sciences and Informatics (OHDSI) open science collaboration.', 'The text shown in the lower banner.'),
    'disclaimer': ('The European Health Data & Evidence Network has received funding from the Innovative Medicines Initiative 2 Joint Undertaking (JU) under grant agreement No 806968. The JU receives support from the European Union’s Horizon 2020 research and innovation programme and EFPIA.', 'Disclaimer for the landing page'),
    'compare_maximum_DBs': (3,'Defines the maximum number of DBs that can be compared (Recommended: value in the range between 2 and 6).', int),
    'terms_of_use_redirect': (False, 'If a logged in user has not accepted the ToU, redirect him to page to read and accept ToU.'),
    'terms_of_use_redirect_on_update': (False, 'Redirect users to ToU consent page if ToU has been updated. Unused if "terms_of_use_redirect" is set to false.'),
    'cookie_disclaimer': ('', 'Defines the cookie disclaimer for the deployment. Leave empty to not show a cookie disclaimer.'),
    'privacy_notice_url': ('', 'URL endpoint of the end user\'s privacy notice (typically \'/static/files/privacy_notice.pdf\'), should it exist. Appends an additional sentence to the cookie disclaimer if not empty.'),
    'return_databases_link': (True, 'Controls if a "Databases" link is added on the fingerprint show page, alongside the database name, working as a return button to the databases listings page.'),

    ###Left menu options below
    'searchMenu':(True,'This option shows the button for this submenu in the menu Catalogue of the left menu'),
    'customViewMenu':(True, 'This option shows the button for this submenu in the menu Catalogue of the left menu'),
    'privateLinksMenu':(True, 'This option shows the button for this submenu in the menu Catalogue of the left menu'),
    'mapMenu':(True, 'This option shows the button for this component in the left menu'),
    'dashboardMenu':(True, 'This option shows the button for this component in the left menu'),
    'apiMenu':(True, 'This option shows the button for this component in the left menu'),
    'aboutMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'historyMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'faqMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'docMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'contactMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'notificationsMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'jobQueueMenu':(True, 'This option shows the button in the section Portal of the left menu'),
    'questionSetsMenu':(True,'This option shows the button for this submenu in the menu Settings of the left menu'),
    'componentsMenu':(True,'This option shows the button for this submenu in the menu Settings of the left menu'),
    'communicationMenu':(True,'This option shows the button for this submenu in the menu Settings of the left menu')

}

CONSTANCE_CONFIG_FIELDSETS = {
    'General Options': ('show_fingerprint_number', 'table_view', 'brand', 'project_name', 'footer_extra', 'copyrightsplash', 'copyright', 'terms_of_use_redirect', 'terms_of_use_redirect_on_update', 'cookie_disclaimer', 'privacy_notice_url', 'portal_installation', 'client_wrapper_name', 'recaptcha_verification', 'compare_maximum_DBs'),
    'Left Menu Options: Catalogue': (
        'searchMenu', 'customViewMenu', 'privateLinksMenu'),
    'Left Menu Options: Community': (
        'mapMenu', 'dashboardMenu', 'apiMenu'),
    'Left Menu Options: Manage': (
        'questionSetsMenu', 'componentsMenu', 'communicationMenu'),
    'Left Menu Options: Portal': (
        'aboutMenu', 'historyMenu', 'faqMenu', 'docMenu', 'contactMenu', 'notificationsMenu', 
        'jobQueueMenu'),
    'Features': (
        'Request_Answer', 'population_characteristics', 'compare_populations', 'documents', 'literature',
        'extra_information', 'discussion', 'newsletter', 'more_like_this', 'geolocation', 'datatable', 'login_bypass',
        'useCommunityList', 'useFingerprintList', 'useQuestionSetRBAC', "bug_report", "return_databases_link",
    ),
    'Langing Page Options': ('logo', 'title', 'applicationTitle', 'applicationSectionDescription', 'showSummary', 'homeBanner', 'footerBanner', 'disclaimer'),
    'World Map Options': ('country_slug','population_slug', 'map_questionnaire_id'),
}


# Userena settings

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

LOGIN_URL = '/saml2/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Email backend settings
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025

ANONYMOUS_USER_NAME = 'AnonymousUser'

AUTH_PROFILE_MODULE = 'accounts.EmifProfile'
USERENA_REGISTER_PROFILE = False

# Questionaire languages
LANGUAGES = (
    ('en', 'English'),
)

# Defines the progressbar behavior in the questionnaire
# the possible options are 'default', 'async' and 'none'
#
#   'default'
#   The progressbar will be rendered in each questionset together with the
#   questions. This is a good choice for smaller questionnaires as the
#   progressbar will always be up to date.
#
#   'async'
#   The progressbar value is updated using ajax once the questions have been
#   rendered. This approach is the right choice for bigger questionnaires which
#   result in a long time spent on updating the progressbar with each request.
#   (The progress calculation is by far the most time consuming method in
#    bigger questionnaires as all questionsets and questions need to be
#    parsed to decide if they play a role in the current run or not)
#
#   'none'
#   Completely omits the progressbar. Good if you don't want one or if the
#   questionnaire is so huge that even the ajax request takes too long.
QUESTIONNAIRE_PROGRESS = 'async'


#Pages that do not require login
LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^login',
    r'^indexbeta$',
    r'^saml2$',
    r'^saml2/login',
    r'^saml2/metadata',
    r'^saml2/acs',
    r'^saml2/ls',
    r'^about',
    r'^feedback',
    r'^faq',
    r'^accounts/signup',
    r'^accounts/signin',
    r'^accounts/activate/(?P<activation_key>\w+)/$',
    r'^(?P<username>.+)/signup/complete/$',
    r'^accounts/password/reset/',
    r'^accounts/(?P<username>[^/]+)/disabled/',
    r'^api/metadata',
    r'^api/search',
    r'^api-token-auth-create/',
    r'^api/importquestionnaire$',
    r'^import-questionnaire',
    r'^delete-questionnaire',
    r'^bootstrap_ie_compatibility',
    # public shares
    r'^public/fingerprint/(?P<fingerprint_id>[^/]+)',
    r'^public/c/(?P<community>[\w]+)/fingerprint/(?P<fingerprintshare_id>[^/]+)$',

    r'^literature/(?P<fingerprint_id>[^/]+)/(?P<page>[0-9]+)$',
    r'^literature/(?P<fingerprint_id>[^/]+)$',
    r'^fingerprintqs/(?P<runcode>[^/]+)/(?P<qsid>[0-9]+)/$',
    r'^detailedqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$',
    r'^population/jerboafiles/(?P<fingerprint_id>[^/]+)/$',
    r'^population/jerboalistvalues/(?P<var>[^/]+)/(?P<row>[^/]+)/(?P<fingerprint_id>[^/]+)/(?P<revision>[^/]+)$',
    r'^population/filters/(?P<var>[^/]+)/(?P<fingerprint_id>[^/]+)$',
    r'^population/genericfilter/(?P<param>[^/]+)$',
    r'^population/settings/(?P<runcode>[^/]+)/$',

    r'^docsmanager/docfiles/(?P<fingerprint>[^/]+)/$',
    r'^api/getfile',
    r'^controlversion/github_event$',

    r'^achilles/home$',
    r'^achilles/aw/(?P<fid>[^/]+)/(?P<report_name>[a-zA-Z0-9_]+)/$',

    r'^achilles/ds/(?P<fingerprint>[^/]+)/$',

    r'^achilles/zip/ds/(?P<fingerprint>[^/]+)/$',
    r'^achilles/zip/(?P<fingerprint_id>[^/]+)/(?P<name>[a-zA-Z0-9_]+)/$',
    r'^achilles/zip/(?P<fingerprint_id>[^/]+)/(?P<name>[a-zA-Z0-9_]+)/(?P<id>[0-9]+)/$',

    #r'^community/activate/(?P<hash>[\w]+)$',

    # FingerprintProxy
    r'^developer/api/getFingerprintUID/(?P<fingerprint>[^/]+)$',
    r'^developer/api/getAnswers/(?P<fingerprint>[^/]+)$',
    r'^developer/api/getQuestions/(?P<questionnaire>[^/]+)$',

    # datastore
    r'^developer/api/store/getExtra/(?P<fingerprint>[^/]+)$',

    r'^developer/api/store/getDocuments/(?P<fingerprint>[^/]+)$',
    r'^developer/api/store/putDocuments/(?P<fingerprint>[^/]+)$',

    r'^developer/api/store/getPublications/(?P<fingerprint>[^/]+)$',

    r'^developer/api/store/getComments/(?P<fingerprint>[^/]+)$',

    r'^developer/api/store/putComment/(?P<fingerprint>[^/]+)$',

    #allauth
    r'^accounts/google/login/$',
    r'^accounts/google/login/callback/$',
    r'^accounts/github/login/$',
    r'^accounts/github/login/callback/$',
    r'^accounts/orcid/login/$',
    r'^accounts/orcid/login/callback/$',
    r'^accounts/elixir_aai/login/$',
    r'^accounts/elixir_aai/login/callback/$',
    r'^accounts/social/signup/$',
    r'^accounts/inactive/$',
    
    r'^api/',
    
    r'^index$',
    r'^c/(?P<community>[\w]+)/databases/(?P<page>[-]{0,1}\d+)?$',
    r'^community/(?P<community>[\w]+)/questionnaires$',
    r'^c/(?P<community>[\w]+)/q/(?P<questionnaire>[-\w]+)/(?P<page>[-]{0,1}\d+)?$',
)

#Pages that wont be logged into user history
DONTLOG_URLS = (
    r'^controlversion/github_event$',
    r'^fingerprintqs/(?P<runcode>[^/]+)/(?P<qsid>[0-9]+)/$',
    r'^api/(?P<anything>[^/]*)',
    r'^docsmanager/uploadfile/(?P<fingerprint_id>[^/]+)/$',
    r'^docsmanager/docfiles/(?P<fingerprint_id>[^/]+)/$',
    r'^population/settings/(?P<fingerprint_id>[^/]+)/$',
    r'^population/jerboafiles/(?P<fingerprint_id>[^/]+)/$',
    r'^jerboalistvalues/(?P<var>[^/]+)/(?P<row>[^/]+)/(?P<fingerprint_id>[^/]+)/(?P<revision>[^/]+)$'
    r'^searchqs/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/(?P<aqid>[0-9]+)?$',
    r'^addqs/(?P<community>[\w]+)/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$',
    r'^addqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/$',
    r'^c/(?P<community>[\w]+)/addPost/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/(?P<saveid>[0-9]+)$',
    r'^addPost/(?P<questionnaire_id>[0-9]+)/(?P<sortid>[0-9]+)/(?P<saveid>[0-9]+)$',
    r'^dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$',
    r'^dbEdit/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$',
    r'^dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)$',
    r'^dbDetailed/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)$',
    r'^editqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$',
    r'^detailedqs/(?P<fingerprint_id>[^/]+)/(?P<questionnaire_id>[0-9]+)/(?P<sort_id>[0-9]+)/$',
    r'^qs_data_table$',
    r'^admin/jsi18n/',
    r'^community/activate/(?P<hash>[\w]+)$',
)

#Set session idle timeout (seconds)
SESSION_IDLE_TIMEOUT = 7200
SESSION_SAVE_EVERY_REQUEST = True



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
    )

}

#MONGODB
#=======
#Settings of EMIF MongoDB server, this is used to store the analytic data of population characteristics
MONGO_EMIF = {
    'DB_NAME': 'emif_mongo',
    'HOST': 'localhost',
    'PORT': 27017,
    'USER': '',
    'PASS' : '',
    'COLLECTION': 'jerboa_files'
}


# REDIRECT USER ACCORDING TO PROFILE
REDIRECT_DATACUSTODIAN = 'community.views.splash'
REDIRECT_RESEARCHER = 'community.views.splash'



# MEMCACHED
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '{}:{}'.format(os.getenv("MEMCACHED_HOST"), os.getenv("MEMCACHED_PORT")),
    }
}
CONSTANCE_DATABASE_CACHE_BACKEND = 'default'


PUBLIC_LINK_MAX_VIEWS = 50; # number of views
PUBLIC_LINK_MAX_TIME = 24*30; # hours


# Unique views definitions
HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 1 }




# Django-Compressor activation
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# Periodic user updates newsletter settings
NEWSLETTER_DAY='friday'
NEWSLETTER_HOUR = 3
NEWSLETTER_MIN = 0

# Periodic pubmed feed updates
PUBMED_DAY='friday'
PUBMED_HOUR = 4
PUBMED_MIN = 0

# Pubmed Entrez email
PUBMED_EMAIL = "bastiao@ua.pt"

VERIFICATION_SSL_API = False

try:
    from local_settings import *
except:
    pass


if DEBUG:
    INTERNAL_IPS = ('127.0.0.1', "0.0.0.0", "localhost", "172.19.0.1")
    MIDDLEWARE_CLASSES = ("debug_toolbar.middleware.DebugToolbarMiddleware",) + MIDDLEWARE_CLASSES

    INSTALLED_APPS += ("debug_toolbar",)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.profiling.ProfilingDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
    )

    DEBUG_TOOLBAR_CONFIG = {
        # 'INTERCEPT_REDIRECTS': False,
    }


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "custom": {
            "format": "%(asctime)s %(levelname)-5s %(name)s:%(lineno)s %(message)s",
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            "formatter": "custom",
        },
    },
    "root": {
        'handlers': ['console'],
        'level': "DEBUG" if DEBUG else "INFO",
    }
}

if DEBUG:
    MEDIA_ROOT = 'media/'
else:
    MEDIA_ROOT = PROJECT_DIR_ROOT + 'emif/emif/collected-media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = BASE_URL+'media/'


if DEBUG:
    STATIC_ROOT = ''
else:
    STATIC_ROOT = PROJECT_DIR_ROOT + 'emif/emif/collected-static/'



#CONNECT MONGODB
#===============

# Connect on MongoDB Database
from pymongo.errors import ConnectionFailure, CollectionInvalid
import sys


from pymongo import MongoClient
try:
    if  MONGO_EMIF['USER'] != '' and  MONGO_EMIF['PASS']:
        client = MongoClient('mongodb://' + MONGO_EMIF['USER'] + ':' + MONGO_EMIF['PASS'] + '@'+MONGO_EMIF['HOST'] + ':' +str(MONGO_EMIF['PORT']))
    else:
        client = MongoClient('mongodb://' + MONGO_EMIF['HOST'] + ':' +str(MONGO_EMIF['PORT']))
    # db_name_mongo = MONGO_EMIF['DB_NAME']
    # db_mongo = client.db_name_mongo
    db_mongo = client.emif_mongo

    # capped collection, to keep pubmed articles to show into the feed
    db_mongo.pubmed_feed_collection.create_index('pmid', unique=True)

    # jerboa_collection = db_mongo.MONGO_EMIF['COLLECTION']
    jerboa_collection = db_mongo.jerboa_files
    jerboa_aggregation_collection = db_mongo.jerboa_aggregation

    pubmed_feed_collection = db_mongo.pubmed_feed_collection
    MONGOD_ONLINE=True


except ConnectionFailure, e:
    jerboa_collection = None
    jerboa_aggregation_collection = None 
    pubmed_feed_collection = None 
    MONGOD_ONLINE=False

    sys.stderr.write("Could not connect to MongoDB: %s\n" % e)
    sys.stderr.write("WARNING: some components will not work properly \n")
    #sys.exit(1)


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = BASE_URL+'static/'


COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL,
    'GOOGLE_ANALYTICS': GLOBALS['GOOGLE_ANALYTICS']
}


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'emif/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'questionnaire/static/'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'api/static/'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'fingerprint/static/'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'population_characteristics/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'literature/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'docs_manager/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'advancedsearch/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'public/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'compare/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'accounts/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'dashboard/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'achilles/static'),
    os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'webpack_bundles'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [        
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'apps/seantis-questionnaire/questionnaire/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'emif/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'population_characteristics/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'literature/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'control_version/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'docs_manager/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'compare/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'advancedsearch/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'public/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'dashboard/templates'),

            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'notifications/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'accounts/templates'),
            os.path.abspath(PROJECT_DIR_ROOT + MIDDLE_DIR + 'achilles/templates'),
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "emif.context_processors.debug",
                "emif.context_processors.baseurl",
                #"emif.context_processors.profiles_processor",
                'constance.context_processors.config',
                "emif.context_processors.globals",
                "emif.context_processors.thirdparty",
                "emif.context_processors.belongcomms",
                "emif.context_processors.eprofile",
                "emif.context_processors.singlecommunity",
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #     'django.template.loaders.eggs.Loader',
            ]
        },
    },
]

#Userena settings
USERENA_ACTIVATION_REQUIRED = GLOBALS['ACTIVATION_REQUIRED']
USERENA_ADMIN_MODERATION = GLOBALS['ADMIN_MODERATION']
USERENA_SIGNIN_AFTER_SIGNUP = False
USERENA_WITHOUT_USERNAMES = True
USERENA_DISABLE_PROFILE_LIST = True
USERENA_USE_MESSAGES = False
USERENA_REDIRECT_ON_SIGNOUT = BASE_URL
USERENA_SIGNIN_REDIRECT_BASE = BASE_URL
USERENA_SIGNIN_REDIRECT_URL = BASE_URL + ''
USERENA_MODERATE_REGISTRATION = True                    #True - need admin approval (activation)
USERENA_ACTIVATION_REJECTED = 'ACTIVATION_REJECTED'
USERENA_PENDING_MODERATION = 'PENDING_MODERATION'
USERENA_ACTIVATED = 'ALREADY_ACTIVATED'
USERENA_REMEMBER_ME_DAYS = ('a day', 1)
USERENA_HTML_EMAIL = True
USERENA_USE_PLAIN_TEMPLATE = False

LOGIN_REDIRECT_URL = USERENA_SIGNIN_REDIRECT_URL

if SINGLE_COMMUNITY:
    USERENA_SIGNIN_AFTER_SIGNUP = True

LOGIN_URL = BASE_URL + 'login'
LOGOUT_URL = BASE_URL + 'accounts/signout/'

SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': XMLSEC_BIN,

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': IDP_URL+'saml2/metadata',

    # directory with attribute mapping
    'attribute_map_dir': path.join(BASEDIR, 'confs/sso/attributemaps'),

    # this block states what services we provide
    'service': {
         # we are just a lonely SP
        'sp' : {
            'name': 'Emif Catalogue SP',
            'name_id_format': saml.NAMEID_FORMAT_TRANSIENT,
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    (IDP_URL+'saml2/acs/',
                        saml2.BINDING_HTTP_POST),
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    'single_logout_service': [
                        (IDP_URL+'saml2/ls/',
                            saml2.BINDING_HTTP_REDIRECT),
                        (IDP_URL+'saml2/ls/post',
                            saml2.BINDING_HTTP_POST)
                        ],


                },

           # attributes that this project need to identify a user
          'required_attributes': ['uid'],

           # attributes that may be useful to have but not required
          'optional_attributes': ['eduPersonAffiliation'],
          },
      },

  # where the remote metadata is stored
  'metadata': {
      'local': IDP_SERVICES,
      },

  # set to 1 to output debugging information
  'debug': 1,

  # certificate
  'key_file': path.join(BASEDIR, 'confs/sso/certificates/sp.key'),  # private part
  'cert_file': path.join(BASEDIR, 'confs/sso/certificates/sp.crt'),  # public part

  # own metadata settings
  'contact_person': [
      {'given_name': 'José Luis',
       'sur_name': 'Oliveira',
       'company': 'DETI/IEETA',
       'email_address': 'jlo@ua.pt',
       'contact_type': 'administrative'},
      ],
  # you can set multilanguage information here
  'organization': {
      'name': [('EMIF Catalogue', 'en')],
      'display_name': [('EMIF Catalogue', 'en')],
      'url': [('http://bioinformatics.ua.pt/emif', 'en')],
      },
  'valid_for': 24,  # how long is our metadata valid
}

SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
SAML_USE_NAME_ID_AS_USERNAME = False
SAML_CREATE_UNKNOWN_USER = True
SAML_ATTRIBUTE_MAPPING = {
    'mail': ('email', 'username' ),
    'eduPersonPrincipalName': ('email', 'username'),
    'givenName': ('first_name', ),
    'sn': ('last_name', ),
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

RECAPTCH_PUBLIC_KEY='6LcOFxAUAAAAAIW7UoI39uLU4IZ_4yb91LPD6GA6'
RECAPTCH_PRIVATE_KEY='6LcOFxAUAAAAAA0fYpCGTVaBjnlY3Sn4pvC6TIzN'

JS_REVERSE_OUTPUT_PATH='django_js_reverse/js/'

#oauth-all settings


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'orcid': {
        'BASE_DOMAIN': 'orcid.org',
        'MEMBER_API': False,
        'SCOPE': [
            '/authenticate'
        ],
    }
}
ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.forms.SocialSignupFormExtra'
SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_ADAPTER = 'accounts.adapter.SocialAccountAdapter'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
#life science provider URLs
LIFE_SCIENCE_ACCESS_TOKEN_URL = 'https://login.elixir-czech.org/oidc/token'
LIFE_SCIENCE_AUTHORIZE_URL = 'https://login.elixir-czech.org/oidc/authorize'
LIFE_SCIENCE_PROFILE_URL = 'https://login.elixir-czech.org/oidc/userinfo'
