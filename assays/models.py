# coding=utf-8

from django.db import models
from microdevices.models import Microdevice, OrganModel, OrganModelProtocol, MicrophysiologyCenter
# from mps.base.models import LockableModel, RestrictedModel, FlaggableModel
from mps.base.models import LockableModel, FlaggableModel
from django.contrib.auth.models import Group

import urllib
import collections

# TODO MAKE MODEL AND FIELD NAMES MORE CONSISTENT/COHERENT

# TODO DEPRECATED, REMOVE SOON
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

types = (
    ('TOX', 'Toxicity'), ('DM', 'Disease'), ('EFF', 'Efficacy'), ('CC', 'Cell Characterization')
)

# This shouldn't be repeated like so
# Converts: days -> minutes, hours -> minutes, minutes->minutes
TIME_CONVERSIONS = [
    ('day', 1440),
    ('hour', 60),
    ('minute', 1)
]

TIME_CONVERSIONS = collections.OrderedDict(TIME_CONVERSIONS)


# TODO EMPLOY THIS FUNCTION ELSEWHERE
def get_split_times(time_in_minutes):
    """Takes time_in_minutes and returns a dic with the time split into day, hour, minute"""
    times = {
        'day': 0,
        'hour': 0,
        'minute': 0
    }
    time_in_minutes_remaining = time_in_minutes
    for time_unit, conversion in TIME_CONVERSIONS.items():
        initial_time_for_current_field = int(time_in_minutes_remaining / conversion)
        if initial_time_for_current_field:
            times[time_unit] = initial_time_for_current_field
            time_in_minutes_remaining -= initial_time_for_current_field * conversion
    # Add fractions of minutes if necessary
    if time_in_minutes_remaining:
        times['minute'] += time_in_minutes_remaining

    return times


# May be moved
def get_center_id(group_id):
    """Get a center ID from a group ID"""
    data = {}

    try:
        center_data = MicrophysiologyCenter.objects.filter(groups__id=group_id)[0]

        data.update({
            'center_id': center_data.center_id,
            'center_name': center_data.center_name,
        })

    except:
        data.update({
            'center_id': '',
            'center_name': '',
        })

    return data


class UnitType(LockableModel):
    """Unit types for physical units"""

    unit_type = models.CharField(max_length=100)
    description = models.CharField(max_length=256,
                                   blank=True, default='')

    def __unicode__(self):
        return u'{}'.format(self.unit_type)


# TODO THIS NEEDS TO BE REVISED (IDEALLY REPLACED WITH PHYSICALUNIT BELOW)
class PhysicalUnits(LockableModel):
    """Measures of concentration and so on"""

    # USE NAME IN LIEU OF UNIT (unit.unit is confusing and dumb)
    # name = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    description = models.CharField(max_length=255,
                                   blank=True, default='')

    unit_type = models.ForeignKey(UnitType)

    # Base Unit for conversions and scale factor
    base_unit = models.ForeignKey('assays.PhysicalUnits',
                                  blank=True,
                                  null=True)

    # Scale factor gives the conversion to get to the base unit, can also act to sort
    scale_factor = models.FloatField(blank=True,
                                     null=True)

    availability = models.CharField(max_length=255,
                                    blank=True,
                                    default='',
                                    help_text=(u'Type a series of strings for indicating '
                                               u'where this unit should be listed:'
                                               u'\ntest = test results\nreadouts = readouts\ncells = cell samples'))

    # verbose_name_plural is used to avoid a double 's' on the model name
    class Meta(object):
        verbose_name_plural = 'Physical Units'
        ordering = ['unit_type', 'unit']

    def __unicode__(self):
        return u'{}'.format(self.unit)


class AssayModelType(LockableModel):
    """Defines the type of an ASSAY (biochemical, mass spec, and so on)"""

    class Meta(object):
        ordering = ('assay_type_name',)

    assay_type_name = models.CharField(max_length=200, unique=True)
    assay_type_description = models.TextField(blank=True, default='')

    def __unicode__(self):
        return self.assay_type_name


class AssayModel(LockableModel):
    """Defines an ASSAY such as albumin, BUN, and so on"""

    class Meta(object):
        ordering = ('assay_name',)

    assay_name = models.CharField(max_length=200, unique=True)

    # Remember, adding a unique field to existing entries needs to be null during migration
    assay_short_name = models.CharField(max_length=10, default='', unique=True)

    assay_type = models.ForeignKey(AssayModelType)
    version_number = models.CharField(max_length=200, verbose_name='Version',
                                      blank=True, default='')
    assay_description = models.TextField(verbose_name='Description', blank=True,
                                         default='')
    assay_protocol_file = models.FileField(upload_to='assays',
                                           verbose_name='Protocol File',
                                           null=True, blank=True)
    test_type = models.CharField(max_length=13,
                                 choices=types,
                                 verbose_name='Test Type')

    def __unicode__(self):
        return u'{0} ({1})'.format(self.assay_name, self.assay_short_name)


# Assay layout is now a flaggable model
class AssayLayout(FlaggableModel):
    """Defines the layout of a PLATE (parent of all associated wells)"""

    class Meta(object):
        verbose_name = 'Assay Layout'
        ordering = ('layout_name',)

    layout_name = models.CharField(max_length=200, unique=True)
    device = models.ForeignKey(Microdevice)

    # Specifies whether this is a standard (oft used layout)
    standard = models.BooleanField(default=False)

    # base_layout = models.ForeignKey(AssayBaseLayout)

    def __unicode__(self):
        return self.layout_name

    def get_post_submission_url(self):
        return '/assays/assaylayout/'

    def get_absolute_url(self):
        return '/assays/assaylayout/{}/'.format(self.id)

    def get_delete_url(self):
        return '/assays/assaylayout/{}/delete/'.format(self.id)


class AssayWellType(LockableModel):
    """PLATE well type

    Includes the color well types appear as in the interface
    """

    class Meta(object):
        ordering = ('well_type',)

    well_type = models.CharField(max_length=200, unique=True)
    well_description = models.TextField(blank=True, default='')
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


class AssayWell(models.Model):
    """An individual PLATE well"""

    class Meta(object):
        unique_together = [('assay_layout', 'row', 'column')]

    # base_layout = models.ForeignKey(AssayBaseLayout)
    assay_layout = models.ForeignKey(AssayLayout)
    well_type = models.ForeignKey(AssayWellType)

    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayWellTimepoint(models.Model):
    """Timepoints for PLATE wells"""
    assay_layout = models.ForeignKey(AssayLayout)
    timepoint = models.FloatField(default=0)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayWellLabel(models.Model):
    """Arbitrary string label for PLATE wells"""
    assay_layout = models.ForeignKey(AssayLayout)
    label = models.CharField(max_length=150)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayCompoundInstance(models.Model):
    """An instance of a compound used in an assay; used as an inline"""

    class Meta(object):
        unique_together = [
            (
                'chip_setup',
                'compound_instance',
                'concentration',
                'concentration_unit',
                'addition_time',
                'duration'
            )
        ]

    # Stop-gap, subject to change
    chip_setup = models.ForeignKey('assays.AssayChipSetup', null=True, blank=True)

    # COMPOUND INSTANCE IS REQUIRED, however null=True was done to avoid a submission issue
    compound_instance = models.ForeignKey('compounds.CompoundInstance', null=True, blank=True)
    concentration = models.FloatField()
    concentration_unit = models.ForeignKey(
        'assays.PhysicalUnits',
        verbose_name='Concentration Unit'
    )

    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    addition_time = models.FloatField(blank=True)

    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    duration = models.FloatField(blank=True)

    def get_addition_time_string(self):
        split_times = get_split_times(self.addition_time)
        return 'D{0} H{1} M{2}'.format(
            split_times.get('day'),
            split_times.get('hour'),
            split_times.get('minute'),
        )

    def get_duration_string(self):
        split_times = get_split_times(self.duration)
        return 'D{0} H{1} M{2}'.format(
            split_times.get('day'),
            split_times.get('hour'),
            split_times.get('minute'),
        )


