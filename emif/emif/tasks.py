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
from __future__ import absolute_import

from celery import shared_task
from celery import task

from celery import Celery

from emif.settings import *

from docs_manager.storage_handler import *
from emif.models import QueryLog
from django.db.models import Count
import os

from django.template.loader import render_to_string

import time
from django.core.mail import BadHeaderError, EmailMultiAlternatives

from django.conf import settings

celery = Celery('emif', broker=BROKER_CELERY)

@shared_task
def add(x, y):
    return x + y

@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def send_custom_mail(title, description, from_mail, to_mail):

    email = render_to_string('email_template.html', {
            'BRAND': settings.GLOBALS['BRAND'],
            'BRAND_LOGO': settings.GLOBALS['BRAND_LOGO'],
            'title': title,
            'description': description.replace('\n','<br />'),
            'from_mail': from_mail,
            'to_mail': to_mail,
            'current_date': time.strftime("%d/%m/%Y %H:%M:%S")
        })

    msg = EmailMultiAlternatives(title, description, from_mail, to_mail)
    msg.attach_alternative(email, "text/html")

    msg.send()
