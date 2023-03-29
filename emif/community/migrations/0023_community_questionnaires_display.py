# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-03-22 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0022_auto_20220223_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='questionnaires_display',
            field=models.CharField(choices=[(b'list', b'List view'), (b'card', b'Card view')], default=b'list', max_length=4),
        ),
    ]