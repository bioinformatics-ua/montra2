from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import LifeScienceAaiProvider

urlpatterns = default_urlpatterns(LifeScienceAaiProvider)
