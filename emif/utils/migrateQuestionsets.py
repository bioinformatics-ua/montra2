from questionnaire.models import Questionnaire, QuestionSet
from django.db import transaction

@transaction.atomic
def migrateQuestionsets():

    quests = Questionnaire.objects.all()

    for quest in quests:
        qsets = QuestionSet.objects.filter(questionnaire=quest).order_by('sortid')

        for qset in qsets:
            quest.qsets.add(qset)

# migrate old questionset questionnaire foreign keys to a manytomany relation
migrateQuestionsets()