class AssayWellCompound(models.Model):
    """Compound for PLATE wells"""
    assay_layout = models.ForeignKey(AssayLayout)
    # TO BE DEPRECATED: USE AssayCompoundInstance instead
    compound = models.ForeignKey('compounds.Compound', null=True, blank=True)
    # Null=True temporarily
    assay_compound_instance = models.ForeignKey('assays.AssayCompoundInstance', null=True, blank=True)
    # TO BE DEPRECATED: USE AssayCompoundInstance instead
    concentration = models.FloatField(default=0, null=True, blank=True)
    # TO BE DEPRECATED: USE AssayCompoundInstance instead
    concentration_unit = models.ForeignKey(PhysicalUnits, null=True, blank=True)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayQualityIndicator(LockableModel):
    """AssayQualityIndicators show whether a data point needs to be excluded"""
    # Name of the indicator
    name = models.CharField(max_length=255, unique=True)

    # Short version of the indicator for input in the quality field
    # Theoretically, the code should be a single character, but I will err on the side of caution
    code = models.CharField(max_length=10, unique=True)

    # Description of the indicator (for tooltips)
    description = models.CharField(max_length=2000)

    # Is this necessary? Do we assume that all need to be excluded?
    # exclude = models.BooleanField(default=True)

# TO BE DEPRECATED To be merged into single "AssayCells" model
class AssayPlateCells(models.Model):
    """Individual cell parameters for PLATE setup used in inline"""

    assay_plate = models.ForeignKey('AssayPlateSetup')
    cell_sample = models.ForeignKey('cellsamples.CellSample')
    cell_biosensor = models.ForeignKey('cellsamples.Biosensor')
    cellsample_density = models.FloatField(verbose_name='density', default=0)

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default='WE',
                                               choices=(('WE', 'cells / well'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    cell_passage = models.CharField(max_length=16, verbose_name='Passage#',
                                    blank=True, default='')


# TO BE DEPRECATED To be merged into single "AssaySetup" model
class AssayPlateSetup(FlaggableModel):
    """Setup for MICROPLATES"""

    class Meta(object):
        verbose_name = 'Plate Setup'

    # Might as well be consistent
    assay_run_id = models.ForeignKey('assays.AssayRun', verbose_name='Study')

    # The assay layout is approximately equivalent to a chip's Organ Model
    assay_layout = models.ForeignKey('assays.AssayLayout', verbose_name='Assay Layout')

    setup_date = models.DateField(help_text='YYYY-MM-DD')

    # Plate identifier
    assay_plate_id = models.CharField(max_length=512, verbose_name='Plate ID/ Barcode')

    scientist = models.CharField(max_length=100, blank=True, default='')
    notebook = models.CharField(max_length=256, blank=True, default='')
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, default='')

    def __unicode__(self):
        return u'{}'.format(self.assay_plate_id)

    def get_absolute_url(self):
        return '/assays/assayplatesetup/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.assay_run_id_id)

    def get_clone_url(self):
        return '/assays/{0}/assayplatesetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assayplatesetup/{}/delete/'.format(self.id)


class AssayReader(LockableModel):
    """Chip and Plate readers"""

    class Meta(object):
        ordering = ('reader_name',)

    reader_name = models.CharField(max_length=128)
    reader_type = models.CharField(max_length=128)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.reader_name, self.reader_type)


# TO BE DEPRECATED To be merged into single "AssayInstance" model
class AssayPlateReadoutAssay(models.Model):
    """Inline for PLATE readout assays"""

    class Meta(object):
        # Remove restriction that readout can only have one copy of an assay
        # unique_together = [('readout_id', 'assay_id')]
        # Assay-Feature pairs must be unique
        unique_together = [('readout_id', 'assay_id', 'feature')]

    readout_id = models.ForeignKey('assays.AssayPlateReadout', verbose_name='Readout')
    assay_id = models.ForeignKey('assays.AssayModel', verbose_name='Assay', null=True)
    reader_id = models.ForeignKey('assays.AssayReader', verbose_name='Reader')
    # Object excluded for now (presumably will be just well)
    # object_type = models.CharField(max_length=6,
    #                         choices=object_types,
    #                         verbose_name='Object of Interest',
    #                         default='F')
    readout_unit = models.ForeignKey('assays.PhysicalUnits')

    # For the moment, features will be just strings (this avoids potentially complex management)
    feature = models.CharField(max_length=150)

    def __unicode__(self):
        return u'{0}-{1}'.format(self.assay_id.assay_short_name, self.feature)


# TO BE DEPRECATED To be merged into single "AssayData" model
class AssayReadout(models.Model):
    """An individual value for a PLATE readout"""

    assay_device_readout = models.ForeignKey('assays.AssayPlateReadout')
    # A plate can have multiple assays, this differentiates between those assays
    assay = models.ForeignKey('assays.AssayPlateReadoutAssay')
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)
    value = models.FloatField()
    elapsed_time = models.FloatField(default=0)

    # Quality, if it is not the empty string, indicates that a readout is INVALID
    quality = models.CharField(default='', max_length=10)

    # IT WAS DECIDED THAT A FK WOULD NOT BE USED
    # Use quality with each flag separated with a '-' (SUBJECT TO CHANGE)
    # Quality indicator from QualityIndicator table (so that additional can be added)
    # quality_indicator = models.ForeignKey(AssayQualityIndicator, null=True, blank=True)

    # This value contains notes for the data point
    notes = models.CharField(max_length=255, default='')

    # Indicates what replicate this is (0 is for original)
    update_number = models.IntegerField(default=0)


# class ReadoutUnit(LockableModel):
#    """
#    Units specific to readouts (AU, RFU, so on)
#    """
#
#    class Meta(object):
#        ordering = ('readout_unit',)
#
#    readout_unit = models.CharField(max_length=512,unique=True)
#    description = models.CharField(max_length=512,blank=True,null=True)
#
#    def __unicode__(self):
#        return self.readout_unit


# Likely to become deprecated
# Get readout file location
def plate_readout_file_location(instance, filename):
    return '/'.join(['csv', str(instance.setup.assay_run_id_id), 'plate', filename])


