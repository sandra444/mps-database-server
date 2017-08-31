"""Admin tools for assays alongside helper functions

Note that the code for templates can be found here
"""

# import csv

from django.contrib import admin
from django import forms
# from assays.forms import (
#     StudyConfigurationForm,
#     AssayChipReadoutInlineFormset,
#     AssayPlateReadoutInlineFormset,
# )
from assays.utils import (
    save_assay_layout,
    modify_qc_status_chip,
    modify_qc_status_plate,
    DEFAULT_CSV_HEADER
)
# TODO SPAGHETTI CODE
from django.http import HttpResponseRedirect

from assays.models import *
from .utils import parse_file_and_save
# from compounds.models import Compound
from mps.base.admin import LockableAdmin
from assays.resource import *
# from import_export.admin import ImportExportModelAdmin
# from compounds.models import *
# import unicodedata
# from io import BytesIO
# import ujson as json
# I use regular expressions for a string split at one point
# import re
# from django.db import connection, transaction
# from urllib import unquote

from mps.settings import MEDIA_ROOT, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX
import os
import xlsxwriter
# from xlsxwriter.utility import xl_col_to_name


def modify_templates():
    """Writes totally new templates for chips and both types of plates"""
    # Where will I store the templates?
    template_root = MEDIA_ROOT + '/excel_templates/'

    version = 1
    version += len(os.listdir(template_root)) / 3
    version = str(version)

    chip = xlsxwriter.Workbook(template_root + 'chip_template-' + version + '.xlsx')
    plate_tabular = xlsxwriter.Workbook(template_root + 'plate_tabular_template-' + version + '.xlsx')
    plate_block = xlsxwriter.Workbook(template_root + 'plate_block_template-' + version + '.xlsx')

    chip_sheet = chip.add_worksheet()
    plate_tabular_sheet = plate_tabular.add_worksheet()
    plate_block_sheet = plate_block.add_worksheet()

    # Set up formats
    chip_red = chip.add_format()
    chip_red.set_bg_color('#ff6f69')
    chip_green = chip.add_format()
    chip_green.set_bg_color('#96ceb4')

    plate_tabular_red = plate_tabular.add_format()
    plate_tabular_red.set_bg_color('#ff6f69')
    plate_tabular_green = plate_tabular.add_format()
    plate_tabular_green.set_bg_color('#96ceb4')

    plate_block_red = plate_block.add_format()
    plate_block_red.set_bg_color('#ff6f69')
    plate_block_green = plate_block.add_format()
    plate_block_green.set_bg_color('#96ceb4')
    plate_block_yellow = plate_block.add_format()
    plate_block_yellow.set_bg_color('#ffeead')

    # Write the base files
    chip_initial = [
        DEFAULT_CSV_HEADER,
        [''] * 16
    ]

    chip_initial_format = [
        [chip_red] * 16,
        [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            chip_green,
            chip_green,
            chip_green,
            None,
            chip_green,
            None,
            None,
            None,
            None
        ]
    ]

    plate_tabular_initial = [
        [
            'Plate ID',
            'Well Name (e.g. A01,F12)',
            'Assay',
            'Feature',
            'Unit',
            'Time',
            'Time Units',
            'Value',
            'Notes',
            ''
        ],
        [''] * 10
    ]

    plate_tabular_initial_format = [
        [plate_tabular_red] * 10,
        [
            None,
            None,
            plate_tabular_green,
            None,
            plate_tabular_green,
            None,
            plate_tabular_green,
            None,
            None,
            None
        ]
    ]

    plate_block_initial = [
        [
            'Plate ID',
            '{enter Plate ID here}',
            'Assay',
            '',
            'Feature',
            '{enter Feature here}',
            'Unit',
            '',
            '[Time]',
            '[{enter Time here}]',
            '[Time Unit]',
            '',
            'Note: Totally remove the contents of the Time and Time Units cells if you are not using them',
        ],
    ]

    plate_block_initial_format = [
        [
            plate_block_red,
            plate_block_yellow,
            plate_block_red,
            plate_block_green,
            plate_block_red,
            plate_block_yellow,
            plate_block_red,
            plate_block_green,
            plate_block_red,
            plate_block_yellow,
            plate_block_red,
            plate_block_green,
            plate_block_red
        ]
    ]

    # Write out initial
    for row_index, row in enumerate(chip_initial):
        for column_index, column in enumerate(row):
            cell_format = chip_initial_format[row_index][column_index]
            chip_sheet.write(row_index, column_index, column, cell_format)

    for row_index, row in enumerate(plate_tabular_initial):
        for column_index, column in enumerate(row):
            cell_format = plate_tabular_initial_format[row_index][column_index]
            plate_tabular_sheet.write(row_index, column_index, column, cell_format)

    for row_index, row in enumerate(plate_block_initial):
        for column_index, column in enumerate(row):
            cell_format = plate_block_initial_format[row_index][column_index]
            plate_block_sheet.write(row_index, column_index, column, cell_format)

    # Set column widths
    # Chip
    chip_sheet.set_column('A:A', 20)
    chip_sheet.set_column('B:B', 20)
    chip_sheet.set_column('C:C', 20)
    chip_sheet.set_column('D:D', 15)
    chip_sheet.set_column('E:E', 10)
    chip_sheet.set_column('F:F', 10)
    chip_sheet.set_column('G:G', 10)
    chip_sheet.set_column('H:H', 20)
    chip_sheet.set_column('I:I', 20)
    chip_sheet.set_column('J:J', 15)
    chip_sheet.set_column('K:K', 10)
    chip_sheet.set_column('L:L', 10)
    chip_sheet.set_column('M:M', 10)
    chip_sheet.set_column('N:N', 10)
    chip_sheet.set_column('O:O', 10)
    chip_sheet.set_column('P:P', 100)

    chip_sheet.set_column('BA:BD', 30)

    # Plate Tabular
    plate_tabular_sheet.set_column('A:A', 20)
    plate_tabular_sheet.set_column('B:B', 25)
    plate_tabular_sheet.set_column('C:C', 30)
    plate_tabular_sheet.set_column('D:D', 30)
    plate_tabular_sheet.set_column('E:E', 20)
    plate_tabular_sheet.set_column('F:F', 15)
    plate_tabular_sheet.set_column('G:G', 15)
    plate_tabular_sheet.set_column('H:H', 15)
    plate_tabular_sheet.set_column('I:I', 100)
    plate_tabular_sheet.set_column('J:J', 100)

    plate_tabular_sheet.set_column('BA:BC', 30)

    # Plate Block
    plate_block_sheet.set_column('A:A', 10)
    plate_block_sheet.set_column('B:B', 20)
    plate_block_sheet.set_column('C:C', 10)
    plate_block_sheet.set_column('D:D', 30)
    plate_block_sheet.set_column('E:E', 10)
    plate_block_sheet.set_column('F:F', 30)
    plate_block_sheet.set_column('G:G', 10)
    plate_block_sheet.set_column('H:H', 20)
    plate_block_sheet.set_column('I:I', 15)
    plate_block_sheet.set_column('I:I', 10)
    plate_block_sheet.set_column('J:J', 20)
    plate_block_sheet.set_column('K:K', 10)
    plate_block_sheet.set_column('L:L', 15)
    plate_block_sheet.set_column('M:M', 100)

    plate_block_sheet.set_column('BA:BC', 30)

    # Get a list of quality indicators
    quality_indicators = AssayQualityIndicator.objects.all().values_list('name', flat=True)

    # Get list of time units
    time_units = PhysicalUnits.objects.filter(
        unit_type__unit_type='Time'
    ).order_by(
        'scale_factor'
    ).values_list('unit', flat=True)

    # Get list of value units  (TODO CHANGE ORDER_BY)
    value_units = PhysicalUnits.objects.filter(
        availability__contains='readout'
    ).order_by(
        'base_unit',
        'scale_factor'
    ).values_list('unit', flat=True)

    # Get list of assays (for plates) TO BE REPLACED
    assays = AssayModel.objects.all().order_by(
        'assay_name'
    ).values_list('assay_name', flat=True)

    # List of targets
    targets = AssayTarget.objects.all().order_by(
        'name'
    ).values_list('name', flat=True)

    # List of methods
    methods = AssayMethod.objects.all().order_by(
        'name'
    ).values_list('name', flat=True)

    # List of sample locations
    sample_locations = AssaySampleLocation.objects.all().order_by(
        'name'
    ).values_list('name', flat=True)

