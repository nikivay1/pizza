# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 19:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0016_auto_20170818_2200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('position',), 'verbose_name': 'product', 'verbose_name_plural': 'products'},
        ),
    ]
