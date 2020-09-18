from django.db import models
from mps.base.models import LockableModel
from django.utils.html import format_html

from django.utils.safestring import mark_safe


class ResourceSubtype(LockableModel):
    """A Resource Subtype specifies a category (e.g. supplier, database, etc.

    PLEASE NOTE: Subtype is referred to as a 'Category' typically
    """
    class Meta(object):
        verbose_name = 'Resource category'
        verbose_name_plural = 'Resource categories'
        ordering = ['name']

    name = models.TextField(max_length=40, unique=True, verbose_name='Category')
    description = models.TextField(max_length=400, blank=True, default='')

    def __str__(self):
        return self.name


class ResourceType(LockableModel):
    """A Resource Type specifies what a resource specializes in (e.g. images, cells, etc.)"""
    class Meta(object):
        ordering = ['resource_subtype', 'resource_type_name']

    resource_type_name = models.CharField(max_length=40, unique=True, verbose_name="Type")
    description = models.CharField(max_length=400, blank=True, default='')
    resource_subtype = models.ForeignKey(ResourceSubtype, verbose_name="Category", on_delete=models.CASCADE)

    def __str__(self):
        return '{} ({})'.format(self.resource_subtype,
                                 self.resource_type_name)


class Resource(LockableModel):
    """A Resource is a specific website or location to learn more of something"""
    class Meta(object):
        ordering = ['type', 'resource_name']

    resource_name = models.CharField(max_length=60, unique=True, verbose_name="Name")
    resource_website = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, default='')
    type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)

    def __str__(self):
        return self.resource_name

    def subtype(self):
        return self.type.resource_subtype.name


class Definition(LockableModel):
    """A Definition is a definition for the glossary found in Help"""
    class Meta(object):
        verbose_name = 'Help - Glossary'
        verbose_name_plural = 'Help - Glossary'
    term = models.CharField(max_length=60, unique=True)
    definition = models.CharField(max_length=2500, default='')
    reference = models.URLField(default='', blank=True)

    def __str__(self):
        return self.term

    @mark_safe
    def show_url(self):
        if self.reference:
            return format_html(
                "<a target='_blank' href='{url}'><span title='{url}' class='glyphicon glyphicon-link'></span></a>", url=self.reference
            )
        else:
            return ""

    show_url.short_description = "Ref URL"
    show_url.allow_tags = True


class ComingSoonEntry(LockableModel):
    """An entry for the About Page's "Coming Soon" Section"""
    class Meta(object):
        verbose_name = 'Coming Soon Entry'
        verbose_name_plural = 'Coming Soon Entries'

    contents = models.TextField(default='')


class WhatIsNewEntry(LockableModel):
    """An entry for the About Page's "What's New" Section"""
    class Meta(object):
        verbose_name = 'What\'s New Entry'
        verbose_name_plural = 'What\'s New Entries'

    contents = models.TextField(default='')
    short_contents = models.TextField(default='')

class DataSource(LockableModel):
    """Data Sources (external) - for table in Help"""
    class Meta(object):
        verbose_name = 'Help - Data Source'
        verbose_name_plural = 'Help - Data Sources'
        unique_together = [
            (
                'name', 'source_number',
            )
        ]
    name = models.CharField(max_length=60, unique=True)
    source_number = models.IntegerField(
        default=999,
    )
    description = models.CharField(max_length=2500, default='')
    curation = models.CharField(max_length=2500, default='')

    def __str__(self):
        return '{}'.format(self.source_number)


class DatabaseFeature(LockableModel):
    """Database Features - for table in Help"""
    class Meta(object):
        verbose_name = 'Help - Database Feature'
        verbose_name_plural = 'Help - Database Features'

    name = models.CharField(max_length=60, unique=True)
    description = models.CharField(max_length=2500, default='')

    def __str__(self):
        return self.name

class FeatureSourceXref(LockableModel):
    """Database Features - for table in Help"""
    class Meta(object):
        verbose_name = 'Help - Database Features & Sources'
        verbose_name_plural = 'Help - Database Features & Sources'
        unique_together = [
            (
                'database_feature', 'data_source'
            )
        ]
    database_feature = models.ForeignKey(
        DatabaseFeature,
        blank=True,
        default=1,
        on_delete=models.CASCADE
    )
    data_source = models.ForeignKey(
        DataSource,
        blank=True,
        default=1,
        on_delete=models.CASCADE
    )