# TO BE DEPRECATED To be merged into single "AssayDataset" model
class AssayPlateReadout(FlaggableModel):
    """Readout data collected from MICROPLATES"""

    class Meta(object):
        verbose_name = 'Plate Readout'

    # the unique readout identifier
    # can be a barcode or a hand written identifier
    # REMOVING READOUT ID FOR NOW
    # assay_device_id = models.CharField(max_length=512,
    #                                    verbose_name='Readout ID/ Barcode')

    # Cell samples are to be handled in AssayPlateSetup from now on

    setup = models.ForeignKey(AssayPlateSetup)

    timeunit = models.ForeignKey(PhysicalUnits, default=23)

    treatment_time_length = models.FloatField(verbose_name='Treatment Duration',
                                              blank=True, null=True)

    # Assay start time is now in AssayPlateSetup

    readout_start_time = models.DateField(verbose_name='Readout Date', help_text="YYYY-MM-DD")

    notebook = models.CharField(max_length=256, blank=True, default='')
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, default='')
    scientist = models.CharField(max_length=100, blank=True, default='')
    file = models.FileField(upload_to=plate_readout_file_location, verbose_name='Data File',
                            blank=True, null=True)

    def __unicode__(self):
        return u'{0}'.format(self.setup)

    def get_absolute_url(self):
        return '/assays/assayplatereadout/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.setup.assay_run_id_id)

    def get_clone_url(self):
        return '/assays/{0}/assayplatereadout/add?clone={1}'.format(self.setup.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assayplatereadout/{}/delete/'.format(self.id)


SEVERITY_SCORE = (
    ('-1', 'UNKNOWN'), ('0', 'NEGATIVE'), ('1', '+'), ('2', '+ +'),
    ('3', '+ + +'), ('4', '+ + + +'), ('5', '+ + + + +')
)

POSNEG = (
    ('0', 'Negative'), ('1', 'Positive'), ('x', 'Failed')
)


class AssayResultFunction(LockableModel):
    """Function for analysis of CHIP RESULTS"""
    class Meta(object):
        verbose_name = 'Function'
        ordering = ('function_name',)

    function_name = models.CharField(max_length=100, unique=True)
    function_results = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')

    def __unicode__(self):
        return self.function_name


class AssayResultType(LockableModel):
    """Result types for CHIP RESULTS"""

    class Meta(object):
        verbose_name = 'Result type'
        ordering = ('assay_result_type',)

    assay_result_type = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True, default='')

    def __unicode__(self):
        return self.assay_result_type


# TO BE DEPRECATED To be merged into single "AssayResult" model
class AssayPlateResult(models.Model):
    """Individual result parameters for PLATE RESULTS used in inline"""

    assay_name = models.ForeignKey('assays.AssayPlateReadoutAssay',
                                   verbose_name='Assay')

    assay_result = models.ForeignKey('assays.AssayPlateTestResult')

    result_function = models.ForeignKey(AssayResultFunction,
                                        blank=True,
                                        null=True,
                                        verbose_name='Function')

    result = models.CharField(default='1',
                              max_length=8,
                              choices=POSNEG,
                              verbose_name='Result')

    severity = models.CharField(default='-1',
                                max_length=5,
                                choices=SEVERITY_SCORE,
                                verbose_name='Severity',
                                blank=True)

    result_type = models.ForeignKey(AssayResultType,
                                    blank=True,
                                    null=True,
                                    verbose_name='Measure')

    value = models.FloatField(blank=True, null=True)

    test_unit = models.ForeignKey(PhysicalUnits,
                                  blank=True,
                                  null=True)


# TO BE DEPRECATED To be merged into single "AssayResultset" model
class AssayPlateTestResult(FlaggableModel):
    """Test Results from MICROPLATES"""

    class Meta(object):
        verbose_name = 'Plate Result'

    readout = models.ForeignKey('assays.AssayPlateReadout',
                                verbose_name='Plate ID/ Barcode')
    summary = models.TextField(default='', blank=True)

    def __unicode__(self):
        return u'Results for: {}'.format(self.readout)

    def get_absolute_url(self):
        return '/assays/assayplatetestresult/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.readout.setup.assay_run_id_id)

    def get_delete_url(self):
        return '/assays/assayplatetestresult/{}/delete/'.format(self.id)


class StudyConfiguration(LockableModel):
    """Defines how chips are connected together (for integrated studies)"""

    class Meta(object):
        verbose_name = 'Study Configuration'

    # Length subject to change
    name = models.CharField(max_length=50)

    # DEPRECATED when would we ever want an individual configuration?
    # study_format = models.CharField(
    #     max_length=11,
    #     choices=(('individual', 'Individual'), ('integrated', 'Integrated'),),
    #     default='integrated'
    # )

    media_composition = models.CharField(max_length=1000, blank=True, default='')
    hardware_description = models.CharField(max_length=1000, blank=True, default='')
    # Subject to removal
    # image = models.ImageField(upload_to="configuration",null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/assays/studyconfiguration/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/studyconfiguration/'


class StudyModel(models.Model):
    """Individual connections for integrated models"""

    study_configuration = models.ForeignKey(StudyConfiguration)
    label = models.CharField(max_length=2)
    organ = models.ForeignKey(OrganModel)
    sequence_number = models.IntegerField()
    output = models.CharField(max_length=20, blank=True, default='')
    # Subject to change
    integration_mode = models.CharField(max_length=13, default='1', choices=(('0', 'Functional'), ('1', 'Physical')))


# Get readout file location
def bulk_readout_file_location(instance, filename):
    return '/'.join(['csv', str(instance.id), 'bulk', filename])


# To be renamed "AssayStudy" for clarity
# Handling of study type will be changed
# Nature of assay_run_id subject to revision
class AssayRun(FlaggableModel):
    """The encapsulation of all data concerning some plate/chip project"""

    class Meta(object):
        verbose_name = 'Old Study'
        verbose_name_plural = 'Old Studies'
        ordering = ('assay_run_id',)

    # Removed center_id for now: this field is basically for admins anyway
    # May add center_id back later, but group mostly serves the same purpose
    # center_id = models.ForeignKey('microdevices.MicrophysiologyCenter', verbose_name='Center(s)')
    # Study type now multiple boolean fields; May need to add more in the future
    toxicity = models.BooleanField(default=False)
    efficacy = models.BooleanField(default=False)
    disease = models.BooleanField(default=False)
    # TODO PLEASE REFACTOR
    # NOW REFERRED TO AS "Chip Characterization"
    cell_characterization = models.BooleanField(default=False)
    # Subject to change
    study_configuration = models.ForeignKey(StudyConfiguration, blank=True, null=True)
    name = models.TextField(default='Study-01', verbose_name='Study Name',
                            help_text='Name-###')
    start_date = models.DateField(help_text='YYYY-MM-DD')
    # TODO REMOVE AS SOON AS POSSIBLE
    assay_run_id = models.TextField(unique=True, verbose_name='Study ID',
                                    help_text="Standard format 'CenterID-YYYY-MM-DD-Name-###'")
    description = models.TextField(blank=True, default='')

    protocol = models.FileField(
        upload_to='study_protocol',
        verbose_name='Protocol File',
        blank=True,
        null=True,
        help_text='Protocol File for Study'
    )

    bulk_file = models.FileField(
        upload_to=bulk_readout_file_location,
        verbose_name='Data File',
        blank=True, null=True
    )

    # Deprecated
    # File (an Excel file, I assume) of supporting data
    # supporting_data = models.FileField(
    #     upload_to='supporting_data',
    #     blank=True,
    #     null=True,
    #     help_text='Supporting Data for Study'
    # )

    # Image for the study (some illustrative image)
    image = models.ImageField(upload_to='studies', null=True, blank=True)

    use_in_calculations = models.BooleanField(default=False)

    access_groups = models.ManyToManyField(Group, blank=True, related_name='access_groups')

    def study_types(self):
        current_types = ''
        if self.toxicity:
            current_types += 'TOX '
        if self.efficacy:
            current_types += 'EFF '
        if self.disease:
            current_types += 'DM '
        if self.cell_characterization:
            current_types += 'CC '
        return u'{0}'.format(current_types)

    def __unicode__(self):
        return self.assay_run_id

    def get_absolute_url(self):
        return '/assays/{}/'.format(self.id)

    def get_delete_url(self):
        return '/assays/{}/delete/'.format(self.id)


