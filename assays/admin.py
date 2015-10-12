import csv

from django.contrib import admin
from django import forms
from assays.forms import StudyConfigurationForm, AssayChipReadoutInlineFormset, AssayPlateReadoutInlineFormset, label_to_number
from django.http import HttpResponseRedirect

from assays.models import *
from compounds.models import Compound
from mps.base.admin import LockableAdmin
from assays.resource import *
from import_export.admin import ImportExportModelAdmin
from compounds.models import *
import unicodedata
from io import BytesIO
import ujson as json
# I use regular expressions for a string split at one point
import re
from django.db import connection, transaction

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
        'assay_name', 'assay_short_name', 'version_number', 'assay_type', 'assay_description',
        'locked'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    ('assay_name', 'assay_short_name',),
                    ('assay_type','test_type',),
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


# Saving an Assay Layout is somewhat complicated, so a function is useful here (though perhaps not in this file [spaghetti])
# BE CAREFUL! FIELDS THAT ARE NOT IN THE FORM ARE AUTOMATICALLY SET TO NONE!
def save_assay_layout(request, obj, form, change):
    cursor = connection.cursor()

    type_query = ''' INSERT INTO "assays_assaywell"
          ("assay_layout_id", "well_type_id", "row", "column")
          VALUES (%s, %s, %s, %s)'''
    type_query_list = []

    time_query = ''' INSERT INTO "assays_assaywelltimepoint"
          ("assay_layout_id", "timepoint", "row", "column")
          VALUES (%s, %s, %s, %s)'''
    time_query_list = []

    compound_query = ''' INSERT INTO "assays_assaywellcompound"
          ("assay_layout_id", "compound_id", "concentration", "concentration_unit_id", "row", "column")
          VALUES (%s, %s, %s, %s, %s, %s)'''
    compound_query_list = []

    label_query = ''' INSERT INTO "assays_assaywelllabel"
          ("assay_layout_id", "label", "row", "column")
          VALUES (%s, %s, %s, %s)'''
    label_query_list = []

    layout = obj
    layout_id = obj.id

    if change:
        # Delete old types for this assay
        AssayWell.objects.filter(assay_layout=layout).delete()

        # Delete old compound data for this assay
        AssayWellCompound.objects.filter(assay_layout=layout).delete()

        # Delete old timepoint data for this assay
        AssayWellTimepoint.objects.filter(assay_layout=layout).delete()

        # Delete old labels for this assay
        AssayWellLabel.objects.filter(assay_layout=layout).delete()

        obj.modified_by = request.user

    else:
        obj.modified_by = obj.created_by = request.user

    obj.save()

    for key, val in form.data.iteritems():

        # Time points
        if key.endswith('_time'):
            # Cut off '_time'
            content = key[:-5]
            row, column = content.split('_')

            # Add new timepoint info
            time_query_list.append((
                layout_id,
                val,
                row,
                column
            ))

        # Compounds
        # Should refactor soon
        elif key.startswith('well_'):
            # Evaluate val as a JSON dict
            content = json.loads(val)
            well = content['well']
            row, col = well.split('_')

            if 'compound' in content:
                # Add compound info
                compound_query_list.append((
                    layout_id,
                    content['compound'],
                    content['concentration'],
                    content['concentration_unit'],
                    row,
                    col
                ))

        # Labels
        elif key.endswith('_label'):
            # Cut off '_label'
            content = key[:-6]
            row, column = content.split('_')

            # Add new label info
            label_query_list.append((
                layout_id,
                val,
                row,
                column
            ))

        # Types
        elif key.endswith('_type'):
            # Uncertain as to why empty values are passed
            # TODO EXPLORE EMPTY VALUES
            if val:
                # Cut fof '_type'
                content = key[:-5]
                row, column = content.split('_')

                # Add new timepoint info
                type_query_list.append((
                    layout_id,
                    val,
                    row,
                    column
                ))

    cursor.executemany(type_query,type_query_list)
    cursor.executemany(time_query,time_query_list)
    cursor.executemany(compound_query,compound_query_list)
    cursor.executemany(label_query,label_query_list)

    transaction.commit()


