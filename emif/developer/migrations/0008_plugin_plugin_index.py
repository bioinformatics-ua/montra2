# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-01-26 15:16
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developer', '0007_auto_20201206_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='plugin_index',
            field=models.IntegerField(default=1000, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999)]),
        ),
        migrations.AddField(
            model_name='plugin',
            name='plugin_group_index',
            field=models.IntegerField(default=1000, validators=[django.core.validators.MinValueValidator(0),
                                                                django.core.validators.MaxValueValidator(999)]),
        ),
    ]