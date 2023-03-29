# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_invisible_owners(apps, schema_editor):
    Community = apps.get_model("community", "Community")
    for comm in Community.objects.all():
        for invis_owner in comm.invisible_owners.all():
            if invis_owner not in comm.owners.all():
                comm.invisible_owners.remove(invis_owner)


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0016_merge_20210520_1510"),
    ]

    operations = [
        migrations.RunPython(delete_invisible_owners),
    ]
