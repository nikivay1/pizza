# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-09 15:32
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20170709_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sociallink',
            name='icon',
            field=models.ImageField(upload_to=core.utils.upload_path_handler, verbose_name='icon'),
        ),
    ]