# Get readout file location
def study_supporting_data_location(instance, filename):
    return '/'.join(['supporting_data', str(instance.study_id), filename])


class StudySupportingData(models.Model):
    """A file (with description) that gives extra data for a Study"""
    study = models.ForeignKey(AssayRun)

    description = models.CharField(
        max_length=1000,
        help_text='Describes the contents of the supporting data file'
    )

    # Not named file in order to avoid shadowing
    supporting_data = models.FileField(
        upload_to=study_supporting_data_location,
        help_text='Supporting Data for Study'
    )


# TO BE DEPRECATED To be merged into single "AssayData" model
class AssayChipRawData(models.Model):
    """Individual lines of readout data"""

    # class Meta(object):
    #     unique_together = [('assay_chip_id', 'assay_id', 'field_id', 'time')]

    # TO BE REPLACED (readouts likely will not exist in future versions)
    assay_chip_id = models.ForeignKey('assays.AssayChipReadout')
    # DEPRECATED: ACRA WILL BE REPLACED BY ASSAY INSTANCE
    assay_id = models.ForeignKey('assays.AssayChipReadoutAssay', null=True, blank=True)

    # Cross reference for users if study ids diverge
    cross_reference = models.CharField(max_length=255, default='')

    # DEPRECATED: REPLACED BY SAMPLE LOCATION
    field_id = models.CharField(max_length=255, default='0', null=True, blank=True)

    value = models.FloatField(null=True)

    # TO BE RENAMED SIMPLY "time" IN FUTURE MODELS
    # PLEASE NOTE THAT THIS IS NOW ALWAYS MINUTES <-IMPORTANT
    elapsed_time = models.FloatField(default=0, null=True, blank=True)

    # This value will act as quality control, if it evaluates True then the value is considered invalid
    quality = models.CharField(max_length=20, default='')

    # Caution flags for the user
    # Errs on the side of larger flags, currently
    caution_flag = models.CharField(max_length=255, default='')

    # IT WAS DECIDED THAT A FK WOULD NOT BE USED
    # Use quality with each flag separated with a '-' (SUBJECT TO CHANGE)
    # Quality indicator from QualityIndicator table (so that additional can be added)
    # quality_indicator = models.ForeignKey(AssayQualityIndicator, null=True, blank=True)

    # This value contains notes for the data point
    notes = models.CharField(max_length=255, default='')

    # Indicates what replicate this is (0 is for original)
    update_number = models.IntegerField(default=0)

    # New fields
    # TEMPORARILY NOT REQUIRED
    sample_location = models.ForeignKey('assays.AssaySampleLocation', null=True, blank=True)
    # TEMPORARILY NOT REQUIRED
    assay_instance = models.ForeignKey('assays.AssayInstance', null=True, blank=True)

    # DEFAULTS SUBJECT TO CHANGE
    assay_plate_id = models.CharField(max_length=255, default='N/A')
    assay_well_id = models.CharField(max_length=255, default='N/A')

    # Indicates "technical replicates"
    # SUBJECT TO CHANGE
    replicate = models.CharField(max_length=255, default='')

    # Replaces elapsed_time
    time = models.FloatField(default=0)

    # Affiliated upload
    data_upload = models.ForeignKey('assays.AssayDataUpload', null=True, blank=True)


