# coding=utf-8

from django.db import models
from microdevices.models import Microdevice, OrganModel
from mps.base.models import LockableModel

PHYSICAL_UNIT_TYPES = (
    (u'V', u'Volume'),
    (u'C', u'Concentration'),
    (u'M', u'Mass'),
    (u'T', u'Time'),
    (u'F', u'Frequency'),
    (u'RA', u'Rate'),
    (u'RE', u'Relative'),
    (u'O', u'Other'),
)


class PhysicalUnits(LockableModel):
    unit = models.CharField(max_length=256)
    description = models.CharField(max_length=256,
                                   blank=True, null=True)

    unit_type = models.CharField(default='C',
                                 max_length=2,
                                 choices=PHYSICAL_UNIT_TYPES)

    # verbose_name_plural is used to avoid a double 's' on the model name
    class Meta(object):
        verbose_name_plural = 'Physical Units'
        ordering = ['unit_type', 'unit']

    def __unicode__(self):
        return u'{}'.format(self.unit)


class TimeUnits(LockableModel):
    unit = models.CharField(max_length=16)
    description = models.CharField(max_length=256,
                                   blank=True, null=True)
    unit_order = models.FloatField(verbose_name='Seconds', default=0)

    # this meta class is used to avoid a double 's' on the model name
    class Meta(object):
        verbose_name_plural = 'Time Units'
        ordering = ['unit_order']

    def __unicode__(self):
        return self.unit


class AssayModelType(LockableModel):
    class Meta(object):
        ordering = ('assay_type_name',)

    assay_type_name = models.CharField(max_length=200, unique=True)
    assay_type_description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.assay_type_name


class AssayModel(LockableModel):
    class Meta(object):
        ordering = ('assay_name',)

    assay_name = models.CharField(max_length=200, unique=True)
    assay_type = models.ForeignKey(AssayModelType)
    version_number = models.CharField(max_length=200, verbose_name='Version',
                                      blank=True, null=True)
    assay_description = models.TextField(verbose_name='Description', blank=True,
                                         null=True)
    assay_protocol_file = models.FileField(upload_to='assays',
                                           verbose_name='Protocol File',
                                           null=True, blank=True)

    def __unicode__(self):
        return self.assay_name


class AssayLayoutFormat(LockableModel):
    layout_format_name = models.CharField(max_length=200, unique=True)
    number_of_rows = models.IntegerField()
    number_of_columns = models.IntegerField()
    row_labels = models.CharField(max_length=1000,
                                  help_text=
                                  'Space separated list of unique labels, '
                                  'e.g. "A B C D ..."'
                                  ' Number of items must match'
                                  ' number of columns.''')
    column_labels = models.CharField(max_length=1000,
                                     help_text='Space separated list of unique '
                                               'labels, e.g. "1 2 3 4 ...". '
                                               'Number of items must match '
                                               'number of columns.')

    device = models.ForeignKey(Microdevice)

    class Meta(object):
        ordering = ('layout_format_name',)

    def __unicode__(self):
        return self.layout_format_name


class AssayBaseLayout(LockableModel):
    base_layout_name = models.CharField(max_length=200)
    layout_format = models.ForeignKey(AssayLayoutFormat)

    class Meta(object):
        ordering = ('base_layout_name',)

    def __unicode__(self):
        return self.base_layout_name


class AssayWellType(LockableModel):
    class Meta(object):
        ordering = ('well_type',)

    well_type = models.CharField(max_length=200, unique=True)
    well_description = models.TextField(blank=True, null=True)
    background_color = models.CharField(max_length=20,
                                        help_text='Provide color code or name. '
                                                  'You can pick one from: '
                                                  'http://www.w3schools.com'
                                                  '/html/html_colornames.asp')

    def __unicode__(self):
        return self.well_type

    def colored_display(self):
        """Colored display for admin list view."""

        return ('<span style="background-color: {}; padding: 2px">{}</span>'
                .format(self.background_color, self.well_type))

    colored_display.allow_tags = True


class AssayWell(LockableModel):
    class Meta(object):
        unique_together = [('base_layout', 'row', 'column')]

    base_layout = models.ForeignKey(AssayBaseLayout)
    well_type = models.ForeignKey(AssayWellType)

    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayLayout(LockableModel):
    class Meta(object):
        ordering = ('layout_name',)

    layout_name = models.CharField(max_length=200)
    base_layout = models.ForeignKey(AssayBaseLayout)

    def __unicode__(self):
        return self.layout_name


