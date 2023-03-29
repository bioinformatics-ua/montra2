# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taskqueue.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input', models.FileField(blank=True, max_length=1000, null=True, upload_to=taskqueue.models.inputHash)),
                ('output', models.FileField(blank=True, max_length=1000, null=True, upload_to=taskqueue.models.outputHash)),
                ('output_name', models.CharField(blank=True, max_length=300, null=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.CharField(blank=True, max_length=2000, null=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(0, b'Job has started'), (1, b'Job is being processed'), (2, b'Job has finished'), (-1, b'Job has failed execution')], default=0)),
                ('progress', models.IntegerField(default=0)),
                ('runner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]