class AssayChipCells(models.Model):
    """Individual cell parameters for CHIP setup used in inline"""
    assay_chip = models.ForeignKey('AssayChipSetup')
    cell_sample = models.ForeignKey('cellsamples.CellSample')
    cell_biosensor = models.ForeignKey('cellsamples.Biosensor')
    cellsample_density = models.FloatField(verbose_name='density', default=0)

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default="CP",
                                               choices=(('WE', 'cells / well'),
                                                        ('CP', 'cells / chip'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    cell_passage = models.CharField(max_length=16, verbose_name='Passage#',
                                    blank=True, default='')


# TO BE DEPRECATED To be merged into single "AssaySetup" model
class AssayChipSetup(FlaggableModel):
    """The configuration of a Chip for implementing an assay"""
    class Meta(object):
        verbose_name = 'Chip Setup'
        ordering = ('-assay_chip_id', 'assay_run_id',)

    assay_run_id = models.ForeignKey(AssayRun, verbose_name='Study')
    setup_date = models.DateField(help_text='YYYY-MM-DD')

    device = models.ForeignKey(Microdevice, verbose_name='Device')

    # RENAMED (previously field was erroneously device)
    organ_model = models.ForeignKey(OrganModel, verbose_name='Organ Model Name', null=True, blank=True)

    organ_model_protocol = models.ForeignKey(OrganModelProtocol, verbose_name='Organ Model Protocol',
                                             null=True, blank=True)

    variance = models.CharField(max_length=3000, verbose_name='Variance from Protocol', default='', blank=True)

    # the unique chip identifier
    # can be a barcode or a hand written identifier
    assay_chip_id = models.CharField(max_length=512, verbose_name='Chip ID/ Barcode')

    # Control => control, Compound => compound; Abbreviate? Capitalize?
    chip_test_type = models.CharField(max_length=8, choices=(("control", "Control"), ("compound", "Compound")), default="control")

    compound = models.ForeignKey('compounds.Compound', null=True, blank=True)
    concentration = models.FloatField(default=0, verbose_name='Conc.',
                                      null=True, blank=True)
    unit = models.ForeignKey('assays.PhysicalUnits', default=4,
                             verbose_name='conc. Unit',
                             null=True, blank=True)

    scientist = models.CharField(max_length=100, blank=True, default='')
    notebook = models.CharField(max_length=256, blank=True, default='')
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, default='')

    def __unicode__(self):
        return u'{}'.format(self.assay_chip_id)
        # if self.compound:
        #     return u'Chip-{}:{}({}{})'.format(
        #         self.assay_chip_id,
        #         self.compound,
        #         self.concentration,
        #         self.unit
        #     )
        # else:
        #     return u'Chip-{}:Control'.format(self.assay_chip_id)

    def get_absolute_url(self):
        return '/assays/assaychipsetup/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.assay_run_id_id)

    def get_clone_url(self):
        return '/assays/{0}/assaychipsetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assaychipsetup/{}/delete/'.format(self.id)

object_types = (
    ('F', 'Field'), ('C', 'Colony'), ('M', 'Media'), ('X', 'Other')
)


# TO BE DEPRECATED To be merged into single "AssayInstance" model
# FURTHERMORE assays will probably be captured at a study, rather than "readout" level
class AssayChipReadoutAssay(models.Model):
    """Inline for CHIP readout assays"""

    class Meta(object):
        # Changed uniqueness check to include unit (extend to include object?)
        unique_together = [('readout_id', 'assay_id', 'readout_unit')]

    readout_id = models.ForeignKey('assays.AssayChipReadout', verbose_name='Readout')
    # DEPRECATED
    assay_id = models.ForeignKey('assays.AssayModel', verbose_name='Assay', null=True, blank=True)
    # DEPRECATED
    reader_id = models.ForeignKey('assays.AssayReader', verbose_name='Reader', null=True, blank=True)
    # DEPRECATED
    object_type = models.CharField(
        max_length=6,
        choices=object_types,
        verbose_name='Object of Interest',
        default='F',
        blank=True
    )
    # Will be renamed unit in future table
    readout_unit = models.ForeignKey(PhysicalUnits)

    # New fields that will be in AssaySpecificAssay (or AssayInstance, not sure about name)
    # target = models.ForeignKey(AssayTarget)
    # method = models.ForeignKey(AssayMethod)

    def __unicode__(self):
        return u'{}'.format(self.assay_id)


# Likely to become deprecated
# Get readout file location
def chip_readout_file_location(instance, filename):
    return '/'.join(['csv', str(instance.chip_setup.assay_run_id_id), 'chip', filename])


# TO BE DEPRECATED To be merged into single "AssayDataset" model
class AssayChipReadout(FlaggableModel):
    """Readout data for CHIPS"""

    class Meta(object):
        verbose_name = 'Chip Readout'
        ordering = ('chip_setup',)

    chip_setup = models.ForeignKey(AssayChipSetup)

    timeunit = models.ForeignKey(PhysicalUnits, default=23)
    treatment_time_length = models.FloatField(verbose_name='Assay Treatment Duration',
                                              blank=True, null=True)

    readout_start_time = models.DateField(verbose_name='Readout Start Date', help_text="YYYY-MM-DD")

    notebook = models.CharField(max_length=256, blank=True, default='')
    notebook_page = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=2048, blank=True, default='')
    scientist = models.CharField(max_length=100, blank=True, default='')
    file = models.FileField(upload_to=chip_readout_file_location, verbose_name='Data File',
                            blank=True, null=True, help_text='Green = Data from database;'
                                                             ' Red = Line that will not be read'
                                                             '; Gray = Reading with null value'
                                                             ' ***Uploading overwrites old data***')

    # Get a list of every assay for list view
    def assays(self):
        list_of_assays = []
        assays = AssayChipReadoutAssay.objects.filter(
            readout_id=self.id
        ).prefetch_related(
            'assay_id',
            'reader_id',
            'readout_unit'
        )
        for assay in assays:
            list_of_assays.append(str(assay))
        # Convert to unicode for consistency
        return u'{0}'.format(', '.join(list_of_assays))

    def __unicode__(self):
        return u'{0}'.format(self.chip_setup)

    def get_absolute_url(self):
        return '/assays/assaychipreadout/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.chip_setup.assay_run_id.id)

    def get_clone_url(self):
        return '/assays/{0}/assaychipreadout/add?clone={1}'.format(self.chip_setup.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assaychipreadout/{}/delete/'.format(self.id)


# TO BE DEPRECATED To be merged into single "AssayResultSet" model
class AssayChipTestResult(FlaggableModel):
    """Results calculated from Raw Chip Data"""

    class Meta(object):
        verbose_name = 'Chip Result'

    chip_readout = models.ForeignKey('assays.AssayChipReadout', verbose_name='Chip Readout')
    summary = models.TextField(default='', blank=True)

    def __unicode__(self):
        return u'Results for: {}'.format(self.chip_readout)

    def assay(self):
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            return AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')[0].assay_name
        return ''

    def result(self):
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            abbreviation = AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')[0].result
            if abbreviation == '1':
                return u'Positive'
            else:
                return u'Negative'
        return ''

    def result_function(self):
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            return AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')[0].result_function
        return ''

    def result_type(self):
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            return AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')[0].result_type
        return ''

    def severity(self):
        severity_score_dict = dict(SEVERITY_SCORE)
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            return severity_score_dict.get(AssayChipResult.objects.filter(
                assay_result_id=self.id
            ).order_by('id')[0].severity, 'None')
        return ''

    def get_absolute_url(self):
        return '/assays/assaychiptestresult/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.chip_readout.chip_setup.assay_run_id_id)

    def get_delete_url(self):
        return '/assays/assaychiptestresult/{}/delete/'.format(self.id)


# TO BE DEPRECATED To be merged into single "AssayResult" model
class AssayChipResult(models.Model):
    """Individual result parameters for CHIP RESULTS used in inline"""

    assay_name = models.ForeignKey('assays.AssayInstance',
                                   verbose_name='Assay')

    assay_result = models.ForeignKey(AssayChipTestResult)

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
                                blank=True)

    result_type = models.ForeignKey(AssayResultType,
                                    blank=True,
                                    null=True,
                                    verbose_name='Measure')

    value = models.FloatField(blank=True, null=True)

    test_unit = models.ForeignKey(PhysicalUnits,
                                  blank=True,
                                  null=True)


class AssayDataUpload(FlaggableModel):
    """Shows the history of data uploads for a readout; functions as inline"""

    # TO BE DEPRECATED
    # date_created, created_by, and other fields are used but come from FlaggableModel
    file_location = models.URLField(null=True, blank=True)

    # Store the file itself, rather than the location
    # NOTE THAT THIS IS NOT SIMPLY "file" DUE TO COLLISIONS WITH RESERVED WORDS
    # TODO SET LOCATION
    # TODO REQUIRE EVENTUALLY
    data_file = models.FileField(null=True, blank=True)

    # Note that there are both chip and plate readouts listed as one file may supply both
    # TO BE DEPRECATED
    chip_readout = models.ManyToManyField(AssayChipReadout)
    # TO BE DEPRECATED
    plate_readout = models.ManyToManyField(AssayPlateReadout)

    # Supplying study may seem redundant, however:
    # This ensures that uploads for readouts that have been (for whatever reason) deleted will no longer be hidden
    study = models.ForeignKey(AssayRun)

    def __unicode__(self):
        return urllib.unquote(self.file_location.split('/')[-1])


# NEW MODELS, TO BE INTEGRATED FURTHER LATER
class AssayTarget(LockableModel):
    """Describes what was sought by a given Assay"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)

    short_name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.short_name)


class AssayMeasurementType(LockableModel):
    """Describes what was measures with a given method"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.name


