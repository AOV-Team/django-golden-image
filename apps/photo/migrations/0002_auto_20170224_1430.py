# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-24 21:30
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial_squashed_0010_auto_20170210_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photofeed',
            name='photo_limit',
            field=models.IntegerField(blank=True, help_text='Leave blank for unlimited.', null=True, validators=[django.core.validators.MaxValueValidator(9999)], verbose_name='max photos to display'),
        ),
    ]
