from django.apps import AppConfig


class QuestionnaireConfig(AppConfig):
    name = 'questionnaire'

    def ready(self):
        import questionnaire.signals
