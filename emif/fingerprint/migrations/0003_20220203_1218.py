# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fingerprint', '0002_auto_20190601_1808'),
    ]

    operations = [
        migrations.RunSQL("DELETE FROM fingerprint_fingerprintpending WHERE pending=FALSE"),
        migrations.RemoveField(
            model_name='fingerprintpending',
            name='id',
        ),
        migrations.RemoveField(
            model_name='fingerprintpending',
            name='pending',
        ),
        migrations.AlterField(
            model_name='fingerprintpending',
            name='fingerprint',
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to='fingerprint.Fingerprint',
            ),
        ),
    ]
