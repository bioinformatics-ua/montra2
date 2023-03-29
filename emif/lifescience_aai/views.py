# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView)
from provider import LifeScienceAaiProvider
from django.conf import settings
from django.urls import reverse
from allauth.utils import build_absolute_uri


class LifeScienceAaiOAuth2Adapter(OAuth2Adapter):
    provider_id = LifeScienceAaiProvider.id
    access_token_url = settings.LIFE_SCIENCE_ACCESS_TOKEN_URL
    authorize_url = settings.LIFE_SCIENCE_AUTHORIZE_URL
    profile_url = settings.LIFE_SCIENCE_PROFILE_URL

    def get_callback_url(self, request, app):
        callback_url = reverse(self.provider_id + "_callback")
        protocol = self.redirect_uri_protocol
        # Force the use of the domain defined at the django's Site model
        return  build_absolute_uri(None, callback_url, protocol)

    # After successfully logging in, use access token to retrieve user info
    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(LifeScienceAaiOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LifeScienceAaiOAuth2Adapter)
