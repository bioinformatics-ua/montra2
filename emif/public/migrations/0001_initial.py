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
    ]

    operations = [
        migrations.CreateModel(
            name='PublicFingerprintShare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('expiration_date', models.DateTimeField()),
                ('remaining_views', models.IntegerField()),
                ('fingerprint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fingerprint.Fingerprint')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
