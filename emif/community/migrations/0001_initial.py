# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-19 11:45
from __future__ import unicode_literals

import community.models
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=5000, null=True)),
                ('disclaimer', models.CharField(blank=True, max_length=5000, null=True)),
                ('short_desc', models.CharField(max_length=200)),
                ('public', models.BooleanField(default=False)),
                ('auto_accept', models.BooleanField(default=False)),
                ('membership', models.CharField(choices=[(b'open', b'open'), (b'public', b'public'), (b'moderated', b'moderated'), (b'invitation', b'invitation')], default=b'moderated', max_length=100)),
                ('slug', models.CharField(max_length=50)),
                ('icon', django_resized.forms.ResizedImageField(blank=True, null=True, upload_to=community.models.iconHash)),
                ('thumbnail', django_resized.forms.ResizedImageField(blank=True, null=True, upload_to=community.models.iconThumbnail)),
                ('sortid', models.IntegerField(default=0)),
                ('show_popchar', models.BooleanField(default=True)),
                ('show_docs', models.BooleanField(default=True)),
                ('popchar_sortid', models.IntegerField(default=0)),
                ('docs_sortid', models.IntegerField(default=0)),
                ('db_sortid', models.IntegerField(default=0)),
                ('dblist_sortid', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['sortid', 'id'],
                'verbose_name_plural': 'Communities',
            },
        ),
        migrations.CreateModel(
            name='CommunityActivation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(default=community.models.randomHash, max_length=32)),
                ('used', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityDatabasePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityFields',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sortid', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('removed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('export_dblist', models.BooleanField(default=True)),
                ('export_fingerprint', models.BooleanField(default=True)),
                ('export_datatable', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityPlugins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sortid', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CommunityUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, b'Waiting approval in community'), (1, b'Enabled in community'), (2, b'Enabled, but with restricted access to certain databases'), (3, b'Blocked by community owner')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PluginPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allow', models.BooleanField(default=False)),
                ('communitygroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityGroup')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionSetAccessGroups',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('can_read', models.BooleanField(default=True)),
                ('can_write', models.BooleanField(default=True)),
                ('communitygroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityGroup')),
                ('qset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questionnaire.QuestionSet')),
            ],
        ),
    ]