class AssaySupplier(LockableModel):
    """Assay Supplier so we can track where kits came from"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.name


class AssayMethod(LockableModel):
    """Describes how an assay was performed"""
    # We may want to modify this so that it is unique on name in combination with measurement type?
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)
    measurement_type = models.ForeignKey(AssayMeasurementType)

    # May or may not be required in the future
    supplier = models.ForeignKey(AssaySupplier, blank=True, null=True)

    # TODO STORAGE LOCATION
    # TODO TEMPORARILY NOT REQUIRED
    protocol_file = models.FileField(upload_to='assays', null=True, blank=True)

    def __unicode__(self):
        return self.name


class AssaySampleLocation(LockableModel):
    """Describes a location for where a sample was acquired"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.name


# TODO WE WILL NEED TO ADD INSTRUMENT/READER IT SEEMS
class AssayInstance(models.Model):
    """Specific assays used in the 'inlines'"""
    study = models.ForeignKey(AssayRun, null=True, blank=True)
    study_new = models.ForeignKey('assays.AssayStudy', null=True, blank=True)
    target = models.ForeignKey(AssayTarget)
    method = models.ForeignKey(AssayMethod)
    # Name of model "PhysicalUnits" should be renamed, methinks
    unit = models.ForeignKey(PhysicalUnits)

    def __unicode__(self):
        return u'{0}|{1}|{2}'.format(self.target, self.method, self.unit)


# Preliminary schema
# Please note that I opted to use CharFields in lieu of TextFields (we can limit characters that way)
class AssayStudyType(LockableModel):
    """Used as in a many-to-many field in Assay Study to indicate the purpose(s) of the Study"""
    name = models.CharField(max_length=255, unique=True)
    # Abbreviation for the study type
    code = models.CharField(max_length=20, unique=True)
    # Description as per usual
    description = models.CharField(max_length=2000, default='')

    def __unicode__(self):
        return self.name


class AssayStudy(FlaggableModel):
    """The encapsulation of all data concerning a project"""
    class Meta(object):
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'

    # Subject to change
    # Perhaps we will not continue to use StudyConfiguration (the table name for which should arguably be changed!)
    study_configuration = models.ForeignKey(StudyConfiguration, blank=True, null=True)
    # Whether or not the name should be unique is an interesting question
    # We could have a constraint on the combination of name and start_date
    # But to constrain by name, start_date, and study_types, we will need to do that in the forms.py file
    # Otherwise we can change study_types such that it is not longer a ManyToMany
    name = models.CharField(max_length=2000, verbose_name='Study Name')
    start_date = models.DateField(help_text='YYYY-MM-DD')
    description = models.CharField(max_length=2000, blank=True, default='')

    protocol = models.FileField(
        upload_to='study_protocol',
        verbose_name='Protocol File',
        blank=True,
        null=True,
        help_text='Protocol File for Study'
    )

    # We prefer adding multiple files at once, it seems
    # Will we still upload files for an entire study?
    # bulk_file = models.FileField(
    #     upload_to=bulk_readout_file_location,
    #     verbose_name='Data File',
    #     blank=True, null=True
    # )

    study_types = models.ManyToManyField(AssayStudyType)

    # Image for the study (some illustrative image)
    image = models.ImageField(upload_to='studies', null=True, blank=True)

    use_in_calculations = models.BooleanField(default=False)

    # Group is now explicitly defined here as opposed to using a mixin
    group = models.ForeignKey(Group, help_text='Bind to a group')

    # Access groups
    access_groups = models.ManyToManyField(Group, blank=True, related_name='study_access_groups')

    # DEPRECATED
    # TODO the access choices should probably be file-level scope
    # THIS HAS BEEN DECIDED AGAINST
    # WE WILL USE HAVE A SERIES OF GROUPS TO SELECT FROM INSTEAD OR SOMETHING LIKE THAT
    # access indicates who can see the study and its data
    # access = models.CharField(
    #     max_length=255,
    #     verbose_name='Access Level',
    #     choices=(
    #         ('editors', 'Group Editors'),
    #         ('viewers', 'Consortium Viewers'),
    #         ('public', 'Public')
    #     ),
    #     default=''
    # )

    def get_study_types_string(self):
        study_types = '-'.join(
            sorted([study_type.code for study_type in self.study_types.all()])
        )
        return study_types

    # TODO
    def __unicode__(self):
        center_id = get_center_id(self.group.id).get('center_id')
        study_types = self.get_study_types_string()
        return '-'.join([
            center_id,
            study_types,
            unicode(self.start_date),
            self.name
        ])

    def get_absolute_url(self):
        return '/assays/{}/'.format(self.id)

    def get_delete_url(self):
        return '/assays/{}/delete/'.format(self.id)


# ON THE FRONT END, MATRICES ARE LIKELY TO BE CALLED STUDY SETUPS
class AssayMatrix(FlaggableModel):
    """Used to organize data in the interface. An Matrix is a set of setups"""
    class Meta(object):
        verbose_name_plural = 'Assay Matrices'
        unique_together = [('study', 'name')]

    # TODO Name made unique within Study? What will the constraint be?
    name = models.CharField(max_length=255)

    # TODO THINK OF HOW TO HANDLE PLATES HERE
    # TODO REALLY NEEDS TO BE REVISED
    representation = models.CharField(
        max_length=255,
        choices=(
            ('chips', 'Multiple Chips'),
            # Should there be an option for single chips?
            # Probably not!
            # ('chip', 'Chip'),
            ('plate', 'Plate'),
            # What other things might interest us?
            ('', '')
        )
    )

    study = models.ForeignKey(AssayStudy)

    device = models.ForeignKey(Microdevice, null=True, blank=True)

    # Decided against the inclusion of organ model here
    # organ_model = models.ForeignKey(OrganModel, null=True, blank=True)
    #
    # organ_model_protocol = models.ForeignKey(
    #     OrganModelProtocol,
    #     verbose_name='Model Protocol',
    #     null=True,
    #     blank=True
    # )
    #
    # # formerly just 'variance'
    # variance_from_organ_model_protocol = models.CharField(
    #     max_length=3000,
    #     verbose_name='Variance from Protocol',
    #     default='',
    #     blank=True
    # )

    # Number of rows and columns
    # Only required for representations without dimensions already
    number_of_rows = models.IntegerField(null=True, blank=True)
    number_of_columns = models.IntegerField(null=True, blank=True)

    # May be useful
    notes = models.CharField(max_length=2048, blank=True, default='')

    def __unicode__(self):
        return u'{0}'.format(self.name)

    # TODO
    def get_absolute_url(self):
        pass
        # return '/assays/assaychipsetup/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/{}/'.format(self.study.id)
        # return '/assays/{}/'.format(self.assay_run_id_id)

    def get_clone_url(self):
        pass
        # return '/assays/{0}/assaychipsetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        pass
        # return '/assays/assaychipsetup/{}/delete/'.format(self.id)


