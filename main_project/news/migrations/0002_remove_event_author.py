# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-20 14:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='author',
        ),
    ]
