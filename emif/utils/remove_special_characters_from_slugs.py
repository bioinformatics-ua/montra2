from __future__ import print_function

from django.db import transaction
from django.db.models import Q

from questionnaire.models import Question
from searchengine.models import Slugs

__all__ = ["apply"]


def slug_exists_in_quest(slug, quest):
    return Question.objects.filter(questionset__questionnaire=quest, slug_fk__slug1=slug).exists()


@transaction.atomic
def apply():
    bad_characters = "<>'+-"

    filter = Q()
    for c in bad_characters:
        filter |= Q(slug1__contains=c)

    for slug in Slugs.objects.filter(filter):
        new_slug = slug.slug1
        new_slug = new_slug.replace("<", "_lt_")
        new_slug = new_slug.replace(">", "_gt_")
        for c in "'+-":
            new_slug = new_slug.replace(c, "_")

        # lets check if the new slug is in use on the existing questionnaires
        quests = set(question.questionset.questionnaire for question in slug.question_set.all())
        i = 0
        while any(slug_exists_in_quest(new_slug + str(i), quest) for quest in quests):
            i += 1
        if i != 0:
            new_slug = new_slug + str(i)

        if slug.slug1 != new_slug:
            slug.slug1 = new_slug
            slug.save()

            for question in slug.question_set.all():
                question.slug = new_slug
                question.save()
