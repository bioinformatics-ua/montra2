from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import get_user_model
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.conf import settings

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        """

        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # get email from provider
        provider = sociallogin.account.get_provider()
        common_data = provider.extract_common_fields(sociallogin.account.extra_data)
        try:
            email = common_data['email']
        except:
            email = None

        # check if given email address already exists.
        if email is not None:
            user_model = get_user_model()
            users = user_model.objects.filter(email=email)

            if users:
                # if it does, connect this new social login to the existing user
                sociallogin.connect(request, users[0])

                perform_login(request, users[0], email_verification='optional')
                raise ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL.format(id=request.user.id)))
