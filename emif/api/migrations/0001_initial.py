# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-07 13:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FingerprintAPI',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fingerprintID', models.CharField(max_length=255)),
                ('field', models.TextField()),
                ('value', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
