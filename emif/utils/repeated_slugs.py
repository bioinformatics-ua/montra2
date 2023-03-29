from questionnaire.models import *
from searchengine.models import *
from django.shortcuts import render_to_response, get_object_or_404
import sys
from searchengine.models import Slugs


def minute():
    quest = Questionnaire.objects.filter(slug='ukdp')[0]
    print quest

    qsets = QuestionSet.objects.filter(questionnaire=quest).order_by('sortid')
    slugs  = []
    print len(qsets)
    counter = 1
    questions = quest.questions()
    print len(questions)
    for q in questions:
        
        if q.slug_fk.slug1 in slugs:
            print(q.slug)
            print(q.slug_fk.slug1)
            while q.slug in slugs:
                q.slug = q.slug + str(counter)
                counter = counter + 1 
            if len(Slugs.objects.filter(slug1=q.slug))>0:
                x = Slugs.objects.filter(slug1=q.slug)[0]
            else:
                x = Slugs()
            x.slug1 = q.slug
            x.description = q.text
            x.save()
            q.slug_fk = x 
            q.save()
        else:
            slugs.append(q.slug_fk.slug1)
    print len(slugs)
