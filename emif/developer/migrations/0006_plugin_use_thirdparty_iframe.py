# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-12-01 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer', '0005_plugin_plugin_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='use_thirdparty_iframe',
            field=models.BooleanField(default=False),
        ),
    ]