#     for index, value in enumerate(quality_indicators):
#         chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 3, value)
#         plate_tabular_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 3, value)
#         # Plate templates are slated to be deprecated
# #         plate_block_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 3, value)

    for index, value in enumerate(time_units):
        # chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 2, value)
        plate_tabular_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 2, value)
        plate_block_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 2, value)

    for index, value in enumerate(sample_locations):
        chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 3, value)

    for index, value in enumerate(methods):
        chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 2, value)

    for index, value in enumerate(value_units):
        chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 1, value)
        plate_tabular_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 1, value)
        plate_block_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 1, value)

    for index, value in enumerate(targets):
        chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX, value)

    for index, value in enumerate(assays):
        # chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX, value)
        plate_tabular_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX, value)
        plate_block_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX, value)

    # quality_indicators_range = '=$BD$1:$BD$' + str(len(quality_indicators))
    time_units_range = '=$BC$1:$BC$' + str(len(time_units))
    value_units_range = '=$BB$1:$BB$' + str(len(value_units))
    assays_range = '=$BA$1:$BA$' + str(len(assays))

    targets_range = '=$BA$1:$BA$' + str(len(assays))
    methods_range = '=$BC$1:$BC$' + str(len(assays))
    sample_locations_range = '=$BD$1:$BD$' + str(len(assays))

    # chip_sheet.data_validation('H2', {'validate': 'list',
    #                            'source': quality_indicators_range})
    chip_sheet.data_validation('H2', {'validate': 'list',
                                      'source': targets_range})
    chip_sheet.data_validation('I2', {'validate': 'list',
                               'source': methods_range})
    chip_sheet.data_validation('J2', {'validate': 'list',
                               'source': sample_locations_range})
    chip_sheet.data_validation('L2', {'validate': 'list',
                               'source': value_units_range})

    plate_tabular_sheet.data_validation('C2', {'validate': 'list',
                                        'source': assays_range})
    plate_tabular_sheet.data_validation('E2', {'validate': 'list',
                                        'source': value_units_range})
    plate_tabular_sheet.data_validation('G2', {'validate': 'list',
                                        'source': time_units_range})

    plate_block_sheet.data_validation('D1', {'validate': 'list',
                                      'source': assays_range})
    plate_block_sheet.data_validation('H1', {'validate': 'list',
                                      'source': value_units_range})
    plate_block_sheet.data_validation('L1', {'validate': 'list',
                                      'source': time_units_range})

    # Save
    chip.close()
    plate_tabular.close()
    plate_block.close()


