# Generated by Django 2.2.9 on 2020-02-06 22:12

import assays.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assays', '0037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assaymeasurementtype',
            options={'verbose_name': 'Measurement Type'},
        ),
        migrations.AlterModelOptions(
            name='assaymethod',
            options={'verbose_name': 'Method'},
        ),
        migrations.AlterModelOptions(
            name='assayreference',
            options={'verbose_name': 'Reference'},
        ),
        migrations.AlterModelOptions(
            name='assaysamplelocation',
            options={'verbose_name': 'MPS Model Location'},
        ),
        migrations.AlterModelOptions(
            name='assaysetting',
            options={'verbose_name': 'Setting'},
        ),
        migrations.AlterModelOptions(
            name='assaysupplier',
            options={'verbose_name': 'Assay Supplier'},
        ),
        migrations.AlterModelOptions(
            name='assaytarget',
            options={'verbose_name': 'Target'},
        ),
        migrations.AlterModelOptions(
            name='physicalunits',
            options={'ordering': ['unit_type', 'unit'], 'verbose_name': 'Unit'},
        ),
        migrations.AddField(
            model_name='assaystudy',
            name='flow_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Flow Rate (μL/hour)'),
        ),
        migrations.AddField(
            model_name='assaystudy',
            name='number_of_relevant_cells',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of PK Relevant Cells per MPS Model'),
        ),
        migrations.AddField(
            model_name='assaystudy',
            name='pbpk_bolus',
            field=models.BooleanField(default=False, verbose_name='Bolus'),
        ),
        migrations.AddField(
            model_name='assaystudy',
            name='pbpk_steady_state',
            field=models.BooleanField(default=False, verbose_name='Continuous Infusion'),
        ),
        migrations.AddField(
            model_name='assaystudy',
            name='total_device_volume',
            field=models.FloatField(blank=True, null=True, verbose_name='Total Device Volume (μL)'),
        ),
        migrations.AlterField(
            model_name='assaycategory',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaycategory',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaycategory',
            name='targets',
            field=models.ManyToManyField(to='assays.AssayTarget', verbose_name='Targets'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='assay_plate_id',
            field=models.CharField(default='N/A', max_length=255, verbose_name='Assay Plate ID'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='assay_well_id',
            field=models.CharField(default='N/A', max_length=255, verbose_name='Assay Well ID'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='caution_flag',
            field=models.CharField(default='', max_length=255, verbose_name='Caution Flag'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='cross_reference',
            field=models.CharField(default='', max_length=255, verbose_name='Cross Reference'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='data_file_upload',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssayDataFileUpload', verbose_name='Data File Upload'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='excluded',
            field=models.BooleanField(default=False, verbose_name='Excluded'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='matrix_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrixItem', verbose_name='Matrix Item'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='notes',
            field=models.CharField(default='', max_length=255, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='replaced',
            field=models.BooleanField(default=False, verbose_name='Replaced'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='replicate',
            field=models.CharField(default='', max_length=255, verbose_name='Replicate'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='sample_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySampleLocation', verbose_name='Sample Location'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='study_assay',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudyAssay', verbose_name='Study Assay'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='subtarget',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySubtarget', verbose_name='Subtarget'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='time',
            field=models.FloatField(default=0, verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='update_number',
            field=models.IntegerField(default=0, verbose_name='Update Number'),
        ),
        migrations.AlterField(
            model_name='assaydatapoint',
            name='value',
            field=models.FloatField(null=True, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='assay_plate_id',
            field=models.CharField(default='N/A', max_length=255, verbose_name='Assay Plate ID'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='assay_well_id',
            field=models.CharField(default='N/A', max_length=255, verbose_name='Assay Well ID'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='field',
            field=models.CharField(max_length=255, verbose_name='Field'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='field_description',
            field=models.CharField(default='', max_length=500, verbose_name='Field Description'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='file_name',
            field=models.CharField(max_length=255, verbose_name='File Name'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='matrix_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrixItem', verbose_name='Matrix Item'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMethod', verbose_name='Method'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='notes',
            field=models.CharField(default='', max_length=500, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='replicate',
            field=models.CharField(default='', max_length=255, verbose_name='Replicate'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='sample_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySampleLocation', verbose_name='Sample Location'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='setting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayImageSetting', verbose_name='Setting'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='subtarget',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySubtarget', verbose_name='Subtarget'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayTarget', verbose_name='Target'),
        ),
        migrations.AlterField(
            model_name='assayimage',
            name='time',
            field=models.FloatField(verbose_name='Time'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='color_mapping',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Color Mapping'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='label_description',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Label Description'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='label_id',
            field=models.CharField(blank=True, default='', max_length=40, verbose_name='Label ID'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='label_name',
            field=models.CharField(max_length=255, verbose_name='Label Name'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='magnification',
            field=models.CharField(max_length=40, verbose_name='Magnification'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='resolution',
            field=models.CharField(max_length=40, verbose_name='Resolution'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='resolution_unit',
            field=models.CharField(max_length=40, verbose_name='Resolution Unit'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assayimagesetting',
            name='wave_length',
            field=models.CharField(max_length=255, verbose_name='Wave Length'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='microdevices.Microdevice', verbose_name='Device'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='number_of_columns',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of Columns'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='number_of_rows',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of Rows'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='representation',
            field=models.CharField(choices=[('chips', 'Multiple Chips'), ('plate', 'Plate'), ('', '')], max_length=255, verbose_name='Representation'),
        ),
        migrations.AlterField(
            model_name='assaymatrix',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='column_index',
            field=models.IntegerField(verbose_name='Column Index'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='failure_reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssayFailureReason', verbose_name='Failure Reason'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='failure_time',
            field=models.FloatField(blank=True, null=True, verbose_name='Failure Time'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='matrix',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrix', verbose_name='Matrix'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='name',
            field=models.CharField(max_length=512, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='notebook',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Notebook'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='notebook_page',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Notebook Page'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='organ_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='microdevices.OrganModel', verbose_name='MPS Model'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='organ_model_protocol',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='microdevices.OrganModelProtocol', verbose_name='MPS Model Version'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='row_index',
            field=models.IntegerField(verbose_name='Row Index'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='scientist',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Scientist'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='setup_date',
            field=models.DateField(help_text='YYYY-MM-DD', verbose_name='Setup Date'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaymatrixitem',
            name='test_type',
            field=models.CharField(choices=[('', '--------'), ('control', 'Control'), ('compound', 'Treated')], max_length=8, verbose_name='Test Type'),
        ),
        migrations.AlterField(
            model_name='assaymeasurementtype',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaymeasurementtype',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='alt_name',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Alternative Name'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='measurement_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMeasurementType', verbose_name='Measurement Type'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='protocol_file',
            field=models.FileField(blank=True, null=True, upload_to='assays', verbose_name='Protocol File'),
        ),
        migrations.AlterField(
            model_name='assaymethod',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySupplier', verbose_name='Supplier'),
        ),
        migrations.AlterField(
            model_name='assaysamplelocation',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaysamplelocation',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaysetting',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaysetting',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='addition_location',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySampleLocation', verbose_name='Addition Location'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='addition_time',
            field=models.FloatField(blank=True, null=True, verbose_name='Addition Time'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='biosensor',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='cellsamples.Biosensor', verbose_name='Biosensor'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='cell_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cellsamples.CellSample', verbose_name='Cell Sample'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='density_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.PhysicalUnits', verbose_name='Density Unit'),
        ),
        migrations.AlterField(
            model_name='assaysetupcell',
            name='matrix_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrixItem', verbose_name='Matrix Item'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='addition_location',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySampleLocation', verbose_name='Addition Location'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='addition_time',
            field=models.FloatField(blank=True, verbose_name='Addition Time'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='compound_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='compounds.CompoundInstance', verbose_name='Compound Instance'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='concentration',
            field=models.FloatField(verbose_name='Concentration'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='duration',
            field=models.FloatField(blank=True, verbose_name='Duration'),
        ),
        migrations.AlterField(
            model_name='assaysetupcompound',
            name='matrix_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrixItem', verbose_name='Matrix Item'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='addition_location',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySampleLocation', verbose_name='Addition Location'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='addition_time',
            field=models.FloatField(blank=True, verbose_name='Addition Time'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='duration',
            field=models.FloatField(blank=True, verbose_name='Duration'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='matrix_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMatrixItem', verbose_name='Matrix Item'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='setting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssaySetting', verbose_name='Setting'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='unit',
            field=models.ForeignKey(blank=True, default=14, on_delete=django.db.models.deletion.CASCADE, to='assays.PhysicalUnits', verbose_name='Unit'),
        ),
        migrations.AlterField(
            model_name='assaysetupsetting',
            name='value',
            field=models.CharField(max_length=255, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='access_groups',
            field=models.ManyToManyField(blank=True, related_name='study_access_groups', to='auth.Group', verbose_name='Access Groups'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='cell_characterization',
            field=models.BooleanField(default=False, verbose_name='Cell Characterization'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='collaborator_groups',
            field=models.ManyToManyField(blank=True, related_name='study_collaborator_groups', to='auth.Group', verbose_name='Collaborator Groups'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='description',
            field=models.CharField(blank=True, default='', max_length=8000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='disease',
            field=models.BooleanField(default=False, verbose_name='Disease'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='efficacy',
            field=models.BooleanField(default=False, verbose_name='Efficacy'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='studies', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='organ_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='microdevices.OrganModel', verbose_name='MPS Model'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='organ_model_protocol',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='microdevices.OrganModelProtocol', verbose_name='MPS Model Version'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='repro_nums',
            field=models.CharField(blank=True, default='', help_text='Excellent|Acceptable|Poor', max_length=40, verbose_name='Reproducibility'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='restricted',
            field=models.BooleanField(default=True, help_text='Check box to restrict to the Access Groups selected below. Access is granted to access group(s) after Data Group admin and all designated Stakeholder Group admin(s) sign off on the study', verbose_name='Restricted'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='signed_off_notes',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Signed Off Notes'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='start_date',
            field=models.DateField(help_text='YYYY-MM-DD', verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='study_configuration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudyConfiguration', verbose_name='Study Configuration'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='toxicity',
            field=models.BooleanField(default=False, verbose_name='Toxicity'),
        ),
        migrations.AlterField(
            model_name='assaystudy',
            name='use_in_calculations',
            field=models.BooleanField(default=False, verbose_name='Use in Calculations'),
        ),
        migrations.AlterField(
            model_name='assaystudyassay',
            name='method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayMethod', verbose_name='Method'),
        ),
        migrations.AlterField(
            model_name='assaystudyassay',
            name='study',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaystudyassay',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayTarget', verbose_name='Target'),
        ),
        migrations.AlterField(
            model_name='assaystudyassay',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.PhysicalUnits', verbose_name='Unit'),
        ),
        migrations.AlterField(
            model_name='assaystudyreference',
            name='reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayReference', verbose_name='Reference'),
        ),
        migrations.AlterField(
            model_name='assaystudyreference',
            name='reference_for',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Reference For'),
        ),
        migrations.AlterField(
            model_name='assaystudyset',
            name='assays',
            field=models.ManyToManyField(to='assays.AssayStudyAssay', verbose_name='Assays'),
        ),
        migrations.AlterField(
            model_name='assaystudyset',
            name='description',
            field=models.CharField(blank=True, default='', max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaystudyset',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaystudyset',
            name='studies',
            field=models.ManyToManyField(to='assays.AssayStudy', verbose_name='Studies'),
        ),
        migrations.AlterField(
            model_name='assaystudysetreference',
            name='reference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayReference', verbose_name='Reference'),
        ),
        migrations.AlterField(
            model_name='assaystudysetreference',
            name='reference_for',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudySet', verbose_name='Reference For'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='sign_off_required',
            field=models.BooleanField(default=True, verbose_name='Signed Off Required'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='signed_off_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Signed Off By'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='signed_off_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Signed Off Date'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='signed_off_notes',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Signed Off Notes'),
        ),
        migrations.AlterField(
            model_name='assaystudystakeholder',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaystudysupportingdata',
            name='description',
            field=models.CharField(help_text='Describes the contents of the supporting data file', max_length=1000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaystudysupportingdata',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.AssayStudy', verbose_name='Study'),
        ),
        migrations.AlterField(
            model_name='assaystudysupportingdata',
            name='supporting_data',
            field=models.FileField(help_text='Supporting Data for Study', upload_to=assays.models.study_supporting_data_location, verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='assaysupplier',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaysupplier',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='alt_name',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Alternative Name'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='description',
            field=models.CharField(max_length=2000, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='methods',
            field=models.ManyToManyField(to='assays.AssayMethod', verbose_name='Methods'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='name',
            field=models.CharField(max_length=512, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='assaytarget',
            name='short_name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Short Name'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='availability',
            field=models.CharField(blank=True, default='', help_text='Type a series of strings for indicating where this unit should be listed:\ntest = test results\nreadouts = readouts\ncells = cell samples', max_length=255, verbose_name='Availability'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='base_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assays.PhysicalUnits', verbose_name='Base Unit'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='scale_factor',
            field=models.FloatField(blank=True, null=True, verbose_name='Scale Factor'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='unit',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='physicalunits',
            name='unit_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assays.UnitType', verbose_name='Unit Type'),
        ),
        migrations.AlterField(
            model_name='unittype',
            name='unit_type',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
    ]