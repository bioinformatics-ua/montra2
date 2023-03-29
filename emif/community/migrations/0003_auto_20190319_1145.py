# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tag', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fingerprint', '0001_initial'),
        ('community', '0002_auto_20190319_1145'),
        ('questionnaire', '0001_initial'),
        ('developer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitydatabasepermission',
            name='database',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fingerprint.Fingerprint'),
        ),
        migrations.AddField(
            model_name='communitydatabasepermission',
            name='plugin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.Plugin'),
        ),
        migrations.AddField(
            model_name='communityactivation',
            name='commuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityUser'),
        ),
        migrations.AddField(
            model_name='community',
            name='invisible_owners',
            field=models.ManyToManyField(blank=True, related_name='invisible', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='community',
            name='list_fields',
            field=models.ManyToManyField(through='community.CommunityFields', to='questionnaire.Question'),
        ),
        migrations.AddField(
            model_name='community',
            name='owners',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='community',
            name='plugins',
            field=models.ManyToManyField(through='community.CommunityPlugins', to='developer.Plugin'),
        ),
        migrations.AddField(
            model_name='community',
            name='questionnaires',
            field=models.ManyToManyField(blank=True, to='questionnaire.Questionnaire'),
        ),
        migrations.AddField(
            model_name='community',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tag.Tag'),
        ),
    ]