class AssayQualityIndicatorFormAdmin(forms.ModelForm):
    """Admin Form for Quality Indicators"""
    class Meta(object):
        model = AssayQualityIndicator
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssayQualityIndicatorAdmin(LockableAdmin):
    save_on_top = True
    list_display = ('code', 'name', 'description')

    form = AssayQualityIndicatorFormAdmin

    def save_model(self, request, obj, form, change):
        template_change = False

        # Check whether template needs to change
        # Change if assay name has changed or it is new
        if obj.pk is not None:
            original = AssayQualityIndicator.objects.get(pk=obj.pk)
            if original.name != obj.name:
                template_change = True
        else:
            template_change = True

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        if template_change:
            modify_templates()

admin.site.register(AssayQualityIndicator, AssayQualityIndicatorAdmin)


# class AssayModelTypeAdmin(LockableAdmin):
#     """Admin for Assay Model Type ('Biochemical')"""
#     save_on_top = True
#     list_display = ('assay_type_name', 'assay_type_description', 'locked')
#     list_per_page = 300
#     fieldsets = (
#         (
#             None, {
#                 'fields': (
#                     'assay_type_name',
#                     'assay_type_description',
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#     )
#
# admin.site.register(AssayModelType, AssayModelTypeAdmin)
#
#
# class AssayModelAdmin(LockableAdmin):
#     """Admin for Assay Model ('ALT')"""
#     save_on_top = True
#     list_per_page = 300
#     list_display = (
#         'assay_name', 'assay_short_name', 'version_number', 'assay_type', 'assay_description',
#         'locked'
#     )
#
#     fieldsets = (
#         (
#             None, {
#                 'fields': (
#                     ('assay_name', 'assay_short_name',),
#                     ('assay_type', 'test_type',),
#                     ('version_number', 'assay_protocol_file',),
#                     ('assay_description',))
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on',),
#                     ('modified_by', 'modified_on',),
#                     ('signed_off_by', 'signed_off_date',),
#                 )
#             }
#         ),
#     )
#
#     def save_model(self, request, obj, form, change):
#         template_change = False
#
#         # Check whether template needs to change
#         # Change if assay name has changed or it is new
#         if obj.pk is not None:
#             original = AssayModel.objects.get(pk=obj.pk)
#             if original.assay_name != obj.assay_name:
#                 template_change = True
#         else:
#             template_change = True
#
#         if change:
#             obj.modified_by = request.user
#         else:
#             obj.modified_by = obj.created_by = request.user
#
#         obj.save()
#
#         if template_change:
#             modify_templates()
#
#
# admin.site.register(AssayModel, AssayModelAdmin)
#
#
# class AssayWellTypeAdmin(LockableAdmin):
#     """Admin for Well Types
#
#     Allows us to specify well type and color
#     """
#     save_on_top = True
#     list_per_page = 300
#     list_display = ('colored_display', 'well_description', 'locked')
#
#     fieldsets = (
#         (
#             None, {
#                 'fields': (
#                     'well_type',
#                     'well_description',
#                     'background_color',
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#     )
#
#
# admin.site.register(AssayWellType, AssayWellTypeAdmin)
#
#
# class AssayReaderAdmin(LockableAdmin):
#     """Admin for Assay Reader (the device the readout came from)"""
#     save_on_top = True
#     list_per_page = 300
#     list_display = ('reader_name', 'reader_type')
#
#     fieldsets = (
#         (
#             None, {
#                 'fields': (
#                     ('reader_name', 'reader_type'),
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         )
#     )
#
# admin.site.register(AssayReader, AssayReaderAdmin)


class AssayCompoundInstanceAdmin(admin.ModelAdmin):
    """Admin for Assay Compound Instance"""
    save_on_top = True

    list_display = (
        'compound_instance',
        'chip_setup',
        'concentration',
        'concentration_unit',
        'addition_time',
        'duration'
    )

admin.site.register(AssayCompoundInstance, AssayCompoundInstanceAdmin)


