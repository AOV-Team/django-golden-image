# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-09-14 20:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communication', '0007_auto_20180914_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('message_count', models.PositiveIntegerField()),
                ('participants', models.ManyToManyField(related_name='participants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DirectMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('index', models.PositiveIntegerField()),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation', to='communication.Conversation')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Direct Messages',
            },
        ),
    ]
