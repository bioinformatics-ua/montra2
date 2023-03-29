from django.core.management.base import BaseCommand, CommandError
from utils import delete_questionnaire

class Command(BaseCommand):

    args = ''
    help = 'Recounts answers, to account for possible schema modifications on the questionnaires'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        if len(args) == 1:
            delete_questionnaire.delete(None, args[0])
        else:
            self.stdout.write('-- USAGE: \n    '+
                'python manage.py delete_questionnaire <ID>'+
                '\n\n')
