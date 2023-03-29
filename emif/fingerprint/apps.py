from django.apps import AppConfig


class FingerprintConfig(AppConfig):
    name = 'fingerprint'

    def ready(self):
        import fingerprint.signals
