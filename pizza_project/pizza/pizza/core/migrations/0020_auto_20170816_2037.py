# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-16 17:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170816_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(default='', max_length=1024, verbose_name='title')),
                ('text', models.TextField(default='', verbose_name='text')),
            ],
            options={
                'db_tablespace': '',
                'verbose_name': 'action Translation',
                'default_permissions': (),
                'db_table': 'core_action_translation',
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='action',
            name='text',
        ),
        migrations.RemoveField(
            model_name='action',
            name='title',
        ),
        migrations.AddField(
            model_name='actiontranslation',
            name='master',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='core.Action'),
        ),
        migrations.AlterUniqueTogether(
            name='actiontranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
