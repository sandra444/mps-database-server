from .models import (
    AssayWell,
    AssayWellCompound,
    AssayWellTimepoint,
    AssayWellLabel,
    AssayModel,
    AssayReadout,
    AssayPlateReadout,
    AssayPlateReadoutAssay,
    AssayChipRawData,
    AssayChipReadout,
    AssayChipReadoutAssay
)
from .forms import (
    get_sheet_type,
    get_bulk_datalist,
    get_row_and_column,
    process_readout_value,
    unicode_csv_reader,
    valid_chip_row
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
            # Combine values in a tuple for index
            index = (row, col, time, assay, feature)
            # Just make value X for now (isn't even used)
            value = 'X'
            qc_status.update({index: value})

    return qc_status


@transaction.atomic
def modify_qc_status_plate(current_plate_readout, form):
    """Update the QC status of a plate

    Note that this function uses the @transaction.atomic decorator
    """
    # Get the readouts
    readouts = AssayReadout.objects.filter(
        assay_device_readout=current_plate_readout
    ).prefetch_related(
        'assay'
    ).select_related(
        'assay__assay_id'
    )

    # Get QC status for each line
    qc_status = get_qc_status_plate(form)

    for readout in readouts:
        index_long = (
            readout.row,
            readout.column,
            readout.elapsed_time,
            readout.assay.assay_id.assay_name.upper(),
            readout.assay.feature
        )
        index_short = (
            readout.row,
            readout.column,
            readout.elapsed_time,
            readout.assay.assay_id.assay_short_name.upper(),
            readout.assay.feature
        )
        # If the quality marker is present
        if index_long in qc_status or index_short in qc_status:
            readout.quality = 'X'
            readout.save()
        # If the quality marker has been removed
        elif index_long not in qc_status and index_short not in qc_status and readout.quality:
            readout.quality = u''
            readout.save()


# TODO REVIEW
# Rows are currently numeric, not alphabetical, when stored in the database
def parse_readout_csv(current_assay_readout, current_file, upload_type, overwrite_option, form=None):
    """Stores the readout data parsed from a csv file"""
    # remove_existing_readout(current_assay_readout)
    # AssayReadout.objects.filter(assay_device_readout=current_assay_readout).delete()

    old_readout_data = AssayReadout.objects.filter(
        assay_device_readout=current_assay_readout
    ).prefetch_related(
        'assay__assay_id',
        'assay_chip_id'
    )

    conflicting_data = {}
    # Fill check for conflicting otherwise
    if overwrite_option not in ['keep_conflicting_data', 'delete_all_old_data', 'mark_all_old_data']:
        for readout in old_readout_data:
            conflicting_data.setdefault(
                (readout.assay_id, readout.row, readout.column, readout.elapsed_time), []
            ).append(readout)

    # Connect to the database
    cursor = connection.cursor()

    # The generic query
    query = ''' INSERT INTO "assays_assayreadout"
          ("assay_device_readout_id", "assay_id", "row", "column", "value", "elapsed_time", "quality", "notes")
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

    # The list of queries to execute
    query_list = []
    # Current id
    current_assay_readout_id = current_assay_readout.id

    # Create a reader for the unicode data
    datareader = unicode_csv_reader(current_file, delimiter=',')
    # Turn each row into an entry in a list
    datalist = list(datareader)

    # Create a dictionary that matches (assay, feature) to an AssayPlateReadoutAssay ID
    assays = {}
    for assay in AssayPlateReadoutAssay.objects.filter(readout_id=current_assay_readout):
        assay_name = assay.assay_id.assay_name.upper()
        assay_short_name = assay.assay_id.assay_short_name.upper()
        feature = assay.feature
        current_apra_id = assay.id

        assays.update({(assay_name, feature): current_apra_id})
        assays.update({(assay_short_name, feature): current_apra_id})

    # If the type is a block
    if upload_type == 'Block':
        # Current assay
        assay = None
        # Current time
        time = None

        # Used to discern number of headers for offset
        number_of_assays = 0
        # Used to discern row offset
        number_of_rows = current_assay_readout.setup.assay_layout.device.number_of_rows
        # Used to discern where to read values
        number_of_columns = current_assay_readout.setup.assay_layout.device.number_of_columns

        for row_id, line in enumerate(datalist):
            # TODO HOW DO I DEAL WITH BLANK LINES???
            # If line is blank, move to the next row
            if not line:
                continue

            # If this line is a header
            # Headers should look like:
            # PLATE ID, {{}}, ASSAY, {{}}, FEATURE, {{}}, READOUT UNIT, {{}}, TIME, {{}}. TIME UNIT, {{}}
            if 'PLATE ID' in line[0].upper():
                # Get the assay and feature
                assay_name = line[3].upper()
                feature = line[5]

                # Get the APRA ID
                assay = assays.get((assay_name, feature))

                # Increase the number of assays
                number_of_assays += 1

                # Check if there is a time and take it if it exists
                if len(line) >= 12:
                    time = line[9]

                else:
                    time = None

            # Otherwise the line contains datapoints for the current assay
            # Break if the column_id exceeds the number of columns
            else:
                for column_id, value in enumerate(line[:number_of_columns]):
                    # Treat empty strings as NULL values and do not save the data point
                    if not value:
                        continue

                    # Process the value
                    processed_value = process_readout_value(value)
                    value = processed_value.get('value')
                    quality = processed_value.get('quality')

                    # MUST OFFSET ROW (due to multiple datablocks)
                    offset_row_id = (row_id-number_of_assays) % number_of_rows

                    # Note default elapsed time of 0
                    if not time:
                        time = 0

                    # Right now notes are not available in block
                    notes = ''

                    # Deal with conflicting data
                    conflicting_entries = conflicting_data.get(
                        (assay, offset_row_id, column_id, time), []
                    )

                    for entry in conflicting_entries:
                        if overwrite_option == 'delete_conflicting_data':
                            entry.delete()
                        elif overwrite_option == 'mark_conflicting_data':
                            mark_readout_value(entry)

                    # Add the row to be saved
                    query_list.append((
                        current_assay_readout_id,
                        assay,
                        offset_row_id,
                        column_id,
                        value,
                        time,
                        quality,
                        notes
                    ))

    # Otherwise if the upload is tabular
    else:
        # Purge empty lines, they are useless for tabular uploads
        datalist = [row for row in datalist if any(row)]
        # The first line SHOULD be the header
        header = datalist[0]

        # Check if the time has been specified
        if 'TIME' in header[5].upper() and 'UNIT' in header[6].upper():
            time_specified = True
        else:
            time_specified = False

        # Exclude the header to get only the data points
        data = datalist[1:]

        for row_index, row in enumerate(data):
            # The well identifier given
            well = row[1]
            assay_name = row[2].upper()
            feature = row[3]

            # Split the well into alphabetical and numeric
            # PLEASE NOTE THAT THE VALUES ARE OFFSET BY ONE (to begin with 0)
            row_label, column_label = get_row_and_column(well, 1)

            notes = ''

            if time_specified:
                time = row[5]
                value = row[7]
                if len(row) > 8:
                    notes = row[8]

            else:
                value = row[5]
                time = 0
                if len(row) > 6:
                    notes = row[6]

            # NOTE THAT BLANKS ARE CURRENTLY COMPLETELY EXCLUDED
            if value != '':
                processed_value = process_readout_value(value)
                value = processed_value.get('value')
                quality = processed_value.get('quality')

                assay = assays.get((assay_name, feature))

                # Deal with conflicting data
                conflicting_entries = conflicting_data.get(
                    (assay, row_label, column_label, time), []
                )

                for entry in conflicting_entries:
                    if overwrite_option == 'delete_conflicting_data':
                        entry.delete()
                    elif overwrite_option == 'mark_conflicting_data':
                        mark_readout_value(entry)

                query_list.append((
                    current_assay_readout_id,
                    assay,
                    row_label,
                    column_label,
                    value,
                    time,
                    quality,
                    notes
                ))

    cursor.executemany(query, query_list)

    transaction.commit()

    # Check qc if form passed
    if form:
        modify_qc_status_plate(current_assay_readout, form)


def get_qc_status_chip(form):
    """Get QC status for each line"""
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


# NOTE: Tricky thing about chip QC is IT DEPENDS ON WHETHER IT IS BEING ADDED OR UPDATED
# Why? The ORDER OF THE VALUES REFLECTS THE FILE WHEN ADDING, BUT IS SORTED IN UPDATE
@transaction.atomic
def modify_qc_status_chip(current_chip_readout, form):
    """Update the QC for a chip"""
    # Get the readouts as they would appear on the front end
    # PLEASE NOTE THAT ORDER IS IMPORTANT HERE TO MATCH UP WITH THE INPUTS
    readouts = AssayChipRawData.objects.prefetch_related(
        'assay_chip_id__chip_setup',
        'assay_id__assay_id'
    ).filter(
        assay_chip_id=current_chip_readout
    ).order_by(
        'assay_chip_id__chip_setup__assay_chip_id',
        'assay_id__assay_id__assay_short_name',
        'elapsed_time',
        'quality'
    )

    # Get QC status for each line
    qc_status = get_qc_status_chip(form)

    for index, readout in enumerate(readouts):
        readout.quality = qc_status.get(index)
        readout.save()


# TODO WE CAN PROBABLY DO AWAY WITH PASSING FORM
# TODO REFACTOR CAMEL CASE
@transaction.atomic
def parse_chip_csv(current_chip_readout, current_file, headers, overwrite_option, form):
    """Parse a csv file to get chip readout data"""
    # remove_existing_chip(current_chip_readout)
    old_readout_data = AssayChipRawData.objects.filter(
        assay_chip_id=current_chip_readout
    ).prefetch_related(
        'assay_id__assay_id',
        'assay_chip_id'
    )

    conflicting_data = {}
    # Fill check for conflicting otherwise
    if overwrite_option not in ['keep_conflicting_data', 'delete_all_old_data', 'mark_all_old_data']:
        for readout in old_readout_data:
            conflicting_data.setdefault(
                (readout.assay_id_id, readout.field_id, readout.elapsed_time), []
            ).append(readout)

    assay_models = {}

    for assay in AssayModel.objects.all():
        assay_models.update({
            assay.assay_name: assay,
            assay.assay_short_name: assay
        })

    # Get assay chip readout assays
    assay_ids = {
        (acra.assay_id_id, acra.readout_unit.unit): acra for acra in AssayChipReadoutAssay.objects.filter(
            readout_id=current_chip_readout
        ).prefetch_related('readout_unit')
    }

    # Get QC status for each line
    qc_status = get_qc_status_chip(form)

    datareader = unicode_csv_reader(current_file, delimiter=',')
    datalist = list(datareader)

    # Current index for finding correct QC status
    current_index = 0

    # Only take values from headers onward
    for row in datalist[headers:]:
        # Skip any row with insufficient columns
        if len(row) < 7:
            continue

        # Skip any row with incomplete data
        # This does not include the quality and value (which can be null)
        if not valid_chip_row(row):
            continue

        assay_name = row[3]
        field = row[4]
        val = row[5]
        unit = row[6]
        time = float(row[1])
        # The notes are trimmed to 255 characters
        if len(row) > 8:
            notes = row[8][:255]

        # Try getting the assay
        assay = assay_models.get(assay_name)
        assay_id = assay_ids.get((assay.id, unit))

        # PLEASE NOTE Database inputs, not the csv, have the final say
        # Get quality if possible
        quality = u''
        if len(row) > 7:
            quality = row[7]

        # Get quality from added form inputs if possible
        if current_index in qc_status:
            quality = qc_status.get(current_index)
        # Increment current index acquisition
        current_index += 1

        # Treat empty strings as None
        if not val:
            val = None
            # Set quality to 'NULL' if quality was not set by user
            if not quality:
                quality = 'NULL'

        # Deal with conflicting data
        conflicting_entries = conflicting_data.get((assay_id.id, field, time), [])

        for entry in conflicting_entries:
            if overwrite_option == 'delete_conflicting_data':
                entry.delete()
            elif overwrite_option == 'mark_conflicting_data':
                mark_readout_value(entry)

        #How to parse Chip data
        AssayChipRawData(
            assay_chip_id=current_chip_readout,
            assay_id=assay_id,
            field_id=field,
            value=val,
            elapsed_time=time,
            quality=quality,
            notes=notes
        ).save()


def write_out_csv(file_name, data):
    """Write out a Unicode CSV

    Params:
    file_name -- name of the file to write
    data -- data to write to the file (as a list of lists)
    """
    with open(file_name, 'w') as out_file:
        writer = UnicodeWriter(out_file)
        writer.writerows(data)


def get_csv_media_location(file_name):
    """Returns the location given a full path

    Params:
    file_name -- name of the file to write
    """
    split_name = file_name.split('/')
    csv_onward = '/'.join(split_name[-4:])
    return csv_onward


# TODO WE CAN PROBABLY DO AWAY WITH PASSING FORM
def save_chip_files(chip_data, study_id, headers, overwrite_option, form=None):
    """Save all the chip files

    chip_data - chip data as a dictionary linking chip_id to the respective datalist
    study_id - the study ID in question
    headers - the number of header rows (may be passed as 1 by default)
    overwrite_option - what overwrite option was used
    form - the form used so that QC Status can be modified
    """
    csv_root = settings.MEDIA_ROOT.replace('mps/../', '', 1) + '/csv/'
    # Make sure path exists for study
    if not os.path.exists(csv_root + study_id):
        os.makedirs(csv_root + study_id)

    for chip_id, datalist in chip_data.items():

        readout = AssayChipReadout.objects.get(
            chip_setup__assay_run_id_id=study_id,
            chip_setup__assay_chip_id=chip_id
        )

        # Make sure path exists for chip
        if not os.path.exists(csv_root + study_id + '/chip'):
            os.makedirs(csv_root + study_id + '/chip')

        # Get valid file location
        # Note added csv extension
        file_location = get_valid_csv_location(chip_id, study_id, 'chip', overwrite_option)
        # Write the csv
        write_out_csv(file_location, datalist)

        media_location = get_csv_media_location(file_location)

        # Add the file to the readout
        readout.file = media_location
        readout.save()

        # Note that form may be None
        parse_chip_csv(readout, readout.file, headers, overwrite_option, form)


def save_plate_files(plate_data, study_id, upload_type, overwrite_option, form=None):
    """Save all plate files

    plate_data - plate data as a dictionary linking plate_id to the respective datalist
    study_id - the study ID in question
    upload_type - what upload type option was used
    overwrite_option - what overwrite option was used
    """
    csv_root = settings.MEDIA_ROOT.replace('mps/../', '', 1) + '/csv/'
    # Make sure path exists for study
    if not os.path.exists(csv_root + study_id):
        os.makedirs(csv_root + study_id)

    for plate_id, datalist in plate_data.items():
        datalist = plate_data.get(plate_id)

        readout = AssayPlateReadout.objects.get(
            setup__assay_run_id_id=study_id,
            setup__assay_plate_id=plate_id
        )

        # Make sure path exists for chip
        if not os.path.exists(csv_root + study_id + '/plate'):
            os.makedirs(csv_root + study_id + '/plate')

        # Get valid file location
        # Note added csv extension
        file_location = get_valid_csv_location(plate_id, study_id, 'plate', overwrite_option)
        # Write the csv
        write_out_csv(file_location, datalist)

        media_location = get_csv_media_location(file_location)

        # Add the file to the readout
        readout.file = media_location
        readout.save()

        # Note may lack of a form normally used for QC
        parse_readout_csv(readout, readout.file, upload_type, overwrite_option, form)


def acquire_valid_data(datalist, sheet_type, chip_data, tabular_data, block_data, headers=1):
    """Acquire valid data for the different template types

    datalist - the data in question as a list of lists
    sheet_type - whether the sheet is a chip, tabular, or block
    chip_data - dictionary of chip data to be modified {chip_id: datalist} MAY OR MAY NOT BE MODIFIED
    tabular_data - dictionary of tabular plate data to be modified {plate_id: datalist} MAY OR MAY NOT BE MODIFIED
    block_data - dictionary of block plate data to be modified {plate_id: datalist} MAY OR MAY NOT BE MODIFIED
    headers - number of header rows
    """

    chip_header = [
        u'Chip ID',
        u'Time',
        u'Time Unit',
        u'Assay',
        u'Object',
        u'Value',
        u'Value Unit',
        u'QC Status',
        u'Notes'
    ]

    tabular_header_time = [
        u'Plate ID',
        u'Well Name',
        u'Assay',
        u'Feature',
        u'Unit',
        u'Time',
        u'Time Unit',
        u'Value',
        u'Notes'
    ]

    tabular_header_no_time = [
        u'Plate ID',
        u'Well Name',
        u'Assay',
        u'Feature',
        u'Unit',
        u'Value'
    ]

    if sheet_type == 'Chip':
        header = chip_header
        # Skip header
        for row in datalist[headers:]:
            # Make sure the data is valid before adding it
            # Everything but value and QC Status must exist to be valid
            if valid_chip_row(row):
                chip_id = row[0]
                chip_data.setdefault(chip_id, [header]).append(row)

    elif sheet_type == 'Tabular':
        header = datalist[0]
        # Header if time
        if 'TIME' in header[5].upper() and 'UNIT' in header[6].upper():
            header = tabular_header_time
        # Header if no time
        else:
            header = tabular_header_no_time

        # Skip header
        for row in datalist[1:]:
            # Make sure the data is valid before adding it
            # The first 6 cells must be filled (time and time unit are not required)
            if row and all(row[:6]):
                plate_id = row[0]
                tabular_data.setdefault(plate_id, [header]).append(row)

    elif sheet_type == 'Block':
        # DO NOT skip header
        plate_id = None
        for row in datalist:
            if 'PLATE' in row[0].upper():
                plate_id = row[1]
            block_data.setdefault(plate_id, []).append(row)


# TODO SPAGHETTI CODE
def mark_readout_value(readout_value):
    """Marks a readout value"""
    modified_qc_status = 'OLD ' + readout_value.quality
    modified_qc_status = modified_qc_status[:19]
    readout_value.quality = modified_qc_status
    readout_value.notes = 'Marked on ' + timezone.now().strftime("%Y-%m-%d") + readout_value.notes
    readout_value.save()


def parse_file_and_save(input_file, study_id, overwrite_option, interface, readout=None, headers=1, form=None):
    """Parse the given file and save the associated chip/plate reaodut data

    input_file - the file in question
    study_id - the study ID (as a string PK)
    overwrite_option - the overwrite option selected
    headers - the number of headers (default 1)
    form - the form for saving QC data for chips (likely to be deprecated)
    """
    # Set input file to beginning
    input_file.seek(0, 0)

    if interface == 'Bulk':
        old_chip_data = AssayChipRawData.objects.filter(
            assay_chip_id__chip_setup__assay_run_id_id=study_id
        ).prefetch_related(
            'assay_chip_id__chip_setup__assay_run_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_chip_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            for readout in old_chip_data:
                mark_readout_value(readout)

        old_plate_data = AssayReadout.objects.filter(
            assay_device_readout__setup__assay_run_id_id=study_id
        ).prefetch_related(
            'assay_device_readout__setup__assay_run_id_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_plate_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            for readout in old_plate_data:
                mark_readout_value(readout)

    elif interface == 'Chip':
        old_chip_data = AssayChipRawData.objects.filter(
            assay_chip_id=readout
        ).prefetch_related(
            'assay_chip_id'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_chip_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            for readout in old_chip_data:
                mark_readout_value(readout)

    elif interface == 'Plate':
        old_plate_data = AssayReadout.objects.filter(
            assay_device_readout=readout
        ).prefetch_related(
            'assay_device_readout'
        )

        # Delete all old data
        if overwrite_option == 'delete_all_old_data':
            old_plate_data.delete()
        # Add 'OLD' to qc status of all old data
        elif overwrite_option == 'mark_all_old_data':
            for readout in old_plate_data:
                mark_readout_value(readout)

    excel_file = None
    datalist = None

    try:
        # Turn bulk file to sheets
        file_data = input_file.read()
        excel_file = xlrd.open_workbook(file_contents=file_data)
    except xlrd.XLRDError:
        datareader = unicode_csv_reader(input_file, delimiter=',')
        datalist = list(datareader)

    chip_data = {}
    tabular_data = {}
    block_data = {}

    if excel_file:
        for index, sheet in enumerate(excel_file.sheets()):
            # Skip sheets without anything
            if sheet.nrows < 1:
                continue

            datalist = get_bulk_datalist(sheet)
            # Get the header row
            header = datalist[0]
            sheet_type = get_sheet_type(header)
            acquire_valid_data(datalist, sheet_type, chip_data, tabular_data, block_data, headers=headers)

    # Otherwise, if csv
    else:
        # Get the header row
        header = datalist[0]
        sheet_type = get_sheet_type(header)
        acquire_valid_data(datalist, sheet_type, chip_data, tabular_data, block_data, headers=headers)

    if chip_data:
        save_chip_files(chip_data, study_id, headers, overwrite_option, form)
    if tabular_data:
        save_plate_files(tabular_data, study_id, 'Tabular', overwrite_option, form)
    if block_data:
        save_plate_files(block_data, study_id, 'Block', overwrite_option, form)