class AssayTimepoint(models.Model):
    assay_layout = models.ForeignKey(AssayLayout)
    timepoint = models.FloatField(default=0)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayCompound(models.Model):
    assay_layout = models.ForeignKey(AssayLayout)
    compound = models.ForeignKey('compounds.Compound')
    concentration = models.FloatField(default=0)
    concentration_unit = models.CharField(max_length=64, default="μM")
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayReadout(models.Model):
    assay_device_readout = models.ForeignKey('assays.AssayDeviceReadout')
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)
    value = models.FloatField()
    elapsed_time = models.FloatField(default=0)


class ReadoutUnit(LockableModel):
    class Meta(object):
        ordering = ('readout_unit',)
    readout_unit = models.CharField(max_length=512,unique=True)
    description = models.CharField(max_length=512,blank=True,null=True)
    def __unicode__(self):
        return self.readout_unit


class AssayDeviceReadout(LockableModel):
    # Readout data collected from MICROPLATES
    class Meta(object):
        verbose_name = 'Plate Readout'
        ordering = ('assay_device_id', 'assay_name',)

    # the unique readout identifier
    # can be a barcode or a hand written identifier
    assay_device_id = models.CharField(max_length=512,
                                       verbose_name='Device ID/ Barcode')

    cell_sample = models.ForeignKey('cellsamples.CellSample')

    cellsample_density = models.FloatField(verbose_name='density', default=0)

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default="ML",
                                               choices=(('WE', 'cells / well'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    assay_name = models.ForeignKey(AssayModel, verbose_name='Assay', null=True)
    assay_layout = models.ForeignKey(AssayLayout)

    reader_name = models.ForeignKey('assays.AssayReader', verbose_name='Reader')

    readout_unit = models.ForeignKey(ReadoutUnit)
    timeunit = models.ForeignKey(TimeUnits)

    treatment_time_length = models.FloatField(verbose_name='Treatment Duration',
                                              blank=True, null=True)

    assay_start_time = models.DateTimeField(blank=True, null=True)
    readout_start_time = models.DateTimeField(blank=True, null=True)

    notebook = models.CharField(max_length=256, blank=True, null=True)
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, null=True)
    scientist = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='csv', verbose_name='Data File',
                            blank=True, null=True)

    def assay_device_name(self):
        return u'{0}'.format(self.assay_device_id)

    def __unicode__(self):
        return u'{0}'.format(self.assay_device_id)


class AssayReader(LockableModel):
    class Meta(object):
        ordering = ('reader_name',)

    reader_name = models.CharField(max_length=128)
    reader_type = models.CharField(max_length=128)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.reader_name, self.reader_type)


SEVERITY_SCORE = (
    ('-1', 'UNKNOWN'), ('0', 'NEGATIVE'), ('1', '+'), ('2', '+ +'),
    ('3', '+ + +'), ('4', '+ + + +'), ('5', '+ + + + +')
)


POSNEG = (
    ('0', 'Neg'), ('1', 'Pos')
)


class AssayResultFunction(LockableModel):
#   Function for analysis of CHIP RESULTS
    class Meta(object):
        verbose_name = 'Function'
        ordering = ('function_name', )

    function_name = models.CharField(max_length=100, unique=True)
    function_results = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.function_name

class AssayResultType(LockableModel):
#   Result types for CHIP RESULTS
    class Meta(object):
        verbose_name = 'Result type'
        ordering = ('assay_result_type', )

    assay_result_type = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.assay_result_type


class AssayTestResult(LockableModel):
#   Results calculated from Raw Chip Data
    class Meta(object):
        verbose_name = 'Chip Result'
    assay_device_readout = models.ForeignKey('assays.AssayRun',
                                             verbose_name='Chip Study')

    def __unicode__(self):
        return u''


class AssayResult(models.Model):
#   Individual result parameters for CHIP RESULTS used in inline
    assay_result = models.ForeignKey(AssayTestResult,
                                     blank=True,
                                     null=True)

    result_function = models.ForeignKey(AssayResultFunction,
                                        blank=True,
                                        null=True,
                                        verbose_name='Function')

    result = models.CharField(default='1',
                              max_length=8,
                              choices=POSNEG,
                              verbose_name='Pos/Neg?')

    severity = models.CharField(default='-1',
                                max_length=5,
                                choices=SEVERITY_SCORE,
                                verbose_name='Severity',
                                blank=True,
                                null=True)

    result_type = models.ForeignKey(AssayResultType,
                                    blank=True,
                                    null=True,
                                    verbose_name='Measure')

    value = models.FloatField(blank=True, null=True)

    test_unit = models.ForeignKey(PhysicalUnits,
                                  blank=True,
                                  null=True)


