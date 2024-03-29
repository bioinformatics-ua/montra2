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
            name='AdvancedQuery',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('title', models.TextField(blank=True, null=True)),
                ('serialized_query_hash', models.TextField()),
                ('serialized_query', models.TextField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('removed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AdvancedQueryAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='InvitePending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_date', models.DateField()),
                ('latest_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='QueryLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('query', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('latest_date', models.DateTimeField(auto_now=True)),
                ('removed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SharePending',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('db_id', models.TextField()),
                ('activation_code', models.TextField()),
                ('pending', models.BooleanField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_invited', to=settings.AUTH_USER_MODEL)),
                ('user_invite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_that_invites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
