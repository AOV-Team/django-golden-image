# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-05-23 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_user_signup_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gear',
            name='link',
            field=models.URLField(blank=True, max_length=2083, null=True),
        ),
    ]
