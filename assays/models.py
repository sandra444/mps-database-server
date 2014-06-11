# coding=utf-8

from django.db import models
from microdevices.models import Microdevice
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
    assay_type_name = models.CharField(max_length=200, unique=True)
    assay_type_description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.assay_type_name


class AssayModel(LockableModel):
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
                                  ' number of columns.')
    column_labels = models.CharField(max_length=1000,
                                     help_text='Space separated list of unique '
                                               'labels, e.g. "1 2 3 4 ...". '
                                               'Number of items must match '
                                               'number of columns.')

    device = models.ForeignKey(Microdevice)

    def __unicode__(self):
        return self.layout_format_name


class AssayBaseLayout(LockableModel):
    base_layout_name = models.CharField(max_length=200)
    layout_format = models.ForeignKey(AssayLayoutFormat)

    def __unicode__(self):
        return self.base_layout_name


class AssayWellType(LockableModel):
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


class AssayTest(LockableModel):
    """

    The AssayTest model contains both the Cell Characterization results
    (not the raw readouts) and the MPS device results

    """

    assay_device_id = models.CharField(max_length=512,
                                       verbose_name='Device ID/ Barcode')
    microdevice = models.ForeignKey('microdevices.Microdevice',
                                    verbose_name='Model Name')
    assay_layout = models.ForeignKey(AssayLayout)
    reader_name = models.ForeignKey('assays.AssayReader', verbose_name='Reader')
    cell_sample = models.ForeignKey('cellsamples.CellSample')
    compound = models.ForeignKey('compounds.Compound', null=True, blank=True)
    test_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.assay_device_id)


class AssayResult(LockableModel):
    assay_test = models.ForeignKey(AssayTest)

    test_name = models.ForeignKey('drugtrials.Test',
                                  verbose_name='Test',
                                  blank=True,
                                  null=True)

    test_time = models.FloatField(verbose_name='Time',
                                  blank=True, null=True)

    time_units = models.ForeignKey(TimeUnits,
                                   blank=True,
                                   null=True)

    value = models.FloatField(blank=True, null=True)

    test_unit = models.ForeignKey(PhysicalUnits,
                                  blank=True,
                                  null=True)


class AssayDeviceReadout(LockableModel):
    # the unique readout identifier
    # can be a barcode or a hand written identifier
    assay_device_id = models.CharField(max_length=512,
                                       verbose_name='Device ID/ Barcode')

    cell_sample = models.ForeignKey('cellsamples.CellSample')
    organ_name = models.ForeignKey('cellsamples.Organ', verbose_name='Organ',
                                   null=True)
    cellsample_density = models.FloatField(verbose_name='density', default=0)

    # Cell samples
    #
    # Option 1 is cells / well
    # Option 2 is cells / mL
    # Option 3 is cells / mm^2

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default="ML",
                                               choices=(('WE', 'cells / well'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    assay_name = models.ForeignKey(AssayModel, verbose_name='Assay', null=True)
    assay_layout = models.ForeignKey(AssayLayout)
    microdevice = models.ForeignKey('microdevices.Microdevice',
                                    verbose_name='Assay Device')
    reader_name = models.ForeignKey('assays.AssayReader', verbose_name='Reader')

    readout_unit = models.CharField(default='RFU',
                                    max_length=16,
                                    choices=(('RFU', 'RFU'),
                                             ('RLU', 'RLU'),
                                             ('Absorbance', 'Absorbance')))

    READOUT_CHOICES = ((u'E', u'Endpoint'), (u'K', u'Kinetic'))

    readout_type = models.CharField(default='E',
                                    max_length=2,
                                    choices=READOUT_CHOICES)

    timeunit = models.ForeignKey(TimeUnits)

    treatment_time_length = models.FloatField(verbose_name='Treatment Duration',
                                              blank=True, null=True)

    timepoint = models.FloatField(verbose_name='End time', blank=True,
                                  null=True,
                                  help_text='Leave blank if using Kinetic type')

    time_interval = models.FloatField(blank=True, null=True)

    assay_timestamp = models.DateTimeField(auto_now_add=True, blank=True,
                                           null=True)

    readout_timestamp = models.DateTimeField(auto_now_add=True, blank=True,
                                             null=True)

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
    reader_name = models.CharField(max_length=128)
    reader_type = models.CharField(max_length=128)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.reader_name, self.reader_type)

