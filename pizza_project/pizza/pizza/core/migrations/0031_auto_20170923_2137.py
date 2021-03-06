# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-23 18:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_siteconfiguration_notification_is_enabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('name', models.CharField(default='', max_length=512, verbose_name='Name')),
                ('is_active', models.BooleanField(default=False, verbose_name='Is active')),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
            },
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='location',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='config', to='core.Location', verbose_name='Location'),
        ),
    ]
