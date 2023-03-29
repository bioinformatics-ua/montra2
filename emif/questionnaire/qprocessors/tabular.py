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
from questionnaire import *
from questionnaire import Processors, QuestionProcessors, Fingerprint_Summary

from django.utils.translation import ugettext as _

from questionnaire import *
from django.utils.translation import ugettext as _
from json import dumps

from django.template.loader import render_to_string

import json
import re

@question_proc('choice-tabular')
def question_pub(request, question):
    cd = question.getcheckdict()

    key = "question_%s" % question.number
    value = question.getcheckdict().get('default','')
    #print "PUB"
    #print key
    #print request.POST
    if key in request.POST:
        value = request.POST[key]
        #print "REQUEST" + value
    return {
        'required' : question.getcheckdict().get('required', False),
        'value' : value,
        "hasValue": value!="",
        'template' : 'questionnaire/choice-tabular.html',
    }

@show_summary('choice-tabular')
def show_summ(value, question=None):

    if value== "":
        return ""

    if not value.startswith('['):
        value = '['+value+']'

    try:
        return render_to_string('questionnaire/tabular-summary.html', {'choices': value, 'question': question})
    except:
        raise
        return ""

@show_index('choice-tabular')
def show_index(value):
    tmp = []

    jload = json.loads(value)

    def __simplex(val):
        return re.sub('[^a-z0-9]', '', val.lower())


    tmp.append({
            'key': '',
            'value': value
        })

    for val in jload:
        extra = val.get('extra', None)

        if extra:
            y = __simplex(val.get('y', ''))
            tmp.append({
                    'key': '_'+y+'_opt',
                    'value': '%s %s' % (val['y'], val['extra'])
                })
        else:
            x = __simplex(val.get('x', ''))
            y = __simplex(val.get('y', ''))
            tmp.append({
                    'key': '_'+x+'_'+y,
                    'value': '%s %s %s' % (val['x'], val['y'], val['val'])
                })

    print tmp

    return tmp

add_type('choice-tabular', 'Tabular - Choice')





