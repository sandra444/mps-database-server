import csv

from django.contrib import admin
from django import forms
from assays.forms import AssayChipResultForm, StudyConfigurationForm, CloneableBaseInlineFormSet
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
import string
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
        'assay_name', 'version_number', 'assay_type', 'assay_description',
        'locked'
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    ('assay_name', 'assay_type','test_type'),
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

        # if not key.startswith('well_') and not '_time' in key:
        #     continue

        # ## BEGIN save timepoint data ###

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

            # AssayWellTimepoint(
            #     assay_layout=obj,
            #     timepoint=val,
            #     row=row,
            #     column=column
            # ).save()

        ### END save timepoint data ###

        ### BEGIN save compound information ###

        # if not key.startswith('well_'):
        #     continue

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

                # AssayWellCompound(
                #     assay_layout=obj,
                #     compound_id=content['compound'],
                #     concentration=content['concentration'],
                #     concentration_unit=content['concentration_unit'],
                #     row=row,
                #     column=col
                # ).save()

        ### END save compound information ###

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

            # AssayWellLabel(
            #     assay_layout=obj,
            #     label=val,
            #     row=row,
            #     column=column
            # ).save()

        # Types
        elif key.endswith('_type'):
            # Uncertain as to why empty values are past
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

                # AssayWell(
                #     assay_layout=obj,
                #     well_type_id=val,
                #     row=row,
                #     column=column
                # ).save()

    cursor.executemany(type_query,type_query_list)
    cursor.executemany(time_query,time_query_list)
    cursor.executemany(compound_query,compound_query_list)
    cursor.executemany(label_query,label_query_list)

    transaction.commit()


# TODO REVISE SAVING
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

# This function turns a label to a number
def label_to_number(label):
    num = 0
    for char in label:
        if char in string.ascii_letters:
            num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num

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


# TODO CHANGE BLOCK UPLOAD
# TODO ADD TABULAR UPLOAD
# TODO CHANGE ROW TO BE ALPHABETICAL IN LIEU OF NUMERIC?
def parseReadoutCSV(currentAssayReadout, file, upload_type):
    removeExistingReadout(currentAssayReadout)

    cursor = connection.cursor()

    query = ''' INSERT INTO "assays_assayreadout"
          ("assay_device_readout_id", "assay_id", "row", "column", "value", "elapsed_time")
          VALUES (%s, %s, %s, %s, %s, %s)'''

    query_list = []

    currentAssayReadoutId = currentAssayReadout.id

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    assays = dict((o.feature, o.id) for o in AssayPlateReadoutAssay.objects.filter(readout_id=currentAssayReadout).only('feature'))

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
            # Headers should look like: FEATURE, {{FEATURE}}, READOUT UNIT, {{READOUT UNIT}}, TIME, {{TIME}}. TIME UNIT, {{TIME UNIT}}
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

                        # AssayReadout(
                        #     assay_device_readout_id=currentAssayReadoutId,
                        #     row=offset_row_id,
                        #     column=column_id,
                        #     value=value,
                        #     # the associated assay
                        #     assay_id=assay,
                        #     elapsed_time=time
                        # ).save()
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

                        # AssayReadout(
                        #     assay_device_readout_id=currentAssayReadoutId,
                        #     row=offset_row_id,
                        #     column=column_id,
                        #     value=value,
                        #     assay_id=assay,
                        # ).save()

    # Otherwise if the upload is tabular
    else:
        # Purge empty lines, they are useless for tabular uploads
        datalist = [row for row in datalist if any(row)]
        # The first line SHOULD be the header
        header = datalist[0]

        if header[1].lower().strip() == 'time':
            # The features are the third column of the header onward
            features = header[3:]
            time_specified = True
        else:
            # The features are the third column of the header onward
            features = header[1:]
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # The well identifier given
            well = row[0]
            # Split the well into alphabetical and numeric
            row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well)

            # TODO PLEASE NOTE THAT THE VALUES ARE OFFSET BY ONE (to begin with 0)
            # Convert row_label to a number
            row_label = label_to_number(row_label) - 1
            # Convert column label to an integer
            column_label = int(column_label) - 1

            if time_specified:
                # Values are the slice of the fourth item onward
                values = row[3:]
                time = row[1]

            else:
                # Values are the slice of the first item onward
                values = row[1:]
                time = 0

            for column_index, value in enumerate(values):
                feature = features[column_index]
                # TODO NOTE THAT BLANKS ARE CURRENTLY COMPLETELY EXCLUDED
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
                    # AssayReadout(
                    #     assay_device_readout_id=currentAssayReadoutId,
                    #     row=row_label,
                    #     column=column_label,
                    #     value=value,
                    #     assay_id=assay,
                    # ).save()

    cursor.executemany(query,query_list)

    transaction.commit()

    # for rowID, rowValue in enumerate(datalist):
    #     # rowValue holds all of the row elements
    #     # rowID is the index of the current row from top to bottom
    #     for columnID, columnValue in enumerate(rowValue):
    #         # columnValue is a single number: the value of our specific cell
    #         # columnID is the index of the current column
    #
    #         # Treat empty strings as NULL values and do not save the data point
    #         if not columnValue:
    #             continue
    #
    #         AssayReadout(
    #             assay_device_readout=currentAssayReadout,
    #             row=rowID,
    #             column=columnID,
    #             value=columnValue
    #         ).save()


