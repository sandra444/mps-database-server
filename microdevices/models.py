# coding=utf-8

from django.db import models
from django.contrib.auth.models import Group

from mps.base.models import LockableModel


class MicrophysiologyCenter(LockableModel):
    """Microphysiology Center gives details for a collaborating center

    Note that this is the model by which groups are affiliated with assays, cells, etc.
    """
    class Meta(object):
        ordering = ('center_name', )

    center_name = models.CharField(max_length=100)
    center_id = models.CharField(max_length=20, default='-')
    description = models.CharField(max_length=400, blank=True, default='')
    contact_person = models.CharField(max_length=250, blank=True, default='')
    center_website = models.URLField(blank=True, null=True)

    groups = models.ManyToManyField(Group)

    def __unicode__(self):
        return self.center_name


class Manufacturer(LockableModel):
    """Manufacturer gives details for a manufacturer of devices and/or componentry"""
    class Meta(object):
        ordering = ('manufacturer_name', )

    manufacturer_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=250, blank=True, default='')
    Manufacturer_website = models.URLField(blank=True, null=True)

    def __unicode__(self):
        return self.manufacturer_name


class Microdevice(LockableModel):
    """A Microdevice describes a physical vessel for performing experiments (a plate, chip, etc.)"""
    class Meta(object):
        ordering = ('device_name', 'organ', )

    device_name = models.CharField(max_length=200)

    organ = models.ForeignKey('cellsamples.Organ', blank=True, null=True)
    center = models.ForeignKey(MicrophysiologyCenter, blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, null=True, blank=True)
    barcode = models.CharField(
        max_length=200, verbose_name='version/ catalog#', default='', blank=True)

    description = models.CharField(max_length=400, default='', blank=True)

    device_width = models.FloatField(
        verbose_name='width (mm)', null=True, blank=True)
    device_length = models.FloatField(
        verbose_name='length (mm)', null=True, blank=True)
    device_thickness = models.FloatField(
        verbose_name='thickness (mm)', null=True, blank=True)
    device_size_unit = models.CharField(max_length=50, default='', blank=True)

    device_image = models.ImageField(upload_to='assays', null=True, blank=True)
    device_cross_section_image = models.ImageField(
        upload_to='assays', null=True, blank=True)

    device_fluid_volume = models.FloatField(verbose_name='device fluid volume (uL)', null=True, blank=True)
    # device fluid volume will now always be micro liters
    # device_fluid_volume_unit = models.CharField(
    #     max_length=50, null=True, blank=True)

    substrate_thickness = models.FloatField(
        verbose_name='substrate thickness (um)', null=True, blank=True)
    substrate_material = models.CharField(
        max_length=150, default='', blank=True)

    # Specify whether the device is a plate or a chip
    device_type = models.CharField(max_length=8,
                                   choices=(('chip', 'Microchip'),
                                            ('plate', 'Plate')))

    # Optional fields primarily intended for plates
    # (though certain chips appear in a series)
    number_of_rows = models.IntegerField(blank=True, null=True)
    number_of_columns = models.IntegerField(blank=True, null=True)
    row_labels = models.CharField(blank=True,
                                  default='',
                                  max_length=1000,
                                  help_text=
                                  'Space separated list of unique labels, '
                                  'e.g. "A B C D ..."'
                                  ' Number of items must match'
                                  ' number of columns.')
    column_labels = models.CharField(blank=True,
                                     default='',
                                     max_length=1000,
                                     help_text='Space separated list of unique '
                                               'labels, e.g. "1 2 3 4 ...". '
                                               'Number of items must match '
                                               'number of columns.')

    def __unicode__(self):
        return self.device_name

    def get_absolute_url(self):
        return "/microdevices/device/{}/".format(self.id)

    def get_post_submission_url(self):
        return '/microdevices/device/'


class OrganModel(LockableModel):
    """An Organ Model describes a way of preparing a device to emulate a particular organ"""
    class Meta(object):
        verbose_name = 'Organ Model'
        ordering = ('model_name', 'organ', )

    model_name = models.CharField(max_length=200)
    organ = models.ForeignKey('cellsamples.Organ')
    center = models.ForeignKey(MicrophysiologyCenter, null=True, blank=True)
    device = models.ForeignKey(Microdevice)
    description = models.CharField(max_length=400, default='', blank=True)

    model_image = models.ImageField(upload_to='models', null=True, blank=True)

    epa = models.BooleanField(
        default=False,
        help_text='Whether this compound is part of the EPA project'
    )
    mps = models.BooleanField(
        default=False,
        help_text='Whether this compound is part of the MPS project'
    )

    # Removed in favor of protocol inline
    # protocol = models.FileField(upload_to='protocols', verbose_name='Protocol File',
    #                        blank=True, null=True, help_text='File detailing the protocols for this model')

    def __unicode__(self):
        return self.model_name

    def get_absolute_url(self):
        return "/microdevices/model/{}/".format(self.id)

    def get_post_submission_url(self):
        return '/microdevices/model/'


# It is somewhat odd that ValidatedAssays are inlines in lieu of a manytomany field
# This was done originally so that additional fields could be added to a validated assay
# If no new fields become apparent, it may be worthwhile to do away with inlines and move to M2M
class ValidatedAssay(models.Model):
    """Validated Assays show which assays have been approved for a particular Organ Model"""
    # Validated assays for an organ model used in inline
    organ_model = models.ForeignKey(OrganModel, verbose_name='Organ Model')
    assay = models.ForeignKey('assays.AssayModel', verbose_name='Assay Model')


class OrganModelProtocol(models.Model):
    """Organ Model Protocols point to a file detailing the preparation of a model

    This model is intended to be an inline
    """

    class Meta(object):
        unique_together = [('version', 'organ_model')]

    organ_model = models.ForeignKey(OrganModel, verbose_name='Organ Model')
    version = models.CharField(max_length=20)
    file = models.FileField(upload_to='protocols', verbose_name='Protocol File')

    def __unicode__(self):
        return self.version
