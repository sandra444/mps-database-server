# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microdevices', '0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organmodel',
            name='center',
            field=models.ForeignKey(default=1, to='microdevices.MicrophysiologyCenter'),
            preserve_default=False,
        ),
    ]