# TODO REVISE SAVING
# TODO ADMIN IS NOT FUNCTIONAL AT THE MOMENT
# class AssayLayoutAdmin(LockableAdmin):
#     """Admin for Assay Layouts (not currently functional)"""
#
#     class Media(object):
#         js = ('assays/plate_display.js', 'assays/assaylayout_add.js',)
#         css = {'all': ('assays/customize_admin.css',)}
#
#     save_as = True
#     save_on_top = True
#     list_per_page = 300
#     fieldsets = (
#         (
#             'Layout Parameters', {
#                 'fields': (
#                     (
#                         'layout_name',
#                         'device',
#                         'standard',
#                         'locked',
#                     )
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     (
#                         'created_by', 'created_on',
#                     ),
#                     (
#                         'modified_by', 'modified_on',
#                     ),
#                     (
#                         'signed_off_by', 'signed_off_date'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
#     def save_model(self, request, obj, form, change):
#         save_assay_layout(request, obj, form, change)
#
# admin.site.register(AssayLayout, AssayLayoutAdmin)
#
#
# class AssayPlateCellsInline(admin.TabularInline):
#     """Admin for Cells used to construct a plate"""
#     model = AssayPlateCells
#     verbose_name = 'Plate Cells'
#     verbose_name_plural = 'Plate Cells'
#     raw_id_fields = ('cell_sample',)
#     fields = (
#         (
#             'cell_sample', 'cell_biosensor', 'cellsample_density',
#             'cellsample_density_unit', 'cell_passage',
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}
#
#
# class AssayPlateSetupAdmin(LockableAdmin):
#     """Admin for the setup of plates"""
#
#     class Media(object):
#         js = ('js/inline_fix.js', 'assays/plate_display.js', 'assays/assayplatesetup_add.js')
#         css = {'all': ('assays/customize_admin.css',)}
#
#     save_on_top = True
#     list_per_page = 300
#     list_display = ('assay_plate_id',
#                     'assay_run_id',
#                     'setup_date')
#
#     inlines = [AssayPlateCellsInline]
#
#     fieldsets = (
#         (
#             'Device Parameters', {
#                 'fields': (
#                     (
#                         'assay_run_id',
#                     ),
#                     (
#                         'assay_plate_id', 'setup_date',
#                     ),
#                     (
#                         'assay_layout',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Reference Parameters', {
#                 'fields': (
#                     (
#                         'scientist', 'notebook', 'notebook_page', 'notes',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     (
#                         'created_by', 'created_on',
#                     ),
#                     (
#                         'modified_by', 'modified_on',
#                     ),
#                     (
#                         'signed_off_by', 'signed_off_date'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
# admin.site.register(AssayPlateSetup, AssayPlateSetupAdmin)


# As much as I like being certain, this code is somewhat baffling
# def remove_existing_readout(currentAssayReadout):
#     AssayReadout.objects.filter(assay_device_readout=currentAssayReadout).delete()
#
#     readouts = AssayReadout.objects.filter(
#         assay_device_readout_id=currentAssayReadout.id)
#
#     for readout in readouts:
#         if readout.assay_device_readout_id == currentAssayReadout.id:
#             readout.delete()
#     return


# class AssayPlateReadoutInline(admin.TabularInline):
#     """Inline for the Assays of a Plate Readout"""
#     formset = AssayPlateReadoutInlineFormset
#     model = AssayPlateReadoutAssay
#     verbose_name = 'Assay Plate Readout Assay'
#     verbose_plural_name = 'Assay Plate Readout Assays'
#
#     fields = (
#         (
#             ('assay_id', 'reader_id', 'readout_unit', 'feature')
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}


# Plate Readout validation occurs in the inline formset
# This form is just to jam in upload_type into the admin
# class AssayPlateReadoutForm(forms.ModelForm):
#     """Assay Plate Readout Form"""
#
#     upload_type = forms.ChoiceField(choices=(('Tabular', 'Tabular'), ('Block', 'Block')))
#
#     class Meta(object):
#         model = AssayPlateReadout
#         exclude = ('',)


# class AssayPlateReadoutAdmin(LockableAdmin):
#     """Admin for Assay Plate Readouts"""
#     resource_class = AssayPlateReadoutResource
#     # form = AssayPlateReadoutForm
#
#     class Media(object):
#         js = ('js/inline_fix.js', 'js/csv_functions.js', 'assays/plate_display.js', 'assays/assayplatereadout_add.js',)
#         css = {'all': ('assays/customize_admin.css',)}
#
#     inlines = [AssayPlateReadoutInline]
#
#     date_hierarchy = 'readout_start_time'
#     # raw_id_fields = ("cell_sample",)
#     save_on_top = True
#     list_per_page = 300
#     list_display = ('id',
#                     # 'assay_device_id',
#                     # 'cell_sample',
#                     'readout_start_time',)
#     fieldsets = (
#         (
#             'Device Parameters', {
#                 'fields': (
#                     # (
#                     #     'assay_device_id',
#                     # ),
#                     (
#                         'setup',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Assay Parameters', {
#                 'fields': (
#                     (
#                         'timeunit', 'treatment_time_length', 'readout_start_time',
#                     ),
#                     (
#                         'file'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Reference Parameters', {
#                 'fields': (
#                     (
#                         'scientist', 'notebook', 'notebook_page', 'notes',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     (
#                         'created_by', 'created_on',
#                     ),
#                     (
#                         'modified_by', 'modified_on',
#                     ),
#                     (
#                         'signed_off_by', 'signed_off_date'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
#     # save_related takes the place of save_model so that the inline can be saved first
#     # this is similar to chip readouts so that we can validate the listed assays THEN the file
#     def save_related(self, request, form, formsets, change):
#         # Prevent saving in Admin for now
#         pass
#         # obj = form.instance
#         #
#         # # Need to get the upload type
#         # # upload_type = form.data.get('upload_type')
#         # overwrite_option = form.data.get('overwrite_option')
#         #
#         # if change:
#         #     obj.modified_by = request.user
#         #
#         # else:
#         #     obj.modified_by = obj.created_by = request.user
#         #
#         # # Save Plate Readout
#         # obj.save()
#         # # Save inline
#         # super(LockableAdmin, self).save_related(request, form, formsets, change)
#         #
#         # if request.FILES:
#         #     # pass the upload file name to the CSV reader if a file exists
#         #     # parse_readout_csv(obj, request.FILES['file'], upload_type, overwrite_option, form)
#         #     pass
#         #     # parse_file_and_save(
#         #     #     request.FILES['file'], obj.study.assay_run_id, overwrite_option, 'Plate', readout=self.object
#         #     # )
#         #
#         # # Need to delete entries when a file is cleared
#         # if request.POST.get('file-clear', '') == 'on':
#         #     # remove_existing_readout(obj)
#         #     AssayReadout.objects.filter(assay_device_readout=obj).delete()
#         #
#         # else:
#         #     modify_qc_status_plate(obj, form)
#
#     # save_model not used; would save twice otherwise
#     def save_model(self, request, obj, form, change):
#         pass
#
# admin.site.register(AssayPlateReadout, AssayPlateReadoutAdmin)


