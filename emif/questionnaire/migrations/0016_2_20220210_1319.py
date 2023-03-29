# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2022-02-10 14:52
from __future__ import unicode_literals

from django.db import migrations, models


def fill_new_fingerprint_field_on_question_set_permissions(apps, schema_editor):
    QuestionSetPermissions = apps.get_model("questionnaire", "QuestionSetPermissions")
    QuestionSet = apps.get_model("questionnaire", "QuestionSet")
    Fingerprint = apps.get_model("fingerprint", "Fingerprint")

    to_recreate = {}

    for obj in QuestionSetPermissions.objects.all():
        fingerprint = Fingerprint.objects.filter(fingerprint_hash=obj.fingerprint_id_old)
        if not fingerprint.exists():
            obj.delete()
            continue
        fingerprint = fingerprint.get()

        obj.fingerprint = fingerprint
        obj.save()

        # lets check if there other records regarding the same fingerprint + question set exist
        others = QuestionSetPermissions.objects.filter(fingerprint=fingerprint, qs=obj.qs)
        if others.count() > 1:
            # if they exist, save their values to later create a single record of
            #  such fingerprint + question set association.
            # if different records have different values, use the most restrict ones.

            visibility = 0
            allow_indexing = True
            allow_exporting = True
            for other in others:
                visibility = other.visibility if other.visibility else visibility
                allow_indexing = allow_indexing and other.allow_indexing
                allow_exporting = allow_exporting and other.allow_exporting

            to_recreate[(fingerprint.id, obj.qs.id)] = (visibility, allow_indexing, allow_exporting)

    for (fingerprint_id, qs_id), (visibility, allow_indexing, allow_exporting) in to_recreate.items():
        QuestionSetPermissions.objects.filter(
            fingerprint__id=fingerprint_id,
            qs__id=qs_id,
        ).delete()

        QuestionSetPermissions.objects.create(
            fingerprint=Fingerprint.objects.get(id=fingerprint_id),
            qs=QuestionSet.objects.get(id=qs_id),
            visibility=visibility,
            allow_indexing=allow_indexing,
            allow_exporting=allow_exporting,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0016_1_20220211_1937'),
    ]

    operations = [
        migrations.RunPython(fill_new_fingerprint_field_on_question_set_permissions),
    ]
