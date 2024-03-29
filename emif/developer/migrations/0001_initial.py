# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

import developer.models
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.CharField(max_length=100, unique=True)),
                ('type', models.IntegerField(choices=[(0, b'Global plugin, for the main dashboard'), (1, b'Database related plugin, for the database view'), (3, b'Full-fledged application widget'), (2, b'Third party full-fledged applications')], default=0)),
                ('icon', django_resized.forms.ResizedImageField(blank=True, null=True, upload_to=developer.models.iconHash)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('latest_update', models.DateTimeField(auto_now=True)),
                ('removed', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PluginFingeprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empty', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PluginVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_remote', models.BooleanField(default=False)),
                ('path', models.TextField()),
                ('version', models.IntegerField()),
                ('approved', models.BooleanField(default=False)),
                ('submitted', models.BooleanField(default=False)),
                ('submitted_desc', models.TextField(blank=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('latest_update', models.DateTimeField(auto_now=True)),
                ('removed', models.BooleanField(default=False)),
                ('plugin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.Plugin')),
            ],
            options={
                'ordering': ['-version'],
                'verbose_name_plural': 'Plugin versions waiting for approval',
            },
        ),
        migrations.CreateModel(
            name='VersionDep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('revision', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('filename', models.CharField(max_length=255)),
                ('size', models.FloatField(default=0)),
                ('removed', models.BooleanField()),
                ('pluginversion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.PluginVersion')),
            ],
            options={
                'ordering': ['-latest_date'],
            },
        ),
    ]
