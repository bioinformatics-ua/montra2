# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-16 14:34
from __future__ import unicode_literals

from django.db import migrations, models
import questionnaire.models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0004_auto_20190516_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='location',
            field=models.CharField(blank=True, default=b'', max_length=128),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='logo',
            field=models.ImageField(blank=True, default=b'', upload_to=questionnaire.models.questionnaire_logo_directory_path),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='long_description',
            field=models.CharField(blank=True, default=b'', max_length=512),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='short_description',
            field=models.CharField(blank=True, default=b'', max_length=128),
        ),
    ]
