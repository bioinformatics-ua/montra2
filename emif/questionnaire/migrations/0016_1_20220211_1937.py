# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0015_auto_20211011_0939'),
    ]

    operations = [
        migrations.RenameField(  # just rename the field so its data can be used to fill the new fingerprint foreign key
            model_name='questionsetpermissions',
            old_name='fingerprint_id',
            new_name='fingerprint_id_old',
        ),
        migrations.AddField(  # first let this field be null
            model_name='questionsetpermissions',
            name='fingerprint',
            field=models.ForeignKey(default=None, null=True, on_delete=models.deletion.CASCADE,
                                    to='fingerprint.Fingerprint'),
            preserve_default=False,
        ),
    ]
