# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-12-04 17:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0010_communityjoinform_communityjoinformreply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communityfields',
            name='icon',
            field=models.CharField(default=b'', max_length=50, null=True),
        ),
    ]
