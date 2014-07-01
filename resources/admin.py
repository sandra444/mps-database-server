from django.contrib import admin
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe

from mps.base.admin import LockableAdmin
from resources.models import *


#don't know if this is necessary

# class URLFieldWidget(AdminURLFieldWidget):
#     def render(self, name, value, attrs=None):
#         widget = super(URLFieldWidget, self).render(name, value, attrs)
#
#         html = \
#             u'<div style="width: 55em; height: 4em;">' \
#             u'<div>' \
#             u'{0}' \
#             u'</div>' \
#             u'<div style="float: right; z-index: 10;' \
#             u' margin-top: -3em; margin-right: -25em;">' \
#             u'<input type="button" ' \
#             u'value="Click here to open the URL in a new window." ' \
#             u'style="float: right; clear: both;" ' \
#             u'onclick="window.' \
#             u'open(document.getElementById(\'{1}\')' \
#             u'.value)" />' \
#             u'</div>' \
#             u'</div>'.format(widget, attrs['id'])
#
#         return mark_safe(html)


class ResourceAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('resource_name', 'type', 'resource_website', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'resource_name',
                    'type'
                    'resource_website',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    actions = ['update_fields']


admin.site.register(Resource, ResourceAdmin)


class ResourceTypeAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300

    fieldsets = (
        (
            None, {
                'fields': (
                    'resource_type_name',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    actions = ['update_fields']


admin.site.register(ResourceType, ResourceTypeAdmin)
