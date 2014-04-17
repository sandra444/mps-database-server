# coding=utf-8

"""

Base Models

"""

from django.db import models


class TrackableModel(models.Model):
    """

    The base model for Trackable models

    NOTE: the "read-only" configuration method resides in base/admin.py

    """

    # CREATION DATA #

    created_by = models.ForeignKey('auth.User',
                                   related_name='%(class)s_created-by',
                                   blank=True,
                                   null=True)

    created_on = models.DateTimeField(auto_now_add=True,
                                      blank=True,
                                      null=True)

    # MODIFICATION DATA #

    modified_by = models.ForeignKey('auth.User',
                                    related_name='%(class)s_modified-by',
                                    blank=True,
                                    null=True)

    modified_on = models.DateTimeField(auto_now=True,
                                       blank=True,
                                       null=True)

    class Meta(object):
        abstract = True


class LockableModel(TrackableModel):
    """

    The base model for Lockable models

    """

    locked = models.BooleanField(default=False,
                                 help_text=
                                 'Check the box and save to lock the entry. '
                                 'Uncheck and save to enable editing.')

    class Meta(object):
        abstract = True
