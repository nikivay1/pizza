# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-29 12:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20170929_1142'),
        ('users', '0004_appuser_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='manage_location',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='managers', to='core.Location', verbose_name='Manage location'),
        ),
    ]