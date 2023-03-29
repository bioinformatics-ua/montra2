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
"""
questionnaire - Django Questionnaire App
========================================

Create flexible questionnaires.

Authors: - Robert Thomson <git AT corporatism.org>
         - Luís A. Bastião Silva <bastiao@bmd-software.com>
"""

from django.conf import settings
from django.dispatch import Signal
import os, os.path
import imp

default_app_config = 'questionnaire.apps.QuestionnaireConfig'

__all__ = [  'show_summary', 'show_flat', 'question_proc', 'answer_proc', 'add_type', 'AnswerException',
            'questionset_done', 'questionnaire_done', 'show_index']

QuestionChoices = []
QuestionProcessors = {} # supply additional information to the templates
Processors = {} # for processing answers
Fingerprint_Summary = {} # for summaries
Fingerprint_Index = {} # for solr indexing
Fingerprint_Flat = {} # for flat representation of structured questions

questionset_done = Signal(providing_args=["runinfo", "questionset"])
questionnaire_done = Signal(providing_args=["runinfo", "questionnaire"])

class AnswerException(Exception):
    "Thrown from an answer processor to generate an error message"
    pass


def question_proc(*names):
    """
    Decorator to create a question processor for one or more
    question types.

    Usage:
    @question_proc('typename1', 'typename2')
    def qproc_blah(request, question):
        ...
    """
    def decorator(func):
        global QuestionProcessors
        for name in names:
            QuestionProcessors[name] = func
        return func
    return decorator

def answer_proc(*names):
    """
    Decorator to create an answer processor for one or more
    question types.

    Usage:
    @answer_proc('typename1', 'typename2')
    def qproc_blah(request, question):
        ...
    """
    def decorator(func):
        global Processors
        for name in names:
            Processors[name] = func
        return func
    return decorator

def show_summary(*names):
    """
    Decorator to create an answer processor for one or more
    question types.

    Usage:
    @show_summary('typename1', 'typename2')
    def qproc_blah(request, question):
        ...
    """
    def decorator(func):
        global Fingerprint_Summary
        for name in names:
            Fingerprint_Summary[name] = func
        return func
    return decorator

def show_index(*names):
    """
    Decorator to create an answer processor for one or more
    question types at index time

    Usage:
    @question_proc('typename1', 'typename2')
    def qproc_blah(request, question):
        ...
    """
    def decorator(func):
        global Fingerprint_Index
        for name in names:
            Fingerprint_Index[name] = func
        return func
    return decorator

def show_flat(*names):
    """
    Decorator to create an answer processor for flattening types

    Usage:
    @show_flat('typename1', 'typename2')
    def qproc_blah(request, question):
        ...
    """
    def decorator(func):
        global Fingerprint_Flat
        for name in names:
            Fingerprint_Flat[name] = func
        return func
    return decorator

def add_type(id, name):
    """
    Register a new question type in the admin interface.
    At least an answer processor must also be defined for this
    type.

    Usage:
        add_type('mysupertype', 'My Super Type [radio]')
    """
    global QuestionChoices
    QuestionChoices.append( (id, name) )


from questionnaire.qprocessors import * # make sure ours are imported first

add_type('sameas', 'Same as Another Question (put question number (alone) in checks')

for app in settings.INSTALLED_APPS:
    if 'django' in app:
        continue

    try:
        app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
    except AttributeError:
        continue

    try:
        imp.find_module('qprocessors', app_path)
    except ImportError:
        continue

    __import__("%s.qprocessors" % app)

