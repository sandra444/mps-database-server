from django import forms
from .models import (
    AssayRun,
    AssayWell,
    AssayWellCompound,
    AssayWellTimepoint,
    AssayWellLabel,
    AssayModel,
    AssayReadout,
    AssayReader,
    AssayPlateSetup,
    AssayPlateReadout,
    AssayPlateReadoutAssay,
    AssayChipSetup,
    AssayChipRawData,
    AssayChipReadout,
    AssayChipReadoutAssay,
    PhysicalUnits,
    AssayDataUpload
)

from django.db import connection, transaction
import ujson as json
from urllib import unquote
from django.utils import timezone
import xlrd

from django.conf import settings
# Convert to valid file name
import string
import re
import os
import codecs
import cStringIO

import csv

from mps.settings import TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX

from chardet.universaldetector import UniversalDetector


def charset_detect(in_file, chunk_size=4096):
    """Use chardet library to detect what encoding is being used"""
    in_file.seek(0)
    chardet_detector = UniversalDetector()
    chardet_detector.reset()
    while 1:
        chunk = in_file.read(chunk_size)
        if not chunk:
            break
        chardet_detector.feed(chunk)
        if chardet_detector.done:
            break
    chardet_detector.close()
    in_file.seek(0)
    return chardet_detector.result


def unicode_csv_reader(in_file, dialect=csv.excel, **kwargs):
    """Returns the contents of a csv in unicode"""
    chardet_results = charset_detect(in_file)
    encoding = chardet_results.get('encoding')
    csv_reader = csv.reader(in_file, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell.decode(encoding)) for cell in row]


class UnicodeWriter:
    """Used to write UTF-8 CSV files"""
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        """Init the UnicodeWriter

        Params:
        f -- the file stream to write to
        dialect -- the "dialect" of csv to use (default excel)
        encoding -- the text encoding set to use (default utf-8)
        """
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        """This function takes a Unicode string and encodes it to the output"""
        self.writer.writerow([s.encode('utf-8') for s in row])
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        """This function writes out all rows given"""
        for row in rows:
            self.writerow(row)


def label_to_number(label):
    """Returns a numeric index from an alphabetical index"""
    num = 0
    for char in label:
        if char in string.ascii_letters:
            num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num


def process_readout_value(value):
    """Returns processed readout value and whether or not to mark it invalid"""

    # Try to parse as a float
    try:
        value = float(value)
        return {'value': value, 'quality': u''}

    except ValueError:
        # If not a float, take slice of all but first character and try again
        sliced_value = value[1:]

        try:
            sliced_value = float(sliced_value)
            return {'value': sliced_value, 'quality': 'X'}

        except ValueError:
            return None


def get_row_and_column(well_id, offset):
    """Takes a well ID in the form A1 and returns a row and column index as a tuple

    Params:
    well_id - the well ID as a string
    offset - offset to resulting row and column indexes (to start at zero, for instance)
    """
     # Split the well into alphabetical and numeric
    row_label, column_label = re.findall(r"[^\W\d_]+|\d+", well_id)

    # PLEASE NOTE THAT THE VALUES ARE OFFSET BY ONE (to begin with 0)
    # Convert row_label to a number
    row_label = label_to_number(row_label) - offset
    # Convert column label to an integer
    column_label = int(column_label) - offset

    return (row_label, column_label)


# Now uses unicode instead of string
def stringify_excel_value(value):
    """Given an excel value, return a unicode cast of it

    This also converts floats to integers when possible
    """
    # If the value is just a string literal, return it
    if type(value) == str or type(value) == unicode:
        return unicode(value)
    else:
        try:
            # If the value can be an integer, make it into one
            if int(value) == float(value):
                return unicode(int(value))
            else:
                return unicode(float(value))
        except:
            return unicode(value)


# SPAGHETTI CODE FIND A BETTER PLACE TO PUT THIS?
def valid_chip_row(row):
    """Confirm that a row is valid"""
    return row and all(row[:4] + [row[6]])


def get_bulk_datalist(sheet):
    """Get a list of lists where each list is a row and each entry is a value"""
    # Get datalist
    datalist = []

    # Include the first row (the header)
    for row_index in range(sheet.nrows):
        datalist.append([stringify_excel_value(value) for value in sheet.row_values(row_index)])

    return datalist


# TODO FIX ORDER OF ARGUMENTS
def get_sheet_type(header, sheet_name=''):
    """Get the sheet type from a given header (chip, tabular, block, or unknown)

    Param:
    header - the header in question
    sheet_name - the sheet name for reporting errors (default empty string)
    """
    # From the header we need to discern the type of upload
    # Check if chip
    if 'CHIP' in header[0].upper() and 'ASSAY' in header[3].upper():
        sheet_type = 'Chip'

    # Check if plate tabular
    elif 'PLATE' in header[0].upper() and 'WELL' in header[1].upper() and 'ASSAY' in header[2].upper()\
            and 'FEATURE' in header[3].upper() and 'UNIT' in header[4].upper():
        sheet_type = 'Tabular'

    # Check if plate block
    elif 'PLATE' in header[0].upper() and 'ASSAY' in header[2].upper() and 'FEATURE' in header[4].upper()\
            and 'UNIT' in header[6].upper():
        sheet_type = 'Block'

    # Throw error if can not be determined
    else:
        # For if we decide not to throw errors
        sheet_type = 'Unknown'
        raise forms.ValidationError(
            'The header of sheet "{0}" was not recognized.'.format(sheet_name)
        )

    return sheet_type


def get_valid_csv_location(file_name, study_id, device_type, overwrite_option):
    """Return a valid csv location

    Params:
    file_name - intial file name to modify
    study_id - study id
    device_type - plate or chip to know where to store data
    overwrite_option - what overwrite option was used
    """
    media_root = settings.MEDIA_ROOT.replace('mps/../', '', 1)

    current_date = timezone.now().strftime("%Y-%m-%d")

    valid_chars = '-_.{0}{1}'.format(string.ascii_letters, string.digits)
    # Get only valid chars
    valid_file_name = ''.join(c for c in file_name if c in valid_chars) + '_' + overwrite_option + '_' + current_date
    # Replace spaces with underscores
    valid_file_name = re.sub(r'\s+', '_', valid_file_name)

    # Check if name is already in use
    if os.path.isfile(os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '.csv')):
        append = 1
        while os.path.isfile(
            os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '_' + str(append) + '.csv')
        ):
            append += 1
        valid_file_name += '_' + str(append)

    return os.path.join(media_root, 'csv', study_id, device_type, valid_file_name + '.csv')


# Saving an Assay Layout is somewhat complicated, so a function is useful here
# (though perhaps not in this file [spaghetti code])
# BE CAREFUL! FIELDS THAT ARE NOT IN THE FORM ARE AUTOMATICALLY SET TO NONE!
def save_assay_layout(request, obj, form, change):
    """Method for saving an Assay Layout

    The data to make an assay layout is passed using a custom form.
    Please note that this function uses raw queries.
    """
    # Connect to the database
    cursor = connection.cursor()

    # Queries for entering data and lists of queries to be ran by the cursor
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

    # Aliases for comprehension
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

    # Wells are saved in the following portion
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

    # Execute the queries
    cursor.executemany(type_query, type_query_list)
    cursor.executemany(time_query, time_query_list)
    cursor.executemany(compound_query, compound_query_list)
    cursor.executemany(label_query, label_query_list)

    transaction.commit()


