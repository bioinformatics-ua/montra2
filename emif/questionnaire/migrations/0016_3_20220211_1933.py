# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0016_2_20220210_1319'),
    ]

    operations = [
        migrations.AlterField(  # now that all records have this field filled, remove the null=True constraint
            model_name='questionsetpermissions',
            name='fingerprint',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='fingerprint.Fingerprint'),
        ),
        migrations.AlterField(  # use django's default id field
            model_name='questionsetpermissions',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(  # add public visibility as default
            model_name='questionsetpermissions',
            name='visibility',
            field=models.IntegerField(choices=[(0, b'public'), (1, b'private')], default=0),
        ),
        migrations.RemoveField(
            model_name='questionsetpermissions',
            name='allow_printing',
        ),
        migrations.RemoveField(
            model_name='questionsetpermissions',
            name='fingerprint_id_old',
        ),
        migrations.AlterUniqueTogether(
            name='questionsetpermissions',
            unique_together={('fingerprint', 'qs')},
        ),
    ]
