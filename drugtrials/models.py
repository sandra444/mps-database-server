from django.db import models

from mps.base.models import LockableModel
from microdevices.models import OrganModel
from cellsamples.models import Organ

from assays.models import PhysicalUnits

from django.core.exceptions import ValidationError


class Species(LockableModel):
    class Meta(object):
        verbose_name_plural = 'species'
        ordering = ('species_name', )

    species_name = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.species_name


PARTICIPANTTYPES = (
    ('I', 'Individual'),
    ('P', 'Population'),
)

TRIALSUBTYPES = (
    ('C', 'Case Report'),
    ('P', 'Population Report'),
    ('U', 'Unknown / Unspecified'),
)

# Participants information is now part of DrugTrials model
# instead of a seperate entity


class TrialSource(LockableModel):
    class Meta(object):
        ordering = ('source_name', )
    source_name = models.CharField(max_length=40, unique=True)
    source_website = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return self.source_name


TRIALTYPES = (
    ('S', 'Microphysiology'),
    ('P', 'Preclinical'),
    ('C', 'Clinical'),
    ('M', 'Post-marketing'),
    ('B', 'Combined Clinical-Post Market'),
    ('U', 'Unknown / Unspecified'),
)


class DrugTrial(LockableModel):
    class Meta(object):
        verbose_name = 'Drug Trial'
        ordering = ('compound', 'species', )

    title = models.CharField(max_length=255, blank=True, null=True)
    condition = models.CharField(max_length=1400, blank=True, null=True)
    source = models.ForeignKey(TrialSource)
    compound = models.ForeignKey('compounds.Compound')

    # Figures
    figure1 = models.ImageField(upload_to='figures', null=True, blank=True)
    figure2 = models.ImageField(upload_to='figures', null=True, blank=True)

    # Participant Information

    species = models.ForeignKey(Species,
                                default='1',
                                blank=True,
                                null=True)

    gender = models.CharField(max_length=1,
                              choices=(
                                  ('F', 'female'), ('M', 'male'),
                                  ('X', 'mixed'),
                                  ('U', 'unknown or unspecified'),
                              ),
                              default='U',
                              blank=True,
                              null=True)

    population_size = models.CharField(max_length=50,
                                       default='1',
                                       blank=True,
                                       null=True)

    age_average = models.FloatField(blank=True, null=True)

    age_max = models.FloatField(blank=True, null=True)

    age_min = models.FloatField(blank=True, null=True)

    age_unit = models.CharField(max_length=1,
                                blank=True,
                                null=True,
                                choices=(
                                    ('M', 'months'), ('Y', 'years')
                                ),
                                default='Y')

    weight_average = models.FloatField(blank=True, null=True)
    weight_max = models.FloatField(blank=True, null=True)
    weight_min = models.FloatField(blank=True, null=True)
    weight_unit = models.CharField(max_length=1, blank=True, null=True,
                                   choices=(
                                       ('K', 'kilograms'), ('L', 'pounds'),
                                   ),
                                   default='L')

    # End of Participant Information

    trial_type = models.CharField(max_length=1, choices=TRIALTYPES)
    trial_sub_type = models.CharField(max_length=1,
                                      choices=TRIALSUBTYPES, default='C')
    trial_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=1400, blank=True, null=True)
    source_link = models.URLField(blank=True, null=True)
    references = models.CharField(max_length=400, null=True,
                                  verbose_name='Trial ID/Reference')

    def __unicode__(self):
        return u'{} for {} from {}'.format(dict(TRIALTYPES)[self.trial_type],
                                           self.compound.name,
                                           self.source.source_name)

    def get_absolute_url(self):
        return "/drugtrials/{}".format(self.id)

class TestType(LockableModel):
    class Meta(object):
        ordering = ('test_type',)
    test_type = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.test_type


