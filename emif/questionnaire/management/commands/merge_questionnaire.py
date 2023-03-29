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
from django.core.management.base import BaseCommand
from questionnaire.imports import ImportQuestionnaire, ImportQuestionnaireExcel
from Levenshtein import ratio

class Command(BaseCommand):
    help = 'Import the questionnaire from excel merging with an already existing questionnaire'

    def add_arguments(self, parser):
        parser.add_argument(
            '--similar',
            default=1,
            type=int,
            help='Instead of exact match, analyse choice changes using an similarity approach')
        parser.add_argument(
            '--ignore',
            default=0.4,
            type=float,
            help='When using a similar approach, ignore strings with proximity lower of 0.4')
        parser.add_argument('file_path')
        parser.add_argument('questionnaire_id', type=int)

    def handle(self, *args, **options):
        file_path = options['file_path']
        questionnaire_id = options['questionnaire_id']

        iq = ImportQuestionnaire.factory('excel', file_path)

        if options['similar'] != 1:
            print "Similarity mode"
            def infer_function(question, new, old):
                # default map translations that need no manual confirmation( this should go to a separate file later)
                default_map = {
                    'Repeated collection(more than once)': 'Repeated collection (specify frequency and/or time interval) ',
                    'Subgroup analyzed (eg. Dementia)': 'Subgroup analyzed (eg. Dementia, please specify subgroup)'
                }

                try:
                    if ratio(unicode(default_map[old]), unicode(new)) > 0.97:
                        return True

                    return False

                except KeyError:
                    print "Not default mapping, manual input required"

                input = None


                # Ignore low scores automatically
                if ratio(old, new) < float(options['ignore']):
                    return False

                while not (input == 'y' or input == 'n'):
                    print """The number of new choices missing processing for question %s is 1, there could be a non obvious match.\n

                    Is '%s' a change of '%s' ? (y/n)
                    """ % (question, new, old)
                    input = raw_input()

                if input == 'y':
                    return True

                return False

            res = iq.import_questionnaire(merge=questionnaire_id, mode=ImportQuestionnaireExcel.SIMILARITY_MODE,
                percentage=float(options['similar']), infer_function=infer_function)


        else:
            print "Exact match mode"

            res = iq.import_questionnaire(merge=questionnaire_id)


        print "RESULT:"
        print res

        print "-- Finished processing " + file_path
