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
from questionnaire.models import Question
from django.db.models import Q

def convert():
    print "\n----------------------------------------------"
    print "Start converting url questions to url type"
    print "-----------------------------------------------"
    #Find all questions related with url
    questions = Question.objects.filter(Q(slug__icontains="website") | Q(slug__icontains="url"))
    for q in questions :
        #print q.slug
        if(q.type != 'url'):
            q.type='url'
            print "Found question with slug "+ q.slug + " mentioning url whose type isn't yet added, converting to url type."
            # Save changes to question
            q.save()
    print "-----------------------------------------------"
    print " End of url type conversion"
    print "-----------------------------------------------"


convert()
