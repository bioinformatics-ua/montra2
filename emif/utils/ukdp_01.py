
from questionnaire.models import *
from searchengine.models import *
from django.shortcuts import render_to_response, get_object_or_404
import sys


quest = Questionnaire.objects.filter(slug='dpuk-proforma_old2')[0]
#quest = Questionnaire.objects.filter(slug='DPUKVFINAL')[0]
print quest

qsets = QuestionSet.objects.filter(questionnaire=quest).order_by('sortid')

for qset in qsets:
    questions = quest.questions()
    for q in questions: 
        if len(q.checks)> 2:
             
            #dependent="4.04,yes"
            dependend = q.checks.split('"')[1]
            #print(dependend)
            dependend = dependend.split(',')[0]
            #print(dependend)
            deps = dependend.split(".")
            if deps[0].isdigit():
                question_slug = Question.objects.filter(number=dependend, questionset__questionnaire=quest)
                #print(question_slug)
                if len(question_slug)>0:
                    question_slug = question_slug[0]
                    depFinal = q.checks.split('"')[0] + '"' + question_slug.slug_fk.slug1 + "," + q.checks.split(',')[1]
                    #print(q.checks)
                    print(depFinal)
                    q.checks = depFinal
                    q.save()
            
            
############ Just for chekcing ############
from questionnaire.models import *
from searchengine.models import *
from django.shortcuts import render_to_response, get_object_or_404
import sys

quest = Questionnaire.objects.filter(slug='ukdp')[0]


questions = quest.questions()
for q in questions: 
    if len(q.checks)> 2:
        #q.checks = q.checks.split("=")[0] + '="' + q.checks.split("=")[1]
        print q.checks 
        print q.pk


############ Fix Slugs ############

from questionnaire.models import *
from searchengine.models import *
from django.shortcuts import render_to_response, get_object_or_404
import sys
from searchengine.models import Slugs
quest = Questionnaire.objects.filter(slug='ukdp')[0]
print quest

qsets = QuestionSet.objects.filter(questionnaire=quest).order_by('sortid')
slugs  = []
for qset in qsets:
    questions = quest.questions()
    for q in questions:
        
        if q.slug_fk.slug1 in slugs:
            print(q.slug)
            print(q.slug_fk.slug1)
            pass
            x = Slugs()
            x.slug1 = q.slug
		    x.description = q.text
            #x.save()
            q.slug_fk = x 
            #q.save()
        else:
            slugs.append(q.slug_fk.slug1)