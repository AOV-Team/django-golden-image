# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-11-02 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0018_auto_20180720_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photoclassification',
            name='name',
            field=models.CharField(max_length=512),
        ),
    ]