class AssayFailureReason(FlaggableModel):
    """Describes a type of failure"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)


# SUBJECT TO REMOVAL (MAY JUST USE ASSAY SETUP)
class AssayMatrixItem(FlaggableModel):
    class Meta(object):
        verbose_name = 'Matrix Item'
        # TODO Should this be by study or by matrix?
        unique_together = [
            ('study', 'name'),
            ('matrix', 'row_index', 'column_index')
        ]

    # Technically the study here is redundant (contained in matrix)
    study = models.ForeignKey(AssayStudy)

    # Probably shouldn't use this trick!
    # This is in fact required, just listed as not being so due to quirk in cleaning
    matrix = models.ForeignKey(AssayMatrix, null=True, blank=True)

    # This is in fact required, just listed as not being so due to quirk in cleaning
    setup = models.ForeignKey('assays.AssaySetup', null=True, blank=True)

    name = models.CharField(max_length=512)
    setup_date = models.DateField(help_text='YYYY-MM-DD')

    # Tentative
    # Do we want a time on top of this?
    # failure_date = models.DateField(help_text='YYYY-MM-DD', null=True, blank=True)
    # Failure time in minutes
    failure_time = models.FloatField(null=True, blank=True)
    # Do we want this is to be table or a static list?
    failure_reason = models.ForeignKey(AssayFailureReason, blank=True, null=True)

    # Do we still want this? Should it be changed?
    scientist = models.CharField(max_length=100, blank=True, default='')
    notebook = models.CharField(max_length=256, blank=True, default='')
    # Should this be an integer field instead?
    notebook_page = models.CharField(max_length=256, blank=True, default='')
    notes = models.CharField(max_length=2048, blank=True, default='')

    # If setups and items are to be merged, these are necessary
    row_index = models.IntegerField()
    column_index = models.IntegerField()


class AssaySetup(FlaggableModel):
    """The configuration of a Chip or Well for implementing an assay"""
    class Meta(object):
        verbose_name = 'Setup'
        # Unfortunately can't use this because uniqueness depends on compounds, cells, etc.
        # unique_together = [
        #     (
        #         'study',
        #         'device',
        #         'organ_model',
        #         'organ_model_protocol',
        #         'variance_from_organ_model_protocol'
        #     )
        # ]

    # Moved
    # study = models.ForeignKey(AssayStudy, verbose_name='Study')
    # setup_date = models.DateField(help_text='YYYY-MM-DD')

    # Setups are now bound to a matrix
    # This is in fact required, just listed as not being so due to quirk in cleaning
    matrix = models.ForeignKey(AssayMatrix, null=True, blank=True)

    # IF THERE IS A DEVICE IN THE MATRIX, MAKE SURE TO LOCK THIS FIELD
    device = models.ForeignKey(Microdevice, verbose_name='Device')

    # IF THERE IS A ORGAN MODEL IN THE MATRIX, MAKE SURE TO LOCK THIS FIELD
    organ_model = models.ForeignKey(OrganModel, verbose_name='Model', null=True, blank=True)

    organ_model_protocol = models.ForeignKey(
        OrganModelProtocol,
        verbose_name='Model Protocol',
        null=True,
        blank=True
    )

    # formerly just 'variance'
    variance_from_organ_model_protocol = models.CharField(
        max_length=3000,
        verbose_name='Variance from Protocol',
        default='',
        blank=True
    )

    compounds = models.ManyToManyField('assays.AssaySetupCompound')
    cells = models.ManyToManyField('assays.AssaySetupCell')
    settings = models.ManyToManyField('assays.AssaySetupSetting')

    # Moved
    # name = models.CharField(max_length=512)

    # scientist = models.CharField(max_length=100, blank=True, default='')
    # notebook = models.CharField(max_length=256, blank=True, default='')
    # notebook_page = models.IntegerField(blank=True, null=True)
    # notes = models.CharField(max_length=2048, blank=True, default='')
    #
    # # If setups and items are to be merged, these are necessary
    # row_index = models.IntegerField()
    # column_index = models.IntegerField()

    def __unicode__(self):
        return u'{0}-{1}'.format(self.matrix, self.device)

    # TODO
    def get_absolute_url(self):
        pass
        # return '/assays/assaychipsetup/{}/'.format(self.id)

    def get_post_submission_url(self):
        pass
        # return '/assays/{}/'.format(self.assay_run_id_id)

    def get_clone_url(self):
        pass
        # return '/assays/{0}/assaychipsetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        pass
        # return '/assays/assaychipsetup/{}/delete/'.format(self.id)


# Controversy has arisen over whether to put this in an organ model or not
# This name is somewhat deceptive, it describes the quantity of cells, not a cell (rename please)
class AssaySetupCell(models.Model):
    """Individual cell parameters for setup used in inline"""
    class Meta(object):
        unique_together = [
            (
                # 'setup',
                'cell_sample',
                'biosensor',
                'density',
                'density_unit',
                'passage'
            )
        ]

    # No longer bound one-to-one
    # setup = models.ForeignKey('AssaySetup')
    cell_sample = models.ForeignKey('cellsamples.CellSample')
    biosensor = models.ForeignKey('cellsamples.Biosensor')
    density = models.FloatField(verbose_name='density', default=0)

    # TODO THIS IS TO BE HAMMERED OUT
    # density_unit = models.CharField(
    #     verbose_name='Unit',
    #     max_length=8,
    #     default='WE',
    #     # TODO ASK ABOUT THESE CHOICES?
    #     choices=(('WE', 'cells / well'),
    #             ('ML', 'cells / mL'),
    #             ('MM', 'cells / mm^2'))
    # )
    density_unit = models.ForeignKey('assays.PhysicalUnits')
    passage = models.CharField(
        max_length=16,
        verbose_name='Passage#',
        blank=True,
        default=''
    )

    # DO WE WANT ADDITION TIME AND DURATION?


# DO WE WANT TRACKING INFORMATION FOR INDIVIDUAL POINTS?
class AssayDataPoint(models.Model):
    """Individual points of data"""

    class Meta(object):
        unique_together = [
            (
                'matrix_item',
                'assay_instance',
                'sample_location',
                'time',
                'update_number',
                'assay_plate_id',
                'assay_well_id',
                'replicate'
            )
        ]

    # setup = models.ForeignKey('assays.AssaySetup')

    # Cross reference for users if study ids diverge
    cross_reference = models.CharField(max_length=255, default='')

    matrix_item = models.ForeignKey('assays.AssayMatrixItem')

    assay_instance = models.ForeignKey('assays.AssayInstance')

    sample_location = models.ForeignKey('assays.AssaySampleLocation')

    value = models.FloatField(null=True)

    # PLEASE NOTE THAT THIS IS IN MINUTES
    time = models.FloatField(default=0)

    # Caution flags for the user
    # Errs on the side of larger flags, currently
    caution_flag = models.CharField(max_length=255, default='')

    # TODO PROPOSED: CHANGE QUALITY TO TWO BOOLEANS: exclude and replaced
    # Kind of sloppy right now, I do not like it!
    # This value will act as quality control, if it evaluates True then the value is considered invalid
    quality = models.CharField(max_length=20, default='')

    # This value contains notes for the data point
    notes = models.CharField(max_length=255, default='')

    # Indicates what replicate this is (0 is for original)
    update_number = models.IntegerField(default=0)

    # DEFAULTS SUBJECT TO CHANGE
    assay_plate_id = models.CharField(max_length=255, default='N/A')
    assay_well_id = models.CharField(max_length=255, default='N/A')

    # Indicates "technical replicates"
    # SUBJECT TO CHANGE
    replicate = models.CharField(max_length=255, default='')

    data_upload = models.ForeignKey('assays.AssayDataUpload')


# # TODO MODIFY AssayCompoundInstance
# DEPRECATED: DO NOT USE
# class AssayCompoundInstance(models.Model):
#     """An instance of a compound used in an assay; used as an inline"""
#     class Meta(object):
#         unique_together = [
#             (
#                 'chip_setup',
#                 # 'setup',
#                 'compound_instance',
#                 'concentration',
#                 'concentration_unit',
#                 'addition_time',
#                 'duration'
#             )
#         ]
#
#     # Stop-gap, subject to change
#     # DEPRECATED
#     chip_setup = models.ForeignKey('assays.AssayChipSetup', null=True, blank=True)
#     # Shouldn't be optional
#     # setup = models.ForeignKey('assays.AssaySetup', null=True, blank=True)
#
#     # COMPOUND INSTANCE IS REQUIRED, however null=True was done to avoid a submission issue
#     compound_instance = models.ForeignKey(
#         'compounds.CompoundInstance',
#         null=True,
#         blank=True
#     )
#     concentration = models.FloatField()
#     concentration_unit = models.ForeignKey(
#         'assays.PhysicalUnits',
#         verbose_name='Concentration Unit'
#     )
#
#     # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
#     addition_time = models.FloatField(blank=True)
#
#     # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
#     duration = models.FloatField(blank=True)


class AssaySetupCompound(models.Model):
    """An instance of a compound used in an assay; used in M2M with setup"""

    class Meta(object):
        unique_together = [
            (
                # 'setup',
                'compound_instance',
                'concentration',
                'concentration_unit',
                'addition_time',
                'duration'
            )
        ]

    # COMPOUND INSTANCE IS REQUIRED, however null=True was done to avoid a submission issue
    compound_instance = models.ForeignKey(
        'compounds.CompoundInstance',
        null=True,
        blank=True
    )
    concentration = models.FloatField()
    concentration_unit = models.ForeignKey(
        'assays.PhysicalUnits',
        verbose_name='Concentration Unit'
    )

    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    addition_time = models.FloatField(blank=True)

    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    duration = models.FloatField(blank=True)


# TODO MODIFY StudySupportingData
class AssayStudySupportingData(models.Model):
    """A file (with description) that gives extra data for a Study"""
    study = models.ForeignKey(AssayStudy)

    description = models.CharField(
        max_length=1000,
        help_text='Describes the contents of the supporting data file'
    )

    # Not named file in order to avoid shadowing
    supporting_data = models.FileField(
        upload_to=study_supporting_data_location,
        help_text='Supporting Data for Study'
    )


# TODO MODIFY AssayDataUpload
# Renamed from AssayDataUpload
# class AssayDataFile(FlaggableModel):
#     """Shows the history of data uploads for a readout; functions as inline"""
#     # date_created, created_by, and other fields are used but come from FlaggableModel
#     file_location = models.URLField(null=True, blank=True)
#     # Note that there are both chip and plate readouts listed as one file may supply both
#     # DEPRECATED
#     chip_readout = models.ManyToManyField(AssayChipReadout)
#     # DEPRECATED
#     plate_readout = models.ManyToManyField(AssayPlateReadout)
#
#     # Data will be related to a setup rather than a "readout" now
#     # setup = models.ManyToManyField(AssaySetup)
#     matrix_item = models.ManyToManyField(AssayMatrixItem)
#
#     # There are a few ways of swapping this in, but we will probably have to edit the migration CAREFULLY
#     study = models.ForeignKey(AssayStudy)
#
#     def __unicode__(self):
#         return urllib.unquote(self.file_location.split('/')[-1])


# TODO ADD ASSAY TO MODEL NAMES
# TODO REMEMBER TO REPLACE ALL OCCURENCES AFTER DOING THIS
class AssayStudyConfiguration(LockableModel):
    """Defines how chips are connected together (for integrated studies)"""

    class Meta(object):
        verbose_name = 'Study Configuration'

    # Length subject to change
    name = models.CharField(max_length=255, unique=True)

    media_composition = models.CharField(max_length=1000, blank=True, default='')
    hardware_description = models.CharField(max_length=1000, blank=True, default='')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/assays/studyconfiguration/{}/'.format(self.id)

    def get_post_submission_url(self):
        return '/assays/studyconfiguration/'


class AssayStudyModel(models.Model):
    """Individual connections for integrated models"""
    study_configuration = models.ForeignKey(AssayStudyConfiguration)
    label = models.CharField(max_length=2)
    organ = models.ForeignKey(OrganModel)
    sequence_number = models.IntegerField()
    output = models.CharField(max_length=20, blank=True, default='')
    # Subject to change
    integration_mode = models.CharField(max_length=13, default='1', choices=(('0', 'Functional'), ('1', 'Physical')))


# TODO Rename PhysicalUnits to PhysicalUnit
# TODO REMEMBER TO REPLACE ALL OCCURRENCES AFTER DOING THIS
# class PhysicalUnit(LockableModel):
#     """Measures of concentration and so on"""
#     unit = models.CharField(max_length=256, unique=True)
#     description = models.CharField(
#         max_length=256,
#         blank=True,
#         default=''
#     )
#
#     unit_type = models.ForeignKey(UnitType)
#
#     # Base Unit for conversions and scale factor
#     base_unit = models.ForeignKey(
#         'assays.PhysicalUnits',
#         blank=True,
#         null=True
#     )
#
#     # Scale factor gives the conversion to get to the base unit, can also act to sort
#     scale_factor = models.FloatField(
#         blank=True,
#         null=True
#     )
#
#     availability = models.CharField(
#         max_length=256,
#         blank=True,
#         default='',
#         help_text=(
#             u'Type a series of strings for indicating '
#             u'where this unit should be listed:'
#             u'\ntest = test results\nreadouts = readouts'
#         )
#     )
#
#     # verbose_name_plural is used to avoid a double 's' on the model name
#     class Meta(object):
#         verbose_name_plural = 'Physical Units'
#         ordering = ['unit_type', 'unit']
#
#     def __unicode__(self):
#         return u'{}'.format(self.unit)


# Proposed, may or may not include
# TODO Probably should have a ControlledVocabularyMixin for defining name and description consistently
class AssaySetting(LockableModel):
    """Defines a type of setting (flowrate etc.)"""
    name = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2000)


class AssaySetupSetting(models.Model):
    """Defines a setting as it relates to a setup"""
    # No longer one-to-one
    # setup = models.ForeignKey('assays.AssaySetup')
    setting = models.ForeignKey('assays.AssaySetting')
    unit = models.ForeignKey('assays.PhysicalUnits')
    value = models.FloatField()

    # Will we include these??
    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    # addition_time = models.FloatField(blank=True)

    # PLEASE NOTE THAT THIS IS IN MINUTES, CONVERTED FROM D:H:M
    # duration = models.FloatField(blank=True)