def get_plate_details(self=None, study=None, readout=None):
    """Get the assays and units as a dictionary with plate ID as the key

    Params:
    self - the form in question
    study - the study in question
    readout - the readout in question
    """
    if study:
        readouts = AssayPlateReadout.objects.filter(
            setup__assay_run_id=study
        ).prefetch_related(
            'setup__assay_run_id',
            'timeunit'
        )
    elif readout:
        readouts = AssayPlateReadout.objects.filter(
            pk=readout.id
        ).prefetch_related(
            'setup__assay_run_id',
            'timeunit'
        )
    else:
        readouts = None

    plate_details = {}

    # If this is for a bulk upload
    if readouts:
        for readout in readouts:
            setup_id = readout.setup.assay_plate_id

            plate_details.update({
                setup_id: {
                    'assays': {},
                    'features': {},
                    'assay_feature_to_unit': {},
                    'timeunit': readout.timeunit.unit,
                    'number_of_rows': readout.setup.assay_layout.device.number_of_rows,
                    'number_of_columns': readout.setup.assay_layout.device.number_of_columns,
                    'readout': readout
                }
            })

            current_assays = plate_details.get(setup_id, {}).get('assays', {})
            current_features = plate_details.get(setup_id, {}).get('features', {})
            current_assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

            assays = AssayPlateReadoutAssay.objects.filter(
                readout_id=readout
            ).prefetch_related(
                'readout_unit',
                'assay_id'
            )

            for assay in assays:
                readout_unit = assay.readout_unit.unit
                assay_name = assay.assay_id.assay_name.upper()
                assay_short_name = assay.assay_id.assay_short_name.upper()
                feature = assay.feature

                current_assays.update({
                    assay_name: True,
                    assay_short_name: True
                })

                current_features.update({feature: True})

                current_assay_feature_to_unit.update({
                    (assay_name, feature): readout_unit,
                    (assay_short_name, feature): readout_unit
                })
    # If this is for an individual upload
    else:
        if self.data.get('setup', ''):
            setup_pk = int(self.data.get('setup'))
        else:
            raise forms.ValidationError('Please choose a plate setup.')
        setup = AssayPlateSetup.objects.get(pk=setup_pk)
        setup_id = setup.assay_plate_id
        study_id = setup.assay_run_id_id

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        current_readout = AssayPlateReadout.objects.filter(setup__assay_run_id_id=study_id, setup__assay_plate_id=setup_id)

        if current_readout:
            current_readout = current_readout[0]
        else:
            current_readout = []

        plate_details.update({
            setup_id: {
                'assays': {},
                'features': {},
                'assay_feature_to_unit': {},
                'timeunit': PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit,
                'number_of_rows': setup.assay_layout.device.number_of_columns,
                'number_of_columns': setup.assay_layout.device.number_of_columns,
                'readout': current_readout
            }
        })

        features = plate_details.get(setup_id, {}).get('features', {})
        assays = plate_details.get(setup_id, {}).get('assays', {})
        assay_feature_to_unit = plate_details.get(setup_id, {}).get('assay_feature_to_unit', {})

        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    feature = form.cleaned_data.get('feature')
                    readout_unit = form.cleaned_data.get('readout_unit').unit

                    # Add feature
                    features.update({feature: True})
                    # Normal assay name
                    assays.update({
                        assay_name: True,
                        assay_short_name: True
                    })
                    if (assay_name, feature) not in assay_feature_to_unit:
                        assay_feature_to_unit.update({
                            (assay_name, feature): readout_unit,
                            (assay_short_name, feature): readout_unit
                        })
                    else:
                        raise forms.ValidationError('Assay-Feature pairs must be unique.')

            # Do nothing if invalid
            except AttributeError:
                pass
        if len(assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

    return plate_details


# TODO FINISH
def get_qc_status_plate(form):
    """Get QC status for each line"""
    qc_status = {}

    for key, val in form.data.iteritems():
        # If this is a QC input
        if key.startswith('{') and key.endswith('}'):
            # Evaluate the key
            key = unquote(key)
            values = json.loads(key)
            row = unicode(values.get('row'))
            col = unicode(values.get('column'))
            # Be sure to convert time to a float
            time = float(values.get('time'))
            # Assay needs to be case insensitive
            assay = values.get('assay').upper()
            feature = values.get('feature')
            replicate = int(values.get('replicate'))
            # Combine values in a tuple for index
            index = (row, col, time, assay, feature, replicate)
            # Set to val
            qc_status.update({index: val[:19]})

    return qc_status


def modify_qc_status_plate(current_plate_readout, form):
    """Update the QC status of a plate"""
    # Get the readouts
    readouts = AssayReadout.objects.filter(
        assay_device_readout=current_plate_readout
    ).prefetch_related(
        'assay__assay_id',
        'assay_device_readout__setup__assay_run_id'
    ).values_list(
        'id',
        'row',
        'column',
        'elapsed_time',
        'assay__assay_id__assay_name',
        'assay__assay_id__assay_short_name',
        'assay__feature',
        'replicate',
        'quality',
        'notes'
    )

    # Get QC status for each line
    qc_status = get_qc_status_plate(form)
    readout_ids_and_notes = []

    for readout_values in readouts:
        index_long = (
            readout_values[1],
            readout_values[2],
            readout_values[3],
            readout_values[4],
            readout_values[6],
            readout_values[7]
        )
        index_short = (
            readout_values[1],
            readout_values[2],
            readout_values[3],
            readout_values[5],
            readout_values[6],
            readout_values[7]
        )

        id = readout_values[0]
        quality = readout_values[8]
        notes = readout_values[9]

        long_name_check = qc_status.get(index_long, None)
        short_name_check = qc_status.get(index_short, None)

        # long_name_removed = not long_name_check and not long_name_check is None
        long_name_empty = long_name_check == u''
        short_name_empty = short_name_check == u''

        if long_name_check:
            new_quality = long_name_check
        elif short_name_check:
            new_quality = short_name_check
        else:
            new_quality = u''

        # If the quality marker is present
        if long_name_check or short_name_check:
            readout_ids_and_notes.append((id, notes, new_quality))
        # If the quality marker has been removed
        elif (long_name_empty or short_name_empty) and quality:
            readout_ids_and_notes.append((id, notes, new_quality))

    mark_plate_readout_values(readout_ids_and_notes)


def validate_plate_readout_file(
        datalist,
        plate_details,
        sheet='',
        overwrite_option=None,
        readout=None,
        form=None,
        save=False
):
    """Validates a Plate Readout CSV file"""
    # Any errors that may have occured
    errors = []
    query_list = []
    readout_data = []

    # Current data to check for replicates
    current_data = {}

    readouts = []
    # Get readouts
    if readout:
        readouts = [readout]
    else:
        for setup_id, values in plate_details.items():
            current_readout = values.get('readout', '')
            if current_readout:
                readouts.append(current_readout)
    if not readout and len(readouts) == 1:
        readout = readouts[0]

    old_readout_data = AssayReadout.objects.filter(
        assay_device_readout__in=readouts
    ).prefetch_related(
        'assay__assay_id',
        'assay_device_readout'
    )

    conflicting_entries = []
    possible_conflicting_data = {}
    for old_readout in old_readout_data:
        possible_conflicting_data.setdefault(
            (old_readout.assay.assay_id_id, old_readout.assay.feature, old_readout.row, old_readout.column, old_readout.elapsed_time), []
        ).append(old_readout)

    # Get assay models
    assay_models = {}
    for assay in AssayModel.objects.all():
        assay_models.update({
            assay.assay_name.upper(): assay,
            assay.assay_short_name.upper(): assay
        })

    assay_feature_to_apra_id = {
        (apra.assay_id_id, apra.feature): apra.id for apra in AssayPlateReadoutAssay.objects.all().prefetch_related(
            'assay_id'
        )
    }

    # Get upload_type
    upload_type = get_sheet_type(datalist[0])

    if upload_type == 'Block':
        # Number of assays found
        assays_found = 0
        # Number of data blocks found
        data_blocks_found = 0

        number_of_rows = u''
        number_of_columns = u''

        time = float(0)
        time_unit = u''
        value_unit = u''
        feature = u''

        for row_index, line in enumerate(datalist):
            # If line is blank, skip it
            if not line:
                continue

            # If this line is a header
            # NOTE THAT ASSAYS AND FEATURES ARE IN PAIRS
            # Headers should look like:
            # PLATE ID, {{}}, ASSAY, {{}}, FEATURE, {{}}, READOUT UNIT, {{}}, TIME, {{}}. TIME UNIT, {{}}
            if 'PLATE' in line[0].upper().strip():
                # Throw error if header too short
                if len(line) < 8:
                    errors.append(
                        sheet + 'Header row: {} is too short'.format(line))

                plate_id = line[1]

                if plate_id not in plate_details:
                    errors.append(
                        sheet + 'The Plate ID "{0}" was not recognized.'
                                ' Make sure a readout for this plate exists.'.format(plate_id)
                    )

                # Set to correct set of assays, features, and pairs
                assays = plate_details.get(plate_id, {}).get('assays', {})
                features = plate_details.get(plate_id, {}).get('features', {})
                assay_feature_to_unit = plate_details.get(plate_id, {}).get('assay_feature_to_unit', {})

                readout_time_unit = plate_details.get(plate_id, {}).get('timeunit', 'X')
                number_of_rows = plate_details.get(plate_id, {}).get('number_of_rows', 0)
                number_of_columns = plate_details.get(plate_id, {}).get('number_of_columns', 0)

                assay_name = line[3].upper().strip()
                feature = line[5]

                assays_found += 1

                value_unit = line[7].strip()

                # TODO OLD
                # TODO REVISE
                # Raise error if feature does not exist
                if feature not in features:
                    errors.append(
                        sheet + 'Plate-%s: No feature with the name "%s" exists; '
                                'please change your file or add this feature'
                        % (plate_id, feature)
                    )
                # Raise error when an assay does not exist
                if assay_name not in assays:
                    errors.append(
                        sheet + 'Plate-%s: '
                                'No assay with the name "%s" exists; please change your file or add this assay'
                        % (plate_id, assay_name)
                    )
                # Raise error if assay-feature pair is not listed
                elif (assay_name, feature) not in assay_feature_to_unit:
                    errors.append(
                        sheet + 'Plate-{0}: The assay-feature pair "{1}-{2}" was not recognized'.format(
                            plate_id,
                            assay_name,
                            feature
                        )
                    )
                # Raise error if value_unit not equal to one listed in APRA
                elif value_unit != assay_feature_to_unit.get((assay_name, feature), ''):
                    errors.append(
                        sheet + 'Plate-%s: '
                                'The value unit "%s" does not correspond with the selected readout unit of "%s"'
                        % (plate_id, value_unit, assay_feature_to_unit.get((assay_name, feature), ''))
                    )

                # Fail if time given without time units
                if len(line) < 12 and len(line) > 8 and any(line[8:]):
                    errors.append(
                        sheet + 'Header row: {} improperly configured'.format(line))

                if len(line) >= 12 and any(line[8:]):
                    time = line[9].strip()
                    time_unit = line[11].strip()

                    # Fail if time is not numeric
                    try:
                        if time != '':
                            time = float(time)
                        # Time is zero if not specified
                        else:
                            time = float(0)
                    except:
                        errors.append(
                            sheet + 'The time "{}" is invalid. Please only enter numeric times'.format(time))

                    # Fail if time unit does not match
                    # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                    if time_unit and (time_unit[0] != readout_time_unit[0]):
                        errors.append(
                            sheet +
                            'Plate-{0}: The time unit "{1}" does not correspond with '
                            'the selected readout time unit of "{2}"'.format(plate_id, time_unit, readout_time_unit)
                        )

            # Otherwise the line contains datapoints for the current assay
            else:
                # TODO REVISE HOW DATA_BLOCKS ARE ACQUIRED
                if data_blocks_found == 0 or (row_index - assays_found) % number_of_rows == 0:
                    data_blocks_found += 1

                # This should handle blocks that have too many rows or do not have a header
                # Don't throw an error if there are not any meaningful values
                if data_blocks_found > assays_found and any(line[:number_of_columns]):
                    errors.append(
                        sheet + 'All plate data must have an assay associated with it. Please add a header line '
                                'and/or make sure there are no blank lines between blocks')

                # TODO NOTE: THIS IS DEPENDENT ON THE LOCATION OF THE TEMPLATE'S VALIDATION CELLS
                # TODO AS A RESULT,
                trimmed_line = [value for value in line[:TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX] if value]

                # This is to deal with an EXCESS of columns
                if len(trimmed_line) > number_of_columns:
                    errors.append(
                        sheet + "Plate-{0}: The number of columns does not correspond "
                                "with the device's dimensions:{1}".format(plate_id, line)
                    )

                # For every value in the line (breaking at number of columns)
                for column_id, value in enumerate(line[:number_of_columns]):
                    # Check every value to make sure it can resolve to a float
                    # Keep empty strings, though they technically can not be converted to floats
                    if value != '':
                        processed_value = process_readout_value(value)

                        if processed_value is None:
                            errors.append(
                                sheet + 'The value "%s" is invalid; please make sure all values are numerical'
                                % str(value)
                            )
                        else:
                            value = processed_value.get('value')
                            quality = processed_value.get('quality')

                        # MUST OFFSET ROW (due to multiple datablocks)
                        offset_row_id = (row_index - assays_found) % number_of_rows

                        # Right now notes are not available in block
                        notes = ''

                        if not errors:
                            current_plate_readout = plate_details.get(plate_id, {}).get('readout', '')

                            # Convert row and column to strings
                            offset_row_id = unicode(offset_row_id)
                            column_id = unicode(column_id)

                            # The current assay
                            assay_model_id = assay_models.get(assay_name).id

                            # Deal with conflicting data
                            current_conflicting_entries = possible_conflicting_data.get(
                                (assay_model_id, feature, offset_row_id, column_id, time), []
                            )
                            conflicting_entries.extend(current_conflicting_entries)

                            # Get possible duplicate current entries
                            duplicate_current = current_data.get(
                                (assay_model_id, feature, offset_row_id, column_id, time), []
                            )

                            number_duplicate_current = len(duplicate_current)
                            number_conflicting_entries = len(current_conflicting_entries)

                            if overwrite_option in ['delete_conflicting_data', 'delete_all_old_data']:
                                number_conflicting_entries = 0

                            # Discern what replicate this is (default 1)
                            replicate = 0 + number_conflicting_entries + number_duplicate_current

                            if save:
                                apra_id = assay_feature_to_apra_id.get((assay_model_id, feature))

                                query_list.append((
                                    current_plate_readout.id,
                                    apra_id,
                                    offset_row_id,
                                    column_id,
                                    value,
                                    time,
                                    quality,
                                    notes,
                                    replicate
                                ))

                            else:
                                if replicate:
                                    notes = notes + '\nReplicate #' + unicode(replicate)

                                readout_data.append({
                                    # Tentative may become useful soon
                                    'plate': plate_id,
                                    'row': offset_row_id,
                                    'column': column_id,
                                    'value': value,
                                    # Can be just string
                                    'assay': assay_name,
                                    'time': time,
                                    # TODO SOMEWHAT FRIVOLOUS CONSIDER REVISING
                                    # can be just string
                                    'time_unit': time_unit,
                                    'value_unit': value_unit,
                                    'feature': feature,
                                    'quality': quality,
                                    'notes': notes,
                                    'replicate': replicate
                                })

                            # Add to current_data
                            current_data.setdefault(
                                (assay_model_id, feature, offset_row_id, column_id, time), []
                            ).append(1)

    # If not block, then it is TABULAR data
    else:
        # Purge empty lines, they are useless for tabular uploads
        # All lines that do not have anything in their first 8 cells are purged
        datalist = [row for row in datalist if any(row[:8])]
        # The first line SHOULD be the header
        header = datalist[0]

        # TODO REVISE
        if len(header) < 6:
            errors.append(
                sheet + 'Please specify Plate ID, Well, Assay, Feature, Feature Unit, [Time, Time Unit], '
                        'and Value in header.')
        if 'TIME' in header[5].upper() and (len(header) < 8 or 'UNIT' not in header[6].upper()):
            errors.append(
                sheet + 'If you are specifying time, you must also specify the time unit')

        if 'TIME' in header[5].upper() and 'UNIT' in header[6].upper():
            time_specified = True
        else:
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # Plate ID given
            plate_id = row[0]

            if plate_id not in plate_details:
                errors.append(
                    sheet + 'The Plate ID "{0}" was not recognized.'
                            ' Make sure a readout for this plate exists.'.format(plate_id)
                )

            # Set to correct set of assays, features, and pairs
            assays = plate_details.get(plate_id, {}).get('assays', {})
            features = plate_details.get(plate_id, {}).get('features', {})
            assay_feature_to_unit = plate_details.get(plate_id, {}).get('assay_feature_to_unit', {})

            readout_time_unit = plate_details.get(plate_id, {}).get('timeunit', 'X')
            number_of_rows = plate_details.get(plate_id, {}).get('number_of_rows', 0)
            number_of_columns = plate_details.get(plate_id, {}).get('number_of_columns', 0)

            # The well identifier given
            well = row[1]
            assay_name = row[2].upper().strip()
            feature = row[3]
            value_unit = row[4]

            # Raise error if feature does not exist
            if feature not in features:
                errors.append(
                    sheet + 'Plate-%s: '
                            'No feature with the name "%s" exists; please change your file or add this feature'
                    % (plate_id, feature)
                )
            # Raise error when an assay does not exist
            elif assay_name not in assays:
                errors.append(
                    sheet + 'Plate-%s: No assay with the name "%s" exists; please change your file or add this assay'
                    % (plate_id, assay_name)
                )
            # Raise error if assay-feature pair is not listed
            elif (assay_name, feature) not in assay_feature_to_unit:
                errors.append(
                    sheet + 'Plate-{0}: The assay-feature pair "{1}-{2}" was not recognized'.format(
                        plate_id, assay_name, feature
                    )
                )
            # Raise error if value_unit not equal to one listed in APRA
            elif value_unit != assay_feature_to_unit.get((assay_name, feature), ''):
                errors.append(
                    sheet + 'Plate-%s: The value unit "%s" does not correspond with the selected readout unit of "%s"'
                    % (plate_id, value_unit, assay_feature_to_unit.get((assay_name, feature), ''))
                )

            time = float(0)
            time_unit = u''
            notes = u''
            # If time is specified
            if time_specified:
                time = row[5]
                time_unit = row[6].strip().lower()
                value = row[7]
                if len(row) > 8:
                    notes = row[8][:255]

                # Check time unit
                # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
                if not time_unit or (time_unit[0] != readout_time_unit[0]):
                    errors.append(
                        sheet + 'Plate-%s: The time unit "%s" does not correspond with the selected readout time unit '
                                'of "%s"'
                        % (plate_id, time_unit, readout_time_unit)
                    )

                # Check time
                try:
                    if time != '':
                        time = float(time)
                    # Time is zero if not specified
                    else:
                        time = float(0)
                except:
                    errors.append(
                        sheet + 'Error while parsing time "{}"'.format(time))

            # If time is not specified
            else:
                value = row[5]
                if len(row) > 6:
                    notes = row[6][:255]

            row_label = u''
            column_label = u''
            # Check if well id is valid
            try:
                # Split the well into alphabetical and numeric
                row_label, column_label = get_row_and_column(well, 1)

                if row_label > number_of_rows:
                    errors.append(
                        sheet + "Plate-{0}: The number of rows does not correspond with the device's dimensions".format(
                            plate_id
                        )
                    )

                if column_label > number_of_columns:
                    errors.append(
                        sheet + "Plate-{0}: The number of columns does not correspond "
                        "with the device's dimensions".format(
                            plate_id
                        )
                    )

            except:
                errors.append(
                    sheet + 'Plate-{0}: Error parsing the well ID: {1}'.format(plate_id, well)
                )

            # Check every value to make sure it can resolve to a float
            # Keep empty strings, though they technically can not be converted to floats
            quality = u''
            if value != '':
                processed_value = process_readout_value(value)
                if processed_value is None:
                    errors.append(
                        sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(value))
                else:
                    value = processed_value.get('value')
                    quality = processed_value.get('quality')

                if not errors:
                    current_plate_readout = plate_details.get(plate_id, {}).get('readout', '')

                    # Convert row and column to strings
                    row_label = unicode(row_label)
                    column_label = unicode(column_label)

                    # Get assay model
                    assay_model_id = assay_models.get(assay_name).id

                    # Deal with conflicting data
                    current_conflicting_entries = possible_conflicting_data.get(
                        (assay_model_id, feature, row_label, column_label, time), []
                    )
                    conflicting_entries.extend(current_conflicting_entries)

                    # Get possible duplicate current entries
                    duplicate_current = current_data.get(
                        (assay_model_id, feature, row_label, column_label, time), []
                    )

                    number_duplicate_current = len(duplicate_current)
                    number_conflicting_entries = len(current_conflicting_entries)

                    if overwrite_option in ['delete_conflicting_data', 'delete_all_old_data']:
                        number_conflicting_entries = 0

                    # Discern what replicate this is (default 1)
                    replicate = 0 + number_conflicting_entries + number_duplicate_current

                    if save:
                        apra_id = assay_feature_to_apra_id.get((assay_model_id, feature))

                        query_list.append((
                            current_plate_readout.id,
                            apra_id,
                            row_label,
                            column_label,
                            value,
                            time,
                            quality,
                            notes,
                            replicate
                        ))

                    else:
                        if replicate:
                            notes = notes + '\nReplicate #' + unicode(replicate)

                        readout_data.append({
                            # Tentative may become useful soon
                            'plate': plate_id,
                            'row': row_label,
                            'column': column_label,
                            'value': value,
                            # Can be just string
                            'assay': assay_name,
                            'time': time,
                            # TODO SOMEWHAT FRIVOLOUS CONSIDER REVISING
                            # can be just string
                            'time_unit': time_unit,
                            'value_unit': value_unit,
                            'feature': feature,
                            'quality': quality,
                            'notes': notes,
                            'replicate': replicate
                        })

                    # Add to current_data
                    current_data.setdefault(
                        (assay_model_id, feature, row_label, column_label, time), []
                    ).append(1)

    if errors:
        raise forms.ValidationError(errors)
    elif save:
        if overwrite_option == 'delete_conflicting_data':
            for entry in conflicting_entries:
                entry.delete()
        elif overwrite_option == 'mark_conflicting_data':
            readout_ids_and_notes = []
            for entry in conflicting_entries:
                readout_ids_and_notes.append((entry.id, entry.notes, entry.quality))
            mark_plate_readout_values(readout_ids_and_notes, stamp=True)

        # Connect to the database
        cursor = connection.cursor()
        # The generic query
        query = ''' INSERT INTO "assays_assayreadout"
              ("assay_device_readout_id", "assay_id", "row", "column", "value", "elapsed_time", "quality", "notes", "replicate")
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

        cursor.executemany(query, query_list)
        transaction.commit()

        if form:
            modify_qc_status_plate(readout, form)

        return True
    else:
        return readout_data


def get_chip_details(self=None, study=None, readout=None):
    """Get the assays and units as a dictionary with chip ID as the key

    Params:
    self - the form in question
    study - the study in question
    readout - the readout in question
    """
    if study:
        readouts = AssayChipReadout.objects.filter(
            chip_setup__assay_run_id=study
        ).prefetch_related(
            'chip_setup__assay_run_id',
            'timeunit'
        )
    elif readout:
        readouts = AssayChipReadout.objects.filter(pk=readout.id).prefetch_related(
            'chip_setup__assay_run_id',
            'timeunit'
        )
    else:
        readouts = None

    chip_details = {}

    # If this is for a bulk upload
    if readouts:
        for readout in readouts:
            setup_id = readout.chip_setup.assay_chip_id

            chip_details.update({setup_id: {
                'assays': {},
                'timeunit': None,
                'readout': readout
            }})
            current_assays = chip_details.get(setup_id, {}).get('assays', {})

            timeunit = readout.timeunit.unit
            chip_details.get(setup_id, {}).update({'timeunit': timeunit})

            assays = AssayChipReadoutAssay.objects.filter(
                readout_id=readout
            ).prefetch_related(
                'readout_id',
                'readout_unit',
                'assay_id'
            )

            for assay in assays:
                readout_unit = assay.readout_unit.unit
                assay_name = assay.assay_id.assay_name.upper()
                assay_short_name = assay.assay_id.assay_short_name.upper()

#                 current_assays.update({
#                     assay_name: readout_unit,
#                     assay_short_name: readout_unit
#                 })
                current_assays.setdefault(assay_name, []).append(readout_unit)
                current_assays.setdefault(assay_short_name, []).append(readout_unit)

    # If this is for an individual upload
    else:
        if self.data.get('chip_setup', ''):
            setup_pk = int(self.data.get('chip_setup'))
        else:
            raise forms.ValidationError('Please choose a chip setup.')
        setup = AssayChipSetup.objects.get(pk=setup_pk)
        setup_id = setup.assay_chip_id
        study_id = setup.assay_run_id_id

        forms_data = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]

        current_readout = AssayChipReadout.objects.filter(chip_setup__assay_run_id_id=study_id, chip_setup__assay_chip_id=setup_id)

        if current_readout:
            current_readout = current_readout[0]
        else:
            current_readout = []

        # Dic of assay names from inline with respective unit as value
        chip_details.update({setup_id: {
            'assays': {},
            # Tedious way of getting timeunit; probably should refactor
            'timeunit': PhysicalUnits.objects.get(id=self.data.get('timeunit')).unit,
            'readout': current_readout
        }})

        current_assays = chip_details.get(setup_id, {}).get('assays', {})
        for form in forms_data:
            try:
                if form.cleaned_data:
                    assay_name = form.cleaned_data.get('assay_id').assay_name.upper()
                    assay_short_name = form.cleaned_data.get('assay_id').assay_short_name.upper()
                    unit = form.cleaned_data.get('readout_unit').unit
                    is_duplicate = current_assays.get(assay_name, '') == unit
                    if not is_duplicate:
#                         current_assays.update({
#                             assay_name: unit,
#                             assay_short_name: unit
#                         })
                        current_assays.setdefault(assay_name, []).append(unit)
                        current_assays.setdefault(assay_short_name, []).append(unit)
                    else:
                        raise forms.ValidationError(
                            'Duplicate assays are not permitted; please blank out or change the duplicate'
                        )
            except AttributeError:
                pass
        if len(current_assays) < 1:
            raise forms.ValidationError('You must have at least one assay')

    return chip_details


# def get_qc_status_chip(form):
#     """Get QC status for each line"""
#     qc_status = {}
#
#     if not form:
#         return qc_status
#
#     for key, val in form.data.iteritems():
#         # If this is a QC input
#         if key.startswith('QC_'):
#             # Get index from key
#             index = int(key.split('_')[-1])
#             # Truncate value to be less than 20 characters to avoid errors
#             quality = val[:19]
#             qc_status.update({index: quality})
#
#     return qc_status
#
#
# # NOTE: Tricky thing about chip QC is IT DEPENDS ON WHETHER IT IS BEING ADDED OR UPDATED
# # Why? The ORDER OF THE VALUES REFLECTS THE FILE WHEN ADDING, BUT IS SORTED IN UPDATE
# @transaction.atomic
# def modify_qc_status_chip(current_chip_readout, form):
#     """Update the QC for a chip"""
#     # Get the readouts as they would appear on the front end
#     # PLEASE NOTE THAT ORDER IS IMPORTANT HERE TO MATCH UP WITH THE INPUTS
#     readouts = AssayChipRawData.objects.prefetch_related(
#         'assay_chip_id__chip_setup',
#         'assay_id__assay_id'
#     ).filter(
#         assay_chip_id=current_chip_readout
#     ).order_by(
#         'assay_chip_id__chip_setup__assay_chip_id',
#         'assay_id__assay_id__assay_short_name',
#         'elapsed_time',
#         'quality'
#     )
#
#     # Get QC status for each line
#     qc_status = get_qc_status_chip(form)
#
#     for index, readout in enumerate(readouts):
#         readout.quality = qc_status.get(index)
#         readout.save()


def get_qc_status_chip(form):
    """Get QC status for each line"""
    qc_status = {}

    for key, val in form.data.iteritems():
        # If this is a QC input
        if key.startswith('{') and key.endswith('}'):
            # Evaluate the key
            key = unquote(key)
            values = json.loads(key)
            object_field = unicode(values.get('field'))
            # Be sure to convert time to a float
            time = float(values.get('time'))
            # Assay needs to be case insensitive
            assay = values.get('assay').upper()
            replicate = int(values.get('replicate'))
            # Combine values in a tuple for index
            index = (object_field, time, assay, replicate)
            # Set to stripped val
            qc_status.update({index: val.strip()[:19]})

    return qc_status


# TODO TODO TODO
def modify_qc_status_chip(current_chip_readout, form):
    """Update the QC status of a plate"""
    # Get the readouts
    readouts = AssayChipRawData.objects.filter(
        assay_chip_id=current_chip_readout
    ).prefetch_related(
        'assay_id__assay_id',
        'assay_chip_id__chip__setup__assay_run_id'
    ).values_list(
        'id',
        'field_id',
        'elapsed_time',
        'assay_id__assay_id__assay_name',
        'assay_id__assay_id__assay_short_name',
        'replicate',
        'quality',
        'notes'
    )

    # Get QC status for each line
    qc_status = get_qc_status_chip(form)
    readout_ids_and_notes = []

    for readout_values in readouts:
        index_long = (
            readout_values[1],
            readout_values[2],
            readout_values[3],
            readout_values[5]
        )
        index_short = (
            readout_values[1],
            readout_values[2],
            readout_values[4],
            readout_values[5]
        )

        id = readout_values[0]
        quality = readout_values[6]
        notes = readout_values[7]

        long_name_check = qc_status.get(index_long, None)
        short_name_check = qc_status.get(index_short, None)

        # long_name_removed = not long_name_check and not long_name_check is None
        long_name_empty = long_name_check == u''
        short_name_empty = short_name_check == u''

        if long_name_check:
            new_quality = long_name_check
        elif short_name_check:
            new_quality = short_name_check
        else:
            new_quality = u''

        # If the quality marker is present
        if long_name_check or short_name_check:
            readout_ids_and_notes.append((id, notes, new_quality))
        # If the quality marker has been removed
        elif (long_name_empty or short_name_empty) and quality:
            readout_ids_and_notes.append((id, notes, new_quality))

    mark_chip_readout_values(readout_ids_and_notes)


# TODO BE SURE TO CHECK CHECK FOR DUPLICATES
# TODO BE SURE TO FIX DELETION OF DUPLICATES
# TODO GET CURRENT CHIP READOUT DEPENDING ON SETUP FIELD FOR BULK UPLOADS
# TODO RATHER THAN DELETING/MARKING FIRST, WAIT UNTIL END TO DELETE AND MARK (SET CONFLICTING NUMBER TO ZERO IF NECESSARY
def validate_chip_readout_file(
    headers,
    datalist,
    chip_details,
    sheet='',
    overwrite_option=None,
    readout=None,
    study=None,
    form=None,
    save=False
):
    """Validates CSV Uploads for Chip Readouts"""
    # A query list to execute to save chip data
    query_list = []
    # A list of readout data for preview
    readout_data = []
    # A list of errors
    errors = []

    # Get assay models
    assay_models = {}
    for assay in AssayModel.objects.all():
        assay_models.update({
            assay.assay_name.upper(): assay,
            assay.assay_short_name.upper(): assay
        })

    physical_units = {
        unit.unit: unit for unit in PhysicalUnits.objects.filter(availability__icontains='readout')
    }

    dummy_reader = AssayReader.objects.all()[0]

    readouts = []
    # Get readouts
    if readout:
        readouts = [readout]
    else:
        for setup_id, values in chip_details.items():
            current_readout = values.get('readout', '')
            if current_readout:
                readouts.append(current_readout)
    if not readout and len(readouts) == 1:
        readout = readouts[0]

    if not study and readout:
        study = readout.chip_setup.assay_run_id

    if not study and form:
        study = AssayChipSetup.objects.get(form.data.get('chip_setup')).assay_run_id

    # Get assay chip readout assays (for existing readouts)
    assay_ids = {
        (acra.assay_id_id, acra.readout_unit.unit): acra for acra in AssayChipReadoutAssay.objects.filter(
            readout_id__in=readouts
        ).prefetch_related(
            'readout_unit',
            'assay_id'
        )
    }

    old_readout_data = AssayChipRawData.objects.filter(
        assay_chip_id__in=readouts
    ).prefetch_related(
        'assay_id__assay_id',
        'assay_chip_id',
        'assay_id__readout_unit'
    )

    # chip_id_to_readout = {}
    #
    # for current_readout in study_readouts:
    #     chip_id_to_readout.update({
    #         current_readout.chip_setup.assay_chip_id: current_readout
    #     })
    #
    # if not study_readouts and readout:
    #     chip_id_to_readout.update({
    #         readout.chip_setup.assay_chip_id: readout
    #     })

    current_data = {}

    possible_conflicting_data = {}
    conflicting_entries = []
    # Fill check for conflicting
    # TODO IS THIS OPTIMAL WAY TO CHECK CONFLICTING?
    for entry in old_readout_data:
        possible_conflicting_data.setdefault(
            (
                entry.assay_chip_id.chip_setup.assay_chip_id,
                entry.assay_id.assay_id_id,
                entry.assay_id.readout_unit.unit,
                entry.field_id, entry.elapsed_time
            ), []
        ).append(entry)

    # Confirm that there is only one chip_id given if this is not a bulk upload
    if not sheet:
        for line in datalist[headers:]:
            if valid_chip_row(line) and chip_details and line and line[0] not in chip_details:
                errors.append(
                    'Chip ID "{0}" does not match current Chip ID. '
                    'You cannot upload data for multiple chips in this interface. '
                    'If you want to upload multiple set of data, '
                    'use the "Upload Excel File of Readout Data" interface instead. '
                    .format(line[0])
                )

    # OLD
    # Get QC status for each line
    # qc_status = get_qc_status_chip(form)
    # Current index for finding correct QC status
    # current_index = 0

    # Read headers going onward
    for line in datalist[headers:]:
        # Some lines may not be long enough (have sufficient commas), ignore such lines
        # Some lines may be empty or incomplete, ignore these as well
        if not valid_chip_row(line):
            continue

        chip_id = line[0]

        time = line[1]
        time_unit = line[2].strip().lower()
        assay_name = line[3].upper()
        field = line[4]
        value = line[5]
        value_unit = line[6].strip()

        # Throw error if no Object
        if not field:
            errors.append(
                sheet + 'Please make sure all rows have an Object. Additionally, check to see if all related data have the SAME Object.'
            )

        # Get notes, if possible
        notes = ''
        if len(line) > 8:
            notes = line[8][:255]

        # PLEASE NOTE Database inputs, not the csv, have the final say
        # Get quality if possible
        quality = u''
        if len(line) > 7:
            quality = line[7]

        # OLD
        # # Get quality from added form inputs if possible
        # if current_index in qc_status:
        #     quality = qc_status.get(current_index)
        # # Increment current index acquisition
        # current_index += 1

        if chip_id not in chip_details:
            errors.append(
                sheet + 'No Chip with the ID "{0}" exists; please change your file or add this assay.'.format(chip_id)
            )

        assays = chip_details.get(chip_id, {}).get('assays', {})
        readout_time_unit = chip_details.get(chip_id, {}).get('timeunit', 'X')

        # Raise error when an assay does not exist
        if assay_name not in assays:
            errors.append(
                sheet + 'Chip-%s: No assay with the name "%s" exists; please change your file or add this assay'
                % (chip_id, assay_name)
            )
        # Raise error if value_unit not in any matching ACRA
        elif value_unit not in assays.get(assay_name, []):
            errors.append(
                sheet + 'Chip-%s: The value unit "%s" does not correspond with the selected readout unit of "%s"'
                % (chip_id, value_unit, assays.get(assay_name, ''))
            )

        # Fail if time unit does not match
        # TODO make a better fuzzy match, right now just checks to see if the first letters correspond
        if not time_unit or (time_unit[0] != readout_time_unit[0]):
            errors.append(
                sheet + 'Chip-%s: The time unit "%s" does not correspond with the selected readout time unit of "%s"'
                % (chip_id, time_unit, readout_time_unit)
            )
        # if (chip_id, time, assay_name, current_object) not in unique:
        #     unique.update({(chip_id, time, assay_name, current_object): True})
        # else:
        #     raise forms.ValidationError(
        #         sheet + 'File contains duplicate reading %s' % str((chip_id, time, assay_name, current_object))
        #     )
        # Check every value to make sure it can resolve to a float
        try:
            # Keep empty strings, though they technically can not be converted to floats
            if value != '':
                value = float(value)
        except:
            errors.append(
                sheet + 'The value "%s" is invalid; please make sure all values are numerical' % str(value)
            )

        # Check to make certain the time is a valid float
        try:
            time = float(time)

        except:
            errors.append(
                sheet + 'The time "%s" is invalid; please make sure all times are numerical' % str(time)
            )

        # Treat empty strings as None
        if value == '':
            value = None
            # Set quality to 'NULL' if quality was not set by user
            if not quality:
                quality = 'NULL'

        if not errors:
            # Try to get readout
            current_chip_readout = chip_details.get(chip_id, {}).get('readout', '')

            # Get a dummy readout
            if not current_chip_readout:
                chip_setup = AssayChipSetup.objects.filter(
                    assay_chip_id=chip_id,
                    assay_run_id=study
                )
                current_chip_readout = AssayChipReadout(
                    chip_setup=chip_setup[0],
                    timeunit=PhysicalUnits.objects.filter(unit=readout_time_unit)[0],
                    readout_start_time=timezone.now()
                )

            # Try getting the assay
            assay = assay_models.get(assay_name)
            assay_id = assay_ids.get((assay.id, value_unit), None)

            if not assay_id:
                assay_id = AssayChipReadoutAssay(
                    readout_id=current_chip_readout,
                    assay_id=assay,
                    # Arbitrary value for reader
                    reader_id=dummy_reader,
                    readout_unit=physical_units.get(value_unit)
                )

            # Deal with conflicting data
            current_conflicting_entries = possible_conflicting_data.get((chip_id, assay.id, value_unit, field, time), [])
            conflicting_entries.extend(current_conflicting_entries)

            # Get possible duplicate current entries
            duplicate_current = current_data.get(
                (chip_id, assay.id, value_unit, field, time), []
            )

            number_duplicate_current = len(duplicate_current)
            number_conflicting_entries = len(current_conflicting_entries)

            if overwrite_option in ['delete_conflicting_data', 'delete_all_old_data']:
                number_conflicting_entries = 0

            # Discern what replicate this is (default 1)
            replicate = 0 + number_conflicting_entries + number_duplicate_current

            if save:
                query_list.append((
                    current_chip_readout.id,
                    assay_id.id,
                    field,
                    value,
                    time,
                    quality,
                    notes,
                    replicate
                ))
            else:
                readout_data.append(
                    AssayChipRawData(
                        assay_chip_id=current_chip_readout,
                        assay_id=assay_id,
                        field_id=field,
                        value=value,
                        elapsed_time=time,
                        quality=quality,
                        notes=notes,
                        replicate=replicate
                    )
                )

            # Add to current_data
            current_data.setdefault(
                (chip_id, assay.id, value_unit, field, time), []
            ).append(1)

    if errors:
        raise forms.ValidationError(errors)
    elif save:
        if overwrite_option == 'delete_conflicting_data':
            for entry in conflicting_entries:
                entry.delete()
        elif overwrite_option == 'mark_conflicting_data':
            readout_ids_and_notes = []
            for entry in conflicting_entries:
                readout_ids_and_notes.append((entry.id, entry.notes, entry.quality))
            mark_chip_readout_values(readout_ids_and_notes, stamp=True)

        # Connect to the database
        cursor = connection.cursor()
        # The generic query
        query = ''' INSERT INTO "assays_assaychiprawdata"
              ("assay_chip_id_id", "assay_id_id", "field_id", "value", "elapsed_time", "quality", "notes", "replicate")
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

        cursor.executemany(query, query_list)
        transaction.commit()

        if form:
            modify_qc_status_chip(readout, form)

        return True
    else:
        return readout_data


def get_csv_media_location(file_name):
    """Returns the location given a full path

    Params:
    file_name -- name of the file to write
    """
    split_name = file_name.split('/')
    csv_onward = '/'.join(split_name[-4:])
    return csv_onward

# TODO CSV_ROOT might be better off in the settings
CSV_ROOT = settings.MEDIA_ROOT.replace('mps/../', '', 1) + '/csv/'


# TODO MAY CAUSE SILENT FAILURE
# TODO WE CAN PROBABLY DO AWAY WITH PASSING FORM
def save_chip_files(datalist, current_file, study_id, headers, overwrite_option, readout=None, form=None):
    """Process chip file data

    datalist - all data from the file datalist
    current_file - the AssayDataFile object to link to
    study_id - the study ID in question
    headers - the number of header rows (may be passed as 1 by default)
    overwrite_option - what overwrite option was used\
    readout - the readout in question
    form - the form used so that QC Status can be modified
    """
    # Make sure path exists for study
    if not os.path.exists(CSV_ROOT + study_id):
        os.makedirs(CSV_ROOT + study_id)

#     for chip_id, datalist in chip_data.items():
#         readout = AssayChipReadout.objects.get(
#             chip_setup__assay_run_id_id=study_id,
#             chip_setup__assay_chip_id=chip_id
#         )

    chip_details = get_chip_details(readout=readout, study=study_id)

    validate_chip_readout_file(
        headers,
        datalist,
        chip_details,
        sheet='',
        overwrite_option=overwrite_option,
        readout=readout,
        study=study_id,
        form=form,
        save=True
    )

    for chip_id, readout_details in chip_details.items():
        current_file.chip_readout.add(readout_details.get('readout'))


# TODO MAY CAUSE SILENT FAILURE
def save_plate_files(datalist, current_file, study_id, overwrite_option, readout=None, form=None):
    """Process plate file data

    datalist - all data from the file datalist
    current_file - the AssayDataFile object to link to
    study_id - the study ID in question
    overwrite_option - what overwrite option was used\
    readout - the readout in question
    form - the form used so that QC Status can be modified
    """
    # Make sure path exists for study
    if not os.path.exists(CSV_ROOT + study_id):
        os.makedirs(CSV_ROOT + study_id)

    plate_details = get_plate_details(readout=readout, study=study_id)

    validate_plate_readout_file(
        datalist,
        plate_details,
        sheet='',
        overwrite_option=overwrite_option,
        readout=readout,
        form=form,
        save=True
    )

    for plate_id, readout_details in plate_details.items():
        current_file.plate_readout.add(readout_details.get('readout'))


def mark_chip_readout_values(readout_ids_and_notes, stamp=False):
    # Connect to the database
    cursor = connection.cursor()

    # The query to set a quality to something new
    query = ''' UPDATE "assays_assaychiprawdata"
                SET quality=%s,notes=%s
                WHERE id=%s;'''

    query_list = []

    # Just make quality 'X' for now
    for readout_id_and_notes in readout_ids_and_notes:
        readout_id = readout_id_and_notes[0]
        notes = readout_id_and_notes[1]
        if stamp:
            notes = 'Marked on ' + timezone.now().strftime("%Y-%m-%d") + ' ' + notes
            notes = notes[:255]
        quality = readout_id_and_notes[2]
        if stamp:
            # Add OLD to quality
            quality = 'OLD ' + quality
            quality = quality[:19]
        query_list.append((quality, notes, readout_id))

    # Execute the queries and close the connection
    cursor.executemany(query, query_list)
    transaction.commit()


def mark_plate_readout_values(readout_ids_and_notes, stamp=False):
    # Connect to the database
    cursor = connection.cursor()

    # The query to set a quality to something new
    query = ''' UPDATE "assays_assayreadout"
                SET quality=%s,notes=%s
                WHERE id=%s;'''

    query_list = []

    # Just make quality 'X' for now
    for readout_id_and_notes in readout_ids_and_notes:
        readout_id = readout_id_and_notes[0]
        notes = readout_id_and_notes[1]
        if stamp:
            notes = 'Marked on ' + timezone.now().strftime("%Y-%m-%d") + ' ' + notes
            notes = notes[:255]
        quality = readout_id_and_notes[2]
        # Change quality to X if it is blank currently
        if not quality:
            quality = 'X'
        query_list.append((quality, notes, readout_id))

    # Execute the queries and close the connection
    cursor.executemany(query, query_list)
    transaction.commit()


# TODO BE SURE TO CHECK IF SAVE=TRUE WHEN IT NEEDS TO BE
def parse_file_and_save(current_file, created_by, study_id, overwrite_option, interface, readout=None, headers=1, form=None):
    """Parse the given file and save the associated chip/plate reaodut data

    input_file - the file to reference for input
    input_file_location - the location of the file on the disk
    created_by - who created the file (ie who made this modification)
    study_id - the study ID (as a string PK)
    overwrite_option - the overwrite option selected
    headers - the number of headers (default 1)
    form - the form for saving QC data for chips (likely to be deprecated)
    """
    input_file = current_file.file
    input_file_location = current_file.url

    # TODO CHANGE TO MATCH
    # Set input file to beginning
    input_file.seek(0, 0)

    # Get the study in question for more data
    current_study = AssayRun.objects.get(pk=int(study_id))

    # Create a AssayDataUpload entry for the upload in question
    current_file = AssayDataUpload(
        file_location=input_file_location,
        created_by=created_by,
        modified_by=created_by,
        group_id=current_study.group_id,
        restricted=current_study.restricted
    )

    # Save the current file
    current_file.save()

    if interface == 'Bulk':
        old_chip_data = AssayChipRawData.objects.filter(
            assay_chip_id__chip_setup__assay_run_id_id=study_id
        ).prefetch_related(
            'assay_chip_id__chip_setup__assay_run_id',
            'assay_id__assay_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_chip_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            readout_ids_and_notes = old_chip_data.values_list('id', 'notes', 'quality')
            mark_chip_readout_values(readout_ids_and_notes, stamp=True)

        old_plate_data = AssayReadout.objects.filter(
            assay_device_readout__setup__assay_run_id_id=study_id
        ).prefetch_related(
            'assay_device_readout__setup__assay_run_id',
            'assay__assay_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_plate_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            readout_ids_and_notes = old_plate_data.values_list('id', 'notes', 'quality')
            mark_plate_readout_values(readout_ids_and_notes, stamp=True)

    elif interface == 'Chip':
        old_chip_data = AssayChipRawData.objects.filter(
            assay_chip_id=readout
        ).prefetch_related(
            'assay_chip_id__chip_setup__assay_run_id',
            'assay_id__assay_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_chip_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            readout_ids_and_notes = old_chip_data.values_list('id', 'notes', 'quality')
            mark_chip_readout_values(readout_ids_and_notes, stamp=True)

    elif interface == 'Plate':
        old_plate_data = AssayReadout.objects.filter(
            assay_device_readout=readout
        ).prefetch_related(
            'assay_device_readout__setup__assay_run_id',
            'assay__assay_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_plate_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            readout_ids_and_notes = old_plate_data.values_list('id', 'notes', 'quality')
            mark_plate_readout_values(readout_ids_and_notes, stamp=True)

    excel_file = None
    datalist = None

    try:
        # Turn bulk file to sheets
        file_data = input_file.read()
        excel_file = xlrd.open_workbook(file_contents=file_data)
    except xlrd.XLRDError:
        datareader = unicode_csv_reader(input_file, delimiter=',')
        datalist = list(datareader)

#     chip_data = {}
#     tabular_data = {}
#     block_data = {}

    if excel_file:
        for index, sheet in enumerate(excel_file.sheets()):
            # Skip sheets without anything
            if sheet.nrows < 1:
                continue

            datalist = get_bulk_datalist(sheet)
            # Get the header row
            header = datalist[0]
            sheet_type = get_sheet_type(header)

            if sheet_type in ['Chip']:
                save_chip_files(datalist, current_file, study_id, headers, overwrite_option, readout=readout, form=form)
            elif sheet_type in ['Tabular', 'Block']:
                save_plate_files(datalist, current_file, study_id, overwrite_option, readout=readout, form=form)

            # acquire_valid_data(datalist, sheet_type, chip_data, tabular_data, block_data, headers=headers)


    # Otherwise, if csv
    else:
        # Get the header row
        header = datalist[0]
        sheet_type = get_sheet_type(header)

        if sheet_type in ['Chip']:
            save_chip_files(datalist, current_file, study_id, headers, overwrite_option, readout=readout, form=form)
        elif sheet_type in ['Tabular', 'Block']:
            save_plate_files(datalist, current_file, study_id, overwrite_option, readout=readout, form=form)
        # acquire_valid_data(datalist, sheet_type, chip_data, tabular_data, block_data, headers=headers)

#     if chip_data:
#         save_chip_files(chip_data, study_id, headers, overwrite_option, form)
#     if tabular_data:
#         save_plate_files(tabular_data, study_id, 'Tabular', overwrite_option, form)
#     if block_data:
#         save_plate_files(block_data, study_id, 'Block', overwrite_option, form)


def validate_sheet_type(interface, sheet_type, sheet='csv'):
    message = None
    if sheet_type == 'Chip' and interface == 'Plate':
        message = 'That sheet "{}" was recognized as using a chip format. Please use a plate format in this interface.'.format(sheet)
    elif sheet_type in ['Tabular', 'Block'] and interface == 'Chip':
        message = 'That sheet "{}" was recognized as using a plate format. Please use a chip format in this interface.'.format(sheet)
    return message


# TODO NEEDS REVISION
def validate_excel_file(self, excel_file, interface, overwrite_option, headers=1, study=None, readout=None,
                        chip_details=None, plate_details=None, upload_type=None):
    """Validate an excel file

    Params:
    self - the form in question
    excel_file - the excel_file as an xlrd object
    headers - the number of header rows (default=1)
    study - the study in question (optional)
    readout - the readout in question (optional)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    upload_type - upload type for plates (optional) [DEPRECATED]
    """
    sheet_names = excel_file.sheet_names()

    chip_preview = []
    plate_preview = []

    errors = []

    for index, sheet in enumerate(excel_file.sheets()):
        sheet_name = sheet_names[index]

        # Skip sheets without anything
        if sheet.nrows < 1:
            continue

        # Get datalist
        datalist = get_bulk_datalist(sheet)

        # Get the header row
        header = [unicode(value) for value in sheet.row_values(0)]

        # From the header we need to discern the type of upload
        sheet_type = get_sheet_type(header, sheet_name)

        # TODO CATCH INTERFACE SHEET_TYPE MISMATCH
        error_message = validate_sheet_type(interface, sheet_type, sheet_name)

        if error_message:
            errors.append(error_message)

        # If chip
        if sheet_type == 'Chip':
            if not chip_details:
                chip_details = get_chip_details(self, study, readout)

            # Validate this sheet
            current_chip_preview = validate_chip_readout_file(
                headers,
                datalist,
                chip_details,
                overwrite_option=overwrite_option,
                sheet='Sheet "' + sheet_name + '": ',
                study=study,
                readout=readout
            )

            chip_preview.extend(current_chip_preview)
        # If plate
        else:
            if not plate_details:
                plate_details = get_plate_details(self, study, readout)

            # DO NOT USE upload_type IN LIEU OF sheet_type
            # if upload_type:
            #     sheet_type = upload_type

            current_plate_preview = validate_plate_readout_file(
                datalist,
                plate_details,
                overwrite_option=overwrite_option,
                readout=readout,
                sheet='Sheet "' + sheet_name + '": ',
            )

            plate_preview.extend(current_plate_preview)

    if not errors:
        return {
            'chip_preview': chip_preview,
            'plate_preview': plate_preview
        }
    else:
        raise forms.ValidationError(errors)


# TODO NEEDS REVISION
def validate_csv_file(self, datalist, interface, overwrite_option, study=None, readout=None,
                      chip_details=None, plate_details=None, headers=1, upload_type=None):
    """Validates a CSV file

    Params:
    self - the form in question
    datalist - the data as a list of lists
    study - the study in question (optional)
    readout - the readout in question (optional)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    headers - the number of header rows (default=1)
    upload_type - upload type for plates (optional)
    """
    # From the header we need to discern the type of upload
    header = datalist[0]
    sheet_type = get_sheet_type(header, 'CSV')

    chip_preview = []
    plate_preview = []

    errors = []

    # TODO CATCH INTERFACE SHEET_TYPE MISMATCH
    error_message = validate_sheet_type(interface, sheet_type)

    if error_message:
        errors.append(error_message)

    if sheet_type == 'Chip':
        if not chip_details:
            chip_details = get_chip_details(self, study, readout)

        chip_preview = validate_chip_readout_file(
            headers,
            datalist,
            chip_details,
            overwrite_option=overwrite_option,
            readout=readout,
            study=study
        )
    else:
        if not plate_details:
            plate_details = get_plate_details(self, study, readout)

        if not upload_type:
            upload_type = sheet_type

        plate_preview = validate_plate_readout_file(
            datalist,
            plate_details,
            overwrite_option=overwrite_option,
            readout=readout
        )

    if not errors:
        return {
            'chip_preview': chip_preview,
            'plate_preview': plate_preview
        }
    else:
        raise forms.ValidationError(errors)


def validate_file(
        self,
        test_file,
        interface,
        headers=1,
        chip_details=None,
        plate_details=None,
        study=None,
        readout=None,
        upload_type=None
):
    """Get data from a file: returns read data from excel and datalist from csv

    Params:
    self - the form in question
    test_file - the file in question
    headers - the number of header rows (default=1)
    chip_details - dictionary of assays and units for each chip (optional)
    plate_details - dictionary of assay and units for each plate (optional)
    study - the study in question (optional)
    readout - the readout in question (optional)
    upload_type - upload type for plates (optional)
    """
    # Get overwrite option
    overwrite_option = self.data.get('overwrite_option')

    try:
        file_data = test_file.read()
        excel_file = xlrd.open_workbook(file_contents=file_data)
        preview_data = validate_excel_file(
            self,
            excel_file,
            interface,
            overwrite_option,
            headers,
            study=study,
            readout=readout,
            chip_details=chip_details,
            plate_details=plate_details,
            upload_type=upload_type
        )

        return preview_data

    # If this fails, it isn't an Excel file, so try reading it as text
    except xlrd.XLRDError:
        datareader = unicode_csv_reader(test_file, delimiter=',')
        datalist = list(datareader)
        preview_data = validate_csv_file(
            self,
            datalist,
            interface,
            overwrite_option,
            study=study,
            readout=readout,
            chip_details=chip_details,
            plate_details=plate_details,
            headers=headers,
            upload_type=upload_type
        )

        return preview_data
