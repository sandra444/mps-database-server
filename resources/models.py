from django.db import models
from mps.base.models import LockableModel


class ResourceSubtype(LockableModel):
    class Meta(object):
        ordering = ['name']

    name = models.TextField(max_length=40, unique=True)
    description = models.TextField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return self.name


class ResourceType(LockableModel):
    class Meta(object):
        ordering = ['resource_type_name', 'resource_subtype']

    resource_type_name = models.CharField(max_length=40, unique=True, verbose_name="Name")
    description = models.CharField(max_length=400, blank=True, null=True)
    resource_subtype = models.ForeignKey(ResourceSubtype, verbose_name="Subtype")

    def __unicode__(self):
        return self.resource_type_name


class Resource(LockableModel):
    class Meta(object):
        ordering = ['type', 'resource_subtype', 'resource_name']

    resource_name = models.CharField(max_length=60, unique=True, verbose_name="Name")
    resource_website = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    type = models.ForeignKey(ResourceType)

    def __unicode__(self):
        return self.resource_name

    def subtype(self):
        return self.type.resource_subtype.name


