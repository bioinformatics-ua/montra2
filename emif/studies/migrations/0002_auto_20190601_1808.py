# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-01 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studymessage',
            name='documents',
            field=models.ManyToManyField(blank=True, default=None, to='studies.StudyDocument'),
        ),
    ]