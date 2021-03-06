# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-29 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20170929_1120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smstemplate',
            name='config',
        ),
        migrations.RemoveField(
            model_name='sociallink',
            name='config',
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='order_phone_notification_number',
            field=models.CharField(blank=True, default='', max_length=16, verbose_name='phone notification'),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='order_telegram_notification_channel',
            field=models.CharField(blank=True, default='', max_length=16, verbose_name='telegram notification'),
        ),
    ]