# TODO REVISE SAVING
# TODO ADMIN IS NOT FUNCTIONAL AT THE MOMENT
class AssayLayoutAdmin(LockableAdmin):
    class Media(object):
        js = ('assays/customize_layout.js',)
        css = {'all': ('assays/customize_admin.css',)}

    save_as = True
    save_on_top = True
    list_per_page = 300
    fieldsets = (
        (
            'Layout Parameters', {
                'fields': (
                    ('layout_name',
                     'device',
                     'locked',
                    )
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

    def save_model(self, request, obj, form, change):
        save_assay_layout(request, obj, form, change)

admin.site.register(AssayLayout, AssayLayoutAdmin)


class AssayPlateCellsInline(admin.TabularInline):
    # Cells used to construct the plate
    model = AssayPlateCells
    verbose_name = 'Plate Cells'
    verbose_name_plural = 'Plate Cells'
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


class AssayPlateSetupAdmin(LockableAdmin):
    # Setups for MICROPLATES

    class Media(object):
        js = ('js/inline_fix.js','assays/customize_plate_setup.js')
        css = {'all': ('assays/customize_admin.css',)}

    save_on_top = True
    list_per_page = 300
    list_display = ('assay_plate_id',
                    'assay_run_id',
                    'setup_date')

    inlines = [AssayPlateCellsInline]

    fieldsets = (
        (
            'Device Parameters', {
                'fields': (
                    (
                        'assay_run_id',
                    ),
                    (
                        'assay_plate_id', 'setup_date',
                    ),
                    (
                        'assay_layout',
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

admin.site.register(AssayPlateSetup, AssayPlateSetupAdmin)

# As much as I like being certain, this code is somewhat baffling
def removeExistingReadout(currentAssayReadout):
    AssayReadout.objects.filter(assay_device_readout=currentAssayReadout).delete()

    # readouts = AssayReadout.objects.filter(
    #     assay_device_readout_id=currentAssayReadout.id)
    #
    # for readout in readouts:
    #     if readout.assay_device_readout_id == currentAssayReadout.id:
    #         readout.delete()
    # return

def get_qc_status_plate(form):
    # Get QC status for each line
    qc_status = {}

    for key, val in form.data.iteritems():
        # If this is a QC input
        if key.endswith('_QC'):
            # Split up the key
            split_up = key.split('_')
            row = split_up[0]
            col = split_up[1]
            # Be sure to convert time to a float
            time = float(split_up[2])
            # Combine values in a tuple for index
            index = (row,col,time)
            # Truncate value to be less than 20 characters to avoid errors
            value = val[:9]
            qc_status.update({index: value})

    return qc_status

@transaction.atomic
def modify_qc_status_plate(current_plate_readout, form):
    # Get the readouts as they would appear on the front end
    # PLEASE NOTE THAT ORDER IS IMPORTANT HERE TO MATCH UP WITH THE INPUTS
    readouts = AssayReadout.objects.filter(assay_device_readout=current_plate_readout)

    # Get QC status for each line
    qc_status = get_qc_status_plate(form)

    for readout in readouts:
        index = (readout.row, readout.column, readout.elapsed_time)
        if index in qc_status:
            readout.quality = qc_status.get(index)
            readout.save()
        # If the quality marker has been removed
        elif index not in qc_status and readout.quality:
            readout.quality = u''
            readout.save()

# Rows are currenly numeric, not alphabetical, when stored in the database
def parseReadoutCSV(currentAssayReadout, file, upload_type):
    removeExistingReadout(currentAssayReadout)

    cursor = connection.cursor()

    query = ''' INSERT INTO "assays_assayreadout"
          ("assay_device_readout_id", "assay_id", "row", "column", "value", "elapsed_time", "quality")
          VALUES (%s, %s, %s, %s, %s, %s, '')'''

    query_list = []

    currentAssayReadoutId = currentAssayReadout.id

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    assays = dict(
        (o.feature, o.id) for o in AssayPlateReadoutAssay.objects.filter(
            readout_id=currentAssayReadout
        ).only('feature')
    )

    if upload_type == 'Block':
        # Current assay
        assay = None
        # Current time
        time = None

        # Used to discern number of headers for offset
        number_of_assays = 0
        # Used to discern row offset
        number_of_rows = currentAssayReadout.setup.assay_layout.device.number_of_rows

        for row_id, line in enumerate(datalist):
            # TODO HOW DO I DEAL WITH BLANK LINES???
            # If line is blank
            if not line:
                continue

            # If this line is a header
            # Headers should look like:
            # FEATURE, {{FEATURE}}, READOUT UNIT, {{READOUT UNIT}}, TIME, {{TIME}}. TIME UNIT, {{TIME UNIT}}
            if line[0].lower().strip() == 'feature':
                feature = line[1]
                # Get the assay
                assay = assays.get(feature)
                number_of_assays += 1

                if len(line) >= 8:
                    time = line[5]

                else:
                    time = None

            # Otherwise the line contains datapoints for the current assay
            else:
                for column_id, value in enumerate(line):
                    # Treat empty strings as NULL values and do not save the data point
                    if not value:
                        continue

                    # MUST OFFSET ROW (due to multiple datablocks)
                    offset_row_id = (row_id-number_of_assays) % number_of_rows

                    if time:
                        query_list.append((
                            currentAssayReadoutId,
                            assay,
                            offset_row_id,
                            column_id,
                            value,
                            time
                        ))

                    else:
                        # Note default elapsed time of 0
                        query_list.append((
                            currentAssayReadoutId,
                            assay,
                            offset_row_id,
                            column_id,
                            value,
                            0
                        ))

    # Otherwise if the upload is tabular
    else:
        # Purge empty lines, they are useless for tabular uploads
        datalist = [row for row in datalist if any(row)]
        # The first line SHOULD be the header
        header = datalist[0]

        if header[1].lower().strip() == 'time':
            # IF TIME The features are the fourth column of the header onward
            features = header[3:]
            time_specified = True
        else:
            # IF NO TIME The features are the second column of the header onward
            features = header[1:]
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # The well identifier given
            well = row[0]
            # Split the well into alphabetical and numeric
            row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well)

            # PLEASE NOTE THAT THE VALUES ARE OFFSET BY ONE (to begin with 0)
            # Convert row_label to a number
            row_label = label_to_number(row_label) - 1
            # Convert column label to an integer
            column_label = int(column_label) - 1

            if time_specified:
                # Values are the slice of the fourth item onward
                values = row[3:]
                time = row[1]

            else:
                # Values are the slice of the second item onward
                values = row[1:]
                time = 0

            for column_index, value in enumerate(values):
                feature = features[column_index]
                # NOTE THAT BLANKS ARE CURRENTLY COMPLETELY EXCLUDED
                if value != '':
                    value = float(value)

                    assay = assays.get(feature)

                    query_list.append((
                        currentAssayReadoutId,
                        assay,
                        row_label,
                        column_label,
                        value,
                        time
                    ))

    cursor.executemany(query,query_list)

    transaction.commit()


class AssayPlateReadoutInline(admin.TabularInline):
    # Assays for ChipReadout
    formset = AssayPlateReadoutInlineFormset
    model = AssayPlateReadoutAssay
    verbose_name = 'Assay Plate Readout Assay'
    verbose_plural_name = 'Assay Plate Readout Assays'

    fields = (
        (
            ('assay_id','reader_id','readout_unit','feature')
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


# Plate Readout validation occurs in the inline formset
# This form is just to jam in upload_type into the admin
class AssayPlateReadoutForm(forms.ModelForm):

    upload_type = forms.ChoiceField(choices=(('Tabular', 'Tabular'), ('Block', 'Block')))

    class Meta(object):
        model = AssayPlateReadout
        exclude = ('',)


class AssayPlateReadoutAdmin(LockableAdmin):
    # Endpoint readouts from MICROPLATES
    resource_class = AssayPlateReadoutResource
    form = AssayPlateReadoutForm

    class Media(object):
        js = ('js/inline_fix.js', 'assays/customize_plate_readout.js',)
        css = {'all': ('assays/customize_admin.css',)}

    inlines = [AssayPlateReadoutInline]

    date_hierarchy = 'readout_start_time'
    # raw_id_fields = ("cell_sample",)
    save_on_top = True
    list_per_page = 300
    list_display = ('id',
                    #'assay_device_id',
                    # 'cell_sample',
                    'readout_start_time',)
    fieldsets = (
        (
            'Device Parameters', {
                'fields': (
                    # (
                    #     'assay_device_id',
                    # ),
                    (
                        'setup',
                    ),
                )
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    (
                        'timeunit', 'treatment_time_length', 'readout_start_time',
                    ),
                    (
                        'file', 'upload_type'
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

    # save_related takes the place of save_model so that the inline can be saved first
    # this is similar to chip readouts so that we can validate the listed assays THEN the file
    def save_related(self, request, form, formsets, change):
        obj = form.instance

        # Need to get the upload type
        upload_type = form.data.get('upload_type')

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        # Save Plate Readout
        obj.save()
        # Save inline
        super(LockableAdmin, self).save_related(request, form, formsets, change)

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseReadoutCSV(obj, request.FILES['file'], upload_type)

        #Need to delete entries when a file is cleared
        if 'file-clear' in request.POST and request.POST['file-clear'] == 'on':
            removeExistingReadout(obj)

        else:
            modify_qc_status_plate(obj, form)

    # save_model not used; would save twice otherwise
    def save_model(self, request, obj, form, change):
        pass

admin.site.register(AssayPlateReadout, AssayPlateReadoutAdmin)

# Case and point for why you should not just copy code without carefully reading it
# TODO these remove functions really should not even exist (one line of code?)
def removeExistingChip(currentChipReadout):
    AssayChipRawData.objects.filter(assay_chip_id=currentChipReadout).delete()
    # readouts = AssayChipRawData.objects.filter(
    #     assay_chip_id_id=currentChipReadout.id)
    #
    # for readout in readouts:
    #     if readout.assay_chip_id_id == currentChipReadout.id:
    #         readout.delete()
    # return

def get_qc_status_chip(form):
    # Get QC status for each line
    qc_status = {}

    if not form:
        return qc_status

    for key, val in form.data.iteritems():
        # If this is a QC input
        if key.startswith('QC_'):
            # Get index from key
            index = int(key.split('_')[-1])
            # Truncate value to be less than 20 characters to avoid errors
            value = val[:19]
            qc_status.update({index: value})

    return qc_status

@transaction.atomic
def modify_qc_status_chip(current_chip_readout, form):
    # Get the readouts as they would appear on the front end
    # PLEASE NOTE THAT ORDER IS IMPORTANT HERE TO MATCH UP WITH THE INPUTS
    readouts = AssayChipRawData.objects.filter(assay_chip_id=current_chip_readout).order_by('assay_id','elapsed_time')

    # Get QC status for each line
    qc_status = get_qc_status_chip(form)

    for index, readout in enumerate(readouts):
        readout.quality = qc_status.get(index)
        readout.save()

@transaction.atomic
def parseChipCSV(currentChipReadout, file, headers, form):
    removeExistingChip(currentChipReadout)

    # Get QC status for each line
    qc_status = get_qc_status_chip(form)

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    # Current index for finding correct QC status
    current_index = 0

    # Only take values from headers onward
    for rowID, rowValue in enumerate(datalist[headers:]):
        # rowValue holds all of the row elements
        # rowID is the index of the current row from top to bottom

        # Skip any row with insufficient commas
        if len(rowValue) < 6:
            continue

        # Skip any row with incomplete data
        # This does not include the quality
        if not all(rowValue[:6]):
            continue

        # Try getting the assay from long name
        try:
            assay = AssayModel.objects.get(assay_name__iexact=rowValue[2])
        # If this fails, then use the short name
        except:
            assay = AssayModel.objects.get(assay_short_name__iexact=rowValue[2])

        field = rowValue[3]
        val = rowValue[4]
        time = rowValue[0]

        # PLEASE NOTE Database inputs, not the csv, have the final say
        # Get quality if possible
        quality = u''
        if len(rowValue) > 6:
            quality = rowValue[6]

        # Get quality from added form inputs if possible
        if current_index in qc_status:
            quality = qc_status.get(current_index)
        # Increment current index acquisition
        current_index += 1

        # Originally permitted none values, will now ignore empty values
        # if not val:
        #     val = None

        #How to parse Chip data
        AssayChipRawData(
            assay_chip_id=currentChipReadout,
            assay_id=AssayChipReadoutAssay.objects.get(readout_id=currentChipReadout, assay_id=assay),
            field_id=field,
            value=val,
            elapsed_time=time,
            quality=quality,
        ).save()



class AssayChipCellsInline(admin.TabularInline):
    # Cells used to construct the model
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
    date_hierarchy = 'setup_date'

    list_per_page = 100
    list_display = ('assay_chip_id', 'assay_run_id', 'setup_date',
                    'device', 'chip_test_type',
                    'compound', 'scientist')

    search_fields = ['assay_chip_id']
    fieldsets = (
        (
            'Study', {
                'fields': (
                    (
                        'assay_run_id', 'setup_date',
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
                    (
                        'variance',
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

    actions = ['update_fields']
    inlines = [AssayChipCellsInline]

    def response_add(self, request, obj):
        """If save and add another, have same response as save and continue"""
        if '_saveasnew' in request.POST or '_addanother' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(AssayChipSetupAdmin, self).response_add(request, obj)

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
    formset = AssayChipReadoutInlineFormset
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

# ChipReadout validation occurs in the inline formset
class AssayChipReadoutForm(forms.ModelForm):

    headers = forms.CharField(required=False)

    class Meta(object):
        model = AssayChipReadout
        exclude = ('',)

class AssayChipReadoutAdmin(LockableAdmin):
    # TIMEPOINT readouts from ORGAN CHIPS
    class Media(object):
        js = ('js/inline_fix.js','assays/customize_chip.js', 'js/d3.min.js', 'js/c3.min.js',)
        css = {'all': ('assays/customize_admin.css', 'css/c3.css',)}

    form = AssayChipReadoutForm
    date_hierarchy = 'readout_start_time'

    raw_id_fields = ("chip_setup",)

    save_on_top = True
    save_as = True

    list_per_page = 100
    list_display = ('id',
                    'chip_setup',
                    'assays',
                    'readout_start_time',
                    'scientist'
                    )

    list_display_links = ('id', 'chip_setup',
                          'readout_start_time',)
    search_fields = ['assay_chip_id']
    fieldsets = (
        (
            'Setup Parameters', {
                'fields': (
                    (
                        'chip_setup'
                    ),
                )
            }
        ),
        (
            'Assay Parameters', {
                'fields': (
                    (
                        'timeunit', 'treatment_time_length', 'readout_start_time',
                    ),
                    (
                        'file',
                    ),
                    (
                        'headers',
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

    inlines = [AssayChipReadoutInline]

    def response_add(self, request, obj):
        """If save and add another, have same response as save and continue"""
        if '_saveasnew' in request.POST or '_addanother' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(AssayChipReadoutAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        """If save as new, redirect to new change model; else go to list"""
        if '_saveasnew' in request.POST:
            return HttpResponseRedirect("../%s" % obj.id)
        else:
            return super(LockableAdmin, self).response_change(request, obj)

    # save_related takes the place of save_model so that the inline can be saved first
    def save_related(self, request, form, formsets, change):
        obj = form.instance

        headers = int(form.data.get('headers')) if form.data.get('headers') else 0

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        # Save Chip Readout
        obj.save()
        # Save inline
        super(LockableAdmin, self).save_related(request, form, formsets, change)

        if request.FILES:
            # pass the upload file name to the CSV reader if a file exists
            parseChipCSV(obj, request.FILES['file'], headers, form)

        # Try to update QC status if no file
        else:
            modify_qc_status_chip(obj, form)

        #Need to delete entries when a file is cleared
        if 'file-clear' in request.POST and request.POST['file-clear'] == 'on':
            removeExistingChip(obj)

    # save_model not used; would save twice otherwise
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


class AssayChipResultInline(admin.TabularInline):
    # Results calculated from CHIP READOUTS
    model = AssayChipResult
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


admin.site.register(PhysicalUnits, PhysicalUnitsAdmin)


#class TimeUnitsAdmin(LockableAdmin):
#    save_on_top = True
#    list_per_page = 300
#
#    list_display = ('unit', 'unit_order',)
#    fieldsets = (
#        (
#            None, {
#                'fields': (
#                    'unit',
#                    'description',
#                    'unit_order',
#                )
#            }
#        ),
#        ('Change Tracking', {
#            'fields': (
#                'locked',
#                ('created_by', 'created_on'),
#                ('modified_by', 'modified_on'),
#                ('signed_off_by', 'signed_off_date'),
#            )
#        }
#        ),
#    )
#
#
#admin.site.register(TimeUnits, TimeUnitsAdmin)


#class ReadoutUnitAdmin(LockableAdmin):
#    save_on_top = True
#    list_per_page = 100
#
#    list_display = ('readout_unit', 'description',)
#    fieldsets = (
#        (
#            None, {
#                'fields': (
#                    'readout_unit',
#                    'description'
#                )
#            }
#        ),
#        ('Change Tracking', {
#            'fields': (
#                'locked',
#                ('created_by', 'created_on'),
#                ('modified_by', 'modified_on'),
#                ('signed_off_by', 'signed_off_date'),
#            )
#        }
#        ),
#    )
#
#
#admin.site.register(ReadoutUnit, ReadoutUnitAdmin)


class AssayChipTestResultAdmin(LockableAdmin):
    # Results calculated from RAW CHIP DATA aka 'Chip Result'
    class Media(object):
        js = ('js/cookies.js','js/whittle.js','js/inline_fix.js','assays/customize_chip_results_admin.js')

    save_as = True
    save_on_top = True
    list_per_page = 300
    list_display = (
        'chip_readout', 'assay', 'result', 'result_function', 'result_type', 'severity'
    )
    search_fields = ['chip_readout']
    actions = ['update_fields']
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on', ]

    fieldsets = (
        (
            'Device/Drug Parameters', {
                'fields': (
                    ('chip_readout',),
                    ('summary',),
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )
    inlines = [AssayChipResultInline]

admin.site.register(AssayChipTestResult, AssayChipTestResultAdmin)


class AssayPlateResultInline(admin.TabularInline):
    # Results calculated from PLATE READOUTS
    model = AssayPlateResult
    verbose_name = 'Assay Plate Result'
    verbose_name_plural = 'Assay Plate Results'
    fields = (
        (
            'assay_name', 'result', 'result_function', 'result_type',
            'value', 'test_unit', 'severity',
        ),
    )
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class AssayPlateTestResultAdmin(LockableAdmin):
    # Test Results from MICROPLATES
    class Media(object):
        js = ('js/cookies.js','js/whittle.js', 'js/inline_fix.js', 'assays/customize_plate_results.js')
        css = {'all': ('assays/customize_admin.css',)}

    inlines = [AssayPlateResultInline,]

    save_as = True
    save_on_top = True
    # raw_id_fields = ('readout',)
    list_per_page = 300
    list_display = (
        'readout',
    )
    search_fields = ['readout']
    actions = ['update_fields']
    readonly_fields = ['created_by', 'created_on',
                       'modified_by', 'modified_on']

    fieldsets = (
        (
            'Device/Drug Parameters', {
                'fields': (
                    ('readout',),
                    ('summary',),
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
        (
            'Flag for Review', {
                'fields': (
                    ('flagged', 'reason_for_flag',)
                )
            }
        ),
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )


admin.site.register(AssayPlateTestResult, AssayPlateTestResultAdmin)

# TODO CHANGE TO USE SETUP IN LIEU OF READOUT ID
# TODO CHANGE TO REMOVE PREVIOUS DATA
# TODO BULK UPLOADS ARE CURRENTLY NOT AVAILABLE
@transaction.atomic
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
                    continue

                # Originally did not ignore empty cells; does now
                # if not val:
                #     val = None

                #How to parse Chip data
                AssayChipRawData(
                    assay_chip_id=AssayChipReadout.objects.get(id=currentChipReadout),
                    assay_id=AssayChipReadoutAssay.objects.get(readout_id=currentChipReadout, assay_id=assay),
                    field_id=field,
                    value=val,
                    elapsed_time=time
                ).save()
    return


class AssayRunFormAdmin(forms.ModelForm):
    class Meta(object):
        model = AssayRun
        widgets = {
            'assay_run_id': forms.Textarea(attrs={'rows': 1}),
            'name': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        exclude = ('',)

    # TODO CLEAN TO USE SETUP IN LIEU OF READOUT ID
    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # clean the form data, before validation
        data = super(AssayRunFormAdmin, self).clean()

        if not any([data['toxicity'],data['efficacy'],data['disease'],data['cell_characterization']]):
            raise forms.ValidationError('Please select at least one study type')

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
                if not assay_name:
                    continue
                if not AssayModel.objects.filter(assay_name=assay_name).exists():
                    raise forms.ValidationError(
                        'No assay with the name "%s" exists; please change your file or add this assay' % assay_name)
                assay = AssayModel.objects.get(assay_name=assay_name)
                for i in range(3,len(readouts)):
                    val = line[i]
                    if val and val != 'None':
                        currentChipReadout = readouts[i]
                        if not AssayChipReadoutAssay.objects.filter(readout_id=currentChipReadout, assay_id=assay).exists():
                            raise forms.ValidationError(
                                'No assay with the name "%s" exists; please change your file or add this assay' % assay_name)
                    # Check every value to make sure it can resolve to a float
                    try:
                        float(val)
                    except:
                        raise forms.ValidationError(
                                'The value "%s" is invalid; please make sure all values are numerical' % str(val))

        return data


class AssayRunAdmin(LockableAdmin):
    # AssayRun is now Organ Chip Study
    # Organ Chip Study should really be simply Study
    class Media(object):
        js = ('assays/customize_run.js',)

    form = AssayRunFormAdmin
    save_on_top = True
    list_per_page = 300
    date_hierarchy = 'start_date'
    list_display = ('assay_run_id', 'study_types', 'start_date', 'description', )
    fieldsets = (
        (
            'Study', {
                'fields': (
                    ('toxicity', 'efficacy', 'disease', 'cell_characterization'),
                    'study_configuration',
                    'start_date',
                    'name',
                    'description',
                    'image',
                )
            }
        ),
        (
            'Study ID (Autocreated from entries above)', {
                'fields': (
                    'assay_run_id',
                )
            }
        ),
        # Removed to avoid confusion
        # (
        #     'Study Data Upload', {
        #         'fields': (
        #             'file',
        #         )
        #     }
        # ),
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
        (
            'Group Access', {
                'fields':(
                    'group','restricted'
                 ),
            }
        ),
    )

    def save_model(self, request, obj, form, change):

        if change:
            obj.modified_by = request.user

        else:
            obj.modified_by = obj.created_by = request.user

        # TODO FIX BULK UPLOAD BEFORE ALLOWING THIS
        # if request.FILES:
        #     # pass the upload file name to the CSV reader if a file exists
        #     parseRunCSV(obj, request.FILES['file'])

        obj.save()


admin.site.register(AssayRun, AssayRunAdmin)


class StudyModelInline(admin.TabularInline):

    model = StudyModel
    verbose_name = 'Study Model'
    fields = (
        (
            'label', 'organ', 'sequence_number', 'output', 'integration_mode',
        ),
    )
    extra = 1

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class StudyConfigurationAdmin(LockableAdmin):
    class Media(object):
        js = ('js/inline_fix.js',)

    form = StudyConfigurationForm
    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'study_format',)
    fieldsets = (
        (
            'Study Configuration', {
                'fields': (
                    'name',
                    'study_format',
                    'media_composition',
                    'hardware_description',
                    #'image',
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
    inlines = [StudyModelInline]


admin.site.register(StudyConfiguration, StudyConfigurationAdmin)
