from django import forms
# TODO REVISE
from .models import (
    # PhysicalUnits,
    AssaySampleLocation,
    TIME_CONVERSIONS,
    AssayDataPoint,
    AssayDataFileUpload,
    AssaySubtarget,
    AssayMatrixItem,
    AssayStudyAssay,
    # AssayImage,
    # AssayImageSetting
    AssayStudy,
    AssayStudyStakeholder
)

from mps.templatetags.custom_filters import VIEWER_SUFFIX, ADMIN_SUFFIX

from django.db import connection, transaction
import xlrd

from django.conf import settings
import string
import codecs
import cStringIO

import pandas as pd
import numpy as np

import csv

from chardet.universaldetector import UniversalDetector

# TODO PLEASE REVIEW TO MAKE SURE CONSISTENT
COLUMN_HEADERS = (
    'CHIP ID',
    'CROSS REFERENCE',
    'ASSAY PLATE ID',
    'ASSAY WELL ID',
    'DAY',
    'HOUR',
    'MINUTE',
    'TARGET/ANALYTE',
    'SUBTARGET',
    'METHOD/KIT',
    'SAMPLE LOCATION',
    'VALUE',
    'VALUE UNIT',
    # SUBJECT TO CHANGE
    'REPLICATE',
    'CAUTION FLAG',
    'EXCLUDE',
    'NOTES'
)
REQUIRED_COLUMN_HEADERS = (
    'CHIP ID',
    'ASSAY PLATE ID',
    'ASSAY WELL ID',
    'DAY',
    'HOUR',
    'MINUTE',
    'TARGET/ANALYTE',
    'METHOD/KIT',
    'SAMPLE LOCATION',
    'VALUE',
    'VALUE UNIT',
    # 'EXCLUDE',
    # 'NOTES',
    # 'REPLICATE'
)
# SUBJECT TO CHANGE
DEFAULT_CSV_HEADER = (
    'Chip ID',
    'Cross Reference',
    'Assay Plate ID',
    'Assay Well ID',
    'Day',
    'Hour',
    'Minute',
    'Target/Analyte',
    'Subtarget',
    'Method/Kit',
    'Sample Location',
    'Value',
    'Value Unit',
    'Replicate',
    'Caution Flag',
    'Exclude',
    'Notes'
)
CSV_HEADER_WITH_COMPOUNDS_AND_STUDY = (
    'Study ID',
    'Chip ID',
    'Cross Reference',
    'Assay Plate ID',
    'Assay Well ID',
    'Day',
    'Hour',
    'Minute',
    'Device',
    'Organ Model',
    'Cells',
    'Compound Treatment(s)',
    'Target/Analyte',
    'Method/Kit',
    'Sample Location',
    'Value',
    'Value Unit',
    'Replicate',
    'Caution Flag',
    'Exclude',
    'Notes'
)

DEFAULT_EXPORT_HEADER = (
    'Study ID',
    'Chip ID',
    'Cross Reference',
    'Assay Plate ID',
    'Assay Well ID',
    'Day',
    'Hour',
    'Minute',
    'Device',
    'Organ Model',
    'Settings',
    'Cells',
    'Compound Treatment(s)',
    'Target/Analyte',
    'Subtarget',
    'Method/Kit',
    'Sample Location',
    'Value',
    'Value Unit',
    'Replicate',
    'Caution Flag',
    'Exclude',
    'Notes'
)

# I should have more tuples for containing prefetch arguments
CHIP_DATA_PREFETCH = (
    'assay_id__assay_id',
    'assay_id__readout_unit',
    'assay_id__reader_id',
    'assay_instance__target',
    'assay_instance__unit',
    'assay_instance__method',
    'assay_instance__study',
    'sample_location',
    'assay_chip_id__chip_setup',
    'assay_chip_id__chip_setup__device',
    'assay_chip_id__chip_setup__organ_model',
    'data_upload'
)

# SUBJECT TO CHANGE
MATRIX_ITEM_PREFETCH = (
    'study',
    'matrix',
    'device',
    # Subject to change
    'failure_reason'
)

# SUBJECT TO CHANGE
MATRIX_PREFETCH = (
    'device',
)


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


