# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-06 06:34
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_favoriteproduct_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='icon',
            field=models.FileField(upload_to=core.utils.upload_path_handler, verbose_name='icon'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to=core.utils.upload_path_handler, verbose_name='image'),
        ),
    ]