class Test(LockableModel):
    class Meta(object):
        unique_together = [('test_type', 'test_name')]
        ordering = ('test_name', 'organ', 'test_type', )

    organ_model = models.ForeignKey(OrganModel,
                                    blank=True, null=True)
    test_type = models.ForeignKey(TestType)
    test_name = models.CharField(max_length=40,
                                 verbose_name='Organ Function Test')
    test_unit = models.CharField(max_length=40, blank=True, null=True)
    organ = models.ForeignKey(Organ, blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return u'{} :: {} :: {}'.format(self.organ,
                                        self.test_type,
                                        self.test_name
                                        )


class FindingType(LockableModel):
    class Meta(object):
        ordering = ('finding_type', )

    finding_type = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.finding_type


class Finding(LockableModel):
    class Meta(object):
        unique_together = [('organ', 'finding_name')]
        ordering = ('organ', 'finding_type', 'finding_name', )

    finding_type = models.ForeignKey(FindingType)
    finding_name = models.CharField(max_length=100)
    finding_unit = models.CharField(max_length=40, blank=True, null=True)
    organ = models.ForeignKey(Organ,
                              blank=True,
                              null=True)
    description = models.CharField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return u'{} :: {} :: {}'.format(self.organ, self.finding_type, self.finding_name)


class ResultDescriptor(LockableModel):
    class Meta(object):
        ordering = ('result_descriptor', )
    result_descriptor = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return self.result_descriptor


SEVERITY_SCORE = (
    ('-1', 'UNKNOWN'), ('0', 'NEGATIVE'), ('1', '+'), ('2', '+ +'),
    ('3', '+ + +'), ('4', '+ + + +'), ('5', '+ + + + +')
)

# This is legacy code
TIME_UNITS = (
    ('u', 'unknown'), ('h', 'hours'), ('d', 'days'),
    ('w', 'weeks'), ('m', 'months'), ('y', 'years')
)

POSNEG = (
    ('0', 'Neg'), ('1', 'Pos')
)

RESULT_TYPE = (
    ('B', 'Biopsy'), ('R', 'Report'), ('M', 'Mechanism'), ('I', 'Information')
)


class TestResult(models.Model):

    drug_trial = models.ForeignKey(DrugTrial)

    test_name = models.ForeignKey(Test,
                                  verbose_name='Test',
                                  blank=True,
                                  null=True)

    test_time = models.FloatField(verbose_name='Time', blank=True, null=True)

    time_units = models.ForeignKey(PhysicalUnits,
                                   blank=True,
                                   null=True,
                                   related_name='test_time_units')

    result = models.CharField(default='1',
                              max_length=8,
                              choices=POSNEG,
                              verbose_name='Pos/Neg?',
                              blank=True,
                              null=True)

    severity = models.CharField(default='-1',
                                max_length=5,
                                choices=SEVERITY_SCORE,
                                verbose_name='Severity',
                                blank=True,
                                null=True)

    percent_min = models.FloatField(blank=True,
                                    null=True,
                                    verbose_name='Min Affected (% Population)')

    percent_max = models.FloatField(blank=True,
                                    null=True,
                                    verbose_name='Max Affected (% Population)')

    descriptor = models.ForeignKey(ResultDescriptor, blank=True, null=True)

    value = models.FloatField(blank=True, null=True)

    value_units = models.ForeignKey(PhysicalUnits, blank=True, null=True, related_name='test_value_units')

    def clean(self):
        """

        Require units to be specified if a value is present

        """

        if self.value or self.value_units:
            if not (self.drug_trial.source and self.drug_trial.source_link
                    and self.value_units and self.value):
                raise ValidationError(
                    "Values and units must have a defined source "
                    "and source link"
                )

        if self.value:
            if not self.value_units:
                raise ValidationError(
                    "You must specify valid units "
                    "for the value you entered"
                )

        if not self.value:
            if self.value_units:
                raise ValidationError("You forgot to enter a value!")

    def __unicode__(self):
        return u''

FREQUENCIES = (
    ('>= 10%','>= 10% : Very Common'), ('1 - < 10%', '1 - < 10% : Common'),
    ('0.1 - < 1%', '0.1 - < 1% : Uncommon'), ('0.01 - < 0.1%', '0.01 - < 0.1% : Rare'),
    ('< 0.01%', '< 0.01% : Very Rare')
)


class FindingResult(models.Model):

    drug_trial = models.ForeignKey(DrugTrial)

    finding_name = models.ForeignKey(Finding,
                                     verbose_name='Finding')

    finding_time = models.FloatField(verbose_name='Time', blank=True, null=True)

    time_units = models.ForeignKey(PhysicalUnits, blank=True, null=True, related_name='finding_time_units')

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

    # May drop percent_min later, hide for now
    percent_min = models.FloatField(blank=True,
                                    null=True,
                                    verbose_name='Min Affected (% Population)')

    # May drop percent_max later, hide for now
    percent_max = models.FloatField(blank=True,
                                    null=True,
                                    verbose_name='Max Affected (% Population)')

    frequency = models.CharField(choices=FREQUENCIES,
                                 max_length=25,
                                 blank=True,
                                 null=True,)

    descriptor = models.ForeignKey(ResultDescriptor, blank=True, null=True)

    value = models.FloatField(blank=True, null=True)

    value_units = models.ForeignKey(PhysicalUnits, blank=True, null=True, related_name='finding_value_units')

    def __unicode__(self):
        return u''


class AdverseEvent(models.Model):

    event = models.CharField(max_length=100)
    organ = models.ForeignKey(Organ, blank=True, null=True)

    def __unicode__(self):
        return u'{}'.format(self.event)


# TODO think of a better name
# TODO what other fields should be placed here?
# Theoretically, we would place usage information here, but that is difficult to acquire
# If we can't think of anything, scrap this model before you put it on production
class OpenFDACompound(LockableModel):

    class Meta(object):
        verbose_name = 'OpenFDA Report'

    compound = models.ForeignKey('compounds.Compound')
    warnings = models.TextField(blank=True, null=True)
    black_box = models.BooleanField(default=False)

    # Insights into non-human toxicology (can be useful)
    nonclinical_toxicology = models.TextField(blank=True, null=True)

    # Deemed less than useful
    #clinical_studies = models.TextField(blank=True, null=True)
    # Deemed less than useful
    # laboratory_tests = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'{}'.format(self.compound.name)

    def get_absolute_url(self):
        return "/adverse_events/{}".format(self.id)


class CompoundAdverseEvent(models.Model):

    # CompoundAdverseEvents are inlines in OpenFDACompound (name subject to change)
    compound = models.ForeignKey('OpenFDACompound')
    event = models.ForeignKey(AdverseEvent)
    frequency = models.IntegerField()

    def __unicode__(self):
        return u'{}:{}'.format(self.compound,self.event)

