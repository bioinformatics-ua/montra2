# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-05-04 19:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0013_auto_20210426_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityjoinform',
            name='required',
            field=models.BooleanField(default=True),
        ),
    ]
