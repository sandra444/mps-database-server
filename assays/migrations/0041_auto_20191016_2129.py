# Generated by Django 2.1.9 on 2019-10-17 01:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0040_auto_20191016_1738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assayplatereadermapitem',
            old_name='sample_location',
            new_name='location',
        ),
        migrations.RenameField(
            model_name='assayplatereadermapitem',
            old_name='sample_replicate',
            new_name='replicate',
        ),
    ]