def get_user_accessible_studies(user):
    """This function acquires a queryset of all studies the user has access to

    Params:
    user - Django user instance
    """
    queryset = AssayStudy.objects.all().prefetch_related(
        'group'
    )

    user_group_names = [
        group.name.replace(VIEWER_SUFFIX, '').replace(ADMIN_SUFFIX, '') for group in user.groups.all()
    ]

    data_group_filter = {}
    access_group_filter = {}
    unrestricted_filter = {}
    unsigned_off_filter = {}
    stakeholder_group_filter = {}
    missing_stakeholder_filter = {}

    stakeholder_group_whitelist = list(set(
        AssayStudyStakeholder.objects.filter(
            group__name__in=user_group_names
        ).values_list('study_id', flat=True)
    ))

    missing_stakeholder_blacklist = list(set(
        AssayStudyStakeholder.objects.filter(
            signed_off_by_id=None,
            sign_off_required=True
        ).values_list('study_id', flat=True)
    ))

    data_group_filter.update({
        'group__name__in': user_group_names
    })
    access_group_filter.update({
        'access_groups__name__in': user_group_names,
    })
    unrestricted_filter.update({
        'restricted': False
    })
    unsigned_off_filter.update({
        'signed_off_by': None
    })
    stakeholder_group_filter.update({
        'id__in': stakeholder_group_whitelist
    })
    missing_stakeholder_filter.update({
        'id__in': missing_stakeholder_blacklist
    })

    # Show if:
    # 1: Study has group matching user_group_names
    # 2: Study has Stakeholder group matching user_group_name AND is signed off on
    # 3: Study has access group matching user_group_names AND is signed off on AND all Stakeholders have signed off
    # 4: Study is unrestricted AND is signed off on AND all Stakeholders have signed off
    combined = queryset.filter(**data_group_filter) | \
               queryset.filter(**stakeholder_group_filter).exclude(**unsigned_off_filter) | \
               queryset.filter(**access_group_filter).exclude(**unsigned_off_filter).exclude(
                   **missing_stakeholder_filter) | \
               queryset.filter(**unrestricted_filter).exclude(**unsigned_off_filter).exclude(
                   **missing_stakeholder_filter)

    combined = combined.distinct().prefetch_related('created_by', 'modified_by', 'signed_off_by')

    return combined


def label_to_number(label):
    """Returns a numeric index from an alphabetical index"""
    num = 0
    for char in label:
        if char in string.ascii_letters:
            num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num


def number_to_label(num):
    """Returns a alphabetical label from a numeric index"""
    if num < 1:
        return ''
    remainder = num % 26
    quotient = num / 26
    if remainder:
        out = chr(64 + remainder).upper()
    else:
        out = 'Z'
        quotient -= 1
    if quotient:
        return number_to_label(quotient) + out
    else:
        return out


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


