# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-27 22:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('push_notifications', '0002_auto_20160106_0850'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('send_at', models.DateTimeField()),
                ('device', models.ManyToManyField(blank=True, help_text='iOS devices to send message to. Message will be sent to all devices if empty', to='push_notifications.APNSDevice', verbose_name='devices')),
            ],
        ),
    ]
