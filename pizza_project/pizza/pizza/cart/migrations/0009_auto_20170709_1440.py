# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-09 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0008_auto_20170709_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='number',
            field=models.PositiveIntegerField(db_index=True, editable=False, unique=True, verbose_name='number'),
        ),
    ]
