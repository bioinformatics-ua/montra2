# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questionnaire', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
        ('developer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pluginpermission',
            name='plugin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.Plugin'),
        ),
        migrations.AddField(
            model_name='communityuser',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AddField(
            model_name='communityuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='communityplugins',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AddField(
            model_name='communityplugins',
            name='plugin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='developer.Plugin'),
        ),
        migrations.AddField(
            model_name='communitypermissions',
            name='community',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='members',
            field=models.ManyToManyField(to='community.CommunityUser'),
        ),
        migrations.AddField(
            model_name='communityfields',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.Community'),
        ),
        migrations.AddField(
            model_name='communityfields',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.Question'),
        ),
        migrations.AddField(
            model_name='communitydatabasepermission',
            name='communitygroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityGroup'),
        ),
    ]
