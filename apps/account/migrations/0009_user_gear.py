# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-03 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20170103_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gear',
            field=models.ManyToManyField(blank=True, to='account.Gear'),
        ),
    ]
