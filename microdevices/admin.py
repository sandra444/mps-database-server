# coding=utf-8

from django.contrib import admin
from mps.base.admin import LockableAdmin
from .models import MicrophysiologyCenter, Manufacturer, Microdevice, OrganModel, ValidatedAssay
from drugtrials.models import Test


class MicrophysiologyCenterAdmin(LockableAdmin):
    save_on_top = True
    list_display = (
        'center_name', 'center_id', 'description', 'contact_person', 'center_site')
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                    'center_name',
                    'center_id',
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

    def center_site(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.center_website, obj.center_website)
    center_site.allow_tags = True

admin.site.register(MicrophysiologyCenter, MicrophysiologyCenterAdmin)


class ManufacturerAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ['manufacturer_name', 'contact_person', 'manufacturer_site']
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

    def manufacturer_site(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.Manufacturer_website, obj.Manufacturer_website)
    manufacturer_site.allow_tags = True

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


# class TestInline(admin.TabularInline):
#     model = Test
#     extra = 1
#     exclude = ['created_by', 'modified_by']
#     fields = ('locked', 'test_name', 'test_type', 'test_unit', 'description')
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}


class ValidatedAssayInline(admin.TabularInline):
    # Results calculated from CHIP READOUTS
    model = ValidatedAssay
    verbose_name = 'Validated Assay'
    verbose_name_plural = 'Validated Assays'
    fields = ('assay',)
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class OrganModelAdmin(LockableAdmin):

    class Media(object):
        js = ('js/inline_fix.js',)

    list_per_page = 300
    list_display = (
        'model_name', 'organ', 'device', 'center', 'description')
    search_fields = [
        'model_name', 'organ', 'device', 'center', 'description']
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on']

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
                        'protocol',
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
    # inlines = [TestInline]
    inlines = [ValidatedAssayInline]

admin.site.register(OrganModel, OrganModelAdmin)
