import csv

from django.contrib import admin
from django import forms
from assays.forms import AssayResultForm
from django.http import HttpResponseRedirect

from assays.models import *
from compounds.models import Compound
from mps.base.admin import LockableAdmin
from assays.resource import *
from import_export.admin import ImportExportModelAdmin
from compounds.models import *
import unicodedata
from io import BytesIO

class AssayLayoutFormatForm(forms.ModelForm):
    class Meta(object):
        model = AssayLayoutFormat

    def clean(self):
        """Validate size of rows/columns and corresponding label counts."""

        # clean the form data, before validation
        data = super(AssayLayoutFormatForm, self).clean()

        if not (int(data['number_of_columns']) ==
                    len(set(data['column_labels'].split()))):
            raise forms.ValidationError('Number of columns and '
                                        'number of unique column '
                                        'labels do not match.')

        # cannot tell if it is number or letter in single entry list
        if not ((int(data['number_of_rows'] ==
            len(set(data['row_labels'].split())))) or
                    ((len(set(data['row_labels']))) == 1)):
            raise forms.ValidationError('Number of rows and '
                                        'number of unique row '
                                        'labels do not match.')
        # need to return clean data if it validates

        # if ((int(data['number_of_rows'])) > 1) and (len(set(data['row_labels'])) == 1):
        #     rows = int(data['number_of_rows'])
        #     row_list = []
        #     start = int(list(data['row_labels'])[0])
        #     for x in range(0, rows):
        #         row_list.append(start)
        #         start += 1
        #     data['row_labels'] = row_list
        #     print data['row_labels']

        return data


class AssayModelTypeAdmin(LockableAdmin):
    save_on_top = True
    list_display = ('assay_type_name', 'assay_type_description', 'locked')
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                    'assay_type_name',
                    'assay_type_description',
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


admin.site.register(AssayModelType, AssayModelTypeAdmin)


class AssayModelAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = (
        'assay_name', 'version_number', 'assay_type', 'assay_description',
        'locked'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    ('assay_name', 'assay_type',),
                    ('version_number', 'assay_protocol_file', ),
                    ('assay_description',), )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on', ),
                    ('modified_by', 'modified_on', ),
                    ('signed_off_by', 'signed_off_date', ),
                )
            }
        ),
    )


admin.site.register(AssayModel, AssayModelAdmin)


class AssayLayoutFormatAdmin(LockableAdmin):
    def device_image_display(self, obj):
        if obj.device.id and obj.device.device_image:
            return '<img src="%s">' % \
                   obj.device.device_image.url
        return ''

    def device_cross_section_image_display(self, obj):
        if obj.device.id and obj.device.device_cross_section_image:
            return '<img src="%s">' % \
                   obj.device.device_cross_section_image.url
        return ''

    device_image_display.allow_tags = True
    device_cross_section_image_display.allow_tags = True
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                    (
                        'layout_format_name', 'device',
                    ),
                    (
                        'number_of_rows', 'number_of_columns',
                    ),
                    (
                        'row_labels', 'column_labels',
                    ),
                    (
                        'device_image_display',
                        'device_cross_section_image_display',
                    )
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    'created_by',
                    'modified_by',
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

    readonly_fields = (
        'device_image_display',
        'device_cross_section_image_display',
    )

    save_as = True
    save_on_top = True
    form = AssayLayoutFormatForm
    list_display = ('layout_format_name', 'locked')


admin.site.register(AssayLayoutFormat, AssayLayoutFormatAdmin)


class AssayWellTypeAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('colored_display', 'well_description', 'locked')

    fieldsets = (
        (
            None, {
                'fields': (
                    'well_type',
                    'well_description',
                    'background_color',
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


admin.site.register(AssayWellType, AssayWellTypeAdmin)


class AssayReaderAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('reader_name', 'reader_type')

    fieldsets = (
        (
            None, {
                'fields': (
                    ('reader_name', 'reader_type'),
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


admin.site.register(AssayReader, AssayReaderAdmin)


class AssayWellInline(admin.TabularInline):
    model = AssayWell
    extra = 1


class AssayBaseLayoutAdmin(LockableAdmin):
    class Media(object):
        js = ('assays/customize_admin.js',)
        css = {'all': ('assays/customize_admin.css',)}

    save_as = True
    save_on_top = True
    list_per_page = 300

    def device_image_display(self, obj):
        if obj.layout_format.device.id \
                and obj.layout_format.device.device_image:
            return '<img src="%s">' % \
                   obj.layout_format.device.device_image.url
        return ''

    def device_cross_section_image_display(self, obj):
        if obj.layout_format.device.id \
                and obj.layout_format.device.device_cross_section_image:
            return '<img src="%s">' % \
                   obj.layout_format.device.device_cross_section_image.url
        return ''

    device_image_display.allow_tags = True
    device_cross_section_image_display.allow_tags = True

    readonly_fields = (
        'device_image_display',
        'device_cross_section_image_display',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    (
                        'base_layout_name', 'layout_format',
                    ),
                    (
                        'device_image_display',
                        'device_cross_section_image_display',
                    ),
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    'created_by',
                    'modified_by',
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):

        if change:
            obj.modified_by = request.user
            wells = {(well.row, well.column): well
                     for well in AssayWell.objects.filter(base_layout=obj)}
        else:
            obj.modified_by = obj.created_by = request.user
            wells = {}

        obj.save()

        layout = AssayLayoutFormat.objects.get(id=obj.layout_format.id)
        column_labels = layout.column_labels.split()
        row_labels = layout.row_labels.split()
        data = form.data

        for row in row_labels:
            for col in column_labels:
                rowcol = (row, col)
                key = 'wt_' + row + '_' + col
                if data.has_key(key):
                    if rowcol in wells:
                        well = wells[rowcol]
                        well.well_type = AssayWellType.objects.get(
                            id=data.get(key))
                        well.save()
                    else:
                        AssayWell(base_layout=obj,
                                  well_type=
                                  AssayWellType.objects.get(id=data.get(key)),
                                  row=row,
                                  column=col
                        ).save()
                elif rowcol in wells:
                    wells[rowcol].delete()


admin.site.register(AssayBaseLayout, AssayBaseLayoutAdmin)


class AssayLayoutAdmin(LockableAdmin):
    class Media(object):
        js = ('assays/customize_admin.js',)
        css = {'all': ('assays/customize_admin.css',)}

    save_as = True
    save_on_top = True
    list_per_page = 300
    fieldsets = (
        (
            None, {
                'fields': (
                    ('layout_name',
                     'base_layout',
                     'locked',
                     ('created_by', 'created_on', ),
                     ('modified_by', 'modified_on', ),
                     ('signed_off_by', 'signed_off_date', ), )
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):

        layout = obj

        if change:
            # Delete old compound data for this assay
            AssayCompound.objects.filter(assay_layout=layout).delete()

            # Delete old timepoint data for this assay
            AssayTimepoint.objects.filter(assay_layout=layout).delete()

            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

        for key, val in form.data.iteritems():

            if not key.startswith('well_') and not '_time' in key:
                continue

            # ## BEGIN save timepoint data ###

            if '_time' in key:
                content = key[:-5]
                r, c = content.split('_')

                # Add new timepoint info
                AssayTimepoint(
                    assay_layout=obj,
                    timepoint=val,
                    row=r,
                    column=c
                ).save()

            ### END save timepoint data ###

            ### BEGIN save compound information ###

            if not key.startswith('well_'):
                continue

            content = eval('dict(' + val + ')')
            well = content['well']
            row, col = well.split('_')

            if 'compound' in content:
                # Add compound info
                AssayCompound(
                    assay_layout=obj,
                    compound=Compound.objects.get(id=content['compound']),
                    concentration=content['concentration'],
                    concentration_unit=content['concentration_unit'],
                    row=row,
                    column=col
                ).save()

                ### END save compound information ###


admin.site.register(AssayLayout, AssayLayoutAdmin)


def removeExistingReadout(currentAssayReadout):
    readouts = AssayReadout.objects.filter(
        assay_device_readout_id=currentAssayReadout.id)

    for readout in readouts:
        if readout.assay_device_readout_id == currentAssayReadout.id:
            readout.delete()
    return


def parseReadoutCSV(currentAssayReadout, file):
    removeExistingReadout(currentAssayReadout)

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    for rowID, rowValue in enumerate(datalist):
        # rowValue holds all of the row elements
        # rowID is the index of the current row from top to bottom
        for columnID, columnValue in enumerate(rowValue):
            # columnValue is a single number: the value of our specific cell
            # columnID is the index of the current column

            # Treat empty strings as NULL values and do not save the data point
            if not columnValue:
                continue

            AssayReadout(
                assay_device_readout=currentAssayReadout,
                row=rowID,
                column=columnID,
                value=columnValue
            ).save()
    return


class AssayDeviceReadoutAdmin(LockableAdmin):
    # Endpoint readouts from MICROPLATES
    resource_class = AssayDeviceReadoutResource

    class Media(object):
        js = ('assays/customize_readout.js',)
        css = {'all': ('assays/customize_admin.css',)}

    raw_id_fields = ("cell_sample",)
    save_on_top = True
    list_per_page = 300
    list_display = ('assay_device_id',
                    'assay_name',
                    'cell_sample',
                    'reader_name')
    search_fields = ['assay_device_id']
    fieldsets = (
        (
            'Device Parameters', {
                'fields': (
                    (
                        'assay_device_id',
                    ),
                    (
                        'assay_layout', 'reader_name',
                    ),
                )
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    (
                        'assay_name',
                    ),
                    (
                        'cell_sample', 'cellsample_density',
                        'cellsample_density_unit',
                    ),
                    (
                        'timeunit', 'readout_unit',
                    ),
                    (
                        'treatment_time_length', 'assay_start_time', 'readout_start_time',
                    ),
                    (
                        'file',
                    ),
                )
            }
        ),
        (
            'Reference Parameters', {
                'fields': (
                    (
                        'scientist', 'notebook', 'notebook_page', 'notes',
                    ),
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    (
                        'created_by', 'created_on',
                    ),
                    (
                        'modified_by', 'modified_on',
                    ),
                    (
                        'signed_off_by', 'signed_off_date'
                    ),
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):

        obj.save()

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseReadoutCSV(obj, request.FILES['file'])

        #Need else to delete entries when a file is cleared
        else:
            removeExistingReadout(obj)

admin.site.register(AssayDeviceReadout, AssayDeviceReadoutAdmin)


def removeExistingChip(currentChipReadout):
    readouts = AssayChipRawData.objects.filter(
        assay_chip_id_id=currentChipReadout.id)

    for readout in readouts:
        if readout.assay_chip_id_id == currentChipReadout.id:
            readout.delete()
    return

# TODO Must test parsing for chip
def parseChipCSV(currentChipReadout, file):
    removeExistingChip(currentChipReadout)

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    for rowID, rowValue in enumerate(datalist):
        # rowValue holds all of the row elements
        # rowID is the index of the current row from top to bottom

        # Skip any row with incomplete data and first row (header) for now
        if not rowValue[0] or not rowValue[1] or not rowValue[2] or rowID == 0:
            continue

        assay = AssayModel.objects.get(assay_name=rowValue[1])
        field = rowValue[2]
        val = rowValue[3]
        time = rowValue[0]

        if not val:
            val = None

        #How to parse Chip data
        AssayChipRawData(
            assay_chip_id=currentChipReadout,
            assay_id=AssayChipReadoutAssay.objects.get(readout_id=currentChipReadout, assay_id=assay),
            field_id=field,
            value=val,
            elapsed_time=time
        ).save()
    return


class AssayChipCellsInline(admin.TabularInline):
    # Cells used to constrcut the model
    model = AssayChipCells
    verbose_name = 'Model Cells'
    verbose_name_plural = 'Model Cells'
    raw_id_fields = ('cell_sample',)
    fields = (
        (
            'cell_sample', 'cell_biosensor', 'cellsample_density',
            'cellsample_density_unit', 'cell_passage',
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class AssayChipSetupAdmin(LockableAdmin):
    # TIMEPOINT readouts from ORGAN CHIPS
    class Media(object):
        js = ('js/inline_fix.js',)
        css = {'all': ('assays/customize_admin.css',)}

    save_on_top = True
    save_as = True

    raw_id_fields = ("compound",)

    list_per_page = 100
    list_display = ('assay_run_id', 'assay_chip_id',
                    'device', 'chip_test_type',
                    'compound', )

    search_fields = ['assay_chip_id']
    fieldsets = (
        (
            'Study', {
                'fields': (
                    (
                        'assay_run_id',
                    ),
                )
            }
        ),
        (
            'Model Parameters', {
                'fields': (
                    (
                        'device', 'assay_chip_id',
                    ),
                )
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    (
                        'chip_test_type', 'compound', 'concentration',
                        'unit',
                    ),
                )
            }
        ),
        (
            'Reference Parameters', {
                'fields': (
                    (
                        'scientist', 'notebook', 'notebook_page', 'notes',
                    ),
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    (
                        'created_by', 'created_on',
                    ),
                    (
                        'modified_by', 'modified_on',
                    ),
                    (
                        'signed_off_by', 'signed_off_date'
                    ),
                )
            }
        ),
    )

    actions = ['update_fields']
    inlines = [AssayChipCellsInline]

    def response_add(self, request, obj, post_url_continue="../%s/"):
        """If save and add another, have same response as save and continue"""
        if '_saveasnew' in request.POST or '_addanother' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(AssayChipSetupAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """If save as new, redirect to new change model; else go to list"""
        if '_saveasnew' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(LockableAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

admin.site.register(AssayChipSetup, AssayChipSetupAdmin)

class AssayChipReadoutInline(admin.TabularInline):
    # Assays for ChipReadout
    model = AssayChipReadoutAssay
    verbose_name = 'Assay Readout Assay'
    verbose_plural_name = 'Assay Readout Assays'

    fields = (
        (
            ('assay_id','object_type','reader_id','readout_unit',)
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}

class AssayChipReadoutForm(forms.ModelForm):
    class Meta(object):
        model = AssayRun

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # clean the form data, before validation
        data = super(AssayChipReadoutForm, self).clean()

        # Check to make sure there is a file and it is not already in memory
        if data['file'] and type(data['file'].file) == BytesIO:
            datareader = csv.reader(data['file'].file, delimiter=',')
            datalist = list(datareader)

            # TODO fix cleaning
            for line in datalist[1:]:
                assay_name = line[1]
                if not AssayModel.objects.filter(assay_name=assay_name).exists():
                    raise forms.ValidationError(
                        'No assay with the name "%s" exists; please change your file or add this assay' % assay_name)

        return data

class AssayChipReadoutAdmin(LockableAdmin):
    # TIMEPOINT readouts from ORGAN CHIPS
    class Media(object):
        js = ('js/inline_fix.js','assays/customize_chip.js', 'js/d3.v3.min.js', 'js/c3.min.js',)
        css = {'all': ('assays/customize_admin.css', 'css/c3.css',)}

    form = AssayChipReadoutForm

    raw_id_fields = ("chip_setup",)

    save_on_top = True
    save_as = True

    list_per_page = 100
    list_display = ('id',
                    'chip_setup',
                    'readout_start_time',
                    )

    list_display_links = ('id', 'chip_setup',
                          'readout_start_time',)
    search_fields = ['assay_chip_id']
    fieldsets = (
        (
            'Run Parameters', {
                'fields': (
                    (
                        'chip_setup', 'type'
                    ),
                )
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    (
                        'timeunit', 'treatment_time_length', 'assay_start_time', 'readout_start_time',
                    ),
                    (
                        'file',
                    ),
                )
            }
        ),
        (
            'Reference Parameters', {
                'fields': (
                    (
                        'scientist', 'notebook', 'notebook_page', 'notes',
                    ),
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    (
                        'created_by', 'created_on',
                    ),
                    (
                        'modified_by', 'modified_on',
                    ),
                    (
                        'signed_off_by', 'signed_off_date'
                    ),
                )
            }
        ),
    )

    inlines = [AssayChipReadoutInline]

    def response_add(self, request, obj, post_url_continue="../%s/"):
        """If save and add another, have same response as save and continue"""
        if '_saveasnew' in request.POST or '_addanother' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(AssayChipReadoutAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """If save as new, redirect to new change model; else go to list"""
        if '_saveasnew' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(LockableAdmin, self).response_change(request, obj)

    def id(self, obj):
        return obj.id

    # TODO test presave

    def save_related(self, request, form, formsets, change):
        obj = form.instance

        # Save Chip Readout
        obj.save()
        # Save inline
        super(LockableAdmin, self).save_related(request, form, formsets, change)

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseChipCSV(obj, request.FILES['file'])

        #Need to delete entries when a file is cleared
        if 'file-clear' in request.POST and request.POST['file-clear'] == 'on':
            removeExistingChip(obj)

    def save_model(self, request, obj, form, change):
        pass

admin.site.register(AssayChipReadout, AssayChipReadoutAdmin)


class AssayResultFunctionAdmin(LockableAdmin):
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


class AssayResultInline(admin.TabularInline):
    # Results calculated from CHIP READOUTS
    model = AssayResult
    form = AssayResultForm
    verbose_name = 'Assay Test'
    verbose_name_plural = 'Assay Test Results'
    fields = (
        (
            'assay_name', 'result', 'result_function', 'result_type',
            'value', 'test_unit', 'severity',
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class PhysicalUnitsAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('unit_type', 'unit', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'unit',
                    'description',
                    'unit_type',
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


admin.site.register(PhysicalUnits, PhysicalUnitsAdmin)


class TimeUnitsAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300

    list_display = ('unit', 'unit_order',)
    fieldsets = (
        (
            None, {
                'fields': (
                    'unit',
                    'description',
                    'unit_order',
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


admin.site.register(TimeUnits, TimeUnitsAdmin)


class ReadoutUnitAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 100

    list_display = ('readout_unit', 'description',)
    fieldsets = (
        (
            None, {
                'fields': (
                    'readout_unit',
                    'description'
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


admin.site.register(ReadoutUnit, ReadoutUnitAdmin)


class AssayTestResultAdmin(LockableAdmin):
    # Results calculated from RAW CHIP DATA aka 'Chip Result'
    class Media(object):
        js = ('js/inline_fix.js',)

    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = (
        'assay_device_readout', 'chip_readout', 'result', 'result_function', 'result_type', 'severity'
    )
    search_fields = ['assay_device_readout']
    actions = ['update_fields']
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on', ]

    fieldsets = (
        (
            'Device/Drug Parameters', {
                'fields': (
                    ('assay_device_readout',),
                ),
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
    inlines = [AssayResultInline]

    def chip_readout(self, obj):
        if obj.id and not len(AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')) == 0:
            return AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')[0].assay_name
        return ''

    def result(self, obj):
        if obj.id and not len(AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')) == 0:
            abbreviation = AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')[0].result
            if abbreviation == '1':
                return u'Positive'
            else:
                return u'Negative'
        return ''

    def result_function(self, obj):
        if obj.id and not len(AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')) == 0:
            return AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')[0].result_function
        return ''

    def result_type(self, obj):
        if obj.id and not len(AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')) == 0:
            return AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')[0].result_type
        return ''

    def severity(self, obj):
        SEVERITY_SCORE = dict((
            ('-1', 'UNKNOWN'), ('0', 'NEGATIVE'), ('1', '+'), ('2', '+ +'),
            ('3', '+ + +'), ('4', '+ + + +'), ('5', '+ + + + +')
        ))
        if obj.id and not len(AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')) == 0:
            return SEVERITY_SCORE[AssayResult.objects.filter(assay_result_id=obj.id).order_by('id')[0].severity]
        return ''


admin.site.register(AssayTestResult, AssayTestResultAdmin)


class AssayPlateTestResultAdmin(LockableAdmin):
    # Test Results from MICROPLATES
    class Media(object):
        js = ('assays/customize_plate_results_admin.js',)
        css = {'all': ('assays/customize_admin.css',)}

    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = (
        'assay_device_id',
        'assay_test_time', 'time_units', 'result', 'severity', 'value', 'value_units'
    )
    search_fields = ['assay_device_id']
    actions = ['update_fields']
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on']

    fieldsets = (
        (
            'Device/Drug Parameters', {
                'fields': (
                    ('assay_device_id',),
                ),
            }
        ),
        (
            'Assay Test Parameters', {
                'fields': (
                    ('result', 'assay_test_time', 'time_units', 'value',
                     'value_units', 'severity', ),
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


admin.site.register(AssayPlateTestResult, AssayPlateTestResultAdmin)

# TODO Must test parsing for runs
def parseRunCSV(currentRun, file):
    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    readouts = []

    for rowID, rowValue in enumerate(datalist):
        # rowValue holds all of the row elements
        # rowID is the index of the current row from top to bottom

        # Get foreign keys from the first row
        if rowID == 0:
            readouts = [x for x in rowValue if x]

        elif not rowValue[0] or not rowValue[1] or not rowValue[2]:
            continue

        else:
            for colID in range(3, len(readouts)):
                currentChipReadout = readouts[colID]
                field = rowValue[2]
                val = rowValue[colID]
                time = rowValue[0]
                assay = AssayModel.objects.get(assay_name=rowValue[1])

                if not val:
                    val = None

                #How to parse Chip data
                AssayChipRawData(
                    assay_chip_id=AssayChipReadout.objects.get(id=currentChipReadout),
                    assay_id=AssayChipReadoutAssay.objects.get(readout_id=currentChipReadout, assay_id=assay),
                    field_id=field,
                    value=val,
                    elapsed_time=time
                ).save()
    return


class AssayRunForm(forms.ModelForm):
    class Meta(object):
        model = AssayRun
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # clean the form data, before validation
        data = super(AssayRunForm, self).clean()

        if data['assay_run_id'].startswith('-'):
            raise forms.ValidationError('Error with assay_run_id; please try again')

        # Check to make sure there is a file and it is not already in memory
        if data['file'] and type(data['file'].file) == BytesIO:
            datareader = csv.reader(data['file'].file, delimiter=',')
            datalist = list(datareader)

            readouts = list(x for x in datalist[0] if x)
            # Check if any Readouts already exist, if so, crash
            for id in readouts[3:]:
                if AssayChipRawData.objects.filter(assay_chip_id=id).count() > 0:
                    raise forms.ValidationError(
                        'Chip Readout id = %s already contains data; please change your batch file' % id)
                if not AssayChipReadout.objects.filter(id=id).exists():
                    raise forms.ValidationError(
                        'Chip Readout id = %s does not exist; please change your batch file or add this readout' % id)

            for line in datalist[1:]:
                assay_name = line[1]
                # TODO CHECK AssayChipReadoutAssay in lieu of AssayModel
                if not AssayChipReadoutAssay.objects.filter(assay_id__assay_name__contains=assay_name).exists():
                    raise forms.ValidationError(
                        'No assay with the name "%s" exists; please change your file or add this assay' % assay_name)

        return data


class AssayRunAdmin(LockableAdmin):
    class Media(object):
        js = ('assays/customize_run.js',)

    form = AssayRunForm
    save_on_top = True
    list_per_page = 300
    list_display = ('assay_run_id', 'study_types', 'start_date', 'description', )
    fieldsets = (
        (
            'Study', {
                'fields': (
                    'center_id',
                    ('type1', 'type2', 'type3'),
                    'start_date',
                    'name',
                    'assay_run_id',
                    'description',
                )
            }
        ),
        (
            'Study Data Upload', {
                'fields': (
                    'file',
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

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseRunCSV(obj, request.FILES['file'])

        obj.save()


admin.site.register(AssayRun, AssayRunAdmin)
