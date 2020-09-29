# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-08 09:15
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170708_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='schedule',
            field=models.CharField(blank=True, default='', max_length=1024, verbose_name='schedule'),
        ),
        migrations.AlterField(
            model_name='sociallink',
            name='icon',
            field=models.ImageField(upload_to=core.utils.upload_path_handler, verbose_name='icon'),
        ),
    ]