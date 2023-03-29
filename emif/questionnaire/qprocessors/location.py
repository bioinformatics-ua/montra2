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
from django.utils.translation import ugettext as _
from json import dumps
import json

# {"adm1": "", "adm2:" ""}

@question_proc('location')
def question_(request, question):
    key = "question_%s" % question.number
    value = question.getcheckdict().get('default','')
    if key in request.POST:
        value = request.POST[key]
        #print value
    return {
        'required' : question.getcheckdict().get('required', False),
        'hasValue': value!="",
        'template' : 'questionnaire/location.html',
        'value' : value,
    }

@answer_proc('location')
def process_(question, ansdict):
    checkdict = question.getcheckdict()
    required = question.getcheckdict().get('required', 0)
    ans = ansdict['ANSWER'] or ''
    qtype = question.get_type()

    if ansdict.has_key('comment') and len(ansdict['comment']) > 0:
        return dumps([ans, [ansdict['comment']]])
    if ans:
        return dumps([ans])
    return dumps([])

@show_summary('location')
def show_summ(value, question=None):
    if value=="" or value=="[{}]":
        return ""

    try:
        representation = json.loads(value)
        #print "***LMF :",representation
        
        order = ['adm5', 'adm4', 'adm3', 'adm2', 'adm1', 'country', 'continent']
        textual_rep = ''

        for level in order:
            #print "*** " + level
            if level in representation and len(representation[level]) > 0:
                # LMF with Bastiao Review.
                if not type(representation[level]) is list:
                    result = representation[level].split('gcode')[0]
                else:
                    result = representation[level][0].split('gcode')[0]
                # Leonardo fix with Bastiao review. 
                #result = representation[level].split('gcode')[0]

                if len(textual_rep) > 0:
                    textual_rep += ', '
                if type(result) is list:
                    textual_rep +=  result[0]
                else:
                    textual_rep += result

        #print "*** place: ",textual_rep

        '''str = value.replace('"','').replace('[{country:','').replace('}]','').replace('adm1:','').replace('adm2:','')

        if str.endswith(','):
            str = str[:-1]
        if str.endswith(','):
            str = str[:-1]
        '''

        return textual_rep
    except:
        #raise 
        return 'Invalid location format'

@show_index('location')
def show_index(value):
    return show_summ(value)

add_type('location','Geographical Location [selects]')