class AssayPlateTestResult(LockableModel):
#   Test Results from MICROPLATES
    assay_device_id = models.ForeignKey('assays.AssayDeviceReadout')

    assay_test_time = models.FloatField(verbose_name='Time', blank=True, null=True)

    time_units = models.ForeignKey(TimeUnits, blank=True, null=True)

    result = models.CharField(default='1',
                              max_length=8,
                              choices=POSNEG,
                              verbose_name='Pos/Neg?')

    severity = models.CharField(default='-1',
                                max_length=5,
                                choices=SEVERITY_SCORE,
                                verbose_name='Severity',
                                blank=True,
                                null=True)

    value = models.FloatField(blank=True, null=True)

    value_units = models.ForeignKey(PhysicalUnits, blank=True, null=True)

    def __unicode__(self):
        return u''

types = (
    ('TOX', 'Toxicity'), ('DM', 'Disease'), ('EFF', 'Efficacy')
)

class AssayRun(LockableModel):
    class Meta(object):
        verbose_name = 'Chip Study'
        verbose_name_plural = 'Chip Studies'
        ordering = ('assay_run_id', )

    #help_text subject to change
    center_id = models.ForeignKey('microdevices.MicrophysiologyCenter', verbose_name='Center Name')
    type1 = models.CharField(max_length=13,
                            choices=types, default='TOX',
                            verbose_name='Study Type 1')
    type2 = models.CharField(max_length=13,
                            choices=types,
                            verbose_name='Study Type 2', null=True, blank=True)
    type3 = models.CharField(max_length=13,
                            choices=types,
                            verbose_name='Study Type 3', null=True, blank=True)
    name = models.TextField(default='Study01',verbose_name='Study Name')
    start_date = models.DateTimeField()
    assay_run_id = models.TextField(unique=True, help_text="Standard format 'CenterID-2014-09-15-R1' or '-R001' if numbering studies sequentially")
    description = models.TextField(blank=True, null=True)

    file = models.FileField(upload_to='csv', verbose_name='Batch Data File',
                            blank=True, null=True, help_text='Do not upload until you have made each Chip Readout')

    def __unicode__(self):
        return self.assay_run_id

class AssayChipRawData(models.Model):
    assay_chip_id = models.ForeignKey('assays.AssayChipReadout')
    field_id = models.CharField(max_length=255, default = '0')
    value = models.FloatField(null=True)
    elapsed_time = models.FloatField(default=0)

class AssayChipReadout(LockableModel):
    class Meta(object):
        verbose_name = 'Chip Readout'
        ordering = ('assay_chip_id', 'assay_name',)

    #Control => control, Compound => compound; Abbreviate? Capitalize?
    chip_test_type = models.CharField(max_length=8, choices=(("control","Control"),("compound","Compound")))

    # the unique readout identifier
    # can be a barcode or a hand written identifier
    assay_chip_id = models.CharField(max_length=512,
                                       verbose_name='Chip ID/ Barcode')

    compound = models.ForeignKey('compounds.Compound')
    concentration = models.FloatField(default=0)
    unit = models.ForeignKey('assays.PhysicalUnits',verbose_name='concentration Unit')

    cell_sample = models.ForeignKey('cellsamples.CellSample')

    cellsample_density = models.FloatField(verbose_name='density', default=0)

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default="ML",
                                               choices=(('WE', 'cells / well'),
                                                        ('CP', 'cells / chip'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    assay_name = models.ForeignKey(AssayModel, verbose_name='Assay', null=True)

    type = models.CharField(max_length=13,
                            choices=types,
                            verbose_name='Test Type')

    assay_run_id = models.ForeignKey(AssayRun, verbose_name = 'Assay Study')
    device = models.ForeignKey(OrganModel, verbose_name = 'Chip Model Name')

    reader_name = models.ForeignKey('assays.AssayReader', verbose_name='Reader')

    readout_unit = models.ForeignKey(ReadoutUnit)
    timeunit = models.ForeignKey(TimeUnits)

    treatment_time_length = models.FloatField(verbose_name='Assay Treatment Duration',
                                              blank=True, null=True)

    assay_start_time = models.DateTimeField(blank=True, null=True)
    readout_start_time = models.DateTimeField(blank=True, null=True)

    notebook = models.CharField(max_length=256, blank=True, null=True)
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, null=True)
    scientist = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='csv', verbose_name='Data File',
                            blank=True, null=True, help_text='Green = Data from database; Red = Line that will not be read'
                                                             '; Gray = Reading with null value')

    def assay_chip_name(self):
        return u'{0}'.format(self.assay_chip_id)

    def __unicode__(self):
        return u'Chip-{0}:{1}:{2}'.format(self.assay_chip_id,
                                        self.assay_name,
                                        self.compound)

