# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

from django.db import migrations


def migrate(apps, schema_editor):
    SocialApp = apps.get_model("socialaccount", "SocialApp")
    try:
        social_app = SocialApp.objects.get(provider="elixir_aai")
    except SocialApp.DoesNotExist:
        pass
    else:
        social_app.name = "Life Science"
        social_app.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.RunPython(migrate)
    ]
