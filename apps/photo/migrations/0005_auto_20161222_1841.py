# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-23 01:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0004_auto_20161216_1814'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'default_permissions': ('add', 'change', 'delete', 'view')},
        ),
        migrations.AlterModelOptions(
            name='photoclassification',
            options={'default_permissions': ('add', 'change', 'delete', 'view')},
        ),
        migrations.AlterModelOptions(
            name='photofeed',
            options={'default_permissions': ('add', 'change', 'delete', 'view')},
        ),
    ]
