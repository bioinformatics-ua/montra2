# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-01 18:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer', '0003_auto_20190601_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versiondep',
            name='removed',
            field=models.BooleanField(default=False),
        ),
    ]
