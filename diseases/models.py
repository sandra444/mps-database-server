from django.db import models
from mps.base.models import LockableModel


class Disease(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(default='', blank=True)

    # Everything necessary for the Overview Page
    overview_state_blurb = models.TextField(default='', blank=True)
    overview_state_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    overview_biology_blurb = models.TextField(default='', blank=True)
    overview_biology_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    overview_clinicaldata_blurb = models.TextField(default='', blank=True)
    overview_clinicaldata_image = models.ImageField(upload_to='disease_images', null=True, blank=True)
    overview_clinicaldata_num_results = models.IntegerField(default=0, null=True, blank=True)
    overview_clinicaldata_num_phaseI = models.IntegerField(default=0, null=True, blank=True)
    overview_clinicaldata_num_phaseII = models.IntegerField(default=0, null=True, blank=True)
    overview_clinicaldata_num_phaseIII = models.IntegerField(default=0, null=True, blank=True)
    overview_clinicaldata_num_phaseIV = models.IntegerField(default=0, null=True, blank=True)

    overview_models_blurb = models.TextField(default='', blank=True)
    overview_models_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    overview_data_blurb = models.TextField(default='', blank=True)
    overview_data_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    # Everything necessary for the Biology Page
    biology_blurb = models.TextField(default='', blank=True)
    biology_image = models.ImageField(upload_to='disease_images', null=True, blank=True)
    kegg_pathway_map = models.ImageField(upload_to='disease_images', null=True, blank=True)

    # Everything necessary for the Clinical Data Page
    clinicaldata_blurb = models.TextField(default='', blank=True)
    clinicaldata_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    # Everything necessary for the Disease Models Page
    models_blurb = models.TextField(default='', blank=True)
    models_image = models.ImageField(upload_to='disease_images', null=True, blank=True)

    # Everything necessary for the Data Analysis Page

    def __unicode__(self):
       return self.name


# class DiseaseOverviewClinicalTrialTableRow(models.Model):
#     disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
#     name = models.CharField(max_length=200, default='', blank=True)
#     description = models.TextField(default='', blank=True)
#     num_results = models.IntegerField(default=0)
#     num_phaseI = models.IntegerField(default=0)
#     num_phaseII = models.IntegerField(default=0)
#     num_phaseIII = models.IntegerField(default=0)
#     num_phaseIV = models.IntegerField(default=0)
#
# class DiseaseBiologyGenomicDatabasesTableRow(models.Model):
#     disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
#     name = models.CharField(max_length=200, default='', blank=True)
#     description = models.TextField(default='', blank=True)
#     url = models.CharField(max_length=200, default='', blank=True)
#
# class DiseaseOtherResources(models.Model):
#     disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
#     name = models.CharField(max_length=200, default='', blank=True)
#     description = models.TextField(default='', blank=True)
#     url = models.CharField(max_length=200, default='', blank=True)
