# Generated by Django 2.1.9 on 2019-10-17 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0041_auto_20191016_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='assayplatereadermapitem',
            name='plate_index',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
