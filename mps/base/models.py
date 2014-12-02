# coding=utf-8

"""

Base Models

"""

from django.db import models
from django.core.exceptions import ValidationError


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

    signed_off_by = models.ForeignKey('auth.User',
                                      related_name='%(class)s_signed_off_by',
                                      blank=True,
                                      null=True)

    signed_off_date = models.DateTimeField(blank=True,
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


class RestrictedModel(LockableModel):
    """

    The base model for Restricted models

    """

    group = models.ForeignKey('auth.Group',
                                      blank=True,
                                      null=True,
                                      help_text=
                                      'Bind to a group')

    restricted = models.BooleanField(default=False,
                                     help_text=
                                     'Check box to restrict to selected group')

    def clean(self):
        """
        Require at least one of ipv4 or ipv6 to be set
        """
        if self.restricted and not self.group:
            raise ValidationError("Can not restrict to NULL group")

    class Meta(object):
        abstract = True
