# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-09 14:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0005_auto_20170709_1356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='comment',
        ),
    ]
