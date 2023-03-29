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
from questionnaire import Processors, QuestionProcessors
from django.utils.translation import ugettext as _

from json import dumps
import re

@question_proc('open-multiple')
def question_open_multiple(request, question):
    cd = question.getcheckdict()

    key = "question_%s" % question.number
    value = question.getcheckdict().get('default','')

    if key in request.POST:
        value = request.POST[key]
    return {
        'required' : question.getcheckdict().get('required', False),
        'value' : value,
        "hasValue": value!= "",
        'template' : 'questionnaire/open-multiple.html',
    }


@answer_proc('open-multiple')
def process_open_multiple(question, ansdict):
    checkdict = question.getcheckdict()
    required = question.getcheckdict().get('required', 0)
    ans = str(ansdict['ANSWER']) or ''
    qtype = question.get_type()

    if ansdict.has_key('comment') and len(ansdict['comment']) > 0:
        return dumps([ans, [ansdict['comment']]])
    if ans:
        return dumps([ans])
    return dumps([])

add_type('open-multiple', 'Multiple answers, open value')
