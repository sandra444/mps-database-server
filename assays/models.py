# coding=utf-8

from django.db import models
from microdevices.models import Microdevice, OrganModel, OrganModelProtocol
from mps.base.models import LockableModel, RestrictedModel, FlaggableModel

# DEPRECATED, REMOVE SOON
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


class UnitType(LockableModel):
    """
    Unit types for physical units
    """

    unit_type = models.CharField(max_length=100)
    description = models.CharField(max_length=256,
                                   blank=True, default='')

    def __unicode__(self):
        return u'{}'.format(self.unit_type)

class PhysicalUnits(LockableModel):
    """
    Measures of concentration and so on
    """

    unit = models.CharField(max_length=256)
    description = models.CharField(max_length=256,
                                   blank=True, default='')

    unit_type = models.ForeignKey(UnitType)

    # Base Unit for conversions and scale factor
    base_unit = models.ForeignKey('assays.PhysicalUnits',
                                  blank=True,
                                  null=True)

    # Scale factor gives the conversion to get to the base unit, can also act to sort
    scale_factor = models.FloatField(blank=True,
                                     null=True)

    availability = models.CharField(max_length=256,
                                    blank=True,
                                    default='',
                                    help_text=(u'Type a series of strings for indicating '
                                               u'where this unit should be listed:'
                                               u'\ntest = test results\nreadouts = readouts'))

    # verbose_name_plural is used to avoid a double 's' on the model name
    class Meta(object):
        verbose_name_plural = 'Physical Units'
        ordering = ['unit_type', 'unit']

    def __unicode__(self):
        return u'{}'.format(self.unit)


class AssayModelType(LockableModel):
    """
    Defines the type of an ASSAY (biochemical, mass spec, and so on)
    """

    class Meta(object):
        ordering = ('assay_type_name',)

    assay_type_name = models.CharField(max_length=200, unique=True)
    assay_type_description = models.TextField(blank=True, default='')

    def __unicode__(self):
        return self.assay_type_name


class AssayModel(LockableModel):
    """
    Defines an ASSAY such as albumin, BUN, and so on
    """

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
    """
    Defines the layout of a PLATE (parent of all associated wells)
    """

    class Meta(object):
        verbose_name = 'Assay Layout'
        ordering = ('layout_name',)

    layout_name = models.CharField(max_length=200)
    device = models.ForeignKey(Microdevice)

    # Specifies whether this is a standard (oft used layout)
    standard = models.BooleanField(default=False)

    #base_layout = models.ForeignKey(AssayBaseLayout)

    def __unicode__(self):
        return self.layout_name

    def get_post_submission_url(self):
        return "/assays/assaylayout/"

    def get_absolute_url(self):
        return "/assays/assaylayout/{}/".format(self.id)

    def get_delete_url(self):
        return '/assays/assaylayout/{}/delete/'.format(self.id)


