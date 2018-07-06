# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-26 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assayimagesetting',
            name='color_mapping',
            field=models.CharField(blank=True, default=b'', max_length=255),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='label_description',
            field=models.CharField(blank=True, default=b'', max_length=500),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='label_id',
            field=models.CharField(blank=True, default=b'', max_length=40),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='notes',
            field=models.CharField(blank=True, default=b'', max_length=500),
        ),
    ]
