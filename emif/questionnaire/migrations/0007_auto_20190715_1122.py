# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-15 10:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0006_auto_20190601_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[(b'timeperiod', b'Time Period [input, select]'), (b'custom', b'Custom'), (b'publication', b'Publication'), (b'choice-tabular', b'Tabular - Choice'), (b'range', b'Ranged slide with custom step size[select]'), (b'choice', b'Choice [radio]'), (b'choice-freeform', b'Choice with a freeform option [radio]'), (b'choice-multiple', b'Multiple-Choice, Multiple-Answers [checkbox]'), (b'choice-multiple-freeform', b'Multiple-Choice, Multiple-Answers, plus freeform [checkbox, input]'), (b'choice-multiple-freeform-options', b'Multiple-Choice with Options, Multiple-Answers, plus freeform [checkbox, input]'), (b'open-multiple-composition', b'Composed variables, multiple answers, open value'), (b'location', b'Geographical Location [selects]'), (b'open-multiple', b'Multiple answers, open value'), (b'numeric', b'Numeric'), (b'open', b'Open Answer, single line [input]'), (b'open-validated', b'Open Validated Answer, single line validated with a regex[input]'), (b'open-button', b'Open Answer, single line [input] with a button to validate'), (b'open-textfield', b'Open Answer, multi-line [textarea]'), (b'choice-yesno', b'Yes/No Choice [radio]'), (b'choice-yesnodontknow', b"Yes/No/Don't know Choice [radio]"), (b'datepicker', b'Date choice'), (b'email', b'Email Address [input]'), (b'url', b'Url Address [input]'), (b'open-location', b'Open Answer, with Location suggestion'), (b'comment', b'Comment Only'), (b'sameas', b'Same as Another Question (put question number (alone) in checks')], help_text="Determines the means of answering the question. An open question gives the user a single-line textfield, multiple-choice gives the user a number of choices he/she can choose from. If a question is multiple-choice, enter the choices this user can choose from below'.", max_length=32, verbose_name='Type of question'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='preview_fingerprint',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preview_questionnaire', to='fingerprint.Fingerprint'),
        ),
    ]