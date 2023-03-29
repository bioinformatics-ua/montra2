# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-04-14 13:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0017_delete_invisible_owners'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitygroup',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='community.Community'),
        ),
        migrations.AlterField(
            model_name='communityuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_users',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
