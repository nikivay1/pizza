# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 19:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_auto_20170816_2109'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['position'], 'verbose_name': 'product', 'verbose_name_plural': 'products'},
        ),
        migrations.AddField(
            model_name='product',
            name='position',
            field=models.PositiveIntegerField(default=0, verbose_name='position'),
        ),
    ]
