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
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True)),
                ('latest_date', models.DateField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('deadline', models.DateField(blank=True, null=True)),
                ('requester_position', models.TextField(blank=True, null=True)),
                ('question', models.TextField()),
                ('status', models.TextField()),
                ('databases', models.TextField(default=b'')),
                ('removed', models.BooleanField(default=False)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudyDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('revision', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('file_name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudyMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('documents', models.ManyToManyField(blank=True, default=None, null=True, to='studies.StudyDocument')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_message_sender', to=settings.AUTH_USER_MODEL)),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studies.Study')),
                ('users', models.ManyToManyField(related_name='study_message_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
