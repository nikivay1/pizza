# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 09:35
from __future__ import unicode_literals

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20170817_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='order_phone_notification',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128, verbose_name='phone notification'),
        ),
    ]