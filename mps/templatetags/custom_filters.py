from django import template
from django.contrib.auth.models import Group

register = template.Library()

# This filter is not currently used within templates, though in theoretically could be
@register.filter(name='has_group')
def has_group(user, group_name):
    """Returns whether or not the user has a specified group"""
    if not group_name:
        return True

    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

    # groups = { group: True for group in user.groups.all() }
    # return True if group_name in groups else False
