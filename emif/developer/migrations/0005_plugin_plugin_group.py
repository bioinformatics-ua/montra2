# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-12-01 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer', '0004_auto_20190601_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='plugin_group',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