class AssayFileProcessor:
    """Processes Assay MIFC files"""
    def __init__(self, current_file, study, user, current_data_file_upload=None, save=False):
        self.current_file = current_file
        self.user = user
        if save:
            self.data_file_upload = AssayDataFileUpload(
                file_location=current_file.url,
                created_by=user,
                modified_by=user,
                study=study
            )
        else:
            self.data_file_upload = AssayDataFileUpload()
        self.study = study
        self.save = save
        # NO REAL REASON FOR THIS TO BE A DIC RATHER THAN ATTRIBUTES
        self.preview_data = {
            'readout_data': [],
            'number_of_conflicting_entries': 0,
            'number_of_total_duplicates': 0
        }
        self.errors = []

    def valid_data_row(self, row, header_indices):
        """Confirm that a row is valid"""
        valid_row = False

        for required_column in REQUIRED_COLUMN_HEADERS:
            # if len(row) < header_indices.get(required_column) or not row[header_indices.get(required_column)]:
            if len(row) < header_indices.get(required_column):
                valid_row = False
                break
            elif row[header_indices.get(required_column)]:
                valid_row = True

        return valid_row

    def get_and_validate_header(self, data_list, number_of_rows_to_check=3):
        """Takes the first three rows of a file and returns the indices in a dic and the row index of the header"""
        valid_header = False
        index = 0
        header_indices = None
        while len(data_list) > index and index < number_of_rows_to_check and not valid_header:
            header = data_list[index]
            header_indices = {
                column_header.upper(): index for index, column_header in enumerate(header) if
                column_header.upper() in COLUMN_HEADERS
            }

            valid_header = True

            for column_header in REQUIRED_COLUMN_HEADERS:
                if column_header not in header_indices:
                    index += 1
                    valid_header = False

        if valid_header:
            data_to_return = {
                'header_starting_index': index,
                'header_indices': header_indices
            }
            return data_to_return

        else:
            return False

    def process_data(self, data_list, sheet=''):
        """Validates CSV Uploads for Chip Readouts"""
        # A query list to execute to save chip data
        query_list = []
        # A list of readout data for preview
        readout_data = []
        number_of_total_duplicates = 0

        # Dictionary of all Study Assays with respective PKs
        assay_data = {}
        study_assays = AssayStudyAssay.objects.filter(
            study_id=self.study.id
        ).prefetch_related(
            'target',
            'method',
            'unit',
            # 'study'
        )
        # Note that the names are in uppercase
        for assay in study_assays:
            assay_data.update({
                (assay.target.name.upper(), assay.method.name.upper(), assay.unit.unit): assay,
                (assay.target.short_name.upper(), assay.method.name.upper(), assay.unit.unit): assay,
            })

        # Get matrix item name
        matrix_items = {
            matrix_item.name: matrix_item for matrix_item in AssayMatrixItem.objects.filter(study_id=self.study.id)
        }

        # Get sample locations
        sample_locations = {
            sample_location.name.upper(): sample_location for sample_location in AssaySampleLocation.objects.all()
        }

        # Get all subtargets
        subtargets = {
            subtarget.name.upper(): subtarget for subtarget in AssaySubtarget.objects.all()
        }

        default_subtarget = subtargets.get('NONE')

        # TODO THIS CALL WILL CHANGE IN FUTURE VERSIONS
        old_data = AssayDataPoint.objects.filter(
            study_id=self.study.id,
            replaced=False
        ).prefetch_related(
            'subtarget'
        )

        old_replaced_data = AssayDataPoint.objects.filter(
            study_id=self.study.id,
            replaced=True
        ).prefetch_related(
            'subtarget'
        )

        current_data = {}

        possible_conflicting_data = {}
        conflicting_entries = []

        # Fill check for conflicting
        # TODO THIS WILL NEED TO BE UPDATED
        # TODO IS THIS OPTIMAL WAY TO CHECK CONFLICTING?
        for entry in old_data:
            possible_conflicting_data.setdefault(
                (
                    entry.matrix_item_id,
                    entry.assay_plate_id,
                    entry.assay_well_id,
                    entry.study_assay_id,
                    entry.sample_location_id,
                    entry.time,
                    entry.replicate,
                    # ADD VALUE!
                    # Uses name to deal with subtargets that don't exist yet
                    entry.subtarget.name,
                    # entry.value
                ), []
            ).append(entry)

        # KIND OF CONFUSING, BUT IT IS EXPEDIENT TO PRETEND REPLACED DATA IS CURRENT DATA FOR UPDATE NUMBER
        for entry in old_replaced_data:
            current_data.setdefault(
                (
                    entry.matrix_item_id,
                    entry.assay_plate_id,
                    entry.assay_well_id,
                    entry.study_assay_id,
                    entry.sample_location_id,
                    entry.time,
                    entry.replicate,
                    # ADD VALUE!
                    # Uses name to deal with subtargets that don't exist yet
                    entry.subtarget.name,
                    # entry.value
                ), []
            ).append(1)

        # Get the headers to know where to get data
        header_data = self.get_and_validate_header(data_list, 3)
        starting_index = header_data.get('header_starting_index') + 1
        header_indices = header_data.get('header_indices')

        if sheet:
            sheet = sheet + ': '

        # Read headers going onward
        for line in data_list[starting_index:]:
            # Some lines may not be long enough (have sufficient commas), ignore such lines
            # Some lines may be empty or incomplete, ignore these as well
            # TODO TODO TODO
            if not self.valid_data_row(line, header_indices):
                continue

            matrix_item_name = line[header_indices.get('CHIP ID')]

            assay_plate_id = line[header_indices.get('ASSAY PLATE ID')]
            assay_well_id = line[header_indices.get('ASSAY WELL ID')]

            # Currently required, may be optional later
            day = line[header_indices.get('DAY')]
            hour = line[header_indices.get('HOUR')]
            minute = line[header_indices.get('MINUTE')]

            times = {
                'day': day,
                'hour': hour,
                'minute': minute
            }
            # Elapsed time in minutes
            # Acquired later
            time = 0

            # Note that the names are in uppercase
            target_name = line[header_indices.get('TARGET/ANALYTE')].strip()
            method_name = line[header_indices.get('METHOD/KIT')].strip()
            sample_location_name = line[header_indices.get('SAMPLE LOCATION')].strip()

            value = line[header_indices.get('VALUE')]
            value_unit_name = line[header_indices.get('VALUE UNIT')].strip()

            # Check for subtarget name, add one if necessary
            if header_indices.get('SUBTARGET'):
                subtarget_name = line[header_indices.get('SUBTARGET')].strip()
            else:
                subtarget_name = ''

            subtarget = subtargets.get(subtarget_name.upper(), None)

            if not subtarget_name:
                subtarget = default_subtarget

            if subtarget_name and not subtarget:
                # TODO TODO TODO TODO MAKE NEW SUBTARGET
                subtarget = AssaySubtarget(name=subtarget_name)

                if self.save:
                    subtarget.save()

                subtargets.update({
                    subtarget_name.upper(): subtarget
                })

            # Throw error if no Sample Location
            if not sample_location_name:
                self.errors.append(
                    sheet + 'Please make sure all rows have a Sample Location. Additionally, check to see if all related data have the SAME Sample Location.'
                )

            sample_location = sample_locations.get(sample_location_name.upper())
            sample_location_id = None
            if not sample_location:
                self.errors.append(
                    unicode(sheet + 'The Sample Location "{0}" was not recognized.').format(sample_location_name)
                )
            else:
                sample_location_id = sample_location.id

            # TODO THE TRIMS HERE SHOULD BE BASED ON THE MODELS RATHER THAN MAGIC NUMBERS
            # Get notes, if possible
            notes = u''
            if header_indices.get('NOTES', '') and header_indices.get('NOTES') < len(line):
                notes = line[header_indices.get('NOTES')].strip()[:255]

            cross_reference = u''
            if header_indices.get('CROSS REFERENCE', '') and header_indices.get('CROSS REFERENCE') < len(line):
                cross_reference = line[header_indices.get('CROSS REFERENCE')].strip()[:255]

            # Excluded sees if ANYTHING is in EXCLUDE
            excluded = False
            if header_indices.get('EXCLUDE', '') and header_indices.get('EXCLUDE') < len(line):
                # PLEASE NOTE: Will only ever add 'X' now
                # quality = line[header_indices.get('QC STATUS')].strip()[:20]
                if line[header_indices.get('EXCLUDE')].strip():
                    excluded = True

            caution_flag = u''
            if header_indices.get('CAUTION FLAG', '') and header_indices.get('CAUTION FLAG') < len(line):
                caution_flag = line[header_indices.get('CAUTION FLAG')].strip()[:20]

            # Get replicate if possible
            # DEFAULT IS SUBJECT TO CHANGE PLEASE BE AWARE
            replicate = ''
            if header_indices.get('REPLICATE', '') and header_indices.get('REPLICATE') < len(line):
                replicate = line[header_indices.get('REPLICATE')].strip()[:255]

            # TODO TODO TODO TODO
            matrix_item = matrix_items.get(matrix_item_name, None)
            matrix_item_id = None
            if not matrix_item:
                self.errors.append(
                    unicode(
                        sheet + 'No Matrix Item with the ID "{0}" exists; please change your file or add this chip.'
                    ).format(matrix_item_name)
                )
            else:
                matrix_item_id = matrix_item.id

            # Raise error when an assay does not exist
            study_assay = assay_data.get((
                target_name.upper(),
                method_name.upper(),
                value_unit_name
            ), None)

            study_assay_id = None
            if not study_assay:
                self.errors.append(
                    unicode(
                        sheet + '{0}: No assay with the target "{1}", the method "{2}", and the unit "{3}" exists. '
                                'Please review your data and add this assay to your study if necessary.').format(
                        matrix_item_name,
                        target_name,
                        method_name,
                        value_unit_name
                    )
                )
            else:
                study_assay_id = study_assay.id

            # Check every value to make sure it can resolve to a float
            try:
                # Keep empty strings, though they technically can not be converted to floats
                if value != '':
                    value = float(value)
            except:
                self.errors.append(
                    sheet + 'The value "{}" is invalid; please make sure all values are numerical'.format(value)
                )

            # Check to make certain the time is a valid float
            for time_unit, conversion in TIME_CONVERSIONS.items():
                current_time_value = times.get(time_unit, 0)

                if current_time_value == '':
                    current_time_value = 0

                try:
                    current_time_value = float(current_time_value)
                    time += current_time_value * conversion
                except:
                    self.errors.append(
                        sheet + 'The {0} "{1}" is invalid; please make sure all times are numerical'.format(
                            time_unit,
                            current_time_value
                        )
                    )

            # Treat empty strings as None
            if value == '':
                value = None

            if not self.errors:
                # Deal with conflicting data
                current_conflicting_entries = possible_conflicting_data.get(
                    (
                        matrix_item_id,
                        assay_plate_id,
                        assay_well_id,
                        study_assay_id,
                        sample_location_id,
                        time,
                        replicate,
                        # ADD VALUE!
                        subtarget.name,
                        # value
                    ), []
                )

                # If value is the same, don't bother considering at all
                total_duplicate = False
                for conflict in current_conflicting_entries:
                    if conflict.value == value:
                        total_duplicate = True
                        number_of_total_duplicates += 1
                        break

                if not total_duplicate:
                    conflicting_entries.extend(current_conflicting_entries)

                # Get possible duplicate current entries
                duplicate_current = current_data.get(
                    (
                        matrix_item_id,
                        assay_plate_id,
                        assay_well_id,
                        study_assay_id,
                        sample_location_id,
                        time,
                        replicate,
                        # ADD VALUE!
                        subtarget.name,
                        # value
                    ), []
                )

                number_duplicate_current = len(duplicate_current)
                number_conflicting_entries = len(current_conflicting_entries)

                # Discern what update_number this is (default 0)
                update_number = 0 + number_conflicting_entries + number_duplicate_current

                if self.save and not total_duplicate:
                    query_list.append((
                        self.study.id,
                        matrix_item_id,
                        cross_reference,
                        assay_plate_id,
                        assay_well_id,
                        study_assay_id,
                        subtarget.id,
                        sample_location_id,
                        value,
                        time,
                        caution_flag,
                        excluded,
                        notes,
                        replicate,
                        update_number,
                        self.data_file_upload.id,
                        False
                    ))
                elif not total_duplicate:
                    readout_data.append(
                        AssayDataPoint(
                            matrix_item=matrix_item,
                            cross_reference=cross_reference,
                            assay_plate_id=assay_plate_id,
                            assay_well_id=assay_well_id,
                            study_assay=study_assay,
                            sample_location=sample_location,
                            value=value,
                            time=time,
                            caution_flag=caution_flag,
                            excluded=excluded,
                            notes=notes,
                            replicate=replicate,
                            update_number=update_number,
                            # data_file_upload=self.data_file_upload
                        )
                    )

                # Add to current_data
                current_data.setdefault(
                    (
                        matrix_item_id,
                        assay_plate_id,
                        assay_well_id,
                        study_assay_id,
                        sample_location_id,
                        time,
                        replicate,
                        # ADD VALUE!
                        subtarget.name,
                        # value
                    ), []
                ).append(1)

        # If errors
        if self.errors:
            self.errors = list(set(self.errors))
            raise forms.ValidationError(self.errors)
        # If there wasn't anything
        elif len(query_list) < 1 and len(readout_data) < 1 and not number_of_total_duplicates:
            raise forms.ValidationError(
                'This file does not contain any valid data. Please make sure every row has values in required columns.'
            )
        elif len(query_list) < 1 and len(readout_data) < 1 and number_of_total_duplicates:
            raise forms.ValidationError(
                'This file contains only duplicate data. Please make sure this is the correct file.'
            )

        # TODO TODO TODO TODO
        # If the intention is to save
        elif self.save:
            # Connect to the database
            cursor = connection.cursor()
            # The generic query
            # TODO TODO TODO TODO
            query = ''' INSERT INTO "assays_assaydatapoint"
                      ("study_id", "matrix_item_id", "cross_reference", "assay_plate_id", "assay_well_id", "study_assay_id", "subtarget_id", "sample_location_id", "value", "time", "caution_flag", "excluded", "notes", "replicate", "update_number", "data_file_upload_id", "replaced")
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor.executemany(query, query_list)
            transaction.commit()
            cursor.close()

        # Be sure to subtract the number of replaced points!
        self.preview_data['readout_data'].extend(readout_data)
        self.preview_data['number_of_conflicting_entries'] += len(conflicting_entries)
        self.preview_data['number_of_total_duplicates'] += number_of_total_duplicates

    def process_excel_file(self):
        file_data = self.current_file.read()
        excel_file = xlrd.open_workbook(file_contents=file_data)

        sheet_names = excel_file.sheet_names()

        at_least_one_valid_sheet = False

        for index, sheet in enumerate(excel_file.sheets()):
            sheet_name = sheet_names[index]

            # Skip sheets without anything and skip sheets that are hidden
            if sheet.nrows < 1 or sheet.visibility != 0:
                continue

            # Get datalist
            data_list = []

            # Include the first row (the header)
            for row_index in range(sheet.nrows):
                data_list.append([stringify_excel_value(value) for value in sheet.row_values(row_index)])

            # Check if header is valid
            valid_header = self.get_and_validate_header(data_list)

            if valid_header:
                self.process_data(data_list, sheet_name)
                at_least_one_valid_sheet = True

        if not at_least_one_valid_sheet:
            self.errors.append(
                'No valid sheets were detected in the file. Please check to make sure your headers are correct and start in the top-left corner.'
            )

    def process_csv_file(self):
        data_reader = unicode_csv_reader(self.current_file, delimiter=',')
        data_list = list(data_reader)

        # Check if header is valid
        valid_header = self.get_and_validate_header(data_list)

        if valid_header:
            self.process_data(data_list)

        # IF NOT VALID, THROW ERROR
        else:
            self.errors.append('The file is not formatted correctly. Please check the header of the file.')

    def process_file(self):
        # Save the data upload if necessary (ostensibly save should only run after validation)
        if self.save:
            self.data_file_upload.save()

        self.current_file.seek(0, 0)
        try:
            self.process_excel_file()
        except xlrd.XLRDError:
            self.process_csv_file()


# TODO TODO TODO PLEASE REVISE STYLES WHEN POSSIBLE
def ICC_A(X):
    #This function is to calculate the ICC absolute agreement value for the input matrix
    icc_mat=X.values

    Count_Row=icc_mat.shape[0] #gives number of row count
    Count_Col=icc_mat.shape[1] #gives number of col count

    #ICC row mean
    icc_row_mean=icc_mat.mean(axis=1)

    #ICC column mean
    icc_col_mean=icc_mat.mean(axis=0)

    #ICC total mean
    icc_total_mean=icc_mat.mean()

    #Sum of squre row and column means
    SSC=sum((icc_col_mean-icc_total_mean)**2)*Count_Row

    SSR=sum((icc_row_mean-icc_total_mean)**2)*Count_Col

    #sum of squre errors
    SSE=0
    for row in range(Count_Row):
        for col in range(Count_Col):
            SSE=SSE+(icc_mat[row,col]-icc_row_mean[row]-icc_col_mean[col]+icc_total_mean)**2

    SSW = SSE + SSC
    MSR = SSR / (Count_Row-1)
    MSE = SSE / ((Count_Row-1)*(Count_Col-1))
    MSC = SSC / (Count_Col-1)
    MSW = SSW / (Count_Row*(Count_Col-1))
    ICC_A = (MSR - MSE) / (MSR + (Count_Col-1)*MSE + Count_Col*(MSC-MSE)/Count_Row)
    return ICC_A


def Max_CV(X):
    #This function is to estimate the maximum CV of all chips' measurements through time (row)
    if X.isnull().sum().sum()>0:
        Y=Matrix_Fill(X)
    else:
        Y=X
    icc_mat=Y.values
    a_count=Y.shape[0]
    CV_Array=pd.DataFrame(index=Y.index,columns=['CV (%)'])
    for row in range(a_count):
        if np.std(icc_mat[row,:])>0:
            CV_Array.iloc[row][0]=np.std(icc_mat[row,:],ddof=1)/np.mean(icc_mat[row,:])*100.0
        else:
            CV_Array.iloc[row][0]=0
    #Calculate Max CV
    Max_CV = CV_Array.max(axis=0)
    return Max_CV


def CV_Array(X):
    #This fuction is to calculate the CVs on every time point
    if X.isnull().sum().sum()>0:
        Y=Matrix_Fill(X)
    else:
        Y=X
    icc_mat=Y.values
    #This fuction is to calculate the CVs on every time point
    a_count=Y.shape[0]
    CV_Array=pd.DataFrame(index=Y.index,columns=['CV (%)'])
    for row in range(a_count):
        if np.std(icc_mat[row,:])>0:
            CV_Array.iloc[row][0]=np.std(icc_mat[row,:],ddof=1)/np.mean(icc_mat[row,:])*100.0
        else:
            CV_Array.iloc[row][0]=0
    CV_Array=CV_Array.round(2)
    return CV_Array


def MAD_score(X):
    #Calculate the MAD score matrix for all chips' mesurements
    if X.isnull().sum().sum()>0:
        Y=Matrix_Fill(X)
    else:
        Y=X
    #MAD Score matrix
    icc_mat=Y.values
    Count_Row=icc_mat.shape[0] #gives number of row count
    Count_Col=icc_mat.shape[1] #gives number of col count
    mad_diff = pd.DataFrame(index=Y.index,columns=Y.columns, dtype='float') #define the empty dataframe
    icc_median=Y.median(axis=1)
    for row in range(Count_Row):
        for col in range(Count_Col):
            mad_diff.iloc[row][col]=abs(Y.iloc[row][col]-icc_median.values[row])

    mad_icc=mad_diff.median(axis=1)
    mad_score = pd.DataFrame(index=Y.index,columns=Y.columns, dtype='float') #define the empty dataframe
    for row in range(Count_Row):
        for col in range(Count_Col):
            if mad_icc.values[row]>0:
                mad_score.iloc[row][col]=0.6745*(Y.iloc[row][col]-icc_median.values[row])/mad_icc.values[row]
            else:
                mad_score.iloc[row][col]=0
    mad_score=mad_score.round(2)
    return mad_score


def chip_med_comp_ICC(X):
    #This fuction calculates the ICC absolute agreement table by comparing each chip mesurements with the median
    #of all chips' measurements. Also report the missing points for each chip
    if X.isnull().sum().sum()>0:
        Y=Matrix_Fill(X)
    else:
        Y=X
    icc_mat=Y.values
    Count_Col=icc_mat.shape[1] #gives number of column count
    col_index=Y.columns
    df_missing=X.isnull().sum(axis=0)
    #define ICC list dataframe
    icc_comp_value=pd.DataFrame(index=range(Count_Col),columns=['Chip ID','ICC Absolute Agreement','Missing Data Points'])
    icc_median=Y.median(axis=1)
    for col in range(Count_Col):
        df=pd.DataFrame(Y,columns=[col_index[col]])
        icc_comp_mat=pd.concat([icc_median, df], join='outer', axis=1)
        icc_comp_value.iloc[col][0]=col_index[col]
        icc_comp_value.iloc[col][1]=ICC_A(icc_comp_mat)
        icc_comp_value.iloc[col][2]=df_missing[col]
    icc_comp_value['ICC Absolute Agreement']=icc_comp_value['ICC Absolute Agreement'].apply(lambda x: round(x,2))
    return icc_comp_value


def Matrix_Fill(X):
    #This function fill the missing data points by average data through time (row)
    missing_stat= X.isnull()
    row_mean=X.mean(axis=1)
    icc_mat=X.values
    Count_Row=icc_mat.shape[0] #gives number of row count
    Count_Col=icc_mat.shape[1] #gives number of col count
    fill_mat = pd.DataFrame(index=X.index,columns=X.columns, dtype='float') #define the empty dataframe
    for row in range(Count_Row):
        for col in range(Count_Col):
            if missing_stat.iloc[row][col] == True:
               fill_mat.iloc[row][col]=row_mean.values[row]
            else:
                fill_mat.iloc[row][col]=X.iloc[row][col]

    return fill_mat


def Reproducibility_Index(X):
    #This function is to calculate the Max CV and ICC absolute agreement data table
    if X.isnull().sum().sum()>0:
        Y=Matrix_Fill(X)
    else:
        Y=X
    Max_CV_value=Max_CV(Y) #Call Max CV function
    ICC_Value=ICC_A(Y) #Call ICC function
    #Create a reproducibility index dataframe
    rep_index=pd.DataFrame(index=range(1),columns=['Max CV','ICC Absolute Agreement'], dtype='float') #define the empty dataframe
    rep_index.iloc[0][0]=Max_CV_value
    rep_index.iloc[0][1]=ICC_Value
    rep_index=rep_index.round(2)
    return rep_index


def Single_Time_Reproducibility_Index(X):
    #This function is to calculate the CV, mean, Median and standard deviation for evaluate the reproducibility of single
    #time measurements
    rep_mean=X.mean(axis=1)
    rep_sd=X.std(axis=1,ddof=1)
    rep_med=X.median(axis=1)
    rep_index=pd.DataFrame(index=range(1),columns=['CV','Mean','Standard Deviation','Median'], dtype='float')
    if rep_sd.iloc[0] > 0:
        rep_index.iloc[0][0]=X.std(axis=1,ddof=1)/X.mean(axis=1)*100

    rep_index.iloc[0][1]=rep_mean
    rep_index.iloc[0][2]=rep_sd
    rep_index.iloc[0][3]=rep_med
    rep_index=rep_index.round(2)
    return rep_index

def Reproducibility_Report(study_data):
    #Calculate and report the reproducibility index and status and other parameters
     #Select unique group rows by study, organ model,sample location, assay and unit
    #Drop null value rows
    study_data= study_data.dropna(subset=['Value'])
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)

    study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit"]]
    study_unique_group=study_group.drop_duplicates()
    study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)

    #create reproducibility report table
    reproducibility_results_table=study_unique_group
    header_list=study_unique_group.columns.values.tolist()
    header_list.append('Max CV')
    header_list.append('ICC Absolute Agreement')
    header_list.append('Reproducibility Status')
    header_list.append('Replica Set')
    header_list.append('# of Chips/Wells')
    header_list.append('# of Time Points')
    header_list.append('Reproducibility Note')

    #Define all columns of reproducibility report table
    reproducibility_results_table = reproducibility_results_table.reindex(columns = header_list)
    #Loop every unique replicate group
    group_count=len(study_unique_group.index)
    for row in range(group_count):
        rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
        rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
        rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
        rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
        rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
        rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
        rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
        #create replicate matrix for intra reproducibility analysis
        icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time (day)',columns=['Chip ID'], aggfunc=np.mean)
        group_id = str(row+1) #Define group ID

        reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Replica Set')] = group_id
        reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('# of Chips/Wells')] = icc_pivot.shape[1]
        reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('# of Time Points')] = icc_pivot.shape[0]

        # Check all coulmns are redundent
        if icc_pivot.shape[1]>1 and all(icc_pivot.eq(icc_pivot.iloc[:, 0], axis=0).all(1)):
            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Note')] ='Duplicate data on chips/wells'
        elif icc_pivot.shape[0]>1 and all(icc_pivot.eq(icc_pivot.iloc[0, :], axis=1).all(1)):
            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Note')] ='Duplicate data on all time points'
        else:
            if icc_pivot.shape[0]>1 and icc_pivot.shape[1]>1:
                #Call a chip time series reproducibility index dataframe
                rep_index=Reproducibility_Index(icc_pivot)
                if pd.isnull(rep_index.iloc[0][0]) != True:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Max CV')] =rep_index.iloc[0][0]
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('ICC Absolute Agreement')] =rep_index.iloc[0][1]

                    if rep_index.iloc[0][0] <= 15 and rep_index.iloc[0][0] >0:
                        if rep_index.iloc[0][0] <= 5:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Excellent (CV)'
                        elif rep_index.iloc[0][1] >= 0.8:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Excellent (ICC)'
                        else:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Acceptable (CV)'
                    else:
                        if rep_index.iloc[0][1] >= 0.8:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Excellent (ICC)'
                        elif rep_index.iloc[0][1] >= 0.2:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Acceptable (ICC)'
                        else:
                            reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Poor (ICC)'
                else:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
            elif icc_pivot.shape[0]<2 and icc_pivot.shape[1]>1:
                 #Call a single time reproducibility index dataframe
                rep_index=Single_Time_Reproducibility_Index(icc_pivot)
                reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Max CV')] =rep_index.iloc[0][0]
                if rep_index.iloc[0][0] <= 5 and rep_index.iloc[0][0] > 0:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Excellent (CV)'
                elif rep_index.iloc[0][0] <= 15 and rep_index.iloc[0][0] > 5:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Acceptable (CV)'
                elif rep_index.iloc[0][0] > 15:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='Poor (CV)'
                elif rep_index.iloc[0][0] < 0:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Note')] ='CV cannot be calculated from negative data.'
                else:
                    reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
            else:
                reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Status')] ='NA'
                reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Reproducibility Note')] ='Insufficient replicate chips/wells to calculate reproducibility. At least 2 replicates are needed.'
            reproducibility_results_table=reproducibility_results_table.round(2)
    return reproducibility_results_table

def study_group_setting(study_unique_group,row):
    group_setting=pd.DataFrame(index=range(study_unique_group.shape[1]),columns=['Replicate Set Parameters','Setting'])
    for i in range(study_unique_group.shape[1]):
        group_setting.iloc[i][0]=study_unique_group.columns.tolist()[i]

    for i in range(study_unique_group.shape[1]):
        group_setting.iloc[i][1]=study_unique_group.iloc[row][i]
    return group_setting


def pivot_data_matrix(study_data,group_index):
    #Drop null value rows
    study_data= study_data.dropna(subset=['Value'])
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)
    row=group_index
    study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit"]]
    study_unique_group=study_group.drop_duplicates()
    study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)
    rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
    rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
    rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
    rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
    rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
    rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
    rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
    #create replicate matrix for intra reproducibility analysis
    icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time (day)',columns=['Chip ID'], aggfunc=np.mean)
    return icc_pivot


def scatter_plot_matrix(study_data,group_index):
    #Drop null value rows
    study_data= study_data.dropna(subset=['Value'])
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)
    row=group_index
    study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit"]]
    study_unique_group=study_group.drop_duplicates()
    study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)
    rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
    rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
    rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
    rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
    rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
    rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
    rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
    #create replicate matrix for intra reproducibility analysis
    icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time (day)',columns=['Chip ID'], aggfunc=np.mean)
    if icc_pivot.isnull().sum().sum()>0:
        Y=Matrix_Fill(icc_pivot)
    else:
        Y=icc_pivot
    d_median = Y.median(axis=1)
    plot_matrix=icc_pivot
    plot_header_list=plot_matrix.columns.values.tolist()
    plot_header_list.insert(0, 'Median')
    plot_matrix = plot_matrix.reindex(columns = plot_header_list)
    for i in range(len(d_median)):
        plot_matrix.iloc[i, plot_matrix.columns.get_loc('Median')] = d_median.iloc[i]

    return plot_matrix


def get_repro_data(datafile):
    #Load the summary data into the dataframe
    study_data = pd.DataFrame(datafile)
    study_data.columns = study_data.iloc[0]
    study_data = study_data.drop(study_data.index[0])
    #Drop null value rows
    study_data['Value'].replace('', np.nan, inplace=True)
    study_data= study_data.dropna(subset=['Value'])
    study_data['Value'] = study_data['Value'].astype(float)
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data['Chip ID'].astype(str)

    #Add Time (day) calculated from three time column
    study_data["Time (day)"] = study_data["Day"] + study_data["Hour"]/24.0+study_data["Minute"]/24.0/60.0
    study_data["Time (day)"] = study_data["Time (day)"].apply(lambda x: round(x,2))

    #Select unique group rows by study, organ model,sample location, assay and unit
    study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit"]]
    study_unique_group=study_group.drop_duplicates()
    study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)

    #create reproducibility report table
    reproducibility_results_table=Reproducibility_Report(study_data)

    datadict = {}

    #Define all columns of reproducibility report table
    reproducibility_results_table_nanless = reproducibility_results_table.fillna('')
    datadict['reproducibility_results_table'] = reproducibility_results_table_nanless.to_dict('split')

    #Loop every unique replicate group
    group_count=len(study_unique_group.index)

    for row in range(group_count):
        datadict[row] = {}

        group_id = str(row+1) #Define group ID

        icc_pivot = pivot_data_matrix(study_data,row)

        #Call MAD score function
        mad_score_matrix=MAD_score(icc_pivot)#.round(2)
        datadict[row]['mad_score_matrix'] = mad_score_matrix.to_dict('split')

        cv_chart=scatter_plot_matrix(study_data,row).fillna('')
        datadict[row]['cv_chart'] = cv_chart.to_dict('split')

        if icc_pivot.shape[0]>1 and all(icc_pivot.eq(icc_pivot.iloc[0, :], axis=1).all(1)):
            CV_array= CV_Array(icc_pivot).round(2).fillna('')
            datadict[row]['CV_array'] = CV_array.to_dict('split')

        elif icc_pivot.shape[0]>1 and icc_pivot.shape[1]>1:
            #Call ICC values by Comparing each chip's observations with the Median of the Chip Observations
            comp_ICC_Value=chip_med_comp_ICC(icc_pivot).fillna('').round(2)
            datadict[row]['comp_ICC_Value'] = comp_ICC_Value.to_dict('list')
            #Call calculated CV array for all time points
            CV_array = CV_Array(icc_pivot).round(2).fillna('')
            datadict[row]['CV_array'] = CV_array.to_dict('split')
            #Call a chip time series reproducibility index dataframe
            rep_index=Reproducibility_Index(icc_pivot).round(2)
            datadict[row]['rep_index'] = rep_index.to_dict('list')
        elif icc_pivot.shape[1]>1:
            #Call a single time reproducibility index dataframe
            rep_index=Single_Time_Reproducibility_Index(icc_pivot).round(2)
            datadict[row]['rep_index'] = rep_index.to_dict('list')
        group_index=study_group_setting(study_unique_group,row)

    return datadict
