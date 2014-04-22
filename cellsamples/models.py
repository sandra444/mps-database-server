# coding=utf-8

"""

CellSamples Models

"""

from django.db import models

# Use our own model base classes instead of models.Model
from mps.base.models import LockableModel


class Organ(models.Model):
    organ_name = models.CharField(max_length=255, unique=True)

    class Meta(object):
        ordering = ('organ_name', )

    def __unicode__(self):
        return u'{}'.format(self.organ_name)


class CellType(models.Model):
    SPECIESTYPE = (
        ('Human', 'Human'),
        ('Rat', 'Rat'),
    )
    cell_type = models.CharField(max_length=255, unique=True,
                                 help_text='Example: hepatocyte, muscle, kidney, etc')
    species = models.CharField(max_length=10,
                               choices=SPECIESTYPE, default='Human', null=True,
                               blank=True)

    cell_subtype = models.ForeignKey('CellSubtype')
    organ = models.ForeignKey('Organ')

    class Meta(object):
        ordering = ('cell_type', 'species', 'cell_subtype',)
        unique_together = [('cell_type', 'species', 'cell_subtype')]


    def __unicode__(self):
        return u'{} {} {}'.format(self.cell_subtype,
                                  self.species,
                                  self.cell_type)

    def cell_name(self):
        return self.__unicode__()


class CellSubtype(models.Model):
    cell_subtype = models.CharField(max_length=255, unique=True,
                                    help_text="Example: motor (type of neuron), "
                                              "skeletal (type of muscle), etc.")

    def __unicode__(self):
        return u'{}'.format(self.cell_subtype)


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return u'{}'.format(self.name)


class CellSample(LockableModel):
    cell_type = models.ForeignKey('CellType')
    CELLSOURCETYPE = (
        ('Freshly isolated', 'Freshly isolated'),
        ('Cryopreserved', 'Cryopreserved'),
        ('Cultured', 'Cultured'),
        ('Other', 'Other'),
    )
    cell_source = models.CharField(max_length=20,
                                   choices=CELLSOURCETYPE, default='Primary',
                                   null=True, blank=True)
    notes = models.TextField(blank=True)
    receipt_date = models.DateField()

    # SAMPLE

    supplier = models.ForeignKey('Supplier')
    barcode = models.CharField(max_length=255, blank=True, verbose_name='Barcode/Lot#')
    product_id = models.CharField(max_length=255, blank=True)

    # PATIENT

    GENDER_CHOICES = (
        ('N', 'Not-specified'),
        ('F', 'Female'),
        ('M', 'Male'),
    )
    patient_age = models.IntegerField(null=True, blank=True)
    patient_gender = models.CharField(max_length=1, choices=GENDER_CHOICES,
                                      default=GENDER_CHOICES[0][0],
                                      blank=True)
    patient_condition = models.CharField(max_length=255,
                                         blank=True)

    # ISOLATION

    isolation_datetime = models.DateTimeField("Isolation")
    isolation_method = models.CharField("Method", max_length=255,
                                        blank=True)
    isolation_notes = models.CharField("Notes", max_length=255,
                                       blank=True)

    # VIABILITY

    viable_count = models.FloatField(null=True, blank=True)
    VIABLE_COUNT_UNIT_CHOICES = (
        ('N', 'Not-specified'),
        ('A', 'per area'),
        ('V', 'per volume'),
    )
    viable_count_unit = models.CharField(max_length=1,
                                         choices=VIABLE_COUNT_UNIT_CHOICES,
                                         default=VIABLE_COUNT_UNIT_CHOICES[0][
                                             0], blank=True)
    percent_viability = models.FloatField(null=True, blank=True)
    cell_image = models.ImageField(upload_to='cellsamples',
                                   null=True, blank=True)

    def __unicode__(self):
        return u'#{} {} {} supplied by {}'.format(self.id,
                                                  self.cell_source,
                                                  self.cell_type,
                                                  self.supplier)
