from django import template
from microdevices.models import MicrophysiologyCenter
from django.contrib.auth.models import Group

register = template.Library()

# AVOID MAGIC STRINGS
VIEWER_SUFFIX = ' Viewer'
ADMIN_SUFFIX = ' Admin'

# One of the tricky things about filters is that they spawn a SQL query each time they are invoked!
@register.filter(name='has_group')
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


# PLEASE BE SURE TO USE is_group_editor IN LIEU OF has_group WHEN NECESSARY
@register.filter(name='is_group_editor')
def is_group_editor(user, group_name):
    """Returns whether or not the user has a group editorship privileges

        Params:
        user - The user in question (as a Django model)
        group_name - The group name (as a string, as opposed to a Django model)
        """
    # In case something has gone wrong, err on the side of caution and deny access
    if not group_name:
        return False

    if user.groups.filter(name__in=[group_name, group_name + ADMIN_SUFFIX]):
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

    if user.groups.filter(name__in=[group_name, group_name + VIEWER_SUFFIX, group_name + ADMIN_SUFFIX]):
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

    if user.groups.filter(name=group_name + ADMIN_SUFFIX):
        return True
    else:
        return False


def filter_groups(user):
    """Filters out groups that can't be used with models

    Params:
    user - The user in question (as a Django model)
    """
    groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
    groups_with_center_full = Group.objects.filter(id__in=groups_with_center)

    groups_with_center_map = {}

    for group in groups_with_center_full:
        groups_with_center_map.update({
            group.name: group.id
        })

    groups_for_user = []

    for group in user.groups.all():
        trimmed_group_name = group.name.replace(ADMIN_SUFFIX, '')
        if trimmed_group_name in groups_with_center_map:
            groups_for_user.append(groups_with_center_map.get(trimmed_group_name))

    group_set = groups_with_center_full.filter(id__in=groups_for_user).order_by('name')

    return group_set
