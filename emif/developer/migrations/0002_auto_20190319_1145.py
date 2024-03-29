# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fingerprint', '0001_initial'),
        ('developer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginfingeprint',
            name='fingerprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fingerprint.Fingerprint'),
        ),
        migrations.AddField(
            model_name='pluginfingeprint',
            name='plugin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.Plugin'),
        ),
        migrations.AddField(
            model_name='plugin',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
