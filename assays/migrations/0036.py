# Generated by Django 2.1.11 on 2019-08-12 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assaysetupcell',
            options={'ordering': ('addition_time', 'cell_sample__cell_type__name', 'cell_sample', 'addition_location__name', 'biosensor__name', 'density', 'density_unit__name', 'passage')},
        ),
        migrations.AlterModelOptions(
            name='assaysetupcompound',
            options={'ordering': ('addition_time', 'compound_instance__compound__name', 'addition_location__name', 'concentration_unit__scale_factor', 'concentration', 'concentration_unit__name', 'duration')},
        ),
        migrations.AlterModelOptions(
            name='assaysetupsetting',
            options={'ordering': ('addition_time', 'setting__name', 'addition_location__name', 'unit__name', 'value', 'duration')},
        ),
        migrations.AlterField(
            model_name='assaychipreadout',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaychipreadout',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assaychipsetup',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaychipsetup',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assaychiptestresult',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaychiptestresult',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assaydatafileupload',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaydataupload',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaydataupload',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assayfailurereason',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaylayout',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaylayout',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaymeasurementtype',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaymodel',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaymodeltype',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayplatereadout',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayplatereadout',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assayplatesetup',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayplatesetup',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assayplatetestresult',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayplatetestresult',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assayqualityindicator',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayreader',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayreference',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayresultfunction',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayresulttype',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayrun',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assayrun',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box and save to restrict *Access* to the Groups selected below. *Access* is granted to *Collaborator Group(s)*, without sign off, and to *Access Group(s)* after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study. Uncheck and save to allow *Public Access*.'),
        ),
        migrations.AlterField(
            model_name='assaysamplelocation',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaysetting',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaystudyconfiguration',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaystudyset',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaysupplier',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='assaywelltype',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
        migrations.AlterField(
            model_name='unittype',
            name='locked',
            field=models.BooleanField(default=False, help_text='Check the box and save to block automatic migration to *Public Access*, 1-year after sign off. Uncheck and save to enable automatic migration to *Public Access*, 1-year after sign off. While this is checked, automatic approvals for Stakeholders are also prevented.', verbose_name='Keep Private Indefinitely (Locked)'),
        ),
    ]
