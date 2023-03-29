# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import questionnaire.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('searchengine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sortid', models.IntegerField()),
                ('value', models.CharField(max_length=1000, verbose_name='Short Value')),
                ('text_en', models.CharField(max_length=2000, verbose_name='Choice Text')),
                ('opt', models.BooleanField(default=True, verbose_name='Has Optional text ?')),
            ],
            options={
                'ordering': ('sortid',),
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(help_text=b'eg. <tt>1</tt>, <tt>2a</tt>, <tt>2b</tt>, <tt>3c</tt><br /> Number is also used for ordering questions.', max_length=255)),
                ('text_en', models.TextField(blank=True)),
                ('type', models.CharField(choices=[(b'choice', b'Choice [radio]'), (b'choice-freeform', b'Choice with a freeform option [radio]'), (b'choice-multiple', b'Multiple-Choice, Multiple-Answers [checkbox]'), (b'choice-multiple-freeform', b'Multiple-Choice, Multiple-Answers, plus freeform [checkbox, input]'), (b'choice-multiple-freeform-options', b'Multiple-Choice with Options, Multiple-Answers, plus freeform [checkbox, input]'), (b'custom', b'Custom'), (b'location', b'Geographical Location [selects]'), (b'numeric', b'Numeric'), (b'open-multiple-composition', b'Composed variables, multiple answers, open value'), (b'open-multiple', b'Multiple answers, open value'), (b'publication', b'Publication'), (b'range', b'Ranged slide with custom step size[select]'), (b'open', b'Open Answer, single line [input]'), (b'open-validated', b'Open Validated Answer, single line validated with a regex[input]'), (b'open-button', b'Open Answer, single line [input] with a button to validate'), (b'open-textfield', b'Open Answer, multi-line [textarea]'), (b'choice-yesno', b'Yes/No Choice [radio]'), (b'choice-yesnodontknow', b"Yes/No/Don't know Choice [radio]"), (b'datepicker', b'Date choice'), (b'email', b'Email Address [input]'), (b'url', b'Url Address [input]'), (b'open-location', b'Open Answer, with Location suggestion'), (b'comment', b'Comment Only'), (b'choice-tabular', b'Tabular - Choice'), (b'timeperiod', b'Time Period [input, select]'), (b'sameas', b'Same as Another Question (put question number (alone) in checks')], help_text="Determines the means of answering the question. An open question gives the user a single-line textfield, multiple-choice gives the user a number of choices he/she can choose from. If a question is multiple-choice, enter the choices this user can choose from below'.", max_length=32, verbose_name='Type of question')),
                ('extra_en', models.CharField(blank=True, help_text='Extra information (use  on question type)', max_length=128, null=True, verbose_name='Extra information')),
                ('checks', models.CharField(blank=True, help_text=b'Additional checks to be performed for this value (space separated)  <br /><br />For text fields, <tt>required</tt> is a valid check.<br />For yes/no choice, <tt>required</tt>, <tt>required-yes</tt>, and <tt>required-no</tt> are valid.<br /><br />If this question is required only if another question\'s answer is something specific, use <tt>requiredif="QuestionNumber,Value"</tt> or <tt>requiredif="QuestionNumber,!Value"</tt> for anything but a specific value.  You may also combine tests appearing in <tt>requiredif</tt> by joining them with the words <tt>and</tt> or <tt>or</tt>, eg. <tt>requiredif="Q1,A or Q2,B"</tt> <br /><br /> If it is a location type question,  reach level can be defined by typing <tt>country</tt>, <tt>adm1</tt> or <tt>adm2</tt>', max_length=128, null=True, verbose_name='Additional checks')),
                ('footer_en', models.TextField(blank=True, help_text=b'Footer rendered below the question interpreted as textile', verbose_name='Footer')),
                ('slug', models.CharField(max_length=128)),
                ('help_text', models.CharField(blank=True, max_length=2255, null=True)),
                ('stats', models.BooleanField(default=False)),
                ('category', models.BooleanField(default=False)),
                ('tooltip', models.BooleanField(default=False, help_text=b'If help text appears in a tooltip')),
                ('visible_default', models.BooleanField(default=False, verbose_name='Comments visible by default')),
                ('mlt_ignore', models.BooleanField(default=False, verbose_name='Ignore on More Like This')),
                ('disposition', models.IntegerField(choices=[(0, b'Vertical'), (1, b'Horizontal'), (2, b'Dropdown')], default=0)),
                ('metadata', models.TextField(blank=True, null=True)),
                ('show_advanced', models.BooleanField(default=True, help_text=b'If question appears in advanced search')),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('redirect_url', models.CharField(default=b'/static/complete.html', help_text=b'URL to redirect to when Questionnaire is complete. Macros: $SUBJECTID, $RUNID, $LANG', max_length=128)),
                ('slug', models.CharField(max_length=128)),
                ('disable', models.CharField(max_length=128)),
            ],
            options={
                'permissions': (('export', 'Can export questionnaire answers'), ('management', 'Management Tools')),
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireWizard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('removed', models.BooleanField(default=False)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Questionnaire')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnareImportFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to=questionnaire.models.fileHash)),
                ('filename', models.CharField(blank=True, max_length=3000, null=True)),
                ('status', models.IntegerField(choices=[(0, b'Questionnaire import started'), (1, b'Questionnaire is being imported'), (2, b'Questionnaire finished importing'), (3, b'Questionnaire import aborted')], default=0)),
                ('uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sortid', models.IntegerField()),
                ('heading', models.CharField(max_length=255)),
                ('checks', models.CharField(blank=True, help_text=b'Current options are \'femaleonly\' or \'maleonly\' and shownif="QuestionNumber,Answer" which takes the same format as <tt>requiredif</tt> for questions.', max_length=128)),
                ('text_en', models.TextField(help_text=b"This is interpreted as Textile: <a href='http://hobix.com/textile/quick.html'>http://hobix.com/textile/quick.html</a>")),
                ('help_text', models.CharField(blank=True, max_length=2255, null=True)),
                ('tooltip', models.BooleanField(default=False, help_text=b'If help text appears in a tooltip')),
                ('show_advanced', models.BooleanField(default=True, help_text=b'If questionset appears in advanced search')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Questionnaire')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSetPermissions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fingerprint_id', models.CharField(max_length=32)),
                ('visibility', models.IntegerField(choices=[(0, b'public'), (1, b'private')])),
                ('allow_printing', models.BooleanField(default=True)),
                ('allow_indexing', models.BooleanField(default=True)),
                ('allow_exporting', models.BooleanField(default=True)),
                ('qs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.QuestionSet')),
            ],
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='qsets',
            field=models.ManyToManyField(related_name='qs_list', to='questionnaire.QuestionSet'),
        ),
        migrations.AddField(
            model_name='question',
            name='questionset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.QuestionSet'),
        ),
        migrations.AddField(
            model_name='question',
            name='slug_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='searchengine.Slugs'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Question'),
        ),
    ]
