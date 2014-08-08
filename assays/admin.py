import csv

from django.contrib import admin
from django import forms
from assays.forms import AssayResultForm
from assays.forms import AssayRunForm

from assays.models import *
from compounds.models import Compound
from mps.base.admin import LockableAdmin
from assays.resource import *
from import_export.admin import ImportExportModelAdmin
from compounds.models import *


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
        if not (int(data['number_of_rows']) ==
                    len(set(data['row_labels'].split()))):
            raise forms.ValidationError('Number of rows and '
                                        'number of unique row '
                                        'labels do not match.')

        # need to return clean data if it validates
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

            ### BEGIN save timepoint data ###

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
                        'compound', 'concentration',
                        'concentration_unit',
                    ),
                    (
                        'cell_sample', 'cellsample_density',
                        'cellsample_density_unit',
                    ),
                    (
                        'timeunit', 'readout_unit',
                    ),
                    (
                        'treatment_time_length', 'assay_start_time','readout_start_time',
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

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseReadoutCSV(obj, request.FILES['file'].file)

        obj.save()


admin.site.register(AssayDeviceReadout, AssayDeviceReadoutAdmin)


class AssayResultInline(admin.TabularInline):
    model = AssayResult
    form = AssayResultForm
    verbose_name = 'Assay/Drug Trial Test'
    verbose_name_plural = 'Assay/Drug Trial Test Results'
    fields = (
        (
            'test_name', 'test_time', 'time_units',
            'value', 'test_unit',
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class AssayTestAdmin(LockableAdmin):

    resource_class = AssayTestResource

    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = (
        'test_date', 'microdevice', 'assay_device_id',
        'compound', 'assay_layout',
        'cell_sample', 'locked'
    )
    search_fields = ['assay_device_id']
    actions = ['update_fields']
    raw_id_fields = ('compound', 'cell_sample',)
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on', 'compound_display']

    def compound_display(self, obj):

        if obj.compound.chemblid:
            url = (u'https://www.ebi.ac.uk/chembldb/compound/'
                   'displayimage/' + obj.compound.chemblid)
            return '<img src="%s">' % \
                url
        else:
            return u''

    compound_display.allow_tags = True
    compound_display.short_description = 'Structure'

    fieldsets = (
        (
            'Device Parameters', {
                'fields': (
                    ('microdevice', 'assay_layout',),
                    ('assay_device_id', 'reader_name'),
                ),
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    ('compound', 'cell_sample', 'test_date'),
                    'compound_display',
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
    inlines = [AssayResultInline]


admin.site.register(AssayTest, AssayTestAdmin)


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

    list_display = ('unit','unit_order',)
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

    list_display = ('readout_unit','description',)
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


class AssayFindingTypeAdmin(LockableAdmin):
    list_per_page = 300
    save_on_top = True
    list_display = ('assay_finding_type', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'assay_finding_type',
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
admin.site.register(AssayFindingType, AssayFindingTypeAdmin)


class AssayFindingAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('assay_finding_name', 'assay_finding_type', 'optional_link')
    list_display_links = ('assay_finding_name',)
    list_filter = sorted(['assay_finding_type'])
    search_fields = ['assay_finding_name', ]
    fieldsets = (
        (
            None, {
                'fields': (
                    'assay_finding_name',
                    'assay_finding_type',
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

    def optional_link(self, obj):
        words = obj.description.split()
        sentence = ''
        for thing in words:
            if thing.startswith("http://"):
                link = '<a href="%s" target="_blank">%s</a>' % (thing, thing)
                sentence += (' ' + link)
            else:
                sentence += (' ' + thing)
        return sentence
    optional_link.allow_tags = True
    optional_link.short_description = "Description"


admin.site.register(AssayFinding, AssayFindingAdmin)


class AssayTestResultAdmin(LockableAdmin):
    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = (
        'assay_device_readout', 'compound', 'assay_finding_name',
            'assay_test_time','time_units','result','severity','value','value_units'
    )
    search_fields = ['assay_device_readout']
    actions = ['update_fields']
    raw_id_fields = ('compound',)
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on', 'compound_display']

    def compound_display(self, obj):

        if obj.compound.chemblid:
            url = (u'https://www.ebi.ac.uk/chembldb/compound/'
                   'displayimage/' + obj.compound.chemblid)
            return '<img src="%s">' % \
                url
        else:
            return u''

    compound_display.allow_tags = True
    compound_display.short_description = 'Structure'

    fieldsets = (
        (
            'Device/Drug Parameters', {
                'fields': (
                    ('assay_device_readout',),
                    ('compound', 'compound_display'),
                ),
            }
        ),
        (
            'Assay Test Parameters', {
                'fields': (
                    ('assay_finding_name', 'assay_test_time','time_units','result','severity','value','value_units'),
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


admin.site.register(AssayTestResult, AssayTestResultAdmin)


class AssayRunAdmin(LockableAdmin):
    form = AssayRunForm
    save_on_top = True
    list_per_page = 300
    list_display = ('assay_run_id', 'name', 'description', 'start_date')
    fieldsets = (
        (
            'None', {
                'fields': (
                    'assay_run_id',
                    'name',
                    'description',
                    'start_date'
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

admin.site.register(AssayRun, AssayRunAdmin)
