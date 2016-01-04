# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='physicalunits',
            name='unit_type_fk',
            field=models.ForeignKey(to='assays.UnitType', null=True),
            preserve_default=True,
        ),
    ]
