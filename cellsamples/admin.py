# coding=utf-8

"""

CellSamples Admin

"""

from django.contrib import admin
from cellsamples.resource import CellSampleResource
from mps.base.admin import LockableAdmin
from models import Organ, CellType, CellSubtype, Supplier, CellSample


class CellTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('cell_name', 'organ')


admin.site.register(CellType, CellTypeAdmin)


class CellTypeInline(admin.TabularInline):
    model = CellType


class OrganAdmin(admin.ModelAdmin):
    save_on_top = True

    inlines = [CellTypeInline]


admin.site.register(Organ, OrganAdmin)


class CellSubtypeAdmin(admin.ModelAdmin):
    save_on_top = True


admin.site.register(CellSubtype, CellSubtypeAdmin)


class CellSampleAdmin(LockableAdmin):

    resource_class = CellSampleResource
    
    save_on_top = True

    list_display = ('__unicode__',  # calls CellSample.__unicode__ function
                    'supplier',
                    'receipt_date',
                    'barcode',
                    'locked')

    search_fields = ['cell_type__cell_type',
                     'cell_type__cell_subtype__cell_subtype',
                     'cell_source',
                     'supplier__name',
                     'barcode',
                     'product_id']
    save_as = True
    fieldsets = (
        (None, {
            'fields': (('locked',
                       'cell_type'),
                       ('cell_source',
                       'receipt_date'),
                       ('cell_image'),
                       ('notes'),)
        }),
        ('Supplier Information', {
            'fields': (('supplier', 'product_id', 'barcode'),)
        }),
        ('Patient Information', {
            'fields': (('patient_age', 'patient_gender',
                       'patient_condition'),)
        }),
        ('Isolation Information', {
            'fields': (('isolation_datetime'), ('isolation_method',
                       'isolation_notes'),)
        }),
        ('Cell Viability', {
            'fields': (('viable_count',
                       'viable_count_unit',
                       'percent_viability'),)
        }),
        ('Change Tracking', {
            'fields': (('created_by',
                       'created_on'),
                       ('modified_by',
                       'modified_on'))
        }),
    )


admin.site.register(CellSample, CellSampleAdmin)


class SupplierAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'phone', 'address')


admin.site.register(Supplier, SupplierAdmin)
