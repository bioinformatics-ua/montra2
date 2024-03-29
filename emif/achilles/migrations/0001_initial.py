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
    ]

    operations = [
        migrations.CreateModel(
            name='Datasource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fingerprint_id', models.CharField(max_length=255, unique=True)),
                ('datasource_url', models.URLField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('progress', models.IntegerField(choices=[(0, b'completed'), (1, b'processing'), (2, b'not_started'), (3, b'error'), (4, b'reverting')], default=2)),
                ('revision', models.IntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DatasourceZip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fingerprint_id', models.CharField(max_length=255, unique=True)),
                ('total_files', models.IntegerField(default=1)),
                ('extracted_files', models.IntegerField(default=0)),
            ],
        ),
    ]
