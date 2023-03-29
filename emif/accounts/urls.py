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
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from userena import settings as userena_settings
from userena import views as userena_views

from community.views import join_first_auto
from .forms import SignupFormExtra
from .views import profile_edit, signin, signup, wrapped_password_reset_confirm

urlpatterns = [
    url(r'^signup/$',
        signup,
        {'signup_form': SignupFormExtra,
         'success_url': settings.BASE_URL},
        name='userena_signup'),

    url(r'^(?P<username>.+)/signup/complete/$',
        userena_views.direct_to_user_template,
        {'template_name': 'userena/signup_complete.html',
         'extra_context': {
             'userena_activation_required': userena_settings.USERENA_ACTIVATION_REQUIRED,
             'userena_activation_days': userena_settings.USERENA_ACTIVATION_DAYS}},
        name='userena_signup_complete'),

    url(r'^signin/$',
        signin,
        name='userena_signin'),

    url(r'^signout/$',
        userena_views.SignoutView.as_view(),
        name='userena_signout'),

    # Edit Profile
    url(r'^profile_edit/$', profile_edit, name='prof_edit'),

    # Reset password
    url(r'^password/reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='userena/password_reset_form.html',
            email_template_name='userena/emails/password_reset_message.txt',
            extra_context={
                'without_usernames': userena_settings.USERENA_WITHOUT_USERNAMES
            },
            success_url=reverse_lazy('userena_password_reset_done'),
        ),
        name='userena_password_reset'),
    url(r'^password/reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='userena/password_reset_done.html'
        ),
        name='userena_password_reset_done'),

     url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        wrapped_password_reset_confirm,
        {
         'template_name': 'userena/password_reset_confirm_form.html'
        },
        name='userena_password_reset_confirm'), 

    url(r'^password/reset/confirm/complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='userena/password_reset_complete.html',
        ),
        name='password_reset_complete'),

    # Activate
    url(r'^activate/(?P<activation_key>\w+)/$',
        userena_views.activate,
        {"success_url": "/accounts/signup/activate/complete/"},
        name='userena_activate'),
    url(r'^activate/retry/(?P<activation_key>\w+)/$',
        userena_views.activate_retry,
        name='userena_activate_retry'),

    # reject user
    url(r'^reject/(?P<activation_key>\w+)/$',
       userena_views.reject,
       name='userena_reject'),

    # Change email and confirm it
    url(r'^(?P<username>[\@\.\+\w-]+)/email/$',
        userena_views.email_change,
        name='userena_email_change'),
    url(r'^(?P<username>[\@\.\+\w-]+)/email/complete/$',
        userena_views.direct_to_user_template,
        {'template_name': 'userena/email_change_complete.html'},
        name='userena_email_change_complete'),
    url(r'^(?P<username>[\@\.\+\w-]+)/confirm-email/complete/$',
        userena_views.direct_to_user_template,
        {'template_name': 'userena/email_confirm_complete.html'},
        name='userena_email_confirm_complete'),
    url(r'^confirm-email/(?P<confirmation_key>\w+)/$',
        userena_views.email_confirm,
        name='userena_email_confirm'),

    # Disabled account
    url(r'^(?P<username>[\@\.\+\w-]+)/disabled/$',
        userena_views.disabled_account,
        {'template_name': 'userena/disabled.html'},
        name='userena_disabled'),

    # Change password
    url(r'^(?P<username>[\@\.\+\w-]+)/password/$',
        userena_views.password_change,
        name='userena_password_change'),
    url(r'^(?P<username>[\@\.\+\w-]+)/password/complete/$',
        userena_views.direct_to_user_template,
        {'template_name': 'userena/password_complete.html'},
        name='userena_password_change_complete'),

    url(r'^(?P<username>[\@\.\+\w-]+)/edit/$',
        userena_views.profile_edit,
        name='userena_profile_edit'),

    # View profiles
    url(r'^(?P<username>(?!(signout|signup|signin)/)[\@\.\+\w-]+)/$',
        userena_views.profile_detail,
        name='userena_profile_detail'),
    url(r'^page/(?P<page>[0-9]+)/$',
        userena_views.ProfileListView.as_view(),
        name='userena_profile_list_paginated'),
    url(r'^$',
        userena_views.ProfileListView.as_view(),
        name='userena_profile_list'),
]

if settings.SINGLE_COMMUNITY:
    # signing up redirects to auto join
    additional_settings = [url(r'^signup/activate/complete/$', join_first_auto, name='userena_activated')]
else:
    # usual activation link
    additional_settings = [url(r'^signup/activate/complete/$',
        TemplateView.as_view(template_name='userena/activation_complete.html'),
        name='userena_activated'),
    ]
urlpatterns += additional_settings