# Case and point for why you should not just copy code without carefully reading it
# TODO these remove functions really should not even exist (one line of code?)
# def remove_existing_chip(current_chip_readout):
#     AssayChipRawData.objects.filter(assay_chip_id=current_chip_readout).delete()
#     readouts = AssayChipRawData.objects.filter(
#         assay_chip_id_id=current_chip_readout.id)
#
#     for readout in readouts:
#         if readout.assay_chip_id_id == current_chip_readout.id:
#             readout.delete()
#     return


# class AssayChipCellsInline(admin.TabularInline):
#     """Inline for Chip Cells (for Chip Setup)"""
#     # Cells used to construct the model
#     model = AssayChipCells
#     verbose_name = 'Model Cells'
#     verbose_name_plural = 'Model Cells'
#     raw_id_fields = ('cell_sample',)
#     fields = (
#         (
#             'cell_sample', 'cell_biosensor', 'cellsample_density',
#             'cellsample_density_unit', 'cell_passage',
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}


# class AssayCompoundInstanceInline(admin.TabularInline):
#     model = AssayCompoundInstance
#     exclude = []
#     extra = 0
#
#
# class AssayChipSetupAdmin(LockableAdmin):
#     """Admin for Chip Setup"""
#     # TIMEPOINT readouts from ORGAN CHIPS
#     class Media(object):
#         js = ('js/inline_fix.js',)
#         css = {'all': ('assays/customize_admin.css',)}
#
#     save_on_top = True
#     save_as = True
#
#     raw_id_fields = ("compound",)
#     date_hierarchy = 'setup_date'
#
#     list_per_page = 100
#     list_display = ('assay_chip_id', 'assay_run_id', 'setup_date',
#                     'device', 'chip_test_type',
#                     'compound', 'scientist')
#
#     search_fields = ['assay_chip_id']
#     fieldsets = (
#         (
#             'Study', {
#                 'fields': (
#                     (
#                         'assay_run_id', 'setup_date',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Model Parameters', {
#                 'fields': (
#                     (
#                         'assay_chip_id',
#                     ),
#                     (
#                         'device', 'organ_model', 'organ_model_protocol'
#                     ),
#                     (
#                         'variance',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Assay Parameters', {
#                 'fields': (
#                     (
#                         'chip_test_type', 'compound', 'concentration',
#                         'unit',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Reference Parameters', {
#                 'fields': (
#                     (
#                         'scientist', 'notebook', 'notebook_page', 'notes',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     (
#                         'created_by', 'created_on',
#                     ),
#                     (
#                         'modified_by', 'modified_on',
#                     ),
#                     (
#                         'signed_off_by', 'signed_off_date'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
#     actions = ['update_fields']
#     inlines = [AssayChipCellsInline, AssayCompoundInstanceInline]
#
#     def response_add(self, request, obj):
#         """If save and add another, have same response as save and continue"""
#         if '_saveasnew' in request.POST or '_addanother' in request.POST:
#             return HttpResponseRedirect("../%s" % obj.id)
#         else:
#             return super(AssayChipSetupAdmin, self).response_add(request, obj)
#
#     def response_change(self, request, obj):
#         """If save as new, redirect to new change model; else go to list"""
#         if '_saveasnew' in request.POST:
#             return HttpResponseRedirect("../%s" % obj.id)
#         else:
#             return super(LockableAdmin, self).response_change(request, obj)
#
#     def save_model(self, request, obj, form, change):
#
#         if change:
#             obj.modified_by = request.user
#
#         else:
#             obj.modified_by = obj.created_by = request.user
#
#         obj.save()
#
# admin.site.register(AssayChipSetup, AssayChipSetupAdmin)
#
#
# class AssayChipReadoutInline(admin.TabularInline):
#     """Assays for ChipReadout"""
#     formset = AssayChipReadoutInlineFormset
#     model = AssayChipReadoutAssay
#     verbose_name = 'Assay Readout Assay'
#     verbose_plural_name = 'Assay Readout Assays'
#
#     fields = (
#         (
#             ('assay_id', 'object_type', 'reader_id', 'readout_unit',)
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}
#
#
# # ChipReadout validation occurs in the inline formset
# class AssayChipReadoutForm(forms.ModelForm):
#     """Form for Chip Readouts"""
#     headers = forms.CharField(required=False)
#
#     class Meta(object):
#         model = AssayChipReadout
#         exclude = ('',)
#
#
# class AssayChipReadoutAdmin(LockableAdmin):
#     """Admin for Assay Chip Readout"""
#     class Media(object):
#         # Removed chip readout display, no need to maintain such scripts
#         js = ('js/inline_fix.js', 'js/csv_functions.js', 'js/d3.min.js', 'js/c3.min.js',)
#         css = {'all': ('assays/customize_admin.css', 'css/c3.min.css',)}
#
#     form = AssayChipReadoutForm
#     date_hierarchy = 'readout_start_time'
#
#     raw_id_fields = ("chip_setup",)
#
#     save_on_top = True
#     save_as = True
#
#     list_per_page = 100
#     list_display = (
#         'id',
#         'chip_setup',
#         'assays',
#         'readout_start_time',
#         'scientist'
#     )
#
#     list_display_links = ('id', 'chip_setup',
#                           'readout_start_time',)
#     search_fields = ['assay_chip_id']
#     fieldsets = (
#         (
#             'Setup Parameters', {
#                 'fields': (
#                     (
#                         'chip_setup'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Assay Parameters', {
#                 'fields': (
#                     (
#                         'timeunit', 'treatment_time_length', 'readout_start_time',
#                     ),
#                     (
#                         'file',
#                     ),
#                     (
#                         'headers',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Reference Parameters', {
#                 'fields': (
#                     (
#                         'scientist', 'notebook', 'notebook_page', 'notes',
#                     ),
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     (
#                         'created_by', 'created_on',
#                     ),
#                     (
#                         'modified_by', 'modified_on',
#                     ),
#                     (
#                         'signed_off_by', 'signed_off_date'
#                     ),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
#     # inlines = [AssayChipReadoutInline]
#
#     def response_add(self, request, obj):
#         """If save and add another, have same response as save and continue"""
#         if '_saveasnew' in request.POST or '_addanother' in request.POST:
#             return HttpResponseRedirect("../%s" % obj.id)
#         else:
#             return super(AssayChipReadoutAdmin, self).response_add(request, obj)
#
#     def response_change(self, request, obj):
#         """If save as new, redirect to new change model; else go to list"""
#         if '_saveasnew' in request.POST:
#             return HttpResponseRedirect("../%s" % obj.id)
#         else:
#             return super(LockableAdmin, self).response_change(request, obj)
#
#     # save_related takes the place of save_model so that the inline can be saved first
#     def save_related(self, request, form, formsets, change):
#         # Prevent saving in Admin for now
#         pass
#         # obj = form.instance
#         #
#         # headers = int(form.data.get('headers')) if form.data.get('headers') else 0
#         # overwrite_option = form.data.get('overwrite_option')
#         #
#         # if change:
#         #     obj.modified_by = request.user
#         #
#         # else:
#         #     obj.modified_by = obj.created_by = request.user
#         #
#         # # Save Chip Readout
#         # obj.save()
#         # # Save inline
#         # super(LockableAdmin, self).save_related(request, form, formsets, change)
#         #
#         # if request.FILES:
#         #     # pass the upload file name to the CSV reader if a file exists
#         #     # parse_chip_csv(obj, request.FILES['file'], headers, form)
#         #     pass
#         #     # parse_file_and_save(
#         #     #     request.FILES['file'], obj.chip_setup.assay_run_id, overwrite_option, 'Chip', form=form, readout=self.object
#         #     # )
#         #
#         # # Try to update QC status if no file
#         # else:
#         #     modify_qc_status_chip(obj, form)
#         #
#         # # Need to delete entries when a file is cleared
#         # if request.POST.get('file-clear', '') == 'on':
#         #     # remove_existing_chip(obj)
#         #     AssayChipRawData.objects.filter(assay_chip_id=obj).delete()
#
#     # save_model not used; would save twice otherwise
#     def save_model(self, request, obj, form, change):
#         pass
#
# admin.site.register(AssayChipReadout, AssayChipReadoutAdmin)


class AssayResultFunctionAdmin(LockableAdmin):
    """Admin for the different functions for results"""

    list_per_page = 30
    save_on_top = True
    list_display = ('function_name', 'function_results', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    ('function_name', 'function_results',),
                    ('description',),
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )


admin.site.register(AssayResultFunction, AssayResultFunctionAdmin)


class AssayResultTypeAdmin(LockableAdmin):
    """Admin for the Result Types"""
    list_per_page = 300
    save_on_top = True
    list_display = ('assay_result_type', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    ('assay_result_type', 'description'),
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )


admin.site.register(AssayResultType, AssayResultTypeAdmin)


# class AssayChipResultInline(admin.TabularInline):
#     """Adming for results calculated from CHIP READOUTS"""
#     model = AssayChipResult
#     verbose_name = 'Assay Test'
#     verbose_name_plural = 'Assay Test Results'
#     fields = (
#         (
#             'assay_name', 'result', 'result_function', 'result_type',
#             'value', 'test_unit', 'severity',
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {"all": ("css/hide_admin_original.css",)}


class UnitTypeFormAdmin(forms.ModelForm):
    """Admin Form for Unit Types"""
    class Meta(object):
        model = UnitType
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class UnitTypeAdmin(LockableAdmin):
    """Admin for Unit Types"""
    form = UnitTypeFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('unit_type', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    ('unit_type', 'description'),
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )


admin.site.register(UnitType, UnitTypeAdmin)


class PhysicalUnitsFormAdmin(forms.ModelForm):
    """Admin Form for Physical Units"""
    class Meta(object):
        model = PhysicalUnits
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class PhysicalUnitsAdmin(LockableAdmin):
    """Admin for Units

    Note that all assay units should link to Physical Units
    """
    form = PhysicalUnitsFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('unit_type', 'unit', 'base_unit', 'scale_factor', 'availability', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'unit',
                    'unit_type',
                    ('base_unit', 'scale_factor'),
                    'availability',
                    'description',
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )

    def save_model(self, request, obj, form, change):
        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        # If this is a readout unit, modify the templates
        if 'readout' in obj.availability:
            modify_templates()


admin.site.register(PhysicalUnits, PhysicalUnitsAdmin)


# class AssayChipTestResultAdmin(LockableAdmin):
#     """Admin for results calculated from RAW CHIP DATA aka 'Chip Result'"""
#     class Media(object):
#         js = ('js/cookies.js', 'js/whittle.js', 'js/inline_fix.js', 'assays/assaychiptestresult_add.js')
#
#     save_as = True
#     save_on_top = True
#     list_per_page = 300
#     list_display = (
#         'chip_readout', 'assay', 'result', 'result_function', 'result_type', 'severity'
#     )
#     search_fields = ['chip_readout']
#     actions = ['update_fields']
#     readonly_fields = ['created_by', 'created_on',
#                        'modified_by', 'modified_on', ]
#
#     fieldsets = (
#         (
#             'Device/Drug Parameters', {
#                 'fields': (
#                     ('chip_readout',),
#                     ('summary',),
#                 ),
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#     inlines = [AssayChipResultInline]
#
# admin.site.register(AssayChipTestResult, AssayChipTestResultAdmin)
#
#
# class AssayPlateResultInline(admin.TabularInline):
#     """Admin for results calculated from PLATE READOUTS"""
#     model = AssayPlateResult
#     verbose_name = 'Assay Plate Result'
#     verbose_name_plural = 'Assay Plate Results'
#     fields = (
#         (
#             'assay_name', 'result', 'result_function', 'result_type',
#             'value', 'test_unit', 'severity',
#         ),
#     )
#     extra = 0
#
#     class Media(object):
#         css = {'all': ('css/hide_admin_original.css',)}
#
#
# class AssayPlateTestResultAdmin(LockableAdmin):
#     """Admin for test Results from MICROPLATES"""
#     class Media(object):
#         js = (
#             'js/cookies.js',
#             'js/whittle.js',
#             'js/inline_fix.js',
#             'js/csv_functions.js',
#             'assays/plate_display.js',
#             'assays/assayplatetestresult_add.js'
#         )
#         css = {'all': ('assays/customize_admin.css',)}
#
#     inlines = [AssayPlateResultInline]
#
#     save_as = True
#     save_on_top = True
#     list_per_page = 300
#     list_display = (
#         'readout',
#     )
#     search_fields = ['readout']
#     actions = ['update_fields']
#     readonly_fields = ['created_by', 'created_on',
#                        'modified_by', 'modified_on']
#
#     fieldsets = (
#         (
#             'Device/Drug Parameters', {
#                 'fields': (
#                     ('readout',),
#                     ('summary',),
#                 ),
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#         (
#             'Flag for Review', {
#                 'fields': (
#                     ('flagged', 'reason_for_flag',)
#                 )
#             }
#         ),
#     )
#
#
# admin.site.register(AssayPlateTestResult, AssayPlateTestResultAdmin)
#
#
# class AssayRunFormAdmin(forms.ModelForm):
#     """Admin Form for Assay Runs (now referred to as Studies)"""
#     class Meta(object):
#         model = AssayRun
#         widgets = {
#             'assay_run_id': forms.Textarea(attrs={'rows': 1}),
#             'name': forms.Textarea(attrs={'rows': 1}),
#             'description': forms.Textarea(attrs={'rows': 10}),
#         }
#         exclude = ('',)
#
#     # TODO CLEAN TO USE SETUP IN LIEU OF READOUT ID
#     def clean(self):
#         """Validate unique, existing Chip Readout IDs"""
#
#         # clean the form data, before validation
#         data = super(AssayRunFormAdmin, self).clean()
#
#         if not any([data['toxicity'], data['efficacy'], data['disease'], data['cell_characterization']]):
#             raise forms.ValidationError('Please select at least one study type')
#
#         if data['assay_run_id'].startswith('-'):
#             raise forms.ValidationError('Error with assay_run_id; please try again')
#
#
# class StudySupportingDataInline(admin.TabularInline):
#     """Inline for Studies"""
#     model = StudySupportingData
#     verbose_name = 'Study Supporting Data'
#     fields = (
#         (
#             'description', 'supporting_data'
#         ),
#     )
#     extra = 1
#
#
# class AssayRunAdmin(LockableAdmin):
#     """Admin for what are now called Organ Chip Studies"""
#     # AssayRun is now Organ Chip Study
#     # Organ Chip Study should really be simply Study
#     class Media(object):
#         js = ('assays/assayrun_add.js',)
#
#     form = AssayRunFormAdmin
#     save_on_top = True
#     list_per_page = 300
#     date_hierarchy = 'start_date'
#     list_display = ('assay_run_id', 'study_types', 'start_date', 'description',)
#     fieldsets = (
#         (
#             'Study', {
#                 'fields': (
#                     ('toxicity', 'efficacy', 'disease', 'cell_characterization'),
#                     'study_configuration',
#                     'start_date',
#                     'name',
#                     'description',
#                     'image',
#                 )
#             }
#         ),
#         (
#             'Study ID (Autocreated from entries above)', {
#                 'fields': (
#                     'assay_run_id',
#                 )
#             }
#         ),
#         (
#             'Protocol File Upload', {
#                 'fields': (
#                     'protocol',
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#         (
#             'Group Access', {
#                 'fields': (
#                     'group',
#                 ),
#             }
#         ),
#     )
#
#     inlines = [StudySupportingDataInline]
#
#     def save_model(self, request, obj, form, change):
#
#         if change:
#             obj.modified_by = request.user
#
#         else:
#             obj.modified_by = obj.created_by = request.user
#
#         obj.save()
#
#
# admin.site.register(AssayRun, AssayRunAdmin)
#
#
# class StudyModelInline(admin.TabularInline):
#     """Inline for Study Configurations"""
#     model = StudyModel
#     verbose_name = 'Study Model'
#     fields = (
#         (
#             'label', 'organ', 'sequence_number', 'output', 'integration_mode',
#         ),
#     )
#     extra = 1
#
#     class Media(object):
#         css = {'all': ('css/hide_admin_original.css',)}
#
#
# class StudyConfigurationAdmin(LockableAdmin):
#     """Admin for study configurations"""
#
#     class Media(object):
#         js = ('js/inline_fix.js',)
#
#     form = StudyConfigurationForm
#     save_on_top = True
#     list_per_page = 300
#     list_display = ('name',)
#     fieldsets = (
#         (
#             'Study Configuration', {
#                 'fields': (
#                     'name',
#                     'media_composition',
#                     'hardware_description',
#                 )
#             }
#         ),
#         (
#             'Change Tracking', {
#                 'fields': (
#                     'locked',
#                     ('created_by', 'created_on'),
#                     ('modified_by', 'modified_on'),
#                     ('signed_off_by', 'signed_off_date'),
#                 )
#             }
#         ),
#     )
#     inlines = [StudyModelInline]
#
#
# admin.site.register(StudyConfiguration, StudyConfigurationAdmin)


class AssayTargetFormAdmin(forms.ModelForm):
    """Admin Form for Targets"""
    class Meta(object):
        model = AssayTarget
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


# TODO MAKE A VARIABLE TO CONTAIN TRACKING DATA TO AVOID COPY/PASTE
class AssayTargetAdmin(LockableAdmin):
    # model = AssayTarget
    form = AssayTargetFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = (
        'name',
        'short_name',
        'description'
    )
    fieldsets = (
        (
            'Target', {
                'fields': (
                    'name',
                    'short_name',
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

    def save_model(self, request, obj, form, change):
        template_change = False

        # Check whether template needs to change
        # Change if assay name has changed or it is new
        if obj.pk is not None:
            original = AssayTarget.objects.get(pk=obj.pk)
            if original.name != obj.name:
                template_change = True
        else:
            template_change = True

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        if template_change:
            modify_templates()

admin.site.register(AssayTarget, AssayTargetAdmin)


class AssaySampleLocationFormAdmin(forms.ModelForm):
    """Admin Form for Sample Locations"""
    class Meta(object):
        model = AssaySampleLocation
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssaySampleLocationAdmin(LockableAdmin):
    # model = AssaySampleLocation

    form = AssaySampleLocationFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    fieldsets = (
        (
            'Sample Location', {
                'fields': (
                    'name',
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

    def save_model(self, request, obj, form, change):
        template_change = False

        # Check whether template needs to change
        # Change if assay name has changed or it is new
        if obj.pk is not None:
            original = AssaySampleLocation.objects.get(pk=obj.pk)
            if original.name != obj.name:
                template_change = True
        else:
            template_change = True

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        if template_change:
            modify_templates()

admin.site.register(AssaySampleLocation, AssaySampleLocationAdmin)


class AssayMeasurementTypeFormAdmin(forms.ModelForm):
    """Admin Form for Measurement Types"""
    class Meta(object):
        model = AssayMeasurementType
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssayMeasurementTypeAdmin(LockableAdmin):
    # model = AssayMeasurementType

    form = AssayMeasurementTypeFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
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

admin.site.register(AssayMeasurementType, AssayMeasurementTypeAdmin)


class AssaySupplierFormAdmin(forms.ModelForm):
    """Admin Form for Suppliers"""
    class Meta(object):
        model = AssaySupplier
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssaySupplierAdmin(LockableAdmin):
    # model = AssaySupplier

    form = AssaySupplierFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
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

admin.site.register(AssaySupplier, AssaySupplierAdmin)


class AssayMethodFormAdmin(forms.ModelForm):
    """Admin Form for Methods"""
    class Meta(object):
        model = AssayMethod
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssayMethodAdmin(LockableAdmin):
    # model = AssayMethod

    form = AssayMethodFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = (
        'name',
        'measurement_type',
        'supplier',
        'protocol_file',
        'description'
    )
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
                    'description',
                    'measurement_type',
                    'supplier',
                    'protocol_file'
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

    def save_model(self, request, obj, form, change):
        template_change = False

        # Check whether template needs to change
        # Change if assay name has changed or it is new
        if obj.pk is not None:
            original = AssayMethod.objects.get(pk=obj.pk)
            if original.name != obj.name:
                template_change = True
        else:
            template_change = True

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        if template_change:
            modify_templates()

admin.site.register(AssayMethod, AssayMethodAdmin)

admin.site.register(AssayStudyType)