class AssayWellType(LockableModel):
    """
    PLATE well type
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
    """
    An individual PLATE well
    """

    class Meta(object):
        unique_together = [('assay_layout', 'row', 'column')]

    #base_layout = models.ForeignKey(AssayBaseLayout)
    assay_layout = models.ForeignKey(AssayLayout)
    well_type = models.ForeignKey(AssayWellType)

    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayWellTimepoint(models.Model):
    """
    Timepoints for PLATE wells
    """

    assay_layout = models.ForeignKey(AssayLayout)
    timepoint = models.FloatField(default=0)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayWellCompound(models.Model):
    """
    Compound for PLATE wells
    """

    assay_layout = models.ForeignKey(AssayLayout)
    compound = models.ForeignKey('compounds.Compound')
    concentration = models.FloatField(default=0)
    concentration_unit = models.ForeignKey(PhysicalUnits)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayWellLabel(models.Model):
    """
    Arbitrary string label for PLATE wells
    """

    assay_layout = models.ForeignKey(AssayLayout)
    label = models.CharField(max_length=150)
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)


class AssayPlateCells(models.Model):
    """
    Individual cell parameters for PLATE setup used in inline
    """

    assay_plate = models.ForeignKey('AssayPlateSetup')
    cell_sample = models.ForeignKey('cellsamples.CellSample')
    cell_biosensor = models.ForeignKey('cellsamples.Biosensor')
    cellsample_density = models.FloatField(verbose_name='density', default=0)

    cellsample_density_unit = models.CharField(verbose_name='Unit',
                                               max_length=8,
                                               default="WE",
                                               choices=(('WE', 'cells / well'),
                                                        ('ML', 'cells / mL'),
                                                        ('MM', 'cells / mm^2')))
    cell_passage = models.CharField(max_length=16, verbose_name='Passage#',
                                    blank=True, default='')


class AssayPlateSetup(FlaggableModel):
    """
    Setup for MICROPLATES
    """

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
        return u'Plate-{}'.format(self.assay_plate_id)

    def get_absolute_url(self):
        return "/assays/assayplatesetup/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.assay_run_id_id)

    def get_clone_url(self):
        return '/assays/{0}/assayplatesetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assayplatesetup/{}/delete/'.format(self.id)


class AssayReader(LockableModel):
    """
    Chip and Plate readers
    """

    class Meta(object):
        ordering = ('reader_name',)

    reader_name = models.CharField(max_length=128)
    reader_type = models.CharField(max_length=128)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.reader_name, self.reader_type)


class AssayPlateReadoutAssay(models.Model):
    """
    Inline for PLATE readout assays
    """

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


class AssayReadout(models.Model):
    """
    An individual value for a PLATE readout
    """

    assay_device_readout = models.ForeignKey('assays.AssayPlateReadout')
    # A plate can have multiple assays, this differentiates between those assays
    assay = models.ForeignKey('assays.AssayPlateReadoutAssay')
    row = models.CharField(max_length=25)
    column = models.CharField(max_length=25)
    value = models.FloatField()
    elapsed_time = models.FloatField(default=0)

    # Quality, if it is not the empty string, indicates that a readout is INVALID
    quality = models.CharField(default='', max_length=10)

#class ReadoutUnit(LockableModel):
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


# Get readout file location
def plate_readout_file_location(instance, filename):
    return '/'.join(['csv', str(instance.setup.assay_run_id_id), 'plate', filename])


class AssayPlateReadout(FlaggableModel):
    """
    Readout data collected from MICROPLATES
    """

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
        return "/assays/assayplatereadout/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.setup.assay_run_id_id)

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
    """
    Function for analysis of CHIP RESULTS
    """
    class Meta(object):
        verbose_name = 'Function'
        ordering = ('function_name', )

    function_name = models.CharField(max_length=100, unique=True)
    function_results = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')

    def __unicode__(self):
        return self.function_name


class AssayResultType(LockableModel):
    """
    Result types for CHIP RESULTS
    """

    class Meta(object):
        verbose_name = 'Result type'
        ordering = ('assay_result_type', )

    assay_result_type = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True, default='')

    def __unicode__(self):
        return self.assay_result_type


class AssayPlateResult(models.Model):
    """
    Individual result parameters for PLATE RESULTS used in inline
    """

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


class AssayPlateTestResult(FlaggableModel):
    """
    Test Results from MICROPLATES
    """

    class Meta(object):
        verbose_name = 'Plate Result'

    readout = models.ForeignKey('assays.AssayPlateReadout',
                                verbose_name='Plate ID/ Barcode')
    summary = models.TextField(default='', blank=True)

    def __unicode__(self):
        return u'Results for: {}'.format(self.readout)

    def get_absolute_url(self):
        return "/assays/assayplatetestresult/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.readout.setup.assay_run_id_id)

    def get_delete_url(self):
        return '/assays/assayplatetestresult/{}/delete/'.format(self.id)


class StudyConfiguration(LockableModel):
    """
    Defines how chips are connected together (for integrated studies to come)
    """

    class Meta(object):
        verbose_name = 'Study Configuration'

    # Length subject to change
    name = models.CharField(max_length=50)
    study_format = models.CharField(
        max_length=11,
        choices=(('individual', 'Individual'), ('integrated', 'Integrated'),)
    )
    media_composition = models.CharField(max_length=1000, blank=True, default='')
    hardware_description = models.CharField(max_length=1000, blank=True, default='')
    # Subject to removal
    # image = models.ImageField(upload_to="configuration",null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/assays/studyconfiguration/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/studyconfiguration/"


class StudyModel(models.Model):
    """
    Individual connections for integrated models
    """

    study_configuration = models.ForeignKey(StudyConfiguration)
    label = models.CharField(max_length=2)
    organ = models.ForeignKey(OrganModel)
    sequence_number = models.IntegerField()
    output = models.CharField(max_length=20, blank=True, default='')
    # Subject to change
    integration_mode = models.CharField(max_length=13, choices=(('0', 'Not Connected'), ('1', 'Connected')))


class AssayRun(RestrictedModel):
    """
    The encapsulation of all data concerning some plate/chip project
    """

    class Meta(object):
        verbose_name = 'Study'
        verbose_name_plural = 'Studies'
        ordering = ('assay_run_id', )

    # Removed center_id for now: this field is basically for admins anyway
    # May add center_id back later, but group mostly serves the same purpose
    # center_id = models.ForeignKey('microdevices.MicrophysiologyCenter', verbose_name='Center(s)')
    # Study type now multiple boolean fields; May need to add more in the future
    toxicity = models.BooleanField(default=False)
    efficacy = models.BooleanField(default=False)
    disease = models.BooleanField(default=False)
    cell_characterization = models.BooleanField(default=False)
    # Subject to change
    study_configuration = models.ForeignKey(StudyConfiguration, blank=True, null=True)
    name = models.TextField(default='Study-01', verbose_name='Study Name',
                            help_text='Name-###')
    start_date = models.DateField(help_text='YYYY-MM-DD')
    assay_run_id = models.TextField(unique=True, verbose_name='Study ID',
                                    help_text="Standard format 'CenterID-YYYY-MM-DD-Name-###'")
    description = models.TextField(blank=True, default='')

    file = models.FileField(upload_to='study_protocol', verbose_name='Protocol File',
                            blank=True, null=True, help_text='Protocol File for Study')

    # Image for the study (some illustrative image)
    image = models.ImageField(upload_to='studies', null=True, blank=True)

    def study_types(self):
        types = ''
        if self.toxicity:
            types += 'TOX '
        if self.efficacy:
            types += 'EFF '
        if self.disease:
            types += 'DM '
        if self.cell_characterization:
            types += 'CC '
        return u'{0}'.format(types)

    def __unicode__(self):
        return self.assay_run_id

    def get_absolute_url(self):
        return "/assays/{}/".format(self.id)

    def get_delete_url(self):
        return '/assays/{}/delete/'.format(self.id)


class AssayChipRawData(models.Model):
    """
    Individual lines of readout data
    """

    # class Meta(object):
    #     unique_together = [('assay_chip_id', 'assay_id', 'field_id', 'elapsed_time')]

    assay_chip_id = models.ForeignKey('assays.AssayChipReadout')
    assay_id = models.ForeignKey('assays.AssayChipReadoutAssay')

    field_id = models.CharField(max_length=255, default='0')

    value = models.FloatField(null=True)

    elapsed_time = models.FloatField(default=0)

    # This value will act as quality control, if it evaluates True then the value is considered invalid
    quality = models.CharField(max_length=20, default='')


class AssayChipCells(models.Model):
    """
    Individual cell parameters for CHIP setup used in inline
    """
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


class AssayChipSetup(FlaggableModel):
    """
    The configuration of a Chip for implementing an assay
    """
    class Meta(object):
        verbose_name = 'Chip Setup'
        ordering = ('-assay_chip_id', 'assay_run_id', )

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

    #Control => control, Compound => compound; Abbreviate? Capitalize?
    chip_test_type = models.CharField(max_length=8, choices=(("control", "Control"), ("compound", "Compound")))

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
        if self.compound:
            return u'Chip-{}:{}({}{})'.format(
                self.assay_chip_id,
                self.compound,
                self.concentration,
                self.unit
            )
        else:
            return u'Chip-{}:Control'.format(self.assay_chip_id)

    def get_absolute_url(self):
        return "/assays/assaychipsetup/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.assay_run_id_id)

    def get_clone_url(self):
        return '/assays/{0}/assaychipsetup/add?clone={1}'.format(self.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assaychipsetup/{}/delete/'.format(self.id)

object_types = (
    ('F', 'Field'), ('C', 'Colony'), ('M', 'Media'), ('X', 'Other')
)


class AssayChipReadoutAssay(models.Model):
    """
    Inline for CHIP readout assays
    """

    class Meta(object):
        unique_together = [('readout_id', 'assay_id')]

    readout_id = models.ForeignKey('assays.AssayChipReadout', verbose_name='Readout')
    assay_id = models.ForeignKey('assays.AssayModel', verbose_name='Assay', null=True)
    reader_id = models.ForeignKey('assays.AssayReader', verbose_name='Reader')
    object_type = models.CharField(
        max_length=6,
        choices=object_types,
        verbose_name='Object of Interest',
        default='F'
    )
    readout_unit = models.ForeignKey(PhysicalUnits)

    def __unicode__(self):
        return u'{}'.format(self.assay_id)


# Get readout file location
def chip_readout_file_location(instance, filename):
    return '/'.join(['csv', str(instance.chip_setup.assay_run_id_id), 'chip', filename])


class AssayChipReadout(FlaggableModel):
    """
    Readout data for CHIPS
    """

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
        return u'{0}'.format(", ".join(list_of_assays))

    def __unicode__(self):
        return u'{0}'.format(self.chip_setup)

    def get_absolute_url(self):
        return "/assays/assaychipreadout/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.chip_setup.assay_run_id.id)

    def get_clone_url(self):
        return '/assays/{0}/assaychipreadout/add?clone={1}'.format(self.chip_setup.assay_run_id_id, self.id)

    def get_delete_url(self):
        return '/assays/assaychipreadout/{}/delete/'.format(self.id)


class AssayChipTestResult(FlaggableModel):
    """
    Results calculated from Raw Chip Data
    """

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
        SEVERITY_SCORE = dict((
            ('-1', 'UNKNOWN'), ('0', 'NEGATIVE'), ('1', '+'), ('2', '+ +'),
            ('3', '+ + +'), ('4', '+ + + +'), ('5', '+ + + + +')
        ))
        if self.id and not len(AssayChipResult.objects.filter(assay_result_id=self.id).order_by('id')) == 0:
            return SEVERITY_SCORE.get(AssayChipResult.objects.filter(
                assay_result_id=self.id
            ).order_by('id')[0].severity, 'None')
        return ''

    def get_absolute_url(self):
        return "/assays/assaychiptestresult/{}/".format(self.id)

    def get_post_submission_url(self):
        return "/assays/{}/".format(self.chip_readout.chip_setup.assay_run_id_id)

    def get_delete_url(self):
        return '/assays/assaychiptestresult/{}/delete/'.format(self.id)


class AssayChipResult(models.Model):
    """
    Individual result parameters for CHIP RESULTS used in inline
    """

    assay_name = models.ForeignKey('assays.AssayChipReadoutAssay',
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
