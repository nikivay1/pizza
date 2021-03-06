# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-09 13:56
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20170708_0915'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='slug name')),
                ('text', models.TextField(default='', verbose_name='text')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_templates', to='core.SiteConfiguration')),
            ],
            options={
                'verbose_name': 'sms template',
                'verbose_name_plural': 'sms templates',
            },
        ),
        migrations.AlterField(
            model_name='sociallink',
            name='icon',
            field=models.ImageField(upload_to=core.utils.upload_path_handler, verbose_name='icon'),
        ),
    ]
