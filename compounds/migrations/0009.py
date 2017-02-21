# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('compounds', '0008'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompoundInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('signed_off_date', models.DateTimeField(null=True, blank=True)),
                ('locked', models.BooleanField(default=False, help_text=b'Check the box and save to lock the entry. Uncheck and save to enable editing.')),
                ('lot', models.CharField(max_length=255)),
                ('receipt_date', models.DateField(null=True, blank=True)),
                ('compound', models.ForeignKey(to='compounds.Compound')),
                ('created_by', models.ForeignKey(related_name='compoundinstance_created_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='compoundinstance_modified_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('signed_off_by', models.ForeignKey(related_name='compoundinstance_signed_off_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompoundSupplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('signed_off_date', models.DateTimeField(null=True, blank=True)),
                ('locked', models.BooleanField(default=False, help_text=b'Check the box and save to lock the entry. Uncheck and save to enable editing.')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('created_by', models.ForeignKey(related_name='compoundsupplier_created_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='compoundsupplier_modified_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('signed_off_by', models.ForeignKey(related_name='compoundsupplier_signed_off_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='compoundinstance',
            name='supplier',
            field=models.ForeignKey(to='compounds.CompoundSupplier', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='compoundinstance',
            unique_together=set([('compound', 'supplier', 'lot', 'receipt_date')]),
        ),
    ]
