from django import template
from microdevices.models import MicrophysiologyCenter
# from django.contrib.auth.models import Group

register = template.Library()


# This filter is not currently used within templates, though in theoretically could be
# @register.filter(name='has_group')
def has_group(user, group_name):
    """Returns whether or not the user has a specified group

    Params:
    user - The user in question (as a Django model)
    group_name - The group name (as a string, as opposed to a Django model)
    """
    # In case something has gone wrong, err on the side of caution and deny access
    if not group_name:
        return False

    if user.groups.filter(name=group_name):
        return True
    else:
        return False


def is_group_viewer(user, group_name):
    """Checks whether the user has permission to view items from the given group

    Params:
    user - The user in question (as a Django model)
    group_name - The group name (as a string, as opposed to a Django model)
    """
    # In case something has gone wrong, err on the side of caution and deny access
    if not group_name:
        return False

    if user.groups.filter(name__in=[group_name, group_name + ' Viewer']):
        return True
    else:
        return False


# Superfluous: too similar to has_group?
# def is_group_editor(user, group_name):
#     """Checks whether the user has permission to edit items from the given group
#
#     Params:
#     user - The user in question (as a Django model)
#     group_name - The group name (as a string, as opposed to a Django model)
#     """
#     # In case something has gone wrong, err on the side of caution and deny access
#     if not group_name:
#         return False
#
#     if user.groups.filter(name=group_name):
#         return True
#     else:
#         return False


@register.filter(name='is_group_admin')
def is_group_admin(user, group_name):
    """Checks whether the user has administrative privilages for the group

    Params:
    user - The user in question (as a Django model)
    group_name - The group name (as a string, as opposed to a Django model)
    """
    # In case something has gone wrong, err on the side of caution and deny access
    if not group_name:
        return False

    if user.groups.filter(name=group_name + ' Admin'):
        return True
    else:
        return False


def filter_groups(user):
    """Filters out groups that can't be used with models

    Params:
    user - The user in question (as a Django model)
    """
    groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
    return user.groups.filter(id__in=groups_with_center).order_by('name')
