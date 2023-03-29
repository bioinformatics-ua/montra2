from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LifeScienceAaiAccount(ProviderAccount):

    def to_str(self):
        dflt = super(LifeScienceAaiAccount, self).to_str()
        return self.account.extra_data.get('preferred_username', dflt)


class LifeScienceAaiProvider(OAuth2Provider):
    id = 'elixir_aai'
    name = 'Life Science AAI'
    account_class = LifeScienceAaiAccount

    def extract_uid(self, data):
        return str(data['sub'])

    def extract_common_fields(self, data):
        return dict(username=data.get('preferred_username'),
                    name=data.get('name'),
                    email=data.get('email'))

    def get_default_scope(self):
        scope = ['voperson_external_affiliation', 'openid', 'email', 'profile']
        return scope


providers.registry.register(LifeScienceAaiProvider)
