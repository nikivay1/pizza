# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20170818_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='availablestreet',
            name='keywords',
            field=models.TextField(default='', verbose_name='keywords'),
        ),
    ]
