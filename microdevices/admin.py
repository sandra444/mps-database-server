# coding=utf-8

from django.contrib import admin
from mps.base.admin import LockableAdmin
from .models import MicrophysiologyCenter, Manufacturer, Microdevice, OrganModel
from drugtrials.models import Test


class MicrophysiologyCenterAdmin(LockableAdmin):
    save_on_top = True
    list_display = (
        'center_name', 'description', 'contact_person', 'center_website')
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                    'center_name',
                    'description',
                    'contact_person',
                    'center_website',
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

admin.site.register(MicrophysiologyCenter, MicrophysiologyCenterAdmin)


class ManufacturerAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                'manufacturer_name',
                'contact_person',
                'Manufacturer_website',
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

admin.site.register(Manufacturer, ManufacturerAdmin)


class MicrodeviceAdmin(LockableAdmin):

    def device_image_display(self, obj):
        if obj.id and obj.device_image:
            return '<img src="%s">' % \
                   obj.device_image.url
        return ''

    def device_cross_section_image_display(self, obj):
        if obj.id and obj.device_cross_section_image:
            return '<img src="%s">' % \
                   obj.device_cross_section_image.url
        return ''
    device_image_display.allow_tags = True
    device_cross_section_image_display.allow_tags = True

    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = ('device_name', 'organ', 'center', 'manufacturer',
                    'description')
    search_fields = ['device_name', 'organ', 'center',  'description']
    list_filter = ['organ', 'center', ]

    fieldsets = (
        (
            None, {
                'fields': (
                    (
                        'center', 'manufacturer',
                    ),
                    (
                        'device_name', 'organ',
                    ),
                    (
                        'description', 'barcode',
                    ),
                    (
                        'device_image_display',
                        'device_cross_section_image_display',
                    ),
                )
            }
        ),
        (
            'Dimensions', {
                'fields': (
                    (
                        'device_width', 'device_length', 'device_thickness',
                    ),
                    (
                        'device_fluid_volume', 'device_fluid_volume_unit',
                    ),
                    (
                        'substrate_material', 'substrate_thickness',
                    ),
                    (
                        'device_image', 'device_cross_section_image',
                    ),
                )
            }
        ),
        (
            None, {
                'fields': (
                    'locked',
                    'created_by',
                    'modified_by',
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    actions = ['update_fields']

    readonly_fields = (
        'device_image_display', 'device_cross_section_image_display',
    )

admin.site.register(Microdevice, MicrodeviceAdmin)


class TestInline(admin.TabularInline):
    model = Test
    extra = 1
    exclude = ['created_by', 'modified_by']
    fields = ('locked', 'test_name', 'test_type', 'test_unit', 'description')

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class OrganModelAdmin(LockableAdmin):
    list_per_page = 300
    filter_horizontal = ('cell_type',)
    list_display = (
        'model_name', 'organ', 'device', 'cell_types', 'center', 'description')
    search_fields = [
        'model_name', 'organ', 'device', 'cell_types', 'center', 'description']
    fieldsets = (
        (
            None, {
                'fields': (
                    (
                        'model_name', 'center',
                    ),
                    (
                        'organ', 'device', 'description',
                    ),
                    (
                        'cell_type',
                    ),
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
        )
    )

    actions = ['update_fields']
    save_on_top = True
    inlines = [TestInline]

admin.site.register(OrganModel, OrganModelAdmin)
