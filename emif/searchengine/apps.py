from django.apps import AppConfig


class SearchEngineConfig(AppConfig):
    name = 'searchengine'

    def ready(self):
        import searchengine.signals
