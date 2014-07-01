from django.db import models
from mps.base.models import LockableModel


class ResourceType(LockableModel):
    class Meta(object):
        ordering = ('resource_type_name',)

    resource_type_name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=400, blank=True, null=True)

    def __unicode__(self):
        return self.resource_type_name


class Resource(LockableModel):
    class Meta(object):
        ordering = ('resource_name', )

    resource_name = models.CharField(max_length=40, unique=True)
    resource_website = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    type = models.ForeignKey(ResourceType)

    def __unicode__(self):
        return self.source_name
