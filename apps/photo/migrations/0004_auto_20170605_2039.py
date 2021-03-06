# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-06-06 02:39
from __future__ import unicode_literals

import apps.common.models
from django.db import migrations, models
from django.core.management import call_command


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'categories', app_label='photo')
    call_command('loaddata', 'photo_feeds', app_label='photo')

class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0003_photo_magazine_authorized'),
    ]

    operations = [
        migrations.AddField(
            model_name='photoclassification',
            name='category_image',
            field=models.ImageField(blank=True, null=True, upload_to=apps.common.models.get_classification_background_file_path),
        ),
        migrations.AddField(
            model_name='photoclassification',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to=apps.common.models.get_classification_icon_file_path),
        ),
        # migrations.RunPython(load_fixture),
    ]
