# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 05:48
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024, verbose_name='header title')),
                ('address', models.CharField(default='', max_length=1024, verbose_name='address')),
                ('address_comment', models.CharField(blank=True, default='', max_length=1024, verbose_name='address comment')),
                ('phone', models.CharField(max_length=512, verbose_name='phone')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
            ],
            options={
                'verbose_name': 'site config',
            },
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=512, verbose_name='name')),
                ('icon', models.ImageField(upload_to=core.utils.upload_path_handler, verbose_name='icon')),
                ('icon_alt', models.CharField(blank=True, default='', max_length=1024, verbose_name='icon alt')),
                ('url', models.CharField(max_length=1024, verbose_name='http link')),
                ('position', models.PositiveIntegerField(default=0, verbose_name='position')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='core.SiteConfiguration')),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'social link',
                'verbose_name_plural': 'social links',
            },
        ),
    ]
