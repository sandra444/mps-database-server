# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalunits',
            name='unit_type',
            field=models.ForeignKey(default=8, to='assays.UnitType'),
            preserve_default=False,
        ),
    ]
