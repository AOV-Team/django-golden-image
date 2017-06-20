# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-24 21:06
# Modified by Martin Ronquillo to add PostGIS extension
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0006_auto_20161223_0718'),
    ]

    operations = [
        CreateExtension('postgis'),
        migrations.RemoveField(
            model_name='photo',
            name='modified_at',
        ),
        migrations.AddField(
            model_name='photo',
            name='coordinates',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]