# TODO CHANGE BLOCK UPLOAD
# TODO ADD TABULAR UPLOAD
# TODO LINKING MULTIPLE ASSAYS TO ONE FEATURE IS AMBIGUOUS: DO NOT ALLOW IT (X?)
# TODO DO NOT ALLOW ROW OR COLUMN OVERFLOW (or underflow?)
class AssayPlateReadoutInlineFormset(CloneableBaseInlineFormSet):
    def clean(self):
        """Validate unique, existing PLATE READOUTS"""

        # Get upload type
        upload_type = self.data.get('upload_type')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Dic of assay names from inline with respective unit as value
        assays = {}
        # Dic of features with respective assay
        features_to_assay = {}
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name
                    unit = form.cleaned_data.get('readout_unit').unit

                    feature = form.cleaned_data.get('feature')

                    # Error when feature assignation ambiguous
                    if feature in features_to_assay:
                        raise forms.ValidationError(
                            'The feature "{}" is used more than once; ambiguous feature binding is not permitted'.format(feature))

                    features_to_assay.update({feature: assay_name})

                    if assay_name not in assays:
                        assays.update({assay_name:unit})
                    else:
                        raise forms.ValidationError(
                            'Duplicate assays are not permitted; please blank out or change the duplicate')
            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

        # TODO
        # If there is already a file in the database and it is not being replaced or cleared (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:

            saved_data = AssayReadout.objects.filter(assay_device_readout=self.instance).prefetch_related('assay')

            for raw in saved_data:

                assay = raw.assay.assay_id.assay_name
                val_unit = raw.assay.readout_unit.unit
                feature = raw.assay.feature

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
                # Raise error if val_unit not equal to one listed in APRA
                if val_unit != assays.get(assay,''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"' % (val_unit, assays.get(assay,'')))
                # TODO Raise error if feature does not correspond?
                if feature not in features_to_assay:
                    raise forms.ValidationError(
                        'You can not remove the feature "{}" because it is in your uploaded data.'.format(feature))
                if features_to_assay.get(feature) != assay:
                    raise forms.ValidationError(
                        'The assay-feature pair in the uploaded data is "{0}-{1}," not "{2}-{3}."'.format(assay,feature,features_to_assay.get(feature),feature))

        # TODO what shall a uniqueness check look like?
        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file','')

            datareader = csv.reader(test_file, delimiter=',')
            datalist = list(datareader)

            # Acquire number of rows and columns
            number_of_rows = self.instance.setup.assay_layout.device.number_of_rows
            number_of_columns = self.instance.setup.assay_layout.device.number_of_columns

            # Tedious way of getting timeunit; probably should refactor
            readout_time_unit = PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit

            if upload_type == 'Block':
                # Number of assays found
                assays_found = 0
                # Number of data blocks found
                data_blocks_found = 0

                for row_index, line in enumerate(datalist):
                    # If line is blank, skip it
                    if not line:
                        continue

                    # If this line is a header
                    # NOTE THAT FEATURE -> ASSAY
                    # Headers should look like: FEATURE, {{FEATURE}}, READOUT UNIT, {{READOUT UNIT}}, TIME, {{TIME}}. TIME UNIT, {{TIME UNIT}}
                    if line[0].lower().strip() == 'feature':
                        # Throw error if header too short
                        if len(line) < 4:
                            raise forms.ValidationError(
                                'Header row: {} is too short'.format(line))

                        feature = line[1].strip()

                        assay = features_to_assay.get(feature, '')
                        assays_found += 1

                        val_unit = line[3].strip()

                        # Raise error if feature does not exist
                        if feature not in features_to_assay:
                            raise forms.ValidationError(
                                'No feature with the name "%s" exists; please change your file or add this feature' % feature)
                        # Raise error when an assay does not exist
                        if assay not in assays:
                            raise forms.ValidationError(
                                'No assay with the name "%s" exists; please change your file or add this assay' % assay)
                        # Raise error if val_unit not equal to one listed in ACRA
                        if val_unit != assays.get(assay,''):
                            raise forms.ValidationError(
                                'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, assays.get(assay,'')))

                        # Fail if time given without time units
                        if len(line) < 8 and len(line) > 4 and any(line[4:]):
                            raise forms.ValidationError(
                                'Header row: {} improperly configured'.format(line))

                        if len(line) >= 8 and any(line[4:]):
                            time = line[5].strip()
                            time_unit = line[7].strip()

                            # Fail if time is not numeric
                            try:
                                float(time)
                            except:
                                raise forms.ValidationError(
                                    'The time "{}" is invalid. Please only enter numeric times'.format(time))

                            # Fail if time unit does not match
                            # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                            if time_unit[0] != readout_time_unit[0]:
                                raise forms.ValidationError('The time unit "{}" does not correspond with the selected readout time unit of "{}"'.format(time_unit, readout_time_unit))

                    # Otherwise the line contains datapoints for the current assay
                    else:
                        # TODO REVISE HOW DATA_BLOCKS ARE ACQUIRED
                        if data_blocks_found == 0 or (row_index-assays_found) % number_of_rows == 0:
                            data_blocks_found += 1

                        # This should handle blocks that have too many rows or do not have a header
                        if data_blocks_found > assays_found:
                            raise forms.ValidationError(
                                        'All plate data must have an assay associated with it. Please add a header line.')

                        # This is to deal with an excess of columns
                        if len(line) != number_of_columns:
                            raise forms.ValidationError(
                                "The number of columns does not correspond with the device's dimensions:{}".format(line))

                        # For every value in the line
                        for val in line:
                            # Check every value to make sure it can resolve to a float
                            try:
                                # Keep empty strings, though they technically can not be converted to floats
                                if val != '':
                                    float(val)
                            except:
                                raise forms.ValidationError(
                                        'The value "%s" is invalid; please make sure all values are numerical' % str(val))

            # If not block, then it is TABULAR data
            else:
                # Purge empty lines, they are useless for tabular uploads
                datalist = [row for row in datalist if any(row)]
                # The first line SHOULD be the header
                header = datalist[0]

                if header[1].lower().strip() == 'time':
                    # The features are the third column of the header onward
                    features = header[3:]
                    time_specified = True
                else:
                    # The features are the third column of the header onward
                    features = header[1:]
                    time_specified = False

                # Exclude the header to get only the data points
                data = datalist[1:]

                # Fail if there are no features
                if len(features) < 1:
                    raise forms.ValidationError(
                        'The file does not contain any features')

                for feature in features:
                    # Get associated assay
                    assay = features_to_assay.get(feature, '')
                    # Raise error if feature does not exist
                    if feature not in features_to_assay:
                        raise forms.ValidationError(
                            'No feature with the name "%s" exists; please change your file or add this feature' % feature)
                    # Raise error when an assay does not exist
                    if assay not in assays:
                        raise forms.ValidationError(
                            'No assay with the name "%s" exists; please change your file or add this assay' % assay)

                for row_index, row in enumerate(data):
                    # Check if well id is valid
                    try:
                        # The well identifier given
                        well = row[0]
                        # Split the well into alphabetical and numeric
                        row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well)
                        # Convert row_label to a number
                        row_label = label_to_number(row_label)
                        # Convert column label to an integer
                        column_label = int(column_label)

                        if row_label > number_of_rows:
                            raise forms.ValidationError(
                                "The number of rows does not correspond with the device's dimensions")

                        if column_label > number_of_columns:
                            raise forms.ValidationError(
                                "The number of columns does not correspond with the device's dimensions")

                    except:
                        raise forms.ValidationError(
                        'Error parsing the well ID: {}'.format(well))

                    if time_specified:
                        # Values are the slice of the fourth item onward
                        values = row[3:]
                        time = row[1]
                        time_unit = row[2]

                        # Check time unit
                        # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                        if time_unit[0] != readout_time_unit[0]:
                            raise forms.ValidationError(
                                'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (time_unit, readout_time_unit))

                        # Check time
                        try:
                            float(time)
                        except:
                            raise forms.ValidationError(
                                'Error while parsing time "{}"'.format(time))
                    else:
                        # Values are the slice of the first item onward
                        values = row[1:]
                        time = 0
                        time_unit = None

                    for column_index, value in enumerate(values):
                        #feature = features[column_index]

                        # Check if all the values can be parsed as floats
                        try:
                            if value != '':
                                float(value)
                        except:
                            raise forms.ValidationError(
                                    'The value {} is invalid; please make sure all values are numerical'.format(value))
        return self.cleaned_data

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

@transaction.atomic
def parseChipCSV(currentChipReadout, file, headers):
    removeExistingChip(currentChipReadout)

    datareader = csv.reader(file, delimiter=',')
    datalist = list(datareader)

    # Only take values from headers onward
    for rowID, rowValue in enumerate(datalist[headers:]):
        # rowValue holds all of the row elements
        # rowID is the index of the current row from top to bottom

        # Skip any row with insufficient commas
        if len(rowValue) < 6:
            continue

        # Skip any row with incomplete data
        if not all(rowValue):
            continue

        assay = AssayModel.objects.get(assay_name=rowValue[2])
        field = rowValue[3]
        val = rowValue[4]
        time = rowValue[0]

        # Originally permitted none values, will now ignore empty values
        # if not val:
        #     val = None

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

class AssayChipReadoutInlineFormset(CloneableBaseInlineFormSet):
    def clean(self):
        """Validate unique, existing Chip Readout IDs"""

        # Throw error if headers is not valid
        try:
            headers = int(self.data.get('headers','')) if self.data.get('headers') else 0
        except:
            raise forms.ValidationError('Please make number of headers a valid number.')

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        # Dic of assay names from inline with respective unit as value
        assays = {}
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name
                    unit = form.cleaned_data.get('readout_unit').unit
                    if assay_name not in assays:
                        assays.update({assay_name:unit})
                    else:
                        raise forms.ValidationError(
                            'Duplicate assays are not permitted; please blank out or change the duplicate')
            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

        # If there is already a file in the database and it is not being replaced or cleared (check for clear is implicit)
        if self.instance.file and not forms_data[-1].files:
            new_time_unit = self.instance.timeunit
            old_time_unit = AssayChipReadout.objects.get(id=self.instance.id).timeunit

            # Fail if time unit does not match
            if new_time_unit != old_time_unit:
                raise forms.ValidationError(
                    'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (new_time_unit, old_time_unit))

            saved_data = AssayChipRawData.objects.filter(assay_chip_id=self.instance).prefetch_related('assay_id')

            for raw in saved_data:

                assay = raw.assay_id.assay_id.assay_name
                val_unit = raw.assay_id.readout_unit.unit

                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'You can not remove the assay "%s" because it is in your uploaded data.' % assay)
                # Raise error if val_unit not equal to one listed in ACRA
                if val_unit != assays.get(assay,''):
                    raise forms.ValidationError(
                        'The current value unit "%s" does not correspond with the readout unit of "%s"' % (val_unit, assays.get(assay,'')))

        # If there is a new file
        if forms_data[-1].files:
            test_file = forms_data[-1].files.get('file','')

            datareader = csv.reader(test_file, delimiter=',')
            datalist = list(datareader)

            # Tedious way of getting timeunit; probably should refactor
            readout_time_unit = PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit

            # All unique rows based on ('assay_id', 'field_id', 'elapsed_time')
            unique = {}

            # Read headers going onward
            for line in datalist[headers:]:

                # Some lines may not be long enough (have sufficient commas), ignore such lines
                # Some lines may be empty or incomplete, ignore these as well
                if len(line) < 6 or not all(line):
                    continue

                time = line[0]
                time_unit = line[1].strip().lower()
                assay = line[2]
                field = line[3]
                val = line[4]
                val_unit = line[5].strip()
                # Raise error when an assay does not exist
                if assay not in assays:
                    raise forms.ValidationError(
                        'No assay with the name "%s" exists; please change your file or add this assay' % assay)
                # Raise error if val_unit not equal to one listed in ACRA
                if val_unit != assays.get(assay,''):
                    raise forms.ValidationError(
                        'The value unit "%s" does not correspond with the selected readout unit of "%s"' % (val_unit, assays.get(assay,'')))
                # Fail if time unit does not match
                # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                if time_unit[0] != readout_time_unit[0]:
                    raise forms.ValidationError(
                        'The time unit "%s" does not correspond with the selected readout time unit of "%s"' % (time_unit, readout_time_unit))
                if (time,assay,field) not in unique:
                    unique.update({(time,assay,field):True})
                else:
                    raise forms.ValidationError(
                        'File contains duplicate reading %s' % str((time,assay,field)))
                # Check every value to make sure it can resolve to a float
                try:
                    # Keep empty strings, though they technically can not be converted to floats
                    if val != '':
                        float(val)
                except:
                    raise forms.ValidationError(
                            'The value "%s" is invalid; please make sure all values are numerical' % str(val))
        return self.cleaned_data
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
        js = ('js/inline_fix.js','assays/customize_chip.js', 'js/d3.v3.min.js', 'js/c3.min.js',)
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

    # save_realted takes the place of save_model so that the inline can be saved first
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
            parseChipCSV(obj, request.FILES['file'], headers)

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
    form = AssayChipResultForm
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
    actions = ['update_fields']
    inlines = [AssayChipResultInline]

admin.site.register(AssayChipTestResult, AssayChipTestResultAdmin)


class AssayPlateResultInline(admin.TabularInline):
    # Results calculated from PLATE READOUTS
    model = AssayPlateResult
    #form = AssayPlateResultForm
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
    actions = ['update_fields']


admin.site.register(AssayPlateTestResult, AssayPlateTestResultAdmin)

# TODO CHANGE TO USE SETUP IN LIEU OF READOUT ID
# TODO CHANGE TO REMOVE PREVIOUS DATA
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
