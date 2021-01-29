import math

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
    AssayStudyStakeholder,
    AssayTarget,
    AssayMethod,
    AssaySampleLocation,
    PhysicalUnits,
    AssayPlateReaderMap,
    AssayPlateReaderMapItem,
    AssayPlateReaderMapItemValue,
    AssayPlateReaderMapDataFile,
    AssayPlateReaderMapDataFileBlock,
    assay_plate_reader_map_info_row_labels_384,
    assay_plate_reader_map_info_col_labels_384,
    assay_plate_reader_map_info_row_labels_24,
    assay_plate_reader_map_info_col_labels_24,
    assay_plate_reader_map_info_row_labels_96,
    assay_plate_reader_map_info_col_labels_96,
    assay_plate_reader_map_info_row_contents_24,
    assay_plate_reader_map_info_row_contents_96,
    assay_plate_reader_map_info_row_contents_384,
    assay_plate_reader_map_info_shape_col_dict,
    assay_plate_reader_map_info_shape_row_dict,
    assay_plate_reader_map_info_plate_size_choices,
    assay_plate_reader_map_info_plate_size_choices_list,
    AssayOmicDataPoint,
    AssayOmicAnalysisTarget,
    AssayOmicDataFileUpload,
    AssayOmicSampleMetadata,
)
from microdevices.models import (
    OrganModelLocation,
)

from mps.templatetags.custom_filters import VIEWER_SUFFIX, ADMIN_SUFFIX

from django.db import connection, transaction
import xlrd
import xlsxwriter

from django.conf import settings
import string
import codecs
import csv
import io
import os
from statistics import mean, mode
import warnings
import copy

import pandas as pd
import numpy as np
import scipy.interpolate as sp
import scipy.stats as stats
from scipy.interpolate import CubicSpline
from scipy import integrate
from scipy.stats import ttest_ind
from scipy import stats
from sympy import gamma
from statsmodels.stats.power import (tt_solve_power, TTestIndPower)
from collections import Counter
import operator
import re
import json
import time
from django.db.models import Q
from scipy.optimize import leastsq
import hashlib
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

# from sklearn.linear_model import LinearRegression
# from sklearn import metrics
# from decimal import Decimal

from chardet.universaldetector import UniversalDetector

from mps.settings import MEDIA_ROOT, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX

# TODO PLEASE REVIEW TO MAKE SURE CONSISTENT
COLUMN_HEADERS = (
    'CHIP ID OR WELL ID',
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
    'CHIP ID OR WELL ID',
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
    'Chip ID or Well ID',
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
    'Chip ID or Well ID',
    'Cross Reference',
    'Assay Plate ID',
    'Assay Well ID',
    'Day',
    'Hour',
    'Minute',
    'Device',
    'MPS Model',
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
    'Chip ID or Well ID',
    'Matrix ID',
    'Cross Reference',
    'Assay Plate ID',
    'Assay Well ID',
    'Day',
    'Hour',
    'Minute',
    'Device',
    'MPS Model',
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

# calibration curve master dictionary
# should be able to change values but NOT THE KEYS or much will get messed up
CALIBRATION_CURVE_MASTER_DICT = {
    'select_one': 'Select One',
    'no_calibration': 'No Calibration',
    'best_fit': 'Best Fit',
    'logistic4': '4 Parameter Logistic w/fitted bounds',
    'logistic4a0': '4 Parameter Logistic w/lower bound = 0',
    'logistic4f': '4 Parameter Logistic w/user specified bound(s)',
    'linear': 'Linear w/fitted intercept',
    'linear0': 'Linear w/intercept = 0',
    'log': 'Logarithmic',
    'poly2': 'Quadratic Polynomial'
}
calibration_choices = []
calibration_keys_list = []
for item in CALIBRATION_CURVE_MASTER_DICT.items():
    calibration_choices.append(item)
    calibration_keys_list.append(item[0])
calibration_keys_list.pop(0)

# STRINGS FOR WHEN NONE OF THE ENTITY IN QUESTION
NO_COMPOUNDS_STRING = '-No Compounds-'
NO_CELLS_STRING = '-No Cells-'
NO_SETTINGS_STRING = '-No Extra Settings-'


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
    csv_reader = csv.reader(codecs.iterdecode(in_file, encoding), dialect=dialect, **kwargs)
    rows = []

    for row in csv_reader:
        rows.append([str(cell) for cell in row])

    return rows


# def modify_templates():
#     """Writes totally new templates based on the dropdowns"""
#     # Where will I store the templates?
#     template_root = MEDIA_ROOT + '/excel_templates/'

#     version = 1
#     version += len(os.listdir(template_root))
#     version = str(version)

#     chip = xlsxwriter.Workbook(template_root + 'chip_template-' + version + '.xlsx')

#     chip_sheet = chip.add_worksheet()

#     # Set up formats
#     chip_red = chip.add_format()
#     chip_red.set_bg_color('#ff6f69')
#     chip_green = chip.add_format()
#     chip_green.set_bg_color('#96ceb4')

#     # Write the base files
#     chip_initial = [
#         DEFAULT_CSV_HEADER,
#         [''] * 17
#     ]

#     chip_initial_format = [
#         [chip_red] * 17,
#         [
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             None,
#             chip_green,
#             None,
#             chip_green,
#             chip_green,
#             None,
#             chip_green,
#             None,
#             None,
#             None,
#             None
#         ]
#     ]

#     # Write out initial
#     for row_index, row in enumerate(chip_initial):
#         for column_index, column in enumerate(row):
#             cell_format = chip_initial_format[row_index][column_index]
#             chip_sheet.write(row_index, column_index, column, cell_format)

#     # Set column widths
#     # Chip
#     chip_sheet.set_column('A:A', 20)
#     chip_sheet.set_column('B:B', 20)
#     chip_sheet.set_column('C:C', 20)
#     chip_sheet.set_column('D:D', 15)
#     chip_sheet.set_column('E:E', 10)
#     chip_sheet.set_column('F:F', 10)
#     chip_sheet.set_column('G:G', 10)
#     chip_sheet.set_column('H:H', 20)
#     chip_sheet.set_column('I:I', 10)
#     chip_sheet.set_column('J:J', 20)
#     chip_sheet.set_column('K:K', 15)
#     chip_sheet.set_column('L:L', 10)
#     chip_sheet.set_column('M:M', 10)
#     chip_sheet.set_column('N:N', 10)
#     chip_sheet.set_column('O:O', 10)
#     chip_sheet.set_column('P:P', 10)
#     chip_sheet.set_column('Q:Q', 100)
#     # chip_sheet.set_column('I:I', 20)
#     # chip_sheet.set_column('J:J', 15)
#     # chip_sheet.set_column('K:K', 10)
#     # chip_sheet.set_column('L:L', 10)
#     # chip_sheet.set_column('M:M', 10)
#     # chip_sheet.set_column('N:N', 10)
#     # chip_sheet.set_column('O:O', 10)
#     # chip_sheet.set_column('P:P', 100)

#     chip_sheet.set_column('BA:BD', 30)

#     # Get list of value units  (TODO CHANGE ORDER_BY)
#     # value_units = PhysicalUnits.objects.filter(
#     #     availability__contains='readout'
#     # ).order_by(
#     #     'base_unit__unit',
#     #     'scale_factor'
#     # ).values_list('unit', flat=True)

#     # REMOVE RESTRICTION, SHOW ALL
#     value_units = PhysicalUnits.objects.order_by(
#         'base_unit__unit',
#         'scale_factor'
#     ).values_list('unit', flat=True)

#     # List of targets
#     targets = AssayTarget.objects.all().order_by(
#         'name'
#     ).values_list('name', flat=True)

#     # List of methods
#     methods = AssayMethod.objects.all().order_by(
#         'name'
#     ).values_list('name', flat=True)

#     # List of sample locations
#     sample_locations = AssaySampleLocation.objects.all().order_by(
#         'name'
#     ).values_list('name', flat=True)

#     for index, value in enumerate(sample_locations):
#         chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 3, value)

#     for index, value in enumerate(methods):
#         chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 2, value)

#     for index, value in enumerate(value_units):
#         chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX + 1, value)

#     for index, value in enumerate(targets):
#         chip_sheet.write(index, TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX, value)

#     value_units_range = '=$BB$1:$BB$' + str(len(value_units))

#     targets_range = '=$BA$1:$BA$' + str(len(targets))
#     methods_range = '=$BC$1:$BC$' + str(len(methods))
#     sample_locations_range = '=$BD$1:$BD$' + str(len(sample_locations))

#     chip_sheet.data_validation('H2', {'validate': 'list',
#                                       'source': targets_range})
#     chip_sheet.data_validation('J2', {'validate': 'list',
#                                'source': methods_range})
#     chip_sheet.data_validation('K2', {'validate': 'list',
#                                'source': sample_locations_range})
#     chip_sheet.data_validation('M2', {'validate': 'list',
#                                'source': value_units_range})

#     # Save
#     chip.close()


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
    collaborator_group_filter = {}
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
    collaborator_group_filter.update({
        'collaborator_groups__name__in': user_group_names,
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
    # 2: Study has Collaborator group matching user_group_names
    # 3: Study has Stakeholder group matching user_group_name AND is signed off on
    # 4: Study has access group matching user_group_names AND is signed off on AND all Stakeholders have signed off
    # 5: Study is unrestricted AND is signed off on AND all Stakeholders have signed off
    combined = queryset.filter(**data_group_filter) | \
               queryset.filter(**collaborator_group_filter) | \
               queryset.filter(**stakeholder_group_filter).exclude(**unsigned_off_filter) | \
               queryset.filter(**access_group_filter).exclude(**unsigned_off_filter).exclude(
                   **missing_stakeholder_filter) | \
               queryset.filter(**unrestricted_filter).exclude(**unsigned_off_filter).exclude(
                   **missing_stakeholder_filter)

    # May be overzealous to prefetch here
    combined = combined.distinct().prefetch_related(
        'created_by',
        'modified_by',
        'signed_off_by'
    )

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
    if type(value) == str or type(value) == str:
        return str(value)
    else:
        try:
            # If the value can be an integer, make it into one
            if int(value) == float(value):
                return str(int(value))
            else:
                return str(float(value))
        except:
            return str(value)


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
    def __init__(self, current_file, study, user, current_data_file_upload=None, save=False, full_path=''):
        self.current_file = current_file
        self.user = user
        self.full_path = full_path

        if save:
            if hasattr(current_file, 'url'):
                self.data_file_upload = AssayDataFileUpload(
                    file_location=current_file.url,
                    created_by=user,
                    modified_by=user,
                    study=study
                )
            else:
                self.data_file_upload = AssayDataFileUpload(
                    file_location=full_path,
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
        """Confirm that a row is 'valid'"""
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
                    # Uses name to deal with subtargets that don't exist yet
                    entry.subtarget.name,
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
                    # Uses name to deal with subtargets that don't exist yet
                    entry.subtarget.name,
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
            # if not self.valid_data_row(line, header_indices):
            #     continue

            if not any(line[:18]):
                continue

            matrix_item_name = line[header_indices.get('CHIP ID OR WELL ID')]

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

            value = line[header_indices.get('VALUE')].replace(',','')
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
                    str(sheet + 'The Sample Location "{0}" was not recognized.').format(sample_location_name)
                )
            else:
                sample_location_id = sample_location.id

            # TODO THE TRIMS HERE SHOULD BE BASED ON THE MODELS RATHER THAN MAGIC NUMBERS
            # Get notes, if possible
            notes = ''
            if header_indices.get('NOTES', '') and header_indices.get('NOTES') < len(line):
                notes = line[header_indices.get('NOTES')].strip()[:255]

            cross_reference = ''
            if header_indices.get('CROSS REFERENCE', '') and header_indices.get('CROSS REFERENCE') < len(line):
                cross_reference = line[header_indices.get('CROSS REFERENCE')].strip()[:255]

            # Excluded sees if ANYTHING is in EXCLUDE
            excluded = False
            if header_indices.get('EXCLUDE', '') and header_indices.get('EXCLUDE') < len(line):
                # PLEASE NOTE: Will only ever add 'X' now
                # quality = line[header_indices.get('QC STATUS')].strip()[:20]
                if line[header_indices.get('EXCLUDE')].strip():
                    excluded = True

            caution_flag = ''
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
                    str(
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
                    str(
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
            for time_unit, conversion in list(TIME_CONVERSIONS.items()):
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
                        subtarget.name,
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

            # CRUDE: MARK ALL CONFLICTING AS REPLACED
            # OBVIOUSLY BAD IDEA TO ITERATE LIKE THIS: VERY SLOW
            for conflicting_entry in conflicting_entries:
                conflicting_entry.replaced = True
                conflicting_entry.save()

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
            raise forms.ValidationError(
                'No valid sheets were detected in the file. Please check to make sure your headers are correct and start in the top-left corner.'
            )

    def process_csv_file(self):
        data_reader = unicode_csv_reader(self.current_file, delimiter=',')
        data_list = data_reader

        # Check if header is valid
        valid_header = self.get_and_validate_header(data_list)

        if valid_header:
            self.process_data(data_list)

        # IF NOT VALID, THROW ERROR
        else:
            raise forms.ValidationError('The file is not formatted correctly. Please check the header of the file.')

    def process_file(self):
        # Save the data upload if necessary (ostensibly save should only run after validation)
        if self.save:
            self.data_file_upload.save()

        self.current_file.seek(0, 0)
        if self.full_path:
            self.process_csv_file()
        else:
            try:
                self.process_excel_file()
            except xlrd.XLRDError:
                self.process_csv_file()


# TODO TODO TODO PLEASE REVISE STYLES WHEN POSSIBLE
# def ICC_A(X):
#    # This function is to calculate the ICC absolute agreement value for the input matrix
#    X = X.dropna()
#    icc_mat = X.values
#
#    Count_Row = icc_mat.shape[0]  # gives number of row count
#    Count_Col = icc_mat.shape[1]  # gives number of col count
#
#    # ICC row mean
#    icc_row_mean = icc_mat.mean(axis=1)
#
#    # ICC column mean
#    icc_col_mean = icc_mat.mean(axis=0)
#
#    # ICC total mean
#    icc_total_mean = icc_mat.mean()
#
#    # Sum of squre row and column means
#    SSC = sum((icc_col_mean - icc_total_mean) ** 2) * Count_Row
#
#    SSR = sum((icc_row_mean - icc_total_mean) ** 2) * Count_Col
#
#    # sum of squre errors
#    SSE = 0
#    for row in range(Count_Row):
#        for col in range(Count_Col):
#            SSE = SSE + (icc_mat[row, col] - icc_row_mean[row] - icc_col_mean[col] + icc_total_mean) ** 2
#
#    # SSW = SSE + SSC
#    MSR = SSR / (Count_Row - 1)
#    MSE = SSE / ((Count_Row - 1) * (Count_Col - 1))
#    MSC = SSC / (Count_Col - 1)
#    # MSW = SSW / (Count_Row*(Count_Col-1))
#    ICC_A = (MSR - MSE) / (MSR + (Count_Col - 1) * MSE + Count_Col * (MSC - MSE) / Count_Row)
#    return ICC_A

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
    icc_comp_value=pd.DataFrame(index=list(range(Count_Col)),columns=['Chip ID','ICC Absolute Agreement','Missing Data Points'])
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
    rep_index=pd.DataFrame(index=list(range(1)),columns=['Max CV','ICC Absolute Agreement'], dtype='float') #define the empty dataframe
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
    rep_index=pd.DataFrame(index=list(range(1)),columns=['CV','Mean','Standard Deviation','Median'], dtype='float')
    if rep_sd.iloc[0] > 0:
        rep_index.iloc[0][0]=X.std(axis=1,ddof=1)/X.mean(axis=1)*100

    rep_index.iloc[0][1]=rep_mean
    rep_index.iloc[0][2]=rep_sd
    rep_index.iloc[0][3]=rep_med
    rep_index=rep_index.round(2)
    return rep_index


def Reproducibility_Report(group_count, study_data):
    #Calculate and report the reproducibility index and status and other parameters
    #Select unique group rows by study, organ model,sample location, assay and unit
    #Drop null value rows
    study_data= study_data.dropna(subset=['Value'])
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)

    # OLD
    # study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit","Settings"]]
    # study_unique_group=study_group.drop_duplicates()
    # study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)
    chip_data = study_data.groupby(['Treatment Group', 'Chip ID', 'Time (day)', 'Study ID'], as_index=False)['Value'].mean()

    #create reproducibility report table
    header_list=chip_data.columns.values.tolist()
    header_list.append('Max CV')
    header_list.append('ICC Absolute Agreement')
    header_list.append('Reproducibility Status')
    header_list.append('Treatment Group')
    header_list.append('# of Chips/Wells')
    header_list.append('# of Time Points')
    header_list.append('Reproducibility Note')

    reproducibility_results_table = []

    for x in range(group_count+1):
        reproducibility_results_table.append(header_list)

    reproducibility_results_table = pd.DataFrame(columns=header_list)

    # Define all columns of reproducibility report table
    # Loop every unique replicate group
    # group_count=len(study_unique_group.index)
    for row in range(group_count):
        # rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
        # rep_matrix=rep_matrix[rep_matrix['Settings']==study_unique_group['Settings'][row]]
        # create replicate matrix for intra reproducibility analysis
        rep_matrix = chip_data[chip_data['Treatment Group'] == str(row + 1)]
        icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time (day)',columns=['Chip ID'], aggfunc=np.mean)

        group_id = str(row+1) #Define group ID

        group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
        reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix, ignore_index=True)

        reproducibility_results_table.iloc[row, reproducibility_results_table.columns.get_loc('Treatment Group')] = group_id
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

# ?
# Used anywhere...?
def study_group_setting(study_unique_group,row):
    group_setting=pd.DataFrame(index=list(range(study_unique_group.shape[1])),columns=['Replicate Set Parameters','Setting'])
    for i in range(study_unique_group.shape[1]):
        group_setting.iloc[i][0]=study_unique_group.columns.tolist()[i]

    for i in range(study_unique_group.shape[1]):
        group_setting.iloc[i][1]=study_unique_group.iloc[row][i]
    return group_setting


def pivot_data_matrix(study_data,group_index):
    rep_matrix = study_data[study_data['Treatment Group']==group_index]
    # #Drop null value rows
    # study_data= study_data.dropna(subset=['Value'])
    # #Define the Chip ID column to string type
    # study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)
    # row=group_index
    # study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit","Settings"]]
    # study_unique_group=study_group.drop_duplicates()
    # study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)
    # rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Settings']==study_unique_group['Settings'][row]]
    #create replicate matrix for intra reproducibility analysis
    icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time (day)',columns=['Chip ID'], aggfunc=np.mean)
    return icc_pivot


def scatter_plot_matrix(study_data,group_index):
    rep_matrix = study_data[study_data['Treatment Group']==group_index]
    # #Drop null value rows
    # study_data= study_data.dropna(subset=['Value'])
    # #Define the Chip ID column to string type
    # study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)
    # row=group_index
    # study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit","Settings"]]
    # study_unique_group=study_group.drop_duplicates()
    # study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)
    # rep_matrix=study_data[study_data['Organ Model']==study_unique_group['Organ Model'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Cells']==study_unique_group['Cells'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Compound Treatment(s)']==study_unique_group['Compound Treatment(s)'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Target/Analyte']==study_unique_group['Target/Analyte'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Method/Kit']==study_unique_group['Method/Kit'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Sample Location']==study_unique_group['Sample Location'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Value Unit']==study_unique_group['Value Unit'][row]]
    # rep_matrix=rep_matrix[rep_matrix['Settings']==study_unique_group['Settings'][row]]
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


def get_repro_data(group_count, data):
    #Load the summary data into the dataframe
    study_data = pd.DataFrame(data)
    study_data.columns = study_data.iloc[0]
    study_data = study_data.drop(study_data.index[0])
    #Drop null value rows
    study_data['Value'].replace('', np.nan, inplace=True)
    study_data= study_data.dropna(subset=['Value'])
    study_data['Value'] = study_data['Value'].astype(float)
    #Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data['Chip ID'].astype(str)

    #Add Time (day) calculated from three time column
    study_data["Time (day)"] = study_data['Time']/1440.0
    study_data["Time (day)"] = study_data["Time (day)"].apply(lambda x: round(x,2))

    # #Select unique group rows by study, organ model,sample location, assay and unit
    # study_group=study_data[["Organ Model","Cells","Compound Treatment(s)","Target/Analyte","Method/Kit","Sample Location","Value Unit","Settings"]]
    # study_unique_group=study_group.drop_duplicates()
    # study_unique_group.set_index([range(study_unique_group.shape[0])],drop=True, append=False, inplace=True)

    #create reproducibility report table
    reproducibility_results_table=Reproducibility_Report(group_count, study_data)

    datadict = {}

    #Define all columns of reproducibility report table
    reproducibility_results_table_nanless = reproducibility_results_table.fillna('')
    datadict['reproducibility_results_table'] = reproducibility_results_table_nanless.to_dict('split')

    #Loop every unique replicate group
    # group_count=len(study_unique_group.index)

    for row in range(group_count):
        datadict[row] = {}

        group_id = str(row+1) #Define group ID

        icc_pivot = pivot_data_matrix(study_data, group_id)

        #Call MAD score function
        mad_score_matrix=MAD_score(icc_pivot)#.round(2)
        datadict[row]['mad_score_matrix'] = mad_score_matrix.to_dict('split')

        cv_chart=scatter_plot_matrix(study_data,group_id).fillna('')
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
        # group_index=study_group_setting(study_data,group_id)

    return datadict


def consecutive_one_new(data):
    longest = 0
    current = 0
    start_row = 0
    long_start_row = 0
    row = 0
    for num in data:
        row = row + 1
        if num == 1:
            current += 1
            if current == 1:
                start_row = row
        else:
            longest = max(longest, current)
            current = 0

        if current > longest:
            long_start_row = start_row

    return max(longest, current), long_start_row


def Single_Time_ANOVA(st_anova_data, inter_level):
    a_data = st_anova_data
    if inter_level == 1:
        samples = [condition[1] for condition in a_data.groupby('MPS User Group')['Value']]
    else:
        samples = [condition[1] for condition in a_data.groupby('Study ID')['Value']]

    f_val, p_val = stats.f_oneway(*samples)
    return p_val


def ICC_A(X):
    # This function is to calculate the ICC absolute agreement value for the input matrix
    X = X.dropna()
    icc_mat = X.values

    Count_Row = icc_mat.shape[0]  # gives number of row count
    Count_Col = icc_mat.shape[1]  # gives number of col count
    if Count_Row < 2:
        ICC_A = np.nan
    elif Count_Col < 2:
        ICC_A = np.nan
    else:
        # ICC row mean
        icc_row_mean = icc_mat.mean(axis=1)

        # ICC column mean
        icc_col_mean = icc_mat.mean(axis=0)

        # ICC total mean
        icc_total_mean = icc_mat.mean()

        # Sum of squre row and column means
        SSC = sum((icc_col_mean - icc_total_mean) ** 2) * Count_Row

        SSR = sum((icc_row_mean - icc_total_mean) ** 2) * Count_Col

        # sum of squre errors
        SSE = 0
        for row in range(Count_Row):
            for col in range(Count_Col):
                SSE = SSE + (icc_mat[row, col] - icc_row_mean[row] - icc_col_mean[col] + icc_total_mean) ** 2

        # SSW = SSE + SSC
        MSR = SSR / (Count_Row - 1)
        MSE = SSE / ((Count_Row - 1) * (Count_Col - 1))
        MSC = SSC / (Count_Col - 1)
        # MSW = SSW / (Count_Row*(Count_Col-1))
        ICC_A = (MSR - MSE) / (MSR + (Count_Col - 1) * MSE + Count_Col * (MSC - MSE) / Count_Row)
    return ICC_A


def Inter_Max_CV(X):
    # This function is to estimate the maximum CV of cross centers or studies' measurements through time (row)
    Y = X.dropna()
    icc_mat = Y.values
    a_count = Y.shape[0]
    CV_Array = pd.DataFrame(index=Y.index, columns=['CV (%)'])
    for row in range(a_count):
        if np.std(icc_mat[row, :]) > 0:
            CV_Array.iloc[row][0] = np.std(icc_mat[row, :], ddof=1) / np.mean(icc_mat[row, :]) * 100.0
        else:
            CV_Array.iloc[row][0] = 0
    # Calculate Max CV
    Max_CV = CV_Array.max(axis=0)
    return Max_CV


def Inter_Reproducibility_Index(X):
    # This function is to calculate the Max CV and ICC absolute agreement data table

    Y = X.dropna()
    Max_CV_value = Inter_Max_CV(Y)  # Call Max CV function
    if Y.shape[0] > 1 and Y.shape[1] > 1:
        ICC_Value = ICC_A(Y)  # Call ICC function
    else:
        ICC_Value = np.nan
    # Create a reproducibility index dataframe
    rep_index = pd.DataFrame(index=list(range(1)), columns=['Max CV', 'ICC Absolute Agreement'],
                             dtype='float')  # define the empty dataframe
    rep_index.iloc[0][0] = Max_CV_value
    rep_index.iloc[0][1] = ICC_Value
    # rep_index = rep_index.round(2)
    return rep_index


def fill_nan(A, interp_method):
    '''
    interpolate to fill nan values
    '''
    try:
        inds = np.arange(A.shape[0])
        good = np.where(np.isfinite(A))
        if interp_method == 'cubic':
            cs = CubicSpline(inds[good], A[good], extrapolate=False)
            B = np.where(np.isfinite(A), A, cs(inds))
            fill_status = True
        else:
            f = sp.interp1d(inds[good], A[good], kind=interp_method, bounds_error=False)
            B = np.where(np.isfinite(A), A, f(inds))
            fill_status = True
    except ValueError:
        B = A
        fill_status = False
    return B, fill_status


def update_missing_nan(update_missing_block, A):
    s_row = update_missing_block.iloc[0, 1] - 1
    e_row = update_missing_block.iloc[0, 1] + update_missing_block.iloc[0, 0] - 1
    for i in range(s_row, e_row):
        A[i] = 0
    return A


def search_nan_blocks(df_s):
    total_rows = len(df_s)
    missing_list = []
    for i in range(total_rows):
        if np.isnan(df_s.iloc[i]):
            missing_list.append(1)
        else:
            missing_list.append(0)

    nan_blocks_df = pd.DataFrame(columns=['nan block size', 'block_start_row', 'Out NaN'])
    block_df = pd.DataFrame(index=[1], columns=['nan block size', 'block_start_row', 'Out NaN'])

    [max_missing_len, max_missing_len_start_row] = consecutive_one_new(missing_list)
    while True:
        if max_missing_len > 0:
            block_df.iloc[0, 0] = max_missing_len
            block_df.iloc[0, 1] = max_missing_len_start_row
            if max_missing_len_start_row == 1 or max_missing_len_start_row + max_missing_len - 1 == total_rows:
                block_df.iloc[0, 2] = True
            else:
                block_df.iloc[0, 2] = False
            nan_blocks_df = nan_blocks_df.append(block_df, ignore_index=True)
            missing_list = update_missing_nan(block_df, missing_list)
            [max_missing_len, max_missing_len_start_row] = consecutive_one_new(missing_list)
        else:
            break
    return nan_blocks_df


def max_in_nan_size_array(df_s):
    nan_blocks = search_nan_blocks(df_s)
    in_nan_blocks = nan_blocks[nan_blocks['Out NaN'] == False]
    if len(in_nan_blocks.index) > 0:
        max_nan_size_array = max(in_nan_blocks.iloc[:, 0])
    else:
        max_nan_size_array = 0
    return max_nan_size_array


def max_in_nan_size_matrix(pivot_group_matrix):
    no_cols = pivot_group_matrix.shape[1]
    max_in_nan_matrix = 0
    for col in range(no_cols):
        curr_size = max_in_nan_size_array(pivot_group_matrix.iloc[:, col])
        if curr_size > max_in_nan_matrix:
            max_in_nan_matrix = curr_size
    return max_in_nan_matrix


def matrix_interpolate(group_chip_data, interp_method, inter_level):
    if inter_level == 1:
        interp_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time', columns=['MPS User Group'],
                                             aggfunc=np.mean)
    else:
        interp_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time', columns=['Study ID'],
                                             aggfunc=np.mean)

    fill_header_list = interp_group_matrix.columns.values.tolist()
    for col in range(interp_group_matrix.shape[1]):
        df_arr = interp_group_matrix.values[:, col]
        df_s = interp_group_matrix.iloc[:, col]
        if max_in_nan_size_array(df_s) > 0:
            [interp_group_matrix[fill_header_list[col]], fill_status] = fill_nan(df_arr, interp_method)
    return interp_group_matrix


def update_group_reproducibility_index_status(group_rep_matrix, rep_index):
    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('ICC Absolute Agreement')] = rep_index.iloc[0, 1]
    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Max CV')] = rep_index.iloc[0, 0]

    if group_rep_matrix.iloc[0, 4] == 0:
        group_rep_matrix.iloc[
            0, group_rep_matrix.columns.get_loc('Reproducibility Note')] = 'No overlaped time for comparing'
    else:
        if pd.isnull(rep_index.iloc[0, 1]) == True:
            if rep_index.iloc[0, 0] <= 5:
                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
            elif rep_index.iloc[0, 0] > 5 and rep_index.iloc[0, 0] <= 15:
                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
            elif rep_index.iloc[0, 0] > 15:
                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Poor (CV)'
            else:
                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = np.nan
        else:
            if rep_index.iloc[0][0] <= 15 and rep_index.iloc[0][0] > 0:
                if rep_index.iloc[0][0] <= 5:
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
                elif rep_index.iloc[0][1] >= 0.8:
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (ICC)'
                else:
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
            else:
                if rep_index.iloc[0][1] >= 0.8:
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (ICC)'
                elif rep_index.iloc[0][1] >= 0.2:
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Acceptable (ICC)'
                elif rep_index.iloc[0][1] < 0.2:
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Poor (ICC)'
                else:
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = np.nan
    return group_rep_matrix


def interpolate_group_rep_index(header_list, group_chip_data, interp_method, inter_level, max_interpolation_size,
                                group_id, initial_Norm=0):
    if inter_level == 1:
        interp_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time', columns=['MPS User Group'],
                                             aggfunc=np.mean)
    else:
        interp_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time', columns=['Study ID'],
                                             aggfunc=np.mean)

    origin_isnull = interp_group_matrix.isnull()
    origin_isnull_col = pivot_transpose_to_column(origin_isnull, inter_level)
    interp_mat = matrix_interpolate(group_chip_data, interp_method, inter_level)  # interpolate

    # Update maximum interpolation size
    if max_in_nan_size_matrix(interp_group_matrix) > max_interpolation_size:
        for col in range(interp_group_matrix.shape[1]):
            df_s = interp_group_matrix.iloc[:, col]
            if max_in_nan_size_array(df_s) > max_interpolation_size:
                nan_blocks = search_nan_blocks(df_s)
                for b_row in range(nan_blocks.shape[0]):
                    if nan_blocks.iloc[b_row, 0] > max_interpolation_size and nan_blocks.iloc[b_row, 2] == False:
                        for i in range(nan_blocks.iloc[b_row, 1] - 1,
                                       nan_blocks.iloc[b_row, 1] - 1 + nan_blocks.iloc[b_row, 0]):
                            interp_mat.iloc[i, col] = np.nan

    if initial_Norm == 1:
        # Normalize each center data by the median value
        norm_pivot_group_matrix = interp_mat
        for norm_col in range(interp_mat.shape[1]):
            med_value = interp_mat.iloc[:, norm_col].dropna().median()

            for norm_row in range(interp_mat.shape[0]):
                if pd.isnull(interp_mat.iloc[norm_row, norm_col]) == False and med_value > 0:
                    norm_pivot_group_matrix.iloc[norm_row, norm_col] = interp_mat.iloc[
                                                                           norm_row, norm_col] / med_value
        interp_mat = norm_pivot_group_matrix

        # Build inter data set
    inter_data_set = pivot_transpose_to_column(interp_mat.dropna(), inter_level)
    inter_data_set['Value Source'] = 'Original'
    inter_data_set['Data Set'] = interp_method
    inter_data_set['Treatment Group'] = group_id

    for set_row in range(inter_data_set.shape[0]):
        time_value = inter_data_set.iloc[set_row, 0]
        inter_value = inter_data_set.iloc[set_row, 1]
        if inter_level == 1:
            null_state = origin_isnull_col[
                (origin_isnull_col['Time'] == time_value) & (origin_isnull_col['MPS User Group'] == inter_value)].iloc[
                0, 2]
        else:
            null_state = origin_isnull_col[
                (origin_isnull_col['Time'] == time_value) & (origin_isnull_col['Study ID'] == inter_value)].iloc[0, 2]

        if null_state == True:
            inter_data_set.iloc[set_row, inter_data_set.columns.get_loc('Value Source')] = 'Interpolated'

    icc_data = interp_mat.dropna()
    group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
    group_rep_matrix.iloc[0, 3] = icc_data.shape[1]
    group_rep_matrix.iloc[0, 4] = icc_data.shape[0]
    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Interpolation Method')] = interp_method.title()
    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Max Interpolation Size')] = max_interpolation_size
    rep_index = Inter_Reproducibility_Index(icc_data)
    group_rep_matrix = update_group_reproducibility_index_status(group_rep_matrix, rep_index)

    return group_rep_matrix, inter_data_set


def pivot_transpose_to_column(pivot_data, inter_level):
    row_count = pivot_data.shape[0]
    col_count = pivot_data.shape[1]
    if inter_level == 1:
        col_name = ['Time', 'MPS User Group', 'Value']
    else:
        col_name = ['Time', 'Study ID', 'Value']
    df_one = pd.DataFrame(index=[0], columns=col_name)
    column_data = pd.DataFrame(columns=col_name)
    for row in range(row_count):
        for col in range(col_count):
            df_one.iloc[0, 0] = pivot_data.index[row]
            df_one.iloc[0, 1] = pivot_data.columns.values[col]
            df_one.iloc[0, 2] = pivot_data.iloc[row, col]
            column_data = column_data.append(df_one, ignore_index=True)
    return column_data


def Inter_reproducibility(group_count, inter_data_df, inter_level=1, max_interpolation_size=2, initial_Norm=0):
    # Evaluate inter-center/study reproducibility

    inter_data_df[['Chip ID']] = inter_data_df[['Chip ID']].astype(str)
    inter_data_df[['Study ID']] = inter_data_df[['Study ID']].astype(str)

    # Calculate the average value group by chip level
    chip_data = inter_data_df.groupby(['Treatment Group', 'Chip ID', 'Time', 'Study ID', 'MPS User Group'], as_index=False)['Value'].mean()

    # create reproducibility report table
    # reproducibility_results_table=group_df
    # header_list=group_df.columns.values.tolist()
    inter_data_header_list = []
    inter_data_header_list.append('Time')
    if inter_level == 1:
        inter_data_header_list.append('MPS User Group')
    else:
        inter_data_header_list.append('Study ID')
    inter_data_header_list.append('Value')
    inter_data_header_list.append('Value Source')
    inter_data_header_list.append('Data Set')
    inter_data_header_list.append('Treatment Group')
    inter_data_table = pd.DataFrame(columns=inter_data_header_list)

    header_list = []
    header_list.append('Treatment Group')
    header_list.append('Interpolation Method')
    header_list.append('Max Interpolation Size')
    if inter_level == 1:
        header_list.append('# of Centers')
        header_list.append('# of Overlaped Cross-Center Time Points')
    else:
        header_list.append('# of Studies')
        header_list.append('# of Overlaped Cross-Study Time Points')
    header_list.append('Max CV')
    header_list.append('ICC Absolute Agreement')
    header_list.append('ANOVA P-Value')
    header_list.append('Reproducibility Status')
    header_list.append('Reproducibility Note')

    # Define all columns of reproducibility report table
    reproducibility_results_table = pd.DataFrame(columns=header_list)

    # Define all columns of original and
    # Loop every unique replicate group
    for row in range(group_count):
        group_id = str(row + 1)
        # group_chip_data = chip_data[chip_data['Treatment Group'] == 'Group ' + str(row + 1)]
        group_chip_data = chip_data[chip_data['Treatment Group'] == str(row + 1)]

        if group_chip_data.shape[0] < 1:
            group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
            group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
            group_rep_matrix.iloc[0, 3] = np.nan
            group_rep_matrix.iloc[
                0, group_rep_matrix.columns.get_loc('Reproducibility Note')] = 'No data for this group'
            reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix, ignore_index=True)
        else:
            if inter_level == 1:
                pivot_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time',
                                                    columns=['MPS User Group'], aggfunc=np.mean)
            else:
                pivot_group_matrix = pd.pivot_table(group_chip_data, values='Value', index='Time', columns=['Study ID'],
                                                    aggfunc=np.mean)

            if pivot_group_matrix.shape[1] < 2:

                group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                # group_rep_matrix.iloc[0, 3] = np.nan
                group_rep_matrix.iloc[0, 3] = pivot_group_matrix.shape[1]
                group_rep_matrix.iloc[
                    0, group_rep_matrix.columns.get_loc('Reproducibility Note')] = 'Fewer than two centers/studies'
                reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                     ignore_index=True)
            else:
                if initial_Norm == 1 and pivot_group_matrix.shape[0] > 0:
                    # Normalize each center data by the median value
                    norm_pivot_group_matrix = pivot_group_matrix
                    for norm_col in range(pivot_group_matrix.shape[1]):
                        med_value = pivot_group_matrix.iloc[:, norm_col].dropna().median()

                        for norm_row in range(pivot_group_matrix.shape[0]):
                            if pd.isnull(pivot_group_matrix.iloc[norm_row, norm_col]) == False and med_value > 0:
                                norm_pivot_group_matrix.iloc[norm_row, norm_col] = pivot_group_matrix.iloc[
                                                                                       norm_row, norm_col] / med_value
                    pivot_group_matrix = norm_pivot_group_matrix

                # Trim nan data points
                no_nan_matrix = pivot_group_matrix.dropna()

                # Add trimmed data to the inter data table when there are overlaped time points existing
                if no_nan_matrix.shape[0] > 0:
                    inter_data_set = pivot_transpose_to_column(no_nan_matrix, inter_level)
                    inter_data_set['Value Source'] = 'Original'
                    inter_data_set['Data Set'] = 'trimmed'
                    inter_data_set['Treatment Group'] = group_id
                    inter_data_table = inter_data_table.append(inter_data_set, ignore_index=True)

                if no_nan_matrix.shape[1] < 2:
                    group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                    group_rep_matrix.iloc[0, 3] = no_nan_matrix.shape[1]
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Reproducibility Note')] = 'Fewer than two centers/studies'
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                elif no_nan_matrix.shape[0] < 1:
                    group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                    group_rep_matrix.iloc[0, 3] = no_nan_matrix.shape[1]
                    group_rep_matrix.iloc[0, 4] = 0
                    group_rep_matrix.iloc[
                        0, group_rep_matrix.columns.get_loc('Reproducibility Note')] = 'No overlaped time for comparing'

                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                elif no_nan_matrix.shape[0] == 1 and no_nan_matrix.shape[1] >= 2:
                    if initial_Norm == 1:
                        single_time = no_nan_matrix.index[0]
                        group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                        group_rep_matrix.iloc[0, 3] = no_nan_matrix.shape[1]
                        group_rep_matrix.iloc[0, 4] = no_nan_matrix.shape[0]
                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('ANOVA P-Value')] = np.nan
                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Max CV')] = np.nan
                        group_rep_matrix.iloc[
                            0, group_rep_matrix.columns.get_loc('Reproducibility Note')
                        ] = 'Normalized by median is not applicable to single time point'
                    else:
                        single_time = no_nan_matrix.index[0]
                        group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                        group_rep_matrix.iloc[0, 3] = no_nan_matrix.shape[1]
                        group_rep_matrix.iloc[0, 4] = no_nan_matrix.shape[0]
                        anova_data = group_chip_data[group_chip_data['Time'] == single_time]

                        p_value = Single_Time_ANOVA(anova_data, inter_level)

                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('ANOVA P-Value')] = '{0:.4g}'.format(p_value)

                        # Calcualate CV
                        single_array = no_nan_matrix.dropna()
                        single_array_val = single_array.values
                        single_CV = np.std(single_array_val, ddof=1) / np.mean(single_array_val) * 100

                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Max CV')] = '{0:.4g}'.format(single_CV)

                        if p_value >= 0.05:
                            if single_CV <= 5:
                                group_rep_matrix.iloc[
                                    0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
                            elif single_CV > 5 and single_CV <= 15:
                                group_rep_matrix.iloc[
                                    0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
                            else:
                                group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc(
                                    'Reproducibility Status')] = 'Acceptable (P-Value)'
                        elif p_value < 0.05:
                            group_rep_matrix.iloc[
                                0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Poor (P-Value)'
                        else:
                            if single_CV <= 5:
                                group_rep_matrix.iloc[
                                    0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
                            elif single_CV > 5 and single_CV <= 15:
                                group_rep_matrix.iloc[
                                    0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
                            else:
                                group_rep_matrix.iloc[
                                    0, group_rep_matrix.columns.get_loc('Reproducibility Status')] = 'Poor (CV)'

                        group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc(
                            'Reproducibility Note')] = 'Single overlaped time for comparing'
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                elif no_nan_matrix.shape[0] > 1 and no_nan_matrix.shape[1] >= 2:
                    group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Treatment Group')] = group_id
                    group_rep_matrix.iloc[0, 3] = no_nan_matrix.shape[1]
                    group_rep_matrix.iloc[0, 4] = no_nan_matrix.shape[0]
                    icc_data = no_nan_matrix

                    rep_index = Inter_Reproducibility_Index(icc_data)
                    group_rep_matrix = update_group_reproducibility_index_status(group_rep_matrix, rep_index)
                    group_rep_matrix.iloc[0, group_rep_matrix.columns.get_loc('Interpolation Method')] = 'Trimmed'
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)

                    # Interpolation Analysis
                if pivot_group_matrix.shape[0] > 2 and pivot_group_matrix.shape[1] > 1 and max_in_nan_size_matrix(
                        pivot_group_matrix) > 0:
                    # nearest interpolation
                    [group_rep_matrix, inter_data_set] = interpolate_group_rep_index(header_list, group_chip_data,
                                                                                     'nearest', inter_level,
                                                                                     max_interpolation_size, group_id,
                                                                                     initial_Norm)
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                    inter_data_table = inter_data_table.append(inter_data_set, ignore_index=True)

                    # linear interpolation
                    [group_rep_matrix, inter_data_set] = interpolate_group_rep_index(header_list, group_chip_data,
                                                                                     'linear', inter_level,
                                                                                     max_interpolation_size, group_id,
                                                                                     initial_Norm)
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                    inter_data_table = inter_data_table.append(inter_data_set, ignore_index=True)

                    # quadratic interpolation
                    [group_rep_matrix, inter_data_set] = interpolate_group_rep_index(header_list, group_chip_data,
                                                                                     'quadratic', inter_level,
                                                                                     max_interpolation_size, group_id,
                                                                                     initial_Norm)
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                    inter_data_table = inter_data_table.append(inter_data_set, ignore_index=True)

                    # cubic interpolation
                    [group_rep_matrix, inter_data_set] = interpolate_group_rep_index(header_list, group_chip_data,
                                                                                     'cubic', inter_level,
                                                                                     max_interpolation_size, group_id,
                                                                                     initial_Norm)
                    reproducibility_results_table = reproducibility_results_table.append(group_rep_matrix,
                                                                                         ignore_index=True)
                    inter_data_table = inter_data_table.append(inter_data_set, ignore_index=True)

    return reproducibility_results_table, inter_data_table


def get_inter_study_reproducibility_report(group_count, inter_data, inter_level, max_interpolation_size, initial_norm):
    """
    @author: Tongying Shun (tos8@pitt.edu)
    """
    # Error if only headers present
    if len(inter_data) < 2:
        return [{}, {
            'errors': 'No data. Please review filter options.'
        }]

    # load inter data
    inter_head = inter_data.pop(0)
    inter_data_df = pd.DataFrame(inter_data)
    inter_data_df.columns = inter_head

    # Counter centers or studies
    if inter_level == 1:
        center_group = inter_data_df[["MPS User Group"]]
        center_unique_group = center_group.drop_duplicates()
        if len(center_unique_group.axes[0]) < 2:
            return [{}, {
                'errors': 'Only one MPS User Group! The cross-center reproducibility cannot be analyzed.'
                          '\nPlease try selecting the "By Study" option and clicking "Refresh."'
            }]
    else:
        study_group = inter_data_df[["Study ID"]]
        study_unique_group = study_group.drop_duplicates()
        if len(study_unique_group.axes[0]) < 2:
            return [{}, {
                'errors': 'Only one Study! The cross-study reproducibility cannot be analyzed.'
            }]

    # Return the summary and datatable
    return Inter_reproducibility(
        group_count,
        inter_data_df,
        inter_level,
        max_interpolation_size,
        initial_norm
    )

def intra_status_for_inter(study_data):
    # Calculate and report the reproducibility index and status and other parameters
    # Select unique group rows by study, organ model,sample location, assay and unit
    # Drop null value rows
    study_data = pd.DataFrame(study_data)
    study_data.columns = ["Time", "Value", "Chip ID"]
    study_data = study_data.dropna(subset=['Value'])
    # Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)

    # create reproducibility report table
    reproducibility_results_table=study_data
    header_list = study_data.columns.values.tolist()
    header_list.append('Reproducibility Status')

    # Define all columns of reproducibility report table
    reproducibility_results_table = reproducibility_results_table.reindex(columns = header_list)

    # Define all columns of reproducibility report table
    reproducibility_results_table = reproducibility_results_table.reindex(columns = header_list)
    # create replicate matrix for intra reproducibility analysis
    icc_pivot = pd.pivot_table(study_data, values='Value', index='Time', columns=['Chip ID'], aggfunc=np.mean)
    # Check all coulmns are redundent
    if icc_pivot.shape[1]>1 and all(icc_pivot.eq(icc_pivot.iloc[:, 0], axis=0).all(1)):
        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'
    elif icc_pivot.shape[0]>1 and all(icc_pivot.eq(icc_pivot.iloc[0, :], axis=1).all(1)):
        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'
    else:
        if icc_pivot.shape[0]>1 and icc_pivot.shape[1]>1:
            # Call a chip time series reproducibility index dataframe
            rep_index=Reproducibility_Index(icc_pivot)
            if pd.isnull(rep_index.iloc[0][0]) != True:
                if rep_index.iloc[0][0] <= 15 and rep_index.iloc[0][0] >0:
                    if rep_index.iloc[0][0] <= 5:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
                    elif rep_index.iloc[0][1] >= 0.8:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Excellent (ICC)'
                    else:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
                else:
                    if rep_index.iloc[0][1] >= 0.8:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Excellent (ICC)'
                    elif rep_index.iloc[0][1] >= 0.2:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Acceptable (ICC)'
                    else:
                        reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Poor (ICC)'
            else:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'
        elif icc_pivot.shape[0]<2 and icc_pivot.shape[1] > 1:
             # Call a single time reproducibility index dataframe
            rep_index=Single_Time_Reproducibility_Index(icc_pivot)
            if rep_index.iloc[0][0] <= 5 and rep_index.iloc[0][0] > 0:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Excellent (CV)'
            elif rep_index.iloc[0][0] <= 15 and rep_index.iloc[0][0] > 5:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Acceptable (CV)'
            elif rep_index.iloc[0][0] > 15:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'Poor (CV)'
            elif rep_index.iloc[0][0] < 0:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'
            else:
                reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'
        else:
            reproducibility_results_table.iloc[0, reproducibility_results_table.columns.get_loc('Reproducibility Status')] = 'NA'

    return reproducibility_results_table.loc[reproducibility_results_table.index[0], 'Reproducibility Status']


# Power Analysis
def pa_effect_size(x, y, type='d'):
    md = np.abs(np.mean(x) - np.mean(y))
    nx = len(x)
    ny = len(y)

    if type == 'gs':
        m = nx + ny - 2
        cm = gamma(m / 2) / (np.sqrt(m / 2) * gamma((m - 1) / 2))
        spsq = ((nx - 1) * np.var(x, ddof=1) +
                (ny - 1) * np.var(y, ddof=1)) / m
        theta = cm * md / np.sqrt(spsq)
    elif type == 'g':
        spsq = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) *
                np.var(y, ddof=1)) / (nx + ny - 2)
        theta = md / np.sqrt(spsq)
    elif type == 'd':
        spsq = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) *
                np.var(y, ddof=1)) / (nx + ny)
        theta = md / np.sqrt(spsq)
    else:
        theta = md / np.std(x, ddof=1)
    return theta


def pa_predicted_sample_size(power, es_value, sig_level=0.05):
    if power > 0 and power < 1 and abs(es_value) > 0:
        analysis = TTestIndPower()
        try:
            result = analysis.solve_power(effect_size=es_value, power=power, nobs1=None, ratio=1.0, alpha=sig_level)
            if np.isscalar(result):
                sample_size = result
            else:
                sample_size = np.NAN
        except:
            sample_size = np.NAN
    else:
        sample_size = np.NAN
    return sample_size


def pa_predicted_power(sample_size, es_value, sig_level=0.05):
    if sig_level > 0 and sig_level < 1 and abs(es_value) > 0:
        analysis = TTestIndPower()
        try:
            result = analysis.solve_power(effect_size=es_value, power=None, nobs1=sample_size, ratio=1.0, alpha=sig_level)
            power_value = result
        except:
            power_value = np.NAN
    else:
        power_value = np.NAN
    return power_value


def pa_predicted_significance_level(sample_size, es_value, power=0.8):
    if power > 0 and power < 1 and abs(es_value) > 0:
        analysis = TTestIndPower()
        try:
            result = analysis.solve_power(effect_size=es_value, power=power, nobs1=sample_size, ratio=1.0, alpha=None)
            sig_level = result
        except:
            sig_level = np.NAN
    else:
        sig_level = np.NAN
    return sig_level


def pa_power_one_sample_size(n, es_value, sig_level=0.05):
    if n > 1 and abs(es_value) > 0:
        analysis = TTestIndPower()
        try:
            result = analysis.solve_power(effect_size=es_value, power=None, nobs1=n, ratio=1.0, alpha=sig_level)
            power_value = result
        except:
            power_value = np.NAN
    else:
        power_value = np.NAN
    return power_value


def pa_power_two_sample_size(n1, n2, es_value, sig_level=0.05):
    if n1 > 1 and n2 > 1 and n1 != n2:
        analysis = TTestIndPower()
        try:
            ratio = n2 / n1
            result = analysis.solve_power(effect_size=es_value, power=None, nobs1=n1, ratio=ratio, alpha=sig_level)
            power_value = result
        except:
            power_value = np.NAN
    elif n1 == n2 and n1 > 1:
        power_value = pa_Power_One_Sample_Size(n1, es_value)
    else:
        power_value = np.NAN
    return power_value


def pa_t_test(x, y):
    try:
        result = ttest_ind(x, y, equal_var=False)
        p_value = result[1]
    except:
        p_value = np.NAN
    return p_value


def pa_predicted_sample_size_time_series(power_group_data, type='d', power=0.8, sig_level=0.05):
    # Predict the sample size for two treatments' time series given power and significance level

    power_group_data = power_group_data.dropna(subset=['Value'])
    # Confirm whether there are two treatments
    study_group = power_group_data[["Compound Treatment(s)"]]
    study_unique_group = study_group.drop_duplicates()
    if study_unique_group.shape[0] != 2:
        # only two treatments can be selected"
        power_analysis_table = np.NAN
    else:
        # Power analysis results
        power_analysis_table_key = power_group_data[["Group", "Time"]]
        power_analysis_table = power_analysis_table_key.drop_duplicates()
        # create power analysis report table
        header_list = power_analysis_table.columns.values.tolist()
        header_list.append('Power')
        header_list.append('Sample Size')
        header_list.append('Significance Level')

        # Define all columns of power analysis report table
        power_analysis_table = power_analysis_table.reindex(
            columns=header_list)
        # Loop every unique replicate group
        time_count = len(power_analysis_table)
        power_analysis_table.index = pd.RangeIndex(len(power_analysis_table.index))

        if study_unique_group.shape[0] != 2:
            err_msg = "two treatments have to be selected"
            print(err_msg)
        else:
            chip_data = power_group_data.groupby(
                ['Compound Treatment(s)', 'Chip ID', 'Time'], as_index=False)['Value'].mean()
            cltr_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[0, 0]]
            treat_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[1, 0]]
            for itime in range(time_count):
                if itime not in power_analysis_table['Time']:
                    continue
                x = cltr_data[cltr_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                y = treat_data[treat_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                # effect size for power analysis calculation
                es_value = pa_effect_size(x, y, type)
                # Predict sample size
                predict_sample_size = pa_predicted_sample_size(
                    power, es_value, sig_level)

                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Power')
                ] = power
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Sample Size')
                ] = predict_sample_size
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Significance Level')
                ] = sig_level

    return power_analysis_table


def pa_predicted_significance_level_time_series(power_group_data, type='d', sample_size=3, power=0.8):
    # Predict the sample size for two treatments' time series given power and significance level

    power_group_data = power_group_data.dropna(subset=['Value'])
    # Confirm whether there are two treatments
    study_group = power_group_data[["Compound Treatment(s)"]]
    study_unique_group = study_group.drop_duplicates()
    if study_unique_group.shape[0] != 2:
        # only two treatments can be selected"
        power_analysis_table = np.NAN
    else:
        # Power analysis results
        power_analysis_table_key = power_group_data[["Group", "Time"]]
        power_analysis_table = power_analysis_table_key.drop_duplicates()
        # create power analysis report table
        header_list = power_analysis_table.columns.values.tolist()
        header_list.append('Power')
        header_list.append('Sample Size')
        header_list.append('Significance Level')

        # Define all columns of power analysis report table
        power_analysis_table = power_analysis_table.reindex(
            columns=header_list)
        # Loop every unique replicate group
        time_count = len(power_analysis_table)

        if study_unique_group.shape[0] != 2:
            err_msg = "two treatments have to be selected"
            print(err_msg)
        else:
            chip_data = power_group_data.groupby(
                ['Compound Treatment(s)', 'Chip ID', 'Time'], as_index=False)['Value'].mean()
            cltr_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[0, 0]]
            treat_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[1, 0]]
            for itime in range(time_count):
                if itime not in power_analysis_table['Time']:
                    continue
                x = cltr_data[cltr_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                y = treat_data[treat_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                # effect size for power analysis calculation
                es_value = pa_effect_size(x, y, type)
                # Predict sample size
                predicted_sig_level = pa_predicted_significance_level(
                    sample_size, es_value, power)

                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Power')
                ] = power
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Sample Size')
                ] = sample_size
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Significance Level')
                ] = predicted_sig_level

    return power_analysis_table


def pa_predicted_power_time_series(power_group_data, type='d', sample_size=3, sig_level=0.05):
    # Predict the sample size for two treatments' time series given power and significance level
    power_group_data = power_group_data.dropna(subset=['Value'])
    # Confirm whether there are two treatments
    study_group = power_group_data[["Compound Treatment(s)"]]
    study_unique_group = study_group.drop_duplicates()
    if study_unique_group.shape[0] != 2:
        # only two treatments can be selected"
        power_analysis_table = np.NAN
    else:
        # Power analysis results
        power_analysis_table_key = power_group_data[["Group", "Time"]]
        power_analysis_table = power_analysis_table_key.drop_duplicates()
        # create power analysis report table
        header_list = power_analysis_table.columns.values.tolist()
        header_list.append('Power')
        header_list.append('Sample Size')
        header_list.append('Significance Level')

        # Define all columns of power analysis report table
        power_analysis_table = power_analysis_table.reindex(
            columns=header_list)
        # Loop every unique replicate group
        time_count = len(power_analysis_table)

        if study_unique_group.shape[0] != 2:
            err_msg = "two treatments have to be selected"
            print(err_msg)
        else:
            chip_data = power_group_data.groupby(
                ['Compound Treatment(s)', 'Chip ID', 'Time'], as_index=False)['Value'].mean()
            cltr_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[0, 0]]
            treat_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[1, 0]]
            for itime in range(time_count):
                if itime not in power_analysis_table['Time']:
                    continue
                x = cltr_data[cltr_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                y = treat_data[treat_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                # effect size for power analysis calculation
                es_value = pa_effect_size(x, y, type)
                # Predict sample size
                predicted_power = pa_predicted_power(
                    sample_size, es_value, sig_level)

                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Power')
                ] = predicted_power
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Sample Size')
                ] = sample_size
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Significance Level')
                ] = sig_level

    return power_analysis_table


def pa_power_analysis_report(power_group_data, type='d', sig_level=0.05):
    # Calculate and report the power analysis for two treatments' time series from replicates assay measurements
    power_group_data = power_group_data.dropna(subset=['Value'])
    # Confirm whether there are two treatments
    study_group = power_group_data[["Compound Treatment(s)"]]
    study_unique_group = study_group.drop_duplicates()
    if study_unique_group.shape[0] != 2:
        # only two treatments can be selected"
        power_analysis_table = np.NAN
    else:
        # Power analysis results
        power_analysis_table_key = power_group_data[["Group", "Time"]]
        power_analysis_table = power_analysis_table_key.drop_duplicates()
        # create power analysis report table
        header_list = power_analysis_table.columns.values.tolist()
        header_list.append('Power')
        header_list.append('P Value')
        header_list.append('Sample Size')

        # Define all columns of power analysis report table
        power_analysis_table = power_analysis_table.reindex(columns=header_list)
        # Loop every unique replicate group
        time_count = len(power_analysis_table)

        # Redefine the result dataframe index
        power_analysis_table.index = pd.RangeIndex(len(power_analysis_table.index))

        if study_unique_group.shape[0] != 2:
            err_msg = "two treatments have to be selected"
            print(err_msg)
        else:
            chip_data = power_group_data.groupby(
                ['Compound Treatment(s)', 'Chip ID', 'Time'], as_index=False)['Value'].mean()
            cltr_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[0, 0]]
            treat_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[1, 0]]
            for itime in range(time_count):
                if itime not in power_analysis_table['Time']:
                    continue
                x = cltr_data[cltr_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                n1 = len(x)
                y = treat_data[treat_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                n2 = len(y)
                if n1 > 1 and n2 > 1:
                    # P-value and effect size for power analysis calculation
                    es_value = pa_effect_size(x, y, type)
                    p_value = pa_t_test(x, y)
                    # Power calculation
                if n1 == n2 and n1 > 1:
                    power_value = pa_power_one_sample_size(n1, es_value, sig_level)
                    sample_size = n1
                    p_value = pa_t_test(x, y)
                elif n1 > 1 and n2 > 1 and n1 != n2:
                    power_value = pa_power_two_sample_size(n1, n2, es_value, sig_level)
                    sample_size = min(n1, n2)
                    p_value = pa_t_test(x, y)
                else:
                    power_value = np.NAN
                    p_value = np.NAN
                    sample_size = np.NAN

                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Power')
                ] = power_value
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('P Value')
                ] = p_value
                power_analysis_table.iloc[
                    itime,
                    power_analysis_table.columns.get_loc('Sample Size')
                ] = sample_size

    return power_analysis_table


def pa_power_sample_size_curves_matrix(power_group_data, power_interval=0.02, type='d', sig_level=0.05):
    # Calculate and report the power analysis for two treatments' time series from replicates assay measurements
    max_power = 1
    power_interval = 0.01

    power_group_data = power_group_data.dropna(subset=['Value'])
    # Confirm whether there are two treatments
    study_group = power_group_data[["Compound Treatment(s)"]]
    study_unique_group = study_group.drop_duplicates()
    study_unique_group.index = pd.RangeIndex(len(study_unique_group.index))
    if study_unique_group.shape[0] != 2:
        # only two treatments can be selected"
        power_analysis_table = np.NAN
        power_sample_curves_table = np.NAN
    else:
        # Power analysis results
        power_analysis_table_key = power_group_data[["Group", "Time"]]
        power_analysis_table = power_analysis_table_key.drop_duplicates()
        # create power analysis report table
        header_list = power_analysis_table.columns.values.tolist()
        header_list.append('Power')
        header_list.append('Sample Size')
        header_list.append('Note')

        power_analysis_table.index = pd.RangeIndex(len(power_analysis_table.index))

        # Define all columns of power analysis report table
        power_sample_curves_table = pd.DataFrame(columns=header_list)
        # Loop every unique replicate group
        time_count = len(power_analysis_table)

        if study_unique_group.shape[0] != 2:
            err_msg = "two treatments have to be selected"
            print(err_msg)
        else:
            chip_data = power_group_data.groupby(
                ['Compound Treatment(s)', 'Chip ID', 'Time'],
                as_index=False
            )['Value'].mean()
            cltr_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[0, 0]]
            treat_data = chip_data[chip_data['Compound Treatment(s)'] == study_unique_group.iloc[1, 0]]
            for itime in range(time_count):
                if itime not in power_analysis_table['Time']:
                    continue
                min_power = 0.4
                x = cltr_data[cltr_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                n1 = len(x)
                y = treat_data[treat_data['Time'] == power_analysis_table['Time'][itime]]['Value']
                n2 = len(y)
                if n1 > 1 and n2 > 1:
                    es_value = pa_effect_size(x, y, type)
                else:
                    es_value = np.NAN
                if n1 == n2 and n1 > 1:
                    power_value = pa_power_one_sample_size(n1, es_value, sig_level)
                elif n1 > 1 and n2 > 1 and n1 != n2:
                    power_value = pa_power_two_sample_size(n1, n2, es_value, sig_level)
                else:
                    power_value = np.NAN

                if power_value < 0.4:
                    min_power = power_value

                power_array = np.arange(min_power, max_power, power_interval)
                n_pc = len(power_array)
                # create dataframe for each time point
                time_power_df = pd.DataFrame(
                    index=range(n_pc), columns=header_list
                )
                if es_value > 0:
                    for k in range(n_pc):
                        input_power = power_array[k]
                        output_sample_size = pa_predicted_sample_size(
                            input_power, es_value, sig_level
                        )
                        time_power_df.iloc[k, 0] = power_analysis_table['Group'][itime]
                        time_power_df.iloc[k, 1] = power_analysis_table['Time'][itime]
                        time_power_df.iloc[k, 2] = input_power
                        time_power_df.iloc[k, 3] = output_sample_size

                # Append the calculate power and sample size matrix at each time
                power_sample_curves_table = power_sample_curves_table.append(
                    time_power_df, ignore_index=True
                )
            power_sample_curves_table = power_sample_curves_table.dropna(subset=['Sample Size'])
            power_sample_curves_table.index = pd.RangeIndex(len(power_sample_curves_table.index))

            # power_sample_curves_table = power_sample_curves_table[pd.notnull(power_sample_curves_table['Sample Size'])]

            power_results_report = pa_power_analysis_report(power_group_data, type, sig_level=sig_level)

            for itime in range(time_count):
                power_curve_set = power_sample_curves_table[power_sample_curves_table['Time'] == power_results_report['Time'][itime]]
                power_curve_row_count = power_curve_set.shape[0]
                if power_results_report['Power'][itime] > 0.99 and power_curve_row_count < 1:
                    cur_group = power_results_report['Group'][itime]
                    cur_time = power_results_report['Time'][itime]
                    cur_power = 1.0
                    cur_sample_size = power_results_report['Sample Size'][itime]
                    cur_note = 'There is no power-sample curve at this time point because the power is close to 1'
                    power_sample_curves_table = power_sample_curves_table.append({
                        'Group':  cur_group,
                        'Time': cur_time,
                        'Power': cur_power,
                        'Sample Size': float(cur_sample_size),
                        'Note': cur_note
                    }, ignore_index=True)

    return power_sample_curves_table


def two_sample_power_analysis(data, type, sig):
    # Initialize a workbook
    # Load the summary data into the dataframe
    power_group_data = pd.DataFrame(
        data,
        columns=['Group',
                 'Time',
                 'Compound Treatment(s)',
                 'Chip ID',
                 'Value']
    )
    # Four different methods for power analysis
    # If type = 'd', it's Cohen's method, this is default method
    # If type 'D', it's Glass’s ∆ method
    # If type 'g' it's Hedges’s g method
    # If type 'gs' it's Hedges’s g* method

    # Call function to get the power values for the two treatments' chip replicates at each time
    power_results_report = pa_power_analysis_report(power_group_data, type=type, sig_level=sig)

    # Call fuction to get the predicted sample size of chip replicates at each time for given power
    power_vs_sample_size_curves_matrix = pa_power_sample_size_curves_matrix(
        power_group_data, power_interval=0.02, type=type, sig_level=sig)

    # Call Sample size prediction
    sample_size_prediction_matrix = pa_predicted_sample_size_time_series(
        power_group_data, type=type, power=0.9, sig_level=sig)

    # Call power prediction
    power_prediction_matrix = pa_predicted_power_time_series(
        power_group_data, type=type, sample_size=3, sig_level=sig)

    # Call significance level prediction
    sig_level_prediction_matrix = pa_predicted_significance_level_time_series(
        power_group_data, type=type, sample_size=3, power=0.8)

    power_results_report_data = power_results_report.where((pd.notnull(power_results_report)), None).to_dict('split')
    power_vs_sample_size_curves_matrix_data = power_vs_sample_size_curves_matrix.where((pd.notnull(power_vs_sample_size_curves_matrix)), None).to_dict('split')
    sample_size_prediction_matrix_data = sample_size_prediction_matrix.where((pd.notnull(sample_size_prediction_matrix)), None).to_dict('split')
    power_prediction_matrix_data = power_prediction_matrix.where((pd.notnull(power_prediction_matrix)), None).to_dict('split')
    sig_level_prediction_matrix_data = sig_level_prediction_matrix.where((pd.notnull(sig_level_prediction_matrix)), None).to_dict('split')

    return {
        "power_results_report": power_results_report_data['data'],
        "power_vs_sample_size_curves_matrix": power_vs_sample_size_curves_matrix_data['data'],
        "sample_size_prediction_matrix": sample_size_prediction_matrix_data['data'],
        "power_prediction_matrix": power_prediction_matrix_data['data'],
        "sig_level_prediction_matrix": sig_level_prediction_matrix_data['data'],
    }


def create_power_analysis_group_table(group_count, study_data):
    # Calculate and report the reproducibility index and status and other parameters
    # Select unique group rows by study, organ model,sample location, assay and unit
    # Drop null value rows
    study_data = pd.DataFrame(study_data)
    study_data.columns = study_data.iloc[0]
    study_data = study_data.drop(study_data.index[0])

    # Drop null value rows
    study_data['Value'].replace('', np.nan, inplace=True)
    study_data = study_data.dropna(subset=['Value'])
    study_data['Value'] = study_data['Value'].astype(float)
    # Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data['Chip ID'].astype(str)

    # Add Time (day) calculated from three time column
    study_data["Time"] = study_data['Time']/1440.0
    study_data["Time"] = study_data["Time"].apply(lambda x: round(x,2))

    # Define the Chip ID column to string type
    study_data[['Chip ID']] = study_data[['Chip ID']].astype(str)
    chip_data = study_data.groupby(['Group', 'Chip ID', 'Time'], as_index=False)['Value'].mean()

    # create reproducibility report table
    header_list=chip_data.columns.values.tolist()
    header_list.append('# of Chips/Wells')
    header_list.append('# of Time Points')

    power_analysis_group_table = []

    for x in range(group_count+1):
        power_analysis_group_table.append(header_list)

    power_analysis_group_table = pd.DataFrame(columns=header_list)

    # Define all columns of reproducibility report table
    for row in range(group_count):

        rep_matrix = chip_data[chip_data['Group'] == str(row + 1)]
        icc_pivot = pd.pivot_table(rep_matrix, values='Value', index='Time', columns=['Chip ID'], aggfunc=np.mean)

        group_id = str(row+1)  # Define group ID

        group_rep_matrix = pd.DataFrame(index=[0], columns=header_list)
        power_analysis_group_table = power_analysis_group_table.append(group_rep_matrix, ignore_index=True)

        power_analysis_group_table.iloc[row, power_analysis_group_table.columns.get_loc('Group')] = group_id
        power_analysis_group_table.iloc[row, power_analysis_group_table.columns.get_loc('# of Chips/Wells')] = icc_pivot.shape[1]
        power_analysis_group_table.iloc[row, power_analysis_group_table.columns.get_loc('# of Time Points')] = icc_pivot.shape[0]

    power_analysis_group_table = power_analysis_group_table.fillna('')

    return power_analysis_group_table.to_dict('split')


# One Sample Power Analysis
def pa1_predict_sample_size_given_delta_and_power(delta, power, sig_level, sd):
    if power > sig_level and power < 1 and delta > 0 and sd != 0:
        es_value = delta/sd
        result = tt_solve_power(effect_size=es_value, nobs=None, alpha=sig_level, power=power, alternative='two-sided')
        if np.isscalar(result):
            sample_size = result
        else:
            sample_size = np.NAN
    else:
        sample_size = np.NAN
    return sample_size


def pa1_predicted_power_given_delta_and_sample_size(delta, sample_size, sig_level, sd):
    if sig_level > 0 and sig_level < 1 and delta > 0 and sd != 0:
        es_value = delta/sd
        result = tt_solve_power(effect_size=es_value, nobs=sample_size, alpha=sig_level, power=None, alternative='two-sided')
        if np.isscalar(result):
            power_value = result
        else:
            power_value = np.NAN
    else:
        power_value = np.NAN
    return power_value


def pa1_predicted_delta_given_sample_size_and_power(sample_size, power, sig_level, sd):
    if power > sig_level and power < 1 and sample_size > 0 and sd != 0:
        result = tt_solve_power(effect_size=None, nobs=sample_size, alpha=sig_level, power=power, alternative='two-sided')
        if np.isscalar(result):
            delta = result * sd
        else:
            delta = np.NAN
    else:
        delta = np.NAN
    return delta


def one_sample_power_analysis_calculation(sample_data, sig_level, difference, sample_size, power):
    # Calculate the standard deviation of sample data
    sd = np.std(sample_data, ddof=1)
    if sd == 0:
        power_analysis_result = {'THE SAMPLE DATA ARE CONSTANT': ''}
    if np.isnan(difference) and np.isnan(power) and np.isnan(sample_size):
        power_analysis_result = {'error': ''}
    else:
        # Given Diffrences
        if ~np.isnan(difference):
            if np.isnan(power) and np.isnan(sample_size):
                pw_columns = ['Sample Size', 'Power']
                sample_size_array = np.arange(2, 101, 0.1)  # Sample size is up to 100
                power_analysis_result = pd.DataFrame(index=range(len(sample_size_array)), columns=pw_columns)
                for i_size in range(len(sample_size_array)):
                    sample_size_loc=sample_size_array[i_size]
                    power_value = pa1_predicted_power_given_delta_and_sample_size(difference, sample_size_loc, sig_level, sd)
                    power_analysis_result.iloc[i_size, 0] = sample_size_loc
                    power_analysis_result.iloc[i_size, 1] = power_value

        # Given sample size
        if ~np.isnan(sample_size) and sample_size >= 2:
            if np.isnan(difference) and np.isnan(power):
                pw_columns = ['Difference', 'Power']
                power_array = np.arange(sig_level+0.01, 0.9999, 0.01)  # power is between 0 and 1
                power_analysis_result = pd.DataFrame(index=range(len(power_array)), columns=pw_columns)
                for i_size in range(len(power_array)):
                    power_loc = power_array[i_size]
                    difference_value = pa1_predicted_delta_given_sample_size_and_power(sample_size, power_loc, sig_level, sd)
                    if difference_value > 0:
                        power_analysis_result.iloc[i_size, 0] = difference_value
                    power_analysis_result.iloc[i_size, 1] = power_loc

        # Given power
        if ~np.isnan(power):
            if np.isnan(difference) and np.isnan(sample_size):
                pw_columns = ['Sample Size', 'Difference']
                sample_size_array = np.arange(2, 101, 0.1)  # power is between 0 and 1
                power_analysis_result = pd.DataFrame(index=range(len(sample_size_array)), columns=pw_columns)
                for i_size in range(len(sample_size_array)):
                    sample_size_loc = sample_size_array[i_size]
                    difference_value = pa1_predicted_delta_given_sample_size_and_power(sample_size_loc, power, sig_level, sd)
                    if difference_value > 0:
                        power_analysis_result.iloc[i_size, 1] = difference_value
                    power_analysis_result.iloc[i_size, 0] = sample_size_loc

        # Given power and sample size predict difference
        if (np.isnan(difference)) and (~np.isnan(power)) and (~np.isnan(sample_size)):
            power_analysis_result = {'Difference': pa1_predicted_delta_given_sample_size_and_power(sample_size, power, sig_level, sd)}

        # Given difference and sample size predict power
        if (~np.isnan(difference)) and (np.isnan(power)) and (~np.isnan(sample_size)):
            power_analysis_result = {'Power': pa1_predicted_power_given_delta_and_sample_size(difference, sample_size, sig_level, sd)}

        # Given difference and power predict sample size
        if (~np.isnan(difference)) and (~np.isnan(power)) and (np.isnan(sample_size)):
            power_analysis_result = {'Sample Size': pa1_predict_sample_size_given_delta_and_power(difference, power, sig_level, sd)}
            if np.isnan(power_analysis_result['Sample Size']):
                power_analysis_result['Sample Size'] = None
    try:
        return power_analysis_result.astype(np.float32)
    except:
        return power_analysis_result
    else:
        return {'error': ''}


def one_sample_power_analysis(one_sample_data,
                              sig_level,
                              one_sample_compound,
                              one_sample_tp,
                              os_diff,
                              os_diff_percentage,
                              os_sample_size,
                              os_power
                              ):

    # Load the summary data into the dataframe
    power_group_data = pd.DataFrame(
        one_sample_data,
        columns=['Group',
                 'Time',
                 'Compound Treatment(s)',
                 'Chip ID',
                 'Value']
    )

    power_group_data = power_group_data.dropna(subset=['Value'])

    # number of unique compounds
    compound_group = power_group_data[["Compound Treatment(s)"]]
    compound_unique_group = compound_group.drop_duplicates()
    # select compound
    compound_index = 2

    # query the target data for selected compound
    # compound_data = power_group_data[power_group_data['Compound Treatment(s)'] == compound_unique_group.iloc[compound_index, 0]]
    compound_data = power_group_data[power_group_data['Compound Treatment(s)'] == one_sample_compound]

    # Get unique time points for selected compound data
    compound_time = compound_data[["Time"]]
    time_unique_group = compound_time.drop_duplicates()

    # Select time point
    # Row of the user's selected time point - PASSED after selection in the the power curves table
    time = one_sample_tp*1440

    # Query sample data series for selected compound and time point
    # sample_data = compound_data[compound_data['Time'] == time]['Value']
    # sample_data = compound_data[compound_data['Time'] == time_unique_group.iloc[time_index, 0]]['Value']
    sample_data = compound_data[abs(compound_data['Time'] - time) <= 0.0000000001]['Value']
    sample_mean = np.mean(sample_data)

    # Sample population size4_Or_More
    number_sample_population = len(sample_data)
    # The power analysis will be exceuted only when the sample population has more than one sample
    # Based the GUI's setting, return the power analysis results by calculated data or 2D curve
    # At defined significance level, given Difference, predict sample size vs power curve

    if number_sample_population < 2:
        return {'error': 'Less Than 2 Samples at Time Point'}
    else:
        ########################One Sample Power Analysis Parameter Setting   ###############################
        if os_diff_percentage != '':
            difference = float(sample_mean * percent_change / 100)
        elif os_diff != '':
            difference = float(os_diff)
        else:
            difference = np.NAN

        if os_sample_size != '':
            sample_size = float(os_sample_size)
        else:
            sample_size = np.NAN

        if os_power != '':
            power = float(os_power)
        else:
            power = np.NAN

        # Check upper limit of delta, see if we exceed it.
        if not np.isnan(power) and not np.isnan(difference):
            sd = np.std(sample_data, ddof=1)
            upper_limit = pa1_predicted_delta_given_sample_size_and_power(2, power, sig_level, sd) // 0.001 / 1000
            if difference > upper_limit:
                return {'error': 'The Upper Limit for \"Difference\" (at a Sample Size of 2) is: {}'.format(upper_limit)}

        # Power analysis results will be returned by user's input
        power_analysis_result = one_sample_power_analysis_calculation(sample_data, sig_level, difference, sample_size, power)

        if type(power_analysis_result) is not dict and type(power_analysis_result) is not float:
            return power_analysis_result.to_dict('split')
        else:
            return power_analysis_result


def pk_clearance_results(pk_type,
                         with_no_cell_data,
                         cell_name,
                         start_time,
                         end_time,
                         total_device_vol_ul,
                         total_cells_in_device,
                         flow_rate,
                         cells_per_tissue_g,
                         total_organ_weight_g,
                         compound_conc,
                         compound_pk_data):
    # Calculate t-half and intrinsic clearance
    compound_pk_data = pd.DataFrame(compound_pk_data, columns=["Time", "Cells", "Value"])
    compound_pk_data = compound_pk_data.dropna()
    if pk_type == "Bolus":
        # Bolus clearance calculation
        cl_ml_min = pk_clearance_bolus(
            start_time,
            end_time,
            cells_per_tissue_g,
            total_organ_weight_g,
            total_device_vol_ul,
            total_cells_in_device,
            compound_pk_data
        )
        return {"clearance": cl_ml_min, "clearance_data": ''}
    else:
        if start_time > end_time:
            return {'error': 'The Selected "Start Time" comes after the selected "End Time". Please adjust these parameters and run the calculation again.'}
        steady_state_table_key = compound_pk_data[["Cells"]]
        if len(steady_state_table_key.drop_duplicates().index) >= 2:
            if len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) > 0:
                clist = [cell_name, '-No Cell Samples-']
                compound_pk_data = compound_pk_data[compound_pk_data.Cells.isin(clist)]
            else:
                compound_pk_data = compound_pk_data[compound_pk_data['Cells'] == cell_name]

        steady_state_table_key = compound_pk_data[["Cells"]]
        if len(steady_state_table_key.drop_duplicates().index) == 2:
            if len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) > 0:
                pk_steady_state_data = pk_calc_clearance_continuous_infusion_matrix(
                    with_no_cell_data,
                    cell_name,
                    total_device_vol_ul,
                    total_cells_in_device,
                    flow_rate,
                    cells_per_tissue_g,
                    total_organ_weight_g,
                    compound_conc,
                    compound_pk_data
                )
                cl_ml_min = pk_calc_clearance_steady_state(
                    pk_steady_state_data,
                    start_time,
                    end_time
                )
                if cl_ml_min < 0:
                    return {'error': 'The "Compound Recovered From Device With Cells" concentration is greater than the "Compound Recovered From Device Without Cells". Do not include cell-free data for PK analysis with this data.'}
            else:
                return {'error': 'There is no data for this compound from device without cells. Please group the PK group sets by Cells.'}
        elif len(steady_state_table_key.drop_duplicates().index) == 1 and len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) == 0:
            with_no_cell_data = False
            pk_steady_state_data = pk_calc_clearance_continuous_infusion_matrix(
                with_no_cell_data,
                cell_name,
                total_device_vol_ul,
                total_cells_in_device,
                flow_rate,
                cells_per_tissue_g,
                total_organ_weight_g,
                compound_conc,
                compound_pk_data
            )
            cl_ml_min = pk_calc_clearance_steady_state(
                pk_steady_state_data,
                start_time,
                end_time
            )
        elif len(steady_state_table_key.drop_duplicates().index) == 1 and len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) > 0:
            return {'error': 'Only Cell-Free Data is Present!'}

    if (np.isnan(cl_ml_min)):
        return {'error': 'Clearance was Null. Please select different times and try again.'}

    return {"clearance": cl_ml_min, "clearance_data": pk_steady_state_data.to_dict('split')}


def pk_clearance_bolus(start_time,
                       end_time,
                       cells_per_tissue_g,
                       total_organ_weight_g,
                       total_device_vol_ul,
                       total_cells_in_device,
                       compound_pk_data):

    # Filter data by defined time interval
    filtered_data = compound_pk_data[compound_pk_data['Time'] <= end_time]
    filtered_data = filtered_data[filtered_data['Time'] >= start_time]
    agg_mean_data = filtered_data.groupby(['Time'], as_index=False)['Value'].mean()

    x = agg_mean_data['Time']*60
    y = np.log(agg_mean_data['Value'])

    # Generated linear regression fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    # Calculate t half
    t_half = np.log(2)/abs(slope)

    # Calculate intrinsic clearance
    intrinsic_clearance = 0.693/t_half*total_device_vol_ul/1000*cells_per_tissue_g*total_organ_weight_g/total_cells_in_device

    return intrinsic_clearance


def pk_calc_clearance_continuous_infusion_matrix(with_no_cell_data,
                                                 cell_name,
                                                 total_device_vol_ul,
                                                 total_cells_in_device,
                                                 flow_rate,
                                                 cells_per_tissue_g,
                                                 total_organ_weight_g,
                                                 compound_conc,
                                                 compound_pk_data):
    influent_conc = compound_conc
    compound_pk_data.dropna()
    steady_state_table_key = compound_pk_data[["Cells"]]
    if len(steady_state_table_key.drop_duplicates().index) >= 2:
        if len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) > 0:
            clist = [cell_name, '-No Cell Samples-']
            compound_pk_data = compound_pk_data[compound_pk_data.Cells.isin(clist)]
        else:
            compound_pk_data = compound_pk_data[compound_pk_data['Cells'] == cell_name]

    steady_state_table_key = compound_pk_data[["Cells"]]
    steady_state_pivot = np.nan
    if len(steady_state_table_key.drop_duplicates().index) == 2:
        steady_state_pivot = pd.pivot_table(compound_pk_data, values='Value', index='Time', columns=['Cells'], aggfunc=np.mean)
        if len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) > 0:
            column_list = steady_state_pivot.columns.values.tolist()
            no_cell_col_index = column_list.index('-No Cell Samples-')
            if no_cell_col_index > 0:
                column_list = column_list[-1:] + column_list[:-1]
                steady_state_pivot=steady_state_pivot[column_list]
            old_column_names = steady_state_pivot.columns.values.tolist()
            new_column_names = ['Compound Recovered From Device Without Cells (\u03BCM)', 'Compound Recovered From Device With Cells (\u03BCM)']
            steady_state_pivot.rename(columns=dict(zip(old_column_names, new_column_names)), inplace=True)
            # Create Continuous Infusion clearance analysis matrix
            header_list = steady_state_pivot.columns.values.tolist()
            header_list.append('Extraction Ratio')
            header_list.append('Clearance from MPS Model (\u03BCL/hr)')
            header_list.append('Predicted intrinsic clearance (\u03BCl/min)')

            # Define all columns of intrinsic clearance analysis table
            steady_state_pivot = steady_state_pivot.reindex(columns=header_list)
            steady_state_pivot['Time'] = steady_state_pivot.index

            if with_no_cell_data:
                for i in range(steady_state_pivot.shape[0]):
                    steady_state_pivot.iloc[i, 2] = (steady_state_pivot.iloc[i, 0]-steady_state_pivot.iloc[i, 1])/steady_state_pivot.iloc[i, 0]
                    steady_state_pivot.iloc[i, 3] = steady_state_pivot.iloc[i, 2]*flow_rate
                    steady_state_pivot.iloc[i, 4] = ((steady_state_pivot.iloc[i, 3]*(cells_per_tissue_g/total_cells_in_device)*total_organ_weight_g)/60*0.001)
            else:
                for i in range(steady_state_pivot.shape[0]):
                    steady_state_pivot.iloc[i, 2] = (influent_conc-steady_state_pivot.iloc[i, 1])/influent_conc
                    steady_state_pivot.iloc[i, 3] = steady_state_pivot.iloc[i, 2]*flow_rate
                    steady_state_pivot.iloc[i, 4] = ((steady_state_pivot.iloc[i, 3]*(cells_per_tissue_g/total_cells_in_device)*total_organ_weight_g)/60*0.001)
        steady_state_matrix = steady_state_pivot
    elif len(steady_state_table_key.drop_duplicates().index) == 1 and len(compound_pk_data.loc[compound_pk_data['Cells'] == '-No Cell Samples-'].index) == 0:
        steady_state_data = compound_pk_data.groupby(['Time'], as_index=False)['Value'].mean()
        old_column_names = steady_state_data.columns.values.tolist()
        new_column_names = ['Time', 'Compound Recovered From Device With Cells (\u03BCM)']
        steady_state_data.rename(columns=dict(zip(old_column_names, new_column_names)), inplace=True)
        # Create Continuous Infusion clearance analysis matrix
        header_list = steady_state_data.columns.values.tolist()
        header_list.append('Extraction Ratio')
        header_list.append('Clearance from MPS Model (\u03BCL/hr)')
        header_list.append('Predicted intrinsic clearance (\u03BCl/min)')

        # Define all columns of intrinsic clearance analysis table
        steady_state_data = steady_state_data.reindex(columns=header_list)
        for i in range(steady_state_data.shape[0]):
            steady_state_data.iloc[i, 2] = (influent_conc-steady_state_data.iloc[i, 1])/influent_conc
            steady_state_data.iloc[i, 3] = steady_state_data.iloc[i, 2]*flow_rate
            steady_state_data.iloc[i, 4] = ((steady_state_data.iloc[i, 3]*(cells_per_tissue_g/total_cells_in_device)*total_organ_weight_g)/60*0.001)
        df1 = steady_state_data.pop('Time')
        steady_state_data['Time'] = df1
        steady_state_data.insert(0, 'Compound Recovered From Device Without Cells (\u03BCM)', 'NA')
        steady_state_matrix = steady_state_data
    else:
        steady_state_matrix = np.nan
    return steady_state_matrix


def pk_calc_clearance_steady_state(pk_steady_state_data, start_time, end_time):
    clearance_start_matrix = pk_steady_state_data.loc[pk_steady_state_data['Time'] >= start_time]
    if not np.isnan(end_time):
        clearance_start_matrix = clearance_start_matrix.loc[clearance_start_matrix['Time'] <= end_time]
    clearance = clearance_start_matrix['Predicted intrinsic clearance (\u03BCl/min)'].mean()
    return clearance


def calculate_pk_parameters(cl_ml_min,
                            pk_volume_data,
                            body_mass,
                            MW,
                            logD,
                            pKa,
                            fu,
                            Vp,
                            VE,
                            REI,
                            VR,
                            ASR,
                            Ki,
                            Ka,
                            Fa,
                            dose_mg,
                            dose_interval,
                            desired_Cp,
                            desired_dose_interval,
                            estimated_fraction_absorbed,
                            prediction_time_length,
                            missing_plasma_values,
                            missing_dosing_values,
                            acidic):

    ElogD = (logD*0.9638)+0.0417
    Log_vo_w = (1.099*logD)-1.31

    # Create the hardcoded organ volume table thing
    vol_data_col_names = pk_volume_data.pop(0)
    pk_volume_data = pd.DataFrame(pk_volume_data, columns=vol_data_col_names)

    # Calculate Vc
    fup_fut = 1
    v_row_count = pk_volume_data.shape[0]

    vol_df = pd.DataFrame(index=range(v_row_count), columns=["A", "B", "C"])
    for i in range(v_row_count):
        vol_df.iloc[i, 0] = ((10**Log_vo_w*(pk_volume_data.iloc[6, 3]+(0.3*pk_volume_data.iloc[6, 4])))+pk_volume_data.iloc[6, 2]+(0.7*pk_volume_data.iloc[6, 4]))/((10**Log_vo_w*(pk_volume_data.iloc[i, 3]+(0.3*pk_volume_data.iloc[i, 4])))+pk_volume_data.iloc[i, 2]+(0.7*pk_volume_data.iloc[i, 4]))
        vol_df.iloc[i, 1] = pk_volume_data.iloc[i, 1]*vol_df.iloc[i, 0]
        vol_df.iloc[i, 2] = vol_df.iloc[i, 1]*fup_fut

    par_col_names = [
        "fi(7.4)",
        "fut",
        "Vp (L)",
        "VE (L)",
        "VR (L)",
        "CL (L/h)",
        "Logvo/w",
        "Vc (L)",
        "ELogD",
        "VDss (L)",
        "Ke(1/h)",
        "Elimination half-life",
        "Ka (1/h)",
        "Fa",
        "AUC"
    ]

    Vc = np.sum(vol_df.iloc[:, 2])
    if acidic:
        fi = 1/(1+(10**((7.4-pKa)*-1)))
    else:
        fi = 1/(1+(10**((7.4-pKa)*1)))
    fut = 10**(0.008-(0.2294*ElogD)-(0.9311*fi)+(0.8885*(np.log10(fu))))
    Vp_L = body_mass*Vp
    VE_L = body_mass*VE
    VR_L = body_mass*VR
    CL_L = (cl_ml_min/1000)*60
    VDss = (Vp_L*(1+REI))+(fu*Vp_L*((VE_L/Vp_L)-REI)+((VR_L*fu)/fut))
    Ke = CL_L/VDss
    if not missing_plasma_values:
        AUC = Fa*dose_mg/VDss/Ke
    else:
        AUC = ""
    EHL = ((0.693*VDss)/CL_L)

    calculate_pk_parameters_df = pd.DataFrame(index=range(1), columns=par_col_names)
    calculate_pk_parameters_df.iloc[0, 0] = fi
    calculate_pk_parameters_df.iloc[0, 1] = fut
    calculate_pk_parameters_df.iloc[0, 2] = Vp_L
    calculate_pk_parameters_df.iloc[0, 3] = VE_L
    calculate_pk_parameters_df.iloc[0, 4] = VR_L
    calculate_pk_parameters_df.iloc[0, 5] = CL_L
    calculate_pk_parameters_df.iloc[0, 6] = Log_vo_w
    calculate_pk_parameters_df.iloc[0, 7] = Vc
    calculate_pk_parameters_df.iloc[0, 8] = ElogD
    calculate_pk_parameters_df.iloc[0, 9] = VDss
    calculate_pk_parameters_df.iloc[0, 10] = Ke
    calculate_pk_parameters_df.iloc[0, 11] = EHL
    calculate_pk_parameters_df.iloc[0, 12] = Ka
    calculate_pk_parameters_df.iloc[0, 13] = Fa
    calculate_pk_parameters_df.iloc[0, 14] = AUC

    if not missing_plasma_values:
        # Single Oral Dose: Calculated PK Parameters
        par_col_names = ["AUC (mg*min/L)", "Mmax (mg)", "Cmax (mg/L)", "tmax (h)"]
        calculate_pk_parameters_single_oral_dose = pd.DataFrame(index=range(1), columns=par_col_names)

        VDss = calculate_pk_parameters_df.iloc[0, 9]
        Ke = calculate_pk_parameters_df.iloc[0, 10]
        Ka = calculate_pk_parameters_df.iloc[0, 12]
        Fa = calculate_pk_parameters_df.iloc[0, 13]
        calculate_pk_parameters_single_oral_dose.iloc[0, 0] = (Fa*dose_mg)/(VDss*Ke)  # AUC (mg*min/L)
        Mmax = (Fa*dose_mg)*((Ke/Ka)**(Ke/(Ka-Ke)))  # Mmax (mg)
        calculate_pk_parameters_single_oral_dose.iloc[0, 1] = Mmax
        calculate_pk_parameters_single_oral_dose.iloc[0, 2] = Mmax/VDss  # Cmax (mg/L)
        calculate_pk_parameters_single_oral_dose.iloc[0, 3] = (np.log(Ka)-np.log(Ke))/(Ka-Ke)  # tmax (hour)

        # Multiple Oral Dose: Calculated PK Parameters
        par_col_names = ["Mss (mg)", "Css (mg/L)", "tmax (h)"]
        calculate_pk_parameters_multiple_oral_dose = pd.DataFrame(index=range(1), columns=par_col_names)

        CL_L = calculate_pk_parameters_df.iloc[0, 5]
        elimination_half_life = calculate_pk_parameters_df.iloc[0, 11]
        AUC = Fa*dose_mg/VDss/Ke
        Mss = (Fa*dose_mg)/(Ke*dose_interval)
        Css = (Fa*dose_mg)/(CL_L*dose_interval)
        tmax = np.log((Ka*(1-np.exp(-Ke*dose_interval)))/(Ke*(1-np.exp(-Ka*dose_interval))))/(Ka-Ke)
        calculate_pk_parameters_multiple_oral_dose.iloc[0, 0] = Mss
        calculate_pk_parameters_multiple_oral_dose.iloc[0, 1] = Css
        calculate_pk_parameters_multiple_oral_dose.iloc[0, 2] = tmax

        # Single oral dose prediction
        single_dose_Mmax = (Fa*dose_mg)*((Ke/Ka)**(Ke/(Ka-Ke)))  # Mmax (mg)
        single_dose_Cmax = Mmax/VDss  # Cmax (mg/L)
        single_dose_tmax = (np.log(Ka)-np.log(Ke))/(Ka-Ke)  # tmax (hour)

        # Multiple oral dose prediction
        multiple_dose_Mss = (Fa*dose_mg)/(Ke*dose_interval)  # Mss (mg)
        multiple_dose_Css = (Fa*dose_mg)/(CL_L*dose_interval)  # Css (mg/L)
        multiple_dose_tmax = np.log((Ka*(1-np.exp(-Ke*dose_interval)))/(Ke*(1-np.exp(-Ka*dose_interval))))/(Ka-Ke)  # tmax (h)
    else:
        elimination_half_life = calculate_pk_parameters_df.iloc[0, 11]
        single_dose_Mmax = 0
        single_dose_Cmax = 0
        single_dose_tmax = 0
        multiple_dose_Mss = 0
        multiple_dose_Css = 0
        multiple_dose_tmax = 0

    # To Reach Desired Plasma Levels:
    if not missing_dosing_values:
        par_col_names = ["Dosecalc (mg)", "No. of Doses to Reach 50%", "No. of Doses to Reach 90%"]
        calculate_pk_parameters_reach_desired_plasma_levels = pd.DataFrame(index=range(1), columns=par_col_names)
        Dosecalc = (((desired_Cp/1000000)*VDss*MW*1000)*Ke*desired_dose_interval)/estimated_fraction_absorbed
        n_doses_reach_50_percent = (3.323*np.log10(1-0.5)/-(desired_dose_interval/elimination_half_life))
        n_doses_reach_90_percent = (3.323*np.log10(1-0.9)/-(desired_dose_interval/elimination_half_life))
        calculate_pk_parameters_reach_desired_plasma_levels.iloc[0, 0] = Dosecalc
        calculate_pk_parameters_reach_desired_plasma_levels.iloc[0, 1] = n_doses_reach_50_percent
        calculate_pk_parameters_reach_desired_plasma_levels.iloc[0, 2] = n_doses_reach_90_percent
    else:
        Dosecalc = 0
        n_doses_reach_50_percent = 0
        n_doses_reach_90_percent = 0

    dosage_data = [single_dose_Mmax, single_dose_Cmax, single_dose_tmax, multiple_dose_Mss, multiple_dose_Css, multiple_dose_tmax, Dosecalc, n_doses_reach_50_percent, n_doses_reach_90_percent]

    if not missing_plasma_values:
        par_col_names = ["Time (hr)", "Time Interval (hr)", "Dose Number", "Single Dose (mg/L)", "Single Dose", "Elimination Coefficient", "Multiple Dose (mg/L)", "Multiple Dose (mg)"]
        prediction_dose_plot_table = pd.DataFrame(index=range(prediction_time_length+1), columns=par_col_names)
        FDK = (Fa*dose_mg*Ka)/(Ka-Ke)

        for i in range(prediction_time_length+1):
            if i == 0:
                prediction_dose_plot_table.iloc[i, 0] = i
                prediction_dose_plot_table.iloc[i, 1] = i
                prediction_dose_plot_table.iloc[i, 2] = 1
            else:
                prediction_dose_plot_table.iloc[i, 0] = (i-1)+1
                if prediction_dose_plot_table.iloc[i-1, 1] < dose_interval:
                    prediction_dose_plot_table.iloc[i, 1] = prediction_dose_plot_table.iloc[i-1, 1]+1
                else:
                    prediction_dose_plot_table.iloc[i, 1] = 1
                if prediction_dose_plot_table.iloc[i, 0] % dose_interval == 0:
                    prediction_dose_plot_table.iloc[i, 2] = prediction_dose_plot_table.iloc[i-1, 2]+1
                else:
                    prediction_dose_plot_table.iloc[i, 2] = prediction_dose_plot_table.iloc[i-1, 2]
            time = prediction_dose_plot_table.iloc[i, 0]
            time_interval = prediction_dose_plot_table.iloc[i, 1]
            dose_no = prediction_dose_plot_table.iloc[i, 2]
            single_dose_calc = ((Fa*dose_mg*Ka)/(VDss*(Ka-Ke)))*(np.exp(-(Ke*time))-np.exp(-(Ka*time)))
            single_dose_mg = single_dose_calc*VDss
            ec1 = (1-np.exp(-dose_no*Ke*dose_interval))
            ec2 = ((ec1/(1-np.exp(-Ke*dose_interval)))*np.exp(-Ke*time_interval))
            ec3 = ((1-np.exp(-dose_no*Ka*dose_interval))/(1-np.exp(-Ka*dose_interval)))
            EC = ec2-(ec3*np.exp(-Ka*time_interval))
            mult_dose_mg = FDK*EC
            mult_dose_calc = mult_dose_mg/VDss
            prediction_dose_plot_table.iloc[i, 3] = single_dose_calc
            prediction_dose_plot_table.iloc[i, 4] = single_dose_mg
            prediction_dose_plot_table.iloc[i, 5] = EC
            prediction_dose_plot_table.iloc[i, 6] = mult_dose_calc
            prediction_dose_plot_table.iloc[i, 7] = mult_dose_mg
        prediction_plot_table = prediction_dose_plot_table[prediction_dose_plot_table["Time (hr)"] <= prediction_time_length]
        x = prediction_plot_table["Time (hr)"]
        y_single = prediction_plot_table["Single Dose (mg/L)"]
        y_multiple = prediction_plot_table["Multiple Dose (mg/L)"]
        max_y = y_multiple.max()
        prediction_plot_table.dropna()

    if not missing_plasma_values and not missing_dosing_values:
        return {'calculated_pk_parameters': calculate_pk_parameters_df.to_dict('list'), 'prediction_plot_table': prediction_plot_table.to_dict('list'), 'dosing_data': dosage_data}
    elif not missing_plasma_values and missing_dosing_values:
        return {'calculated_pk_parameters': calculate_pk_parameters_df.to_dict('list'), 'prediction_plot_table': prediction_plot_table.to_dict('list'), 'dosing_data': dosage_data}
    elif missing_plasma_values and not missing_dosing_values:
        return {'calculated_pk_parameters': calculate_pk_parameters_df.to_dict('list'), 'dosing_data': dosage_data}
    else:
        return {'error': 'Invalid input provided. Please fill out more fields and try again.'}


# sck - assay plate map - fetch information about plate layout by size
def get_the_plate_layout_info_for_assay_plate_map(plate_size):
    """
    Getting the information on how to layout a plate map based on plate size (utility).
    """

    plate_size = int(plate_size)

    # HARDCODED sizes
    # if plate_size == 24:
    #     # print("if 24 utils plate size: ", plate_size)
    #     row_labels = assay_plate_reader_map_info_row_labels_24
    #     col_labels = assay_plate_reader_map_info_col_labels_24
    #     row_contents = assay_plate_reader_map_info_row_contents_24
    # elif plate_size == 96:
    #     # print("if 96 utils plate size: ", plate_size)
    #     row_labels = assay_plate_reader_map_info_row_labels_96
    #     col_labels = assay_plate_reader_map_info_col_labels_96
    #     row_contents = assay_plate_reader_map_info_row_contents_96
    # else:
    #     # print("if 384 utils plate size: ", plate_size)
    #     row_labels = assay_plate_reader_map_info_row_labels_384
    #     col_labels = assay_plate_reader_map_info_col_labels_384
    #     row_contents = assay_plate_reader_map_info_row_contents_384

    plate_sizes = assay_plate_reader_map_info_plate_size_choices_list

    if plate_size in plate_sizes:
        row_labels = eval("assay_plate_reader_map_info_row_labels_" + str(plate_size))
        col_labels = eval("assay_plate_reader_map_info_col_labels_" + str(plate_size))
        row_contents = eval("assay_plate_reader_map_info_row_contents_" + str(plate_size))
    else:
        row_labels = assay_plate_reader_map_info_row_labels_96
        col_labels = assay_plate_reader_map_info_col_labels_96
        row_contents = assay_plate_reader_map_info_row_contents_96

    return [col_labels, row_labels, row_contents]


# sck
# function to make a list of file line, file line length (need in more than one place, so put in function)
def sub_function_inside_utils_plate_reader_map_file_by_line_del(my_file_object, file_delimiter):
    # print("into this with delimiter ", file_delimiter)

    lines_delimiter_list = []
    length_delimiter_list = []

    # make sure at the top of the file
    my_file_object.seek(0)

    # read the FIRST line
    each_line = my_file_object.readline()

    if file_delimiter == 'comma':
        this_delimiter = each_line.decode("utf-8", "replace").split(',')
    elif file_delimiter == 'tab':
        this_delimiter = each_line.decode("utf-8", "replace").split('\t')
    else:
        this_delimiter = each_line.decode("utf-8", "replace").split(' ')

    # print("first line: ", this_delimiter)

    # append the FIRST line
    lines_delimiter_list.append(this_delimiter)
    length_delimiter_list.append(len(this_delimiter))

    # If the file is not empty, keep reading one line at a time, till the file is empty
    while each_line:
        each_line = my_file_object.readline()
        # lines_in_list.append(each_line)
        if file_delimiter == 'comma':
            this_delimiter = each_line.decode("utf-8", "replace").split(',')
        elif file_delimiter == 'tab':
            this_delimiter = each_line.decode("utf-8", "replace").split('\t')
        else:
            this_delimiter = each_line.decode("utf-8", "replace").split(' ')

        # print("this line: ", this_delimiter)

        # append each line to the list
        lines_delimiter_list.append(this_delimiter)
        length_delimiter_list.append(len(this_delimiter))

        # print("lines_delimiter_list")
        # print(lines_delimiter_list)

    return lines_delimiter_list, length_delimiter_list


# sck - assay plate reader analysis of data when defining data blocks (loading the file form)
def review_plate_reader_data_file_return_file_list(my_file_object, file_delimiter):
    """
    Assay PLATE READER FILE UPDATE pull information when viewing or updating and existing plate map FILE (utility).
    """
    # there is rampant plate size and shape HARDCODing in this function!!
    # todo-sck go back and steamline sizes when have a chance

    returned_from_file_by_line = sub_function_inside_utils_plate_reader_map_file_by_line_del(
        my_file_object, file_delimiter)
    file_list = returned_from_file_by_line
    return file_list


# sck - assay plate reader analysis of data when defining data blocks (for the UPDATE file form)
def review_plate_reader_data_file_format(my_file_object, set_dict):
    """
    Assay PLATE READER FILE UPDATE pull information when viewing or updating and existing plate map FILE (utility).
    """
    # there is rampant plate size and shape HARDCODing in this function!!
    # todo-sck go back and steamline sizes when have a chance
    # it is highly customized to specific file formats with an auto detect option
    # currently, the auto detect works okay if the rules are followed but ONLY for VERTICALLY stacked blocks
    # the customized to each file format work for vertical and/or side-by-side blocks

    # get passed IN (from ajax) info into variables
    file_format_selected = int(set_dict.get('this_file_format_selected'))
    file_delimiter = set_dict.get('file_delimiter')
    form_plate_size = int(set_dict.get('form_plate_size'))
    form_number_blocks = int(set_dict.get('form_number_blocks'))
    form_number_blank_columns = int(set_dict.get('form_number_blank_columns'))
    form_number_blank_rows = int(set_dict.get('form_number_blank_rows'))

    set_format = set_dict.get('set_format')
    set_delimiter = set_dict.get('set_delimiter')
    set_plate_size = set_dict.get('set_plate_size')
    set_number_blocks = set_dict.get('set_number_blocks')
    set_number_blank_columns = set_dict.get('set_number_blank_columns')
    set_number_blank_rows = set_dict.get('set_number_blank_rows')

    # print("just inside")
    # print('set_format: ', set_format)
    # print('set_delimiter: ', set_delimiter)
    # print('file_delimiter: ', file_delimiter)
    # print('set_plate_size: ', set_plate_size)
    # print('form_plate_size: ', form_plate_size)
    # print('set_number_blocks: ', set_number_blocks)
    # print('form_number_blocks:', form_number_blocks)
    # print('set_plate_columns: ', set_number_blank_columns)
    # print('form_number_blank_columns:', form_number_blank_columns)
    # print('file object ', my_file_object)

    # Get the list of lines in the file using the file delimiter (find the file delimiter if not known)
    # print('file_list: ', file_list) = list of lines in the file parsed by the delimiter
    # print('file_length_list: ',file_length_list) = number of found columns in the line
    # print('mean_len: ',mean_len) = the mean of the found columns in the whole file
    if set_delimiter == 'true':
        returned_from_file_by_line = sub_function_inside_utils_plate_reader_map_file_by_line_del(
            my_file_object, file_delimiter)
        file_list = returned_from_file_by_line[0]
        file_length_list = returned_from_file_by_line[1]
        mean_len = int(mean(file_length_list))
    else:
        # delimiter is unknown - find it
        # load all options then find the right one based on repeat number of delimiters
        returned_from_file_by_line_comma = sub_function_inside_utils_plate_reader_map_file_by_line_del(
            my_file_object, 'comma')
        lines_comma_list = returned_from_file_by_line_comma[0]
        length_comma_list = returned_from_file_by_line_comma[1]

        returned_from_file_by_line_tab = sub_function_inside_utils_plate_reader_map_file_by_line_del(
            my_file_object, 'tab')
        lines_tab_list = returned_from_file_by_line_tab[0]
        length_tab_list = returned_from_file_by_line_tab[1]

        returned_from_file_by_line_space = sub_function_inside_utils_plate_reader_map_file_by_line_del(
            my_file_object, 'space')
        lines_space_list = returned_from_file_by_line_space[0]
        length_space_list = returned_from_file_by_line_space[1]

        # which delimiter is it - compare
        mean_comma = int(mean(length_comma_list))
        mean_tab = int(mean(length_tab_list))
        mean_space = int(mean(length_space_list))

        # print("mean_comma = ", int(mean(length_comma_list)))
        # print("mean_tab = ", int(mean(length_tab_list)))
        # print("mean_space = ", int(mean(length_space_list)))

        if mean_comma > mean_tab and mean_comma > mean_space:
            # print("likely a comma delimited file")
            file_delimiter = "comma"
            file_list = lines_comma_list
            file_length_list = length_comma_list
            mean_len = mean_comma
        elif mean_tab > mean_space and mean_tab > mean_comma:
            # print("likely a tab delimited file")
            file_delimiter = "tab"
            file_list = lines_tab_list
            file_length_list = length_tab_list
            mean_len = mean_tab
        else:
            # print("likely a space delimited file")
            file_delimiter = "space"
            file_list = lines_space_list
            file_length_list = length_space_list
            mean_len = mean_space

    # print("file_delimiter ", file_delimiter)
    # print('file_list: ', file_list)
    # print('file_length_list: ', file_length_list)
    # print('mean_len: ', mean_len)

    # Now that the file delimiter is known, work with the appropriate file_list
    # For this code, work with indexes (0 - ?), but for formset (in the html), display the indexes + 1

    # make a list of the line numbers and corresponding column numbers (starting with 0)
    # of the lines with 1, 2, 3 and associated columns where the 1, 2, 3 was found
    find_potential_indexes = sub_function_inside_utils_plate_reader_map_file_find_potential_indexes(file_list, file_length_list, mean_len)
    rows_idx_with_1_2_3 = find_potential_indexes[0]
    cols_idx_with_1_of_1_2_3 = find_potential_indexes[1]
    rows_idx_with_blank_or_end = find_potential_indexes[2]
    rows_that_are_empty_all = find_potential_indexes[3]
    rows_that_are_empty_first_if_series = find_potential_indexes[4]

    # Next, get the plate size
    # NEW FORMATS - edit here if new options need to be added where the plate size can be extracted directly from the file
    # assumes only ONE plate size in a file!
    if set_format == 'true' and file_format_selected == 1:
        t2 = 0
        s2 = 0
        # 1 is currently the SoftMax pro formats that Mike C gave to SCK
        # possible locations of the plate size using file format 1 are two places, see if can find
        # do try except because, if null, will error when try to get integer
        #  row 1 (starting at 0) and column 19 (starting at 0)
        string_at_t2 = file_list[1][19].strip()
        string_at_s2 = file_list[1][18].strip()

        # print(string_at_t2)
        # print(string_at_s2)

        if len(string_at_t2) > 0:
            try:
                t2 = int(string_at_t2)
            except:
                t2 = 0

        #  row 2 (starting at 0) and column 18 (starting at 0)
        if len(string_at_s2) > 0:
            try:
                s2 = int(string_at_s2)
            except:
                s2 = 0

        if t2 == 0 and s2 == 0:
            # error in the file format!
            # set plate size to false so it can be detected as best as possible
            set_plate_size = 'false'
        else:
            if t2 in assay_plate_reader_map_info_plate_size_choices_list:
                form_plate_size = t2
            elif s2 in assay_plate_reader_map_info_plate_size_choices_list:
                form_plate_size = s2
            set_plate_size = 'true'

        # print(t2)
        # print(s2)

    # print(set_plate_size)
    # print(form_plate_size)

    if set_plate_size != 'true':
        # use other provided info to guess the plate size
        # the last resort is the one that assumes vertical stacking
        form_plate_size = sub_function_inside_utils_plate_reader_map_file_guess_plate_size(
            file_list, file_length_list, form_number_blank_columns, set_number_blank_columns,
            rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series
            )

    # get the dimensions of the block based on plate size
    # Know or have GUESSED Plate size, HARDCODED rows and columns of data in block are there
    if form_plate_size == 24:
        plate_rows = 4
        plate_columns = 6
    elif form_plate_size == 96:
        plate_rows = 8
        plate_columns = 12
    else:
        # form_plate_size = 384
        plate_rows = 16
        plate_columns = 24

    # print('form_plate_size: ', form_plate_size)
    # print('plate_rows: ', plate_rows)

    # find the blocks
    # NEW FORMATS - edit here if new options need to be added where the plate size can be extracted directly from the file
    if set_format == 'true' and file_format_selected == 1:
        # need special finder because not all the blocks have 123 headers
        lists_needed = sub_function_inside_utils_plate_reader_map_file_find_blocks_format_is_1(
                file_list, file_length_list, form_number_blank_columns, set_number_blank_columns,
                rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series
            )

        start_block_line_indexes = lists_needed[0]
        start_block_delimiter_indexes = lists_needed[1]
        data_block_metadata = lists_needed[2]

    else:
        # need to get the best guess
        lists_needed = sub_function_inside_utils_plate_reader_map_file_best_guess_block_detect(
            file_list,
            plate_rows, plate_columns,
            form_plate_size, set_plate_size,
            form_number_blank_columns, set_number_blank_columns,
            form_number_blank_rows, set_number_blank_rows,
            form_number_blocks, set_number_blocks,
            rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series
            )

        start_block_line_indexes = lists_needed[0]
        start_block_delimiter_indexes = lists_needed[1]
        data_block_metadata = lists_needed[2]

    if len(start_block_line_indexes) == 0:
        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns]
        data_block_metadata = ["could not detect the blocks automatically"]

    # print("start_block_line_indexes: ", start_block_line_indexes)
    # print("start_block_delimiter_indexes: ", start_block_delimiter_indexes)
    # print("data_block_metadata ", data_block_metadata)
    # print("rows_idx_with_1_2_3: ", rows_idx_with_1_2_3)
    # print("cols_idx_with_1_of_1_2_3: ", cols_idx_with_1_of_1_2_3)
    # print("rows_idx_with_blank_or_end ", rows_idx_with_blank_or_end)
    # print("rows_that_are_empty_first_if_series ", rows_that_are_empty_first_if_series)

    # COLLECT INFO TO SEND BACK TO AJAX CALL
    # may want to just send the repeated info once. quickest for now, but sends extra.
    calculated_number_of_blocks = len(start_block_line_indexes)*len(start_block_delimiter_indexes)
    file_list_of_dicts = []
    # for each block (follow along the start_block_line_indexes), make a dictionary
    idx = 0
    for each_line in start_block_line_indexes:
        # find for each start and plate size
        for each_delimiter in start_block_delimiter_indexes:

            # when temperature was in the metadata, the degress was an odd symbol, so, regex it out
            try:
                # if metadata list exists
                this_block_metadata_a = data_block_metadata[idx]
                this_block_metadata   = re.sub('[^A-Za-z0-9\s.:()]+', '', this_block_metadata_a)
            except:
                this_block_metadata = ""

            block_dict = {}
            # print("each_line ", each_line)
            # print("each_delimiter ", each_delimiter)
            block_dict.update({'data_block_metadata': this_block_metadata})
            block_dict.update({'line_start': each_line})
            block_dict.update({'line_end': each_line + plate_rows - 1})
            block_dict.update({'delimited_start': each_delimiter})
            block_dict.update({'delimited_end': each_delimiter + plate_columns - 1})
            block_dict.update({'number_blank_columns': each_delimiter})
            block_dict.update({'number_blank_rows': each_line})
            block_dict.update({'block_delimiter': file_delimiter})
            block_dict.update({'plate_size': form_plate_size})
            block_dict.update({'plate_lines': plate_rows})
            block_dict.update({'plate_columns': plate_columns})
            block_dict.update({'calculated_number_of_blocks': calculated_number_of_blocks})

            # add the dictionary to the list
            file_list_of_dicts.append(block_dict)
        idx = idx + 1

    # print('file_list_of_dicts')
    # print(file_list_of_dicts)
    return [file_list_of_dicts, file_list]


# sck
def sub_function_inside_utils_plate_reader_map_file_find_potential_indexes(file_list, file_length_list, mean_len):
    rows_with_1_2_3 = []
    cols_with_1_of_1_2_3 = []
    rows_with_blank_or_end = []
    rows_that_are_empty_all = []
    rows_that_are_empty_first_if_series = []

    irow = 0
    for this in file_list:
        icol = 0
        while icol < len(this):
            if (icol == 0):
                # print("icol: ", icol)
                if (this[icol].strip().lower() == "~blank" or this[icol].strip().lower() == "~end"):
                    # print("this[icol].lower()")
                    # print(this[icol].lower())
                    rows_with_blank_or_end.append(irow)
            if (this[icol].strip() == '3'):
                if this[icol-1].strip() == '2' and this[icol-2].strip() == '1':
                    # need the +1 because it is the row below the 123 that we want
                    rows_with_1_2_3.append(irow+1)
                    cols_with_1_of_1_2_3.append(icol-2)

            icol = icol + 1
        irow = irow + 1

    irow = 0
    for this_len in file_length_list:
        if this_len < mean_len / 5.:
            rows_that_are_empty_all.append(irow)
        irow = irow + 1

    irow = 0
    for this in rows_that_are_empty_all:
        if irow > 0:
            if rows_that_are_empty_all[irow] == rows_that_are_empty_all[irow-1] + 1:
                pass
            else:
                if (irow > 5):
                    rows_that_are_empty_first_if_series.append(rows_that_are_empty_all[irow])
        else:
            if (irow > 5):
                rows_that_are_empty_first_if_series.append(rows_that_are_empty_all[irow])
        irow = irow + 1

    return [rows_with_1_2_3,
            cols_with_1_of_1_2_3,
            rows_with_blank_or_end,
            rows_that_are_empty_all,
            rows_that_are_empty_first_if_series]


# sck
def sub_function_inside_utils_plate_reader_map_file_find_blocks_format_is_1(
    file_list, file_length_list, form_number_blank_columns, set_number_blank_columns,
    rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series
    ):

    start_block_line_indexes = []
    start_block_delimiter_indexes = sorted(set(cols_idx_with_1_of_1_2_3))
    data_block_metadata = []
    mpc = ""
    tlc = ""
    tvc = ""
    wlc = ""
    wvc = ""

    i_count = 0
    i_metadata_count = 0
    while i_count < len(file_list):
        this_line = file_list[i_count]

        # Is column B of this line a value temperature - these are the top line of block
        # is the line null and are we on, at least, the 3rd row
        # get the associated metadata
        # Plate
        # Temperature
        # value temperature
        # Wave Length
        # value wave length
        mp = ""
        tl = ""
        tv = ""
        wl = ""
        wv = ""

        if len(this_line) > 1 and i_count > 1:
            # get column B
            element2 = this_line[1].strip()
            # if it is not null, try to convert it to a float
            if len(element2) > 0:
                try:
                    float(element2)
                    a_temperature = 'yes'
                except ValueError:
                    a_temperature = 'no'
            else:
                a_temperature = 'no'

            if a_temperature == 'yes':
                i_metadata_count = i_metadata_count + 1
                # save to list of line indexes (actually using the existance of meta data to identify the block location)
                start_block_line_indexes.append(i_count)
                # is it the first time seeing the metadata, if yes, assume it is complete and store it and append it
                if i_metadata_count == 1:
                    mpc = file_list[i_count - 2][1].strip()
                    # can change this to Temperature(deg C) here if wanted (if it is the temperature label confirm)
                    tlc = file_list[i_count - 1][1].strip()
                    tvc = file_list[i_count][1].strip()
                    wlc = file_list[i_count - 1][0].strip()
                    wvc = file_list[i_count][0].strip()
                    data_block_metadata.append(mpc + " " + tlc + " " + tvc + " " + wlc + " " + wvc)
                else:
                    mp = file_list[i_count - 2][1].strip()
                    tl = file_list[i_count - 1][1].strip()
                    tv = file_list[i_count][1].strip()
                    wl = file_list[i_count - 1][0].strip()
                    wv = file_list[i_count][0].strip()

                    if len(mp) == 0:
                        mp = mpc
                    if len(tl) == 0:
                        tl = tlc
                    if len(wl) == 0:
                        wl = wlc

                    data_block_metadata.append(mp + " " + tl + " " + tv + " " + wl + " " + wv)

        i_count = i_count + 1
    return start_block_line_indexes, start_block_delimiter_indexes, data_block_metadata


# sck
def sub_function_inside_utils_plate_reader_map_file_best_guess_block_detect(
        file_list,
        plate_rows, plate_columns,
        form_plate_size, set_plate_size,
        form_number_blank_columns, set_number_blank_columns,
        form_number_blank_rows, set_number_blank_rows,
        form_number_blocks, set_number_blocks,
        rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series
        ):

    # this function has not been robustly tested

    start_block_line_indexes = []
    start_block_delimiter_indexes = []
    data_block_metadata = []

    if set_number_blank_columns == 'true' and \
         form_number_blank_columns == 123:

        start_block_line_indexes = sorted(set(rows_idx_with_1_2_3))
        start_block_delimiter_indexes = sorted(set(cols_idx_with_1_of_1_2_3))
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif set_number_blocks == 'true' and form_number_blocks == 1 and \
         set_number_blank_columns == 'true' and \
         form_number_blank_columns != 123 and \
         set_number_blank_rows == 'true' and \
         form_number_blank_rows != 444:

        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns]
        data_block_metadata = ["Single Data Block"]

    elif set_number_blank_columns == 'true' and \
        form_number_blank_columns != 123 and \
        set_number_blank_rows == 'true' and \
        form_number_blank_rows != 444:

        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns]
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif set_number_blank_columns == 'true' and \
            form_number_blank_columns != 123 and \
            set_number_blank_rows == 'true' and \
            form_number_blank_rows == 444:

        # start_block_line_indexes = [x - plate_rows+1 for x in rows_idx_with_blank_or_end]
        start_block_line_indexes = [x - plate_rows for x in rows_idx_with_blank_or_end]
        start_block_delimiter_indexes = [form_number_blank_columns] * len(start_block_line_indexes)
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif set_number_blank_columns == 'true' and \
            form_number_blank_columns != 123 and \
            set_number_blank_rows == 'false':

        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns] * len(start_block_line_indexes)
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif set_number_blank_columns == 'false' and \
            set_number_blank_rows == 'true' and \
            form_number_blank_rows != 444:

        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns] * len(start_block_line_indexes)
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif len(cols_idx_with_1_of_1_2_3) > 0:
        start_block_line_indexes = sorted(set(rows_idx_with_1_2_3))
        start_block_delimiter_indexes = sorted(set(cols_idx_with_1_of_1_2_3))
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    elif len(rows_idx_with_blank_or_end) > 0:
        start_block_line_indexes = [x - plate_rows for x in rows_idx_with_blank_or_end]
        start_block_delimiter_indexes = [form_number_blank_columns] * len(start_block_line_indexes)
        data_block_metadata = [None] * (len(start_block_line_indexes) * len(start_block_delimiter_indexes))

    else:
        start_block_line_indexes = [form_number_blank_rows]
        start_block_delimiter_indexes = [form_number_blank_columns]
        data_block_metadata = ["no block information available"]

    return start_block_line_indexes, start_block_delimiter_indexes, data_block_metadata


# sck
def sub_function_inside_utils_plate_reader_map_file_guess_plate_size(
        file_list, file_length_list, form_number_blank_columns, set_number_blank_columns,
        rows_idx_with_1_2_3, cols_idx_with_1_of_1_2_3, rows_idx_with_blank_or_end, rows_that_are_empty_first_if_series):

    # function NOT robustly tested.....

    estimate_number_rows_by_123xtag = 0
    estimate_number_columns_by_123xtag = 0
    estimate_number_rows_to_first_tagged_blank = 0
    estimate_number_rows_by_empty_top = 0
    estimate_number_columns_by_length = 0

    # find mode of length of line (number fields)
    # this is based on assumption of vertical stacking and will not work for side-by-side stacking
    try:
        mode_file_length_list = mode(file_length_list)
    except:
        stats = Counter(file_length_list)
        my_maxes = [key for m in [max(stats.values())] for key, val in stats.items() if val == m]
        mode_file_length_list = my_maxes[-1]

    # if vertically stacked, the max number of columns is the most used and we can infer something about the plate size
    estimate_number_columns_by_length = mode_file_length_list

    if len(rows_idx_with_blank_or_end) > 0:
        estimate_number_rows_to_first_tagged_blank = rows_idx_with_blank_or_end[0]

    set_123 = sorted(set(rows_idx_with_blank_or_end))
    if len(set_123) > 1:
        estimate_number_rows_by_123xtag = set_123[1] - set_123[0]

    if len(cols_idx_with_1_of_1_2_3) > 1:
        estimate_number_columns_by_123xtag = cols_idx_with_1_of_1_2_3[1] - cols_idx_with_1_of_1_2_3[0]

    if len(rows_that_are_empty_first_if_series) > 0:
        estimate_number_rows_by_empty_top = rows_that_are_empty_first_if_series[0]

    if set_number_blank_columns == 'true' and form_number_blank_columns == 123 and estimate_number_columns_by_123xtag > 0:
        max_number_columns = estimate_number_columns_by_123xtag
        go_by = "cols"
    elif estimate_number_rows_by_123xtag > 0:
        max_number_of_rows = estimate_number_rows_by_123xtag
        go_by = "rows"
    elif estimate_number_rows_to_first_tagged_blank > 0:
        max_number_of_rows = estimate_number_rows_to_first_tagged_blank
        go_by = "rows"
    elif estimate_number_rows_by_empty_top > 0:
        max_number_of_rows = estimate_number_rows_by_empty_top
        go_by = "rows"
    else:
        # only works for vertically stacked
        max_number_columns = estimate_number_columns_by_length
        go_by = "cols"

    # todo-sck go back and streamline for all sizes in models
    # HARDCODED sizes
    if go_by == "cols":
        if max_number_columns < 12:
            plate_size = 24
        elif max_number_columns < 24:
            plate_size = 96
        else:
            plate_size = 384
    else:
        if max_number_of_rows < 8:
                plate_size = 24
        elif max_number_of_rows < 16:
            plate_size = 96
        else:
            plate_size = 384

    return plate_size

# sck adds the plate data to the map item value table when file form submitted
def add_update_plate_reader_data_map_item_values_from_file(
        pk_for_file,
        block_dict):
    """
    Assay PLATE READER FILE UPDATE puts information in the value item table extracted from the file (utility).
    """
    # this is called from views.py, not from ajax calls in the javascript files

    # What is sent into the function?
    # print('pk_for_file')
    # print(pk_for_file)
    # print('block_data_list_of_dicts')
    # print(block_data_list_of_dicts)
    # pk_for_file
    # 120
    # block_data_list_of_dicts - from AssayPlateReaderMapDataFileBlock
    # < QuerySet[
    #     {'id': 131, 'study_id': 293, 'assayplatereadermap_id': None, 'assayplatereadermapdatafile_id': 120,
    #     'assayplatereadermapdataprocessing_id': None, 'data_block': 1,
    #     'data_block_metadata': 'Plate#1 Temperature(�C) 26.30 Wavelength(nm) 350', 'line_start': 4,
    #     'line_end': 12, 'delimited_start': 3, 'delimited_end': 15, 'over_write_sample_time': None}, {
    #     'id': 132, 'study_id': 293, 'assayplatereadermap_id': None, 'assayplatereadermapdatafile_id': 120,
    #     'assayplatereadermapdataprocessing_id': None, 'data_block': 2,
    #     'data_block_metadata': 'Plate#1 Temperature(�C) 26.30 Wavelength(nm) 360', 'line_start': 13,
    #     'line_end': 21, 'delimited_start': 3, 'delimited_end': 15, 'over_write_sample_time': None}, {
    #   ] >

    true_to_continue = False
    # print("just set true to continue ", true_to_continue)

    pk_this_file = pk_for_file.id
    file_delimiter = pk_for_file.file_delimiter
    upload_plate_size = pk_for_file.upload_plate_size

    list_of_instances = []
    for each_block in block_dict.iterator():
        # if there are any matches for this block pk in the value items model, remove them
        # get the info out of the dictionary for this each_block
        pk_this_block = each_block.get('id')
        platemap_id = each_block.get('assayplatereadermap_id')
        datafile_id = each_block.get('assayplatereadermapdatafile_id')
        # processing_id = each_block.get('assayplatereadermapdataprocessing_id')
        block_label = each_block.get('data_block')
        block_metadata = each_block.get('data_block_metadata')
        data_processing_parsable = each_block.get('data_processing_parsable')
        l_start = each_block.get('line_start')
        l_end = each_block.get('line_end')
        d_start = each_block.get('delimited_start')
        d_end = each_block.get('delimited_end')
        o_time = each_block.get('over_write_sample_time')

        i_ls = l_start - 1
        i_le = l_end - 1
        i_ds = d_start - 1
        i_de = d_end - 1

        # if o_time == None:
        if o_time is None:
            true_to_overwrite_sample_time = False
        else:
            true_to_overwrite_sample_time = True

        try:
            # remember that this is in a loop for each data block in the file
            # if there are data in the map item value table related to this file, remove them all
            instance = AssayPlateReaderMapItemValue.objects.filter(assayplatereadermapdatafileblock=pk_this_block)
            instance.delete()
        except:
            pass

        if platemap_id is None:
            # there was not a plate map assigned to the current block of data in the loop
            # print("no platemap for this block ", pk_this_block, "  label ", block_label)
            pass
        else:
            # this is the guts of the adding data to the AssayPlateReaderMapItemValue table
            # remember, working in a loop for each block at a time
            # for the block, open the file and get the values and order them so they will match the plate index
            this_queryset = AssayPlateReaderMapDataFile.objects.get(
                id=pk_this_file
            )
            my_file_object = this_queryset.plate_reader_file.open()
            # this function is in utils.py
            returned_from_file_by_line = sub_function_inside_utils_plate_reader_map_file_by_line_del(
                my_file_object, file_delimiter)
            file_list = returned_from_file_by_line[0]
            # print('file_list')
            # print(file_list)

            # block indexes
            # i_ls = l_start - 1
            # i_le = l_end - 1
            # i_ds = d_start - 1
            # i_de = d_end - 1
            raw_value_list = []
            # go row then column
            for irow in range(i_ls, i_le+1):
                # print("irow ",irow, "   ", file_list[irow])
                for icol in range(i_ds, i_de+1):
                    # print("irow ",irow,"   icol ", icol)
                    this_raw_value_a = file_list[irow][icol]
                    try:
                        this_raw_value = float(this_raw_value_a)
                    except:
                        this_raw_value = None

                    raw_value_list.append(this_raw_value)

            # print("raw_value_list")
            # print(raw_value_list)
            # print(len(raw_value_list))

            # OLD - NOTE: after MUCH self debate, decided to leave a set of value items with NULL assayplatereadermapdatafileblock_id
            # get a copy of the value item set for each plate map
            # where the AssayPlateReaderMapItemValue.assayplatereadermapdatafileblock is null
            # this gets the default set of map item values
            # this_set_value_items = AssayPlateReaderMapItemValue.objects.filter(
            #     assayplatereadermap=platemap_id
            # ).filter(
            #     assayplatereadermapdatafileblock__isnull=True
            # ).order_by('plate_index',)

            # 20200522 changing schema since do not need to allow edit after plate map association
            this_set_value_items = AssayPlateReaderMapItem.objects.filter(
                assayplatereadermap=platemap_id
            ).order_by(
                'plate_index',
            )

            if len(raw_value_list) == len(this_set_value_items):
                true_to_continue = True
            else:
                true_to_continue = False
                err_msg = "There is a very bad error - the number of cells in the block do not match the number of rows in the values set. Sandra should be notified. The user will not see there raw data in the plate map when they expect to."
                print(err_msg)

            if true_to_continue:
                pidx = 0
                # go through each item of this platemap and make an
                # instance for this data block
                for item in this_set_value_items:
                    # will be sorted by plate index and should go from 0 to size of plate minus 1
                    # check for corruption
                    if item.plate_index == pidx:
                        # all is well, continue
                        # build the instance and append it

                        # do not forget about the overwrite sample time if one was provided
                        if true_to_overwrite_sample_time:
                            use_time = o_time
                        else:
                            use_time = item.default_time

                        # print("~plate_index: ", pidx)
                        # print("study: ", item.study_id)
                        # print("map: ", item.assayplatereadermap_id)
                        # print(pk_this_file)
                        # print(pk_this_block)
                        # print("item id: ", item.id)
                        # print("raw: ", raw_value_list[pidx])
                        # print("time: ", use_time)


                        # pay special attention to the reference to the assayplatereadermapitem_id=item.assayplatereadermapitem_id - this got corrupted before!
                        # pre 20200522
                        # instance = AssayPlateReaderMapItemValue(
                        #     plate_index=item.plate_index,
                        #     well_use=item.well_use,
                        #     raw_value=raw_value_list[pidx],
                        #     time=use_time,
                        #     assayplatereadermap_id=item.assayplatereadermap_id,
                        #     assayplatereadermapdatafile_id=pk_this_file,
                        #     assayplatereadermapdatafileblock_id=pk_this_block,
                        #     assayplatereadermapitem_id=item.assayplatereadermapitem_id,
                        #     study_id=item.study_id,
                        # )


                        instance = AssayPlateReaderMapItemValue(
                            study_id=item.study_id,
                            assayplatereadermap_id=item.assayplatereadermap_id,
                            assayplatereadermapdatafile_id=pk_this_file,
                            assayplatereadermapdatafileblock_id=pk_this_block,
                            assayplatereadermapitem_id=item.id,
                            raw_value=raw_value_list[pidx],
                            time=use_time,
                        )
                        # print(instance.assayplatereadermapitem)



                        # add this list to the list of lists
                        list_of_instances.append(instance)
                        true_to_continue = True
                    else:
                        true_to_continue = False
                        err_msg = "There is a very bad error - the plate index of the data coming in did not match the value set. Sandra should be notified. The user will not see there raw data in the plate map when they expect to."
                        print(err_msg)

                    pidx = pidx + 1

    # print("should be here: ", true_to_continue)
    if true_to_continue:
        # https://www.webforefront.com/django/multiplemodelrecords.html
        # https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
        # http://stefano.dissegna.me/django-pg-bulk-insert.html
        # https://stackoverflow.com/questions/15128705/how-to-insert-a-row-of-data-to-a-table-using-djangos-orm
        # add the data to AssayPlateReaderMapItemValue
        # print('list_of_instances')
        # print(list_of_instances)
        # duplicating the pks when do all at once....
        # this is much faster, but it only increments the pks for the first block...then, duplicate error!


        AssayPlateReaderMapItemValue.objects.bulk_create(list_of_instances)


        # with transaction.atomic():
        #     # Loop over each store and invoke save() on each entry
        #     for each in list_of_instances:
        #         # save() method called on each member to create record
        #         each.save()


    #         for query_instance in this_set.iterator():
    #             print(query_instance, query_instance.time, query_instance.well_use, query_instance.plate_index)

    return "done"


# sck - assay plate reader analysis of data when calibrating/processing
def plate_reader_data_file_process_data(set_dict):
    """
    Assay PLATE READER FILE Data Processing (utility) - called from web page and form save.
    """

    study = int(set_dict.get('study'))
    pk_platemap = int(set_dict.get('pk_platemap'))
    pk_data_block = int(set_dict.get('pk_data_block'))
    plate_name = set_dict.get('plate_name')
    form_calibration_curve = set_dict.get('form_calibration_curve')
    multiplier = set_dict.get('multiplier')
    unit = set_dict.get('unit')
    standard_unit = set_dict.get('standard_unit')
    form_min_standard = set_dict.get('form_min_standard')
    form_max_standard = set_dict.get('form_max_standard')
    form_logistic4_A = set_dict.get('form_logistic4_A')
    form_logistic4_D = set_dict.get('form_logistic4_D')
    form_blank_handling = set_dict.get('form_blank_handling')
    radio_standard_option_use_or_not = set_dict.get('radio_standard_option_use_or_not')
    radio_replicate_handling_average_or_not_0 = set_dict.get('radio_replicate_handling_average_or_not_0')
    borrowed_block_pk = int(set_dict.get('borrowed_block_pk'))
    borrowed_platemap_pk = int(set_dict.get('borrowed_platemap_pk'))
    count_standards_current_plate = int(set_dict.get('count_standards_current_plate'))
    target = set_dict.get('target')
    method = set_dict.get('method')
    time_unit = set_dict.get('time_unit')
    volume_unit = set_dict.get('volume_unit')
    called_from = set_dict.get('called_from')
    user_notes = set_dict.get('user_notes')
    user_omits = set_dict.get('user_omits')
    plate_size = set_dict.get('plate_size')

    sendGeneralQcErrorMessage = ''
    sendFitStandardsMessage = ''
    sendSampleProcessingMessage = ''

    # check for injection of invalid values
    try:
        multiplier = float(multiplier)
    except:
        multiplier = 1.0
    try:
        use_form_min = float(form_min_standard)
    except:
        use_form_min = -1.0
    try:
        use_form_max = float(form_max_standard)
    except:
        use_form_max = -1.0
    try:
        use_plate_size = int(plate_size)
    except:
        use_plate_size = 96
    try:
        passed_logistic4_A = float(form_logistic4_A)
    except:
        passed_logistic4_A = -1.0
    try:
        passed_logistic4_D = float(form_logistic4_D)
    except:
        passed_logistic4_D = -1.0

    # check for injection of invalid values and set to default if not in list
    # for the valid lists, search the forms.py for se_form_calibration_curve
    if radio_replicate_handling_average_or_not_0 not in ['average', 'each']:
        radio_replicate_handling_average_or_not_0 = 'each'
        sendGeneralQcErrorMessage = "Invalid entry - defaults used;  "
    if radio_standard_option_use_or_not not in ['pick_block', 'no_calibration']:
        radio_standard_option_use_or_not = 'no_calibration'
        sendGeneralQcErrorMessage = "Invalid entry - defaults used;  "
    if form_calibration_curve not in calibration_keys_list:
        form_calibration_curve = 'no_calibration'
        sendGeneralQcErrorMessage = "Invalid entry - defaults used;  "
    if form_blank_handling not in [
            'subtracteachfromeach',
            'subtractstandardfromstandard',
            'subtractsamplefromsample',
            'subtractstandardfromall',
            'subtractsamplefromall',
            'ignore']:
        form_blank_handling = 'ignore'
        sendGeneralQcErrorMessage = "Invalid entry - defaults used;  "

    # set defaults
    yes_to_continue = 'yes'
    yes_to_calibrate = 'yes'
    sample_blank_average = 0
    standard_blank_average = 0
    use_calibration_curve = form_calibration_curve
    use_file_pk_for_standards = pk_data_block
    use_platemap_pk_for_standards = pk_platemap
    dict_of_parameter_labels = ({'p1': '-', 'p2': '-', 'p3': '-', 'p4': '-', 'p5': '-'})
    dict_of_parameter_values = ({'p1': 0, 'p2': 0, 'p3': 0, 'p4': 0, 'p5': 0})
    dict_of_curve_info = ({'method': '-', 'equation': '-', 'rsquared': 0})
    dict_of_standard_info = ({'min': 0, 'max': 0, 'standard0average': 0, 'blankaverage': 0})
    list_of_dicts_of_each_standard_row_points = []
    list_of_dicts_of_each_standard_row_ave_points = []
    list_of_dicts_of_each_standard_row_curve = []
    list_of_dicts_of_each_sample_row_each = []
    list_of_dicts_of_each_sample_row_average = []
    notes = ''
    omits = False
    goBackToFileBlockRemovePlateMapToFixMessage = "To deal with this, go to the file block that uses this plate map and remove the plate map and save the file block, then, return to this plate map and add the required information and save. Go back to the file block and re-add this plate map. Return to this plate map and continue.; "
    goBackToFileBlockToFixFileBlockMessage = "A possible cause is that the file block was parsed correctly during file upload. Another possible cause is incorrect plate map setup. All wells designated as something other than empty should have a raw value.; "

    y_preds = []
    y_predStandards_logistic4 = []
    y_predStandards_logistic4a0 = []
    y_predStandards_logistic4f = []
    y_predStandards_linear = []
    y_predStandards_linear0 = []
    y_predStandards_log = []
    y_predStandards_poly2 = []
    slope_linear = 0
    icept_linear = 0
    slope_linear0 = 0
    icept_linear0 = 0
    A4 = 0
    B4 = 0
    C4 = 0
    D4 = 0
    A4a0 = 0
    B4a0 = 0
    C4a0 = 0
    D4a0 = 0
    A4f = 0
    B4f = 0
    C4f = 0
    D4f = 0
    A_log = 0
    B_log = 0
    A_poly2 = 0
    B_poly2 = 0
    C_poly2 = 0
    adj_mid = 0
    con_mid = 0
    number_standard_values_including_0 = 0
    number_standard_values_excluding_0 = 0
    special_note_when_excluding_0_and_curve_change_needed = ""
    # just declare these so can use the same fitting call that was made from later on in the code.
    caution_flag = ''
    df = 1
    cv = 1
    ct = 1

    # START Prelim QC SECTION Some QC that will cause errors if not detected up front
    # Important Note: 'ERROR' is searched in the js to decide if the graph should be shown!!!!

    # use to look for missing collection volume or time when normalizing
    standardunitCellsStart = re.search(r'cells', standard_unit.lower())
    unitCellsStart = re.search(r'cells', unit.lower())

    # use this from and join over and over again
    sqlsFromJoinMapItemID = " FROM ( assays_AssayPlateReaderMapItem "
    sqlsFromJoinMapItemID = sqlsFromJoinMapItemID + " INNER JOIN assays_AssayPlateReaderMapItemValue ON "
    sqlsFromJoinMapItemID = sqlsFromJoinMapItemID + " assays_AssayPlateReaderMapItem.id=assays_AssayPlateReaderMapItemValue.assayplatereadermapitem_id) "
    # use for QC over and over
    sFromWhereSAMPLEItem = " FROM assays_AssayPlateReaderMapItem "
    sFromWhereSAMPLEItem = sFromWhereSAMPLEItem + " WHERE assays_AssayPlateReaderMapItem.well_use = 'sample' "
    sFromWhereSAMPLEItem = sFromWhereSAMPLEItem + " and assays_AssayPlateReaderMapItem.assayplatereadermap_id = "
    sFromWhereSAMPLEItem = sFromWhereSAMPLEItem + str(pk_platemap)

    sAndRawValueNull = " and concat(trim(assays_AssayPlateReaderMapItemValue.raw_value::varchar(255)),'zz') = 'zz' "
    sAndMatrixItemNull = " and ( concat(trim(assays_AssayPlateReaderMapItem.matrix_item_id::varchar(255)),'zz') = 'zz' "
    sAndMatrixItemNull = sAndMatrixItemNull + " or assays_AssayPlateReaderMapItem.matrix_item_id = 0)"
    sAndLocationNull = " and ( concat(trim(assays_AssayPlateReaderMapItem.location_id::varchar(255)),'zz') = 'zz' "
    sAndLocationNull = sAndLocationNull + " or assays_AssayPlateReaderMapItem.location_id = 0)"
    sStandardValueNull = " and concat(trim(assays_AssayPlateReaderMapItem.standard_value::varchar(255)),'zz') = 'zz' "

    # QC - are there samples on this plate?
    # django orm - time compare for single table
    # start_time = time.time()
    # any_of_these = AssayPlateReaderMapItem.objects.filter(
    #     assayplatereadermap=pk_platemap
    # ).filter(
    #     well_use='sample'
    # )
    # if len(any_of_these) == 0:
    #     sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: There are no samples on this plate - no data to process. "
    #     sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
    #     yes_to_continue = 'no'
    # print("e1 time orm ",  time.time() - start_time)
    # sql - time compare
    # start_time = time.time()
    with connection.cursor() as cursor:
        sqls =        " SELECT COUNT(*) "
        sqls = sqls + sFromWhereSAMPLEItem
        # print("0: ", sqls)
        cursor.execute(sqls)
        results = cursor.fetchall()
        # print(results)
        results00 = results[0][0]
        # print("missing samples if == 0? ", results00)

        if results00 == 0:
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: There are no samples on this plate - no data to process. "
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
            yes_to_continue = 'no'
    # print("e1 time sql ", time.time() - start_time)

    # QC - look for samples, standards, or blanks with missing raw values (null)
    # django orm - compare time with link two tables
    # start_time = time.time()
    # any_of_these = AssayPlateReaderMapItemValue.objects.filter(
    #     assayplatereadermap=pk_platemap
    # ).filter(
    #     assayplatereadermapdatafileblock=pk_data_block
    # ).prefetch_related(
    #     'assayplatereadermapitem'
    # ).filter(
    #     Q(assayplatereadermapitem__well_use='sample') |
    #     Q(assayplatereadermapitem__well_use='blank') |
    #     Q(assayplatereadermapitem__well_use='standard') |
    #     Q(assayplatereadermapitem__well_use='standard_blank') |
    #     Q(assayplatereadermapitem__well_use='sample_blank')
    # )
    # if len(any_of_these) > 0:
    #         sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more samples, standards, or blanks have a null raw value in the file. "
    #         sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockToFixFileBlockMessage
    #         yes_to_continue = 'no'
    # print("e2 time orm ",  time.time() - start_time)
    # sql - time compare
    # start_time = time.time()
    # with connection.cursor() as cursor:
        sqls =        " SELECT COUNT(*) "
        sqls = sqls + sqlsFromJoinMapItemID
        sqls = sqls + " WHERE assays_AssayPlateReaderMapItemValue.assayplatereadermap_id = "
        sqls = sqls + str(pk_platemap) + " "
        sqls = sqls + " and (assays_AssayPlateReaderMapItem.well_use = 'sample' "
        sqls = sqls + " or assays_AssayPlateReaderMapItem.well_use = 'standard' "
        sqls = sqls + " or assays_AssayPlateReaderMapItem.well_use = 'sample_blank' "
        sqls = sqls + " or assays_AssayPlateReaderMapItem.well_use = 'standard_blank' "
        sqls = sqls + " or assays_AssayPlateReaderMapItem.well_use = 'blank') "
        sqls = sqls + " and assays_AssayPlateReaderMapItemValue.assayplatereadermapdatafileblock_id = "
        sqls = sqls + str(pk_data_block) + " "
        sqls = sqls + sAndRawValueNull
        # print("3998 look for null raws: ", sqls)
        cursor.execute(sqls)
        results = cursor.fetchall()
        # print(results)
        results00 = results[0][0]
        # print("missing sample raw values? ", results00)

        if results00 > 0:
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more samples, standards, or blanks have a null raw value in the file. "
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockToFixFileBlockMessage
            yes_to_continue = 'no'
    # print("e2 time sql ", time.time() - start_time)
    # in a test on a 96 well plate...that's a compelling reason
    # e1 time orm  0.011256933212280273
    # e1 time sql  0.0007350444793701172
    # e2 time orm  0.012610912322998047
    # e2 time sql  0.0013592243194580078

    # look for samples with missing matrix items
    # with connection.cursor() as cursor:
        sqls =        " SELECT COUNT(*) "
        sqls = sqls + sFromWhereSAMPLEItem
        sqls = sqls + sAndMatrixItemNull
        # print("2: ", sqls)
        cursor.execute(sqls)
        results = cursor.fetchall()
        # print(results)
        results00 = results[0][0]
        # print("missing matrix items? ", results00)

        if results00 > 0:
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more samples are missing a matrix item label. This will cause them to omitted from data processing. "
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
            yes_to_continue = 'no'

    # look for samples with missing sample locations
    # with connection.cursor() as cursor:
        sqls =        " SELECT COUNT(*) "
        sqls = sqls + sFromWhereSAMPLEItem
        sqls = sqls + sAndLocationNull
        # print("3: ", sqls)
        cursor.execute(sqls)
        results = cursor.fetchall()
        # print(results)
        results00 = results[0][0]
        # print("missing sample locations? ", results00)

        if results00 > 0:
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more samples are missing a matrix item label. This will cause them to be omitted from data processing. "
            sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
            yes_to_continue = 'no'


    # need to know what plate has standards for next QC check
    if form_calibration_curve == 'no_calibration':
        yes_to_calibrate = 'no'
    elif count_standards_current_plate == 0 and borrowed_block_pk < 1:
        yes_to_calibrate = 'no'
    elif count_standards_current_plate == 0:
        use_file_pk_for_standards = borrowed_block_pk
        use_platemap_pk_for_standards = borrowed_platemap_pk
    else:
        use_file_pk_for_standards = pk_data_block
        use_platemap_pk_for_standards = pk_platemap

    if yes_to_calibrate == 'yes':

        # need and use several times to get info for standards and standard blanks
        # Make sure these are AFTER the use plate map for standards is set
        sFromWhereSTNDItem = " FROM assays_AssayPlateReaderMapItem "
        sFromWhereSTNDItem = sFromWhereSTNDItem + " WHERE (assays_AssayPlateReaderMapItem.well_use = 'standard' "
        sFromWhereSTNDItem = sFromWhereSTNDItem + " or assays_AssayPlateReaderMapItem.well_use = 'standard_blank') "
        sFromWhereSTNDItem = sFromWhereSTNDItem + " and assays_AssayPlateReaderMapItem.assayplatereadermap_id = "
        sFromWhereSTNDItem = sFromWhereSTNDItem + str(use_platemap_pk_for_standards) + " "

        sWhereSTNDValue = " WHERE assays_AssayPlateReaderMapItemValue.assayplatereadermap_id = "
        sWhereSTNDValue = sWhereSTNDValue + str(use_platemap_pk_for_standards)
        sWhereSTNDValue = sWhereSTNDValue + " and (assays_AssayPlateReaderMapItem.well_use = 'standard' "
        sWhereSTNDValue = sWhereSTNDValue + " or assays_AssayPlateReaderMapItem.well_use = 'standard_blank') "
        sWhereSTNDValue = sWhereSTNDValue + " and assays_AssayPlateReaderMapItemValue.assayplatereadermapdatafileblock_id = "
        sWhereSTNDValue = sWhereSTNDValue + str(use_file_pk_for_standards) + " "

        # look for missing standard concentrations from the plate selected to use for standards
        with connection.cursor() as cursor:
            sqls =        " SELECT COUNT(*) "
            sqls = sqls + sFromWhereSTNDItem
            sqls = sqls + sStandardValueNull
            # print("5: ", sqls)
            cursor.execute(sqls)
            results = cursor.fetchall()
            # print(results)
            results00 = results[0][0]
            # print("missing standard concentrations for well use == standard on selected plate? ",results00)

            if results00 > 0:
                sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more of the wells in the plate map selected for standards are missing a standard concentration. "
                sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
                yes_to_continue = 'no'

        # look for missing standard raw values from the plate selected to use for standards
        # with connection.cursor() as cursor:
            sqls =        " SELECT COUNT(*) "
            sqls = sqls + sqlsFromJoinMapItemID
            sqls = sqls + sWhereSTNDValue
            sqls = sqls + sAndRawValueNull
            # print("look for null raws: ", sqls)
            cursor.execute(sqls)
            results = cursor.fetchall()
            # print(results)
            results00 = results[0][0]
            # print("missing raw standard values? ", results00)
            # print("4091 sqls ", sqls)
            if results00 > 0:
                sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: One or more of the wells in the plate selected for standards have a null raw value in the file. "
                sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + goBackToFileBlockRemovePlateMapToFixMessage
                yes_to_continue = 'no'

    # END Prelim QC SECTION end

    # if passed the preliminary QC, keep going, else, just send back the error message
    # all the other defaults (including the dictionaries) were set to empty above

    if yes_to_continue == 'yes':

        # EXTRA FOR CALIBRATION
        if yes_to_calibrate == 'yes':
            # what inner function for this case so can send global (this function) scope variables

            # Logistic 4 set bottom Parameter Set of Functions
            def plateMapLogistic4f(n, A, B, C, D):
                """4PL logistic equation."""
                if passed_logistic4_A == -1:
                    A
                else:
                    A = passed_logistic4_A
                if passed_logistic4_D == -1:
                    D = D
                else:
                    D = passed_logistic4_D
                signal = ((A - D) / (1.0 + ((n / C) ** B))) + D
                return signal

            def plateMapResidualsLogistic4f(p, r, n):
                """Deviations of data from fitted 4PL curve"""
                A, B, C, D = p
                if passed_logistic4_A == -1:
                    A
                else:
                    A = passed_logistic4_A
                if passed_logistic4_D == -1:
                    D = D
                else:
                    D = passed_logistic4_D
                err = r - plateMapLogistic4f(n, A, B, C, D)
                return err

            # need to deal with sample blanks

            # if subtracting (anything) by average of sample blanks,
            # get average, else, set it = 0 (then can always subtract)
            if form_blank_handling in ['subtracteachfromeach', 'subtractsamplefromsample', 'subtractsamplefromall']:
                # get the average of the sample blanks
                with connection.cursor() as cursor:
                    sqls = "SELECT AVG(assays_AssayPlateReaderMapItemValue.raw_value)"
                    sqls = sqls + sqlsFromJoinMapItemID
                    sqls = sqls + " WHERE assays_AssayPlateReaderMapItemValue.assayplatereadermapdatafileblock_id = "

                    # NOTE: the sample blanks MUST be on the same plate as the standards or this code needs to change!!
                    # this is the plate we are using for standards, if the assumption is that sample blanks
                    # would be on the sample plate, we could change this.
                    # I think it can just be changed back and forth, but, CHECK IT when someone actually does this.
                    # 20200528 Richard indicated he typically puts his standards, sample, and standard blanks on the same plate
                    # so, if borrowing standards from another plate, assume he is also borrowing sample blanks.
                    # sqls = sqls + str(pk_platemap)
                    sqls = sqls + str(use_file_pk_for_standards)
                    sqls = sqls + " and (assays_AssayPlateReaderMapItem.well_use = 'blank' "
                    sqls = sqls + "  or assays_AssayPlateReaderMapItem.well_use = 'sample_blank') "

                    # print("blank average sql: ", sqls)
                    cursor.execute(sqls)
                    results = cursor.fetchall()
                    results00 = results[0][0]

                    if results00 == None:
                        sample_blank_average = 0
                    else:
                        sample_blank_average = results00
            else:
                sample_blank_average = 0

            # if not given or not floatable, assume user wants to use all, so
            # find the min concentration in the plate setup that is being used for the standards
            if use_form_min == -1:
                # find the values we should use
                with connection.cursor() as cursor:
                    sqls = "SELECT "
                    sqls = sqls + " MIN(assays_AssayPlateReaderMapItem.standard_value) "
                    sqls = sqls + sFromWhereSTNDItem
                    # print("all standards sql1: ", sqls)
                    cursor.execute(sqls)
                    results = cursor.fetchall()
                    use_form_min = results[0][0]

            # if not given or not floatable, find the max concentration in the plate setup, so
            # find the max concentration in the plate setup that is being used for the standards
            if use_form_max == -1:
                # find the values we should use
                with connection.cursor() as cursor:
                    sqls = "SELECT "
                    sqls = sqls + " MAX(assays_AssayPlateReaderMapItem.standard_value) "
                    sqls = sqls + sFromWhereSTNDItem
                    # print("all standards sql2: ", sqls)
                    cursor.execute(sqls)
                    results = cursor.fetchall()
                    use_form_max = results[0][0]

            # should be what just found above OR the user entered min and/or max
            # print("use_form_min ", use_form_min)
            # print("use_form_max ", use_form_max)

            # if subtracting by average standard blank, get average, else, set it = 0
            if form_blank_handling in ['subtracteachfromeach', 'subtractstandardfromstandard', 'subtractstandardfromall']:
                # these are to use for 1) graphing and 2) curve fitting

                # get the standard blank average
                with connection.cursor() as cursor:
                    sqls = "SELECT AVG(assays_AssayPlateReaderMapItemValue.raw_value) "
                    sqls = sqls + sqlsFromJoinMapItemID
                    sqls = sqls + sWhereSTNDValue
                    sqls = sqls + " and assays_AssayPlateReaderMapItem.standard_value = 0"

                    # print("standard average sql: ", sqls)
                    cursor.execute(sqls)
                    results = cursor.fetchall()
                    results00 = results[0][0]

                    if results00 == None:
                        standard_blank_average = 0
                    else:
                        standard_blank_average = results00
            else:
                standard_blank_average = 0

            # print("sample_blank_average: ", sample_blank_average)
            # print("standard_blank_average: ", standard_blank_average)

            # There is a two level assignment of what is subtracted from what
            # first:
            #  -  a standard and sample blank average are calculated OR set to 0
            #     based on user selection of blank handling and if blanks on plate(s)
            # second:
            #  - if the user selected to use the standard blank average for all,
            #    or to use sample blanks for all, the calculated average is overwritten (below)

            # NOTE: the logic here will OVERWRITE what to subtract from samples/standards based on user choices
            # These will be used for now on and will show in the parameter details in the GUI
            if form_blank_handling == 'subtractstandardfromall':
                sample_blank_average = standard_blank_average
            elif form_blank_handling == 'subtractsamplefromall':
                standard_blank_average = sample_blank_average

            # for graphing - get all adjusted standards (POINTS)
            # Note, based on how the standard_blank_average had been set above
            # it is okay to treat all the blank handling conditions this way
            with connection.cursor() as cursor:
                sqls = "SELECT "
                sqls = sqls + "   assays_AssayPlateReaderMapItem.standard_value "
                sqls = sqls + ", (assays_AssayPlateReaderMapItemValue.raw_value-" + str(standard_blank_average) + ") as aRaw "
                sqls = sqls + ",  assays_AssayPlateReaderMapItemValue.raw_value "
                sqls = sqls + sqlsFromJoinMapItemID
                sqls = sqls + sWhereSTNDValue
                sqls = sqls + " ORDER BY assays_AssayPlateReaderMapItem.standard_value"
                # print("all standards sql: ", sqls)
                cursor.execute(sqls)
                mystandardsAll = cursor.fetchall()

            # print("all standards: ", mystandardsAll)

            # for fitting - get the average at each concentration that is IN user specified bounds
            # will subtract 0 in not adjusting, so okay to treat all the same
            # bounds should be set correctly if treat all the same (include all or some some subset of user selection)
            # with connection.cursor() as cursor:
                sqls = "SELECT "
                sqls = sqls + "  assays_AssayPlateReaderMapItem.standard_value "
                sqls = sqls + ", AVG(assays_AssayPlateReaderMapItemValue.raw_value-" + str(standard_blank_average) + ") as aRaw "
                sqls = sqls + ", AVG(assays_AssayPlateReaderMapItemValue.raw_value) "

                sqls = sqls + sqlsFromJoinMapItemID
                sqls = sqls + sWhereSTNDValue
                sqls = sqls + " and assays_AssayPlateReaderMapItem.standard_value >= "
                sqls = sqls + str(use_form_min) + " "
                sqls = sqls + " and assays_AssayPlateReaderMapItem.standard_value <= "
                sqls = sqls + str(use_form_max) + " "

                sqls = sqls + " GROUP BY assays_AssayPlateReaderMapItem.standard_value"
                sqls = sqls + " ORDER BY assays_AssayPlateReaderMapItem.standard_value"
                # print("all standards sql: ", sqls)
                cursor.execute(sqls)
                mystandardsAvg = cursor.fetchall()
            # print("mystandardsAvg: ", mystandardsAvg)

            # for fitting, use the first and second column of the one below
            NL = []
            SL = []
            NminNonZero = 9999999999
            Nmin = mystandardsAvg[0][0]
            Nmax = mystandardsAvg[0][0]
            Smin = mystandardsAvg[0][1]
            Smax = mystandardsAvg[0][1]
            for each in mystandardsAvg:
                this_row = {}
                xi = each[0]
                yi = each[1]

                this_row.update({'Concentration': xi})
                this_row.update({'Adjusted Observed Signal': yi})
                this_row.update({'Observed Signal': each[2]})
                # we will populate this field later
                this_row.update({'Fitted Signal': 0})
                list_of_dicts_of_each_standard_row_ave_points.append(this_row)

                NL.append(xi)
                SL.append(yi)
                if xi < Nmin:
                    Nmin = xi
                if yi < Smin:
                    Smin = yi
                if xi > Nmax:
                    Nmax = xi
                if yi > Smax:
                    Smax = yi
                if xi < NminNonZero and xi > 0:
                    NminNonZero = xi

            # need a 1D numpy array for least squares
            N = np.asarray(NL)
            S = np.asarray(SL)
            # print("N ",N)
            # print("S ",S)

            number_standard_values_including_0 = len(N)
            number_standard_values_excluding_0 = len(N)

            for each in N:
                if each == 0:
                    number_standard_values_excluding_0 = number_standard_values_excluding_0 - 1

            if len(N) < 4:
                sendGeneralQcErrorMessage = sendGeneralQcErrorMessage + "ERROR: There are not enough concentrations of standards in bounds (minimum of 4 needed for calibration);  "
                yes_to_continue = 'no'

    if yes_to_continue == 'yes':

        if yes_to_calibrate == 'yes':

            # FUN IS HERE

            # CALIBRATION OPTIONS ALL STARTING FROM
            # https://stats.stackexchange.com/questions/22718/what-is-the-difference-between-linear-regression-on-y-with-x-and-x-with-y
            # That is, we are saying that x is measured without error and constitutes the set of values we care about, but that y has sampling error.
            # https://www.abcam.com/ps/products/102/ab102526/documents/ab102526%20LDH%20Assay%20Kit%20Colorimetric%20protocol%20v13d%20(website).pdf
            # on page 15, the concentration is x and the OD is y. The equation is y = mx + b
            # with that in mind, the fitting was done with concentration as the x and signal as the y.

            r2 = {}

            if number_standard_values_including_0 >= 4:
                # if this condition is not met, it should have be caught in the the QC above

                if form_calibration_curve in ['linear', 'best_fit', 'log', 'logistic4', 'logistic4a0', 'logistic4f']:
                    # avg standard concentration - adjusted raw
                    # N = []
                    # S = []

                    # A is INTERCEPT!!!!!
                    # B is SLOPE!!!

                    # Initial guess for parameters A, B
                    A = 0
                    B = (Smax-Smin)/(Nmax-Nmin)
                    p0 = [A, B]

                    # Fit using least squares optimization
                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLinear, p0, args=(S, N), full_output=1)

                    A_linear = Sfitted[0]
                    B_linear = Sfitted[1]

                    y_predStandards_linear = plateMapLinear(N, A_linear, B_linear)

                    # print("calling linear rsquared")
                    rsquared_linear = plateMapRsquared(N, S, y_predStandards_linear)
                    r2['linear'] = rsquared_linear

                if form_calibration_curve in ['linear0', 'best_fit']:
                    # B is SLOPE!!!
                    A = 0
                    B = (Smax - Smin) / (Nmax - Nmin)
                    p0 = [A, B]
                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLinear0, p0, args=(S, N), full_output=1)
                    A_linear0 = Sfitted[0]
                    B_linear0 = Sfitted[1]
                    y_predStandards_linear0 = plateMapLinear(N, A_linear0, B_linear0)
                    rsquared_linear0 = plateMapRsquared(N, S, y_predStandards_linear0)
                    r2['linear0'] = rsquared_linear0

                if form_calibration_curve in ['poly2', 'best_fit']:
                    A = (Smax - Smin) / len(S)
                    B = (Smax - Smin) / (Nmax - Nmin)
                    C = (Nmax - Nmin) / 2
                    D = Smax
                    p0 = [A, B, C, D]
                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsPoly2, p0, args=(S, N), full_output=1)
                    A_poly2 = Sfitted[0]
                    B_poly2 = Sfitted[1]
                    C_poly2 = Sfitted[2]
                    D_poly2 = Sfitted[3]
                    y_predStandards_poly2 = plateMapPoly2(N, A_poly2, B_poly2, C_poly2, D_poly2)
                    rsquared_poly2 = plateMapRsquared(N, S, y_predStandards_poly2)
                    r2['poly2'] = rsquared_poly2

            if number_standard_values_excluding_0 >= 4:
                # this would not have been caught in the QC above, because the 0's were included for the general QC

                if form_calibration_curve in ['logistic4', 'best_fit']:
                    A = (Smax-Smin)/len(S)
                    B = (Smax-Smin)/(Nmax-Nmin)
                    C = (Nmax-Nmin)/2
                    D = Smax
                    # print("## A, B, C, D ", A, " ", B, " ", C, " ", D, " ")
                    p0 = [A, B, C, D]

                    # need to do some work to prep for logistic4 1) n cannot be 0 in fitting
                    if N[0] == 0:
                        Nno0 = np.delete(N, 0)
                        Sno0 = np.delete(S, 0)
                    else:
                        Nno0 = N
                        Sno0 = S

                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLogistic4, p0, args=(Sno0, Nno0), full_output=1)
                    A4 = Sfitted[0]
                    B4 = Sfitted[1]
                    C4 = Sfitted[2]
                    D4 = Sfitted[3]
                    y_predStandards_logistic4 = plateMapLogistic4(Nno0, A4, B4, C4, D4)
                    rsquared_logistic4 = plateMapRsquared(Nno0, Sno0, y_predStandards_logistic4)
                    r2['logistic4'] = rsquared_logistic4

                if form_calibration_curve in ['logistic4a0']:
                    # the should never be best fit, so don't bother to compute
                    # this was made before the option to set A and D, could redo to use that, but leave it for now
                    A = 0
                    B = (Smax-Smin)/(Nmax-Nmin)
                    C = (Nmax-Nmin)/2
                    D = Smax
                    # print("## A, B, C, D ", A, " ", B, " ", C, " ", D, " ")
                    p0 = [A, B, C, D]

                    # need to do some work to prep for logistic4a0 1) n cannot be 0 in fitting
                    if N[0] == 0:
                        Nno0 = np.delete(N, 0)
                        Sno0 = np.delete(S, 0)
                    else:
                        Nno0 = N
                        Sno0 = S

                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLogistic4a0, p0, args=(Sno0, Nno0), full_output=1)
                    A4a0 = Sfitted[0]
                    B4a0 = Sfitted[1]
                    C4a0 = Sfitted[2]
                    D4a0 = Sfitted[3]

                    y_predStandards_logistic4a0 = plateMapLogistic4a0(Nno0, A4a0, B4a0, C4a0, D4a0)
                    rsquared_logistic4a0 = plateMapRsquared(Nno0, Sno0, y_predStandards_logistic4a0)
                    # r2['logistic4a0'] = rsquared_logistic4a0

                # this really isn't a best file option because the A and D are only available if they pick logistic4f
                if form_calibration_curve in ['logistic4f']:
                    if passed_logistic4_A == -1:
                        A = (Smax - Smin) / len(S)
                    else:
                        A = passed_logistic4_A
                    if passed_logistic4_D == -1:
                        D = Smax
                    else:
                        D = passed_logistic4_D

                    B = (Smax-Smin)/(Nmax-Nmin)
                    C = (Nmax-Nmin)/2

                    # print("## A, B, C, D ", A, " ", B, " ", C, " ", D, " ")
                    p0 = [A, B, C, D]

                    # need to do some work to prep for logistic4 1) n cannot be 0 in fitting
                    if N[0] == 0:
                        Nno0 = np.delete(N, 0)
                        Sno0 = np.delete(S, 0)
                    else:
                        Nno0 = N
                        Sno0 = S

                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLogistic4f, p0, args=(Sno0, Nno0), full_output=1)
                    A4f = Sfitted[0]
                    B4f = Sfitted[1]
                    C4f = Sfitted[2]
                    D4f = Sfitted[3]
                    y_predStandards_logistic4f = plateMapLogistic4f(Nno0, A4f, B4f, C4f, D4f)
                    rsquared_logistic4f = plateMapRsquared(Nno0, Sno0, y_predStandards_logistic4f)
                    # do not want to consider for best fit
                    # r2['logistic4f'] = rsquared_logistic4

                if form_calibration_curve in ['log', 'best_fit']:
                    A = (Smax-Smin)/len(S)
                    B = (Smax-Smin)/(Nmax-Nmin)
                    p0 = [A, B]

                    # need to do some work to prep for log 1) no 0 allowed, and 2) could not take log in the fitting
                    if N[0] == 0:
                        Nno0 = np.delete(N, 0)
                        Sno0 = np.delete(S, 0)
                    else:
                        Nno0 = N
                        Sno0 = S

                    Sfitted, cost, info, msg, success = leastsq(plateMapResidualsLinear, p0, args=(Sno0, np.log(Nno0)), full_output=1)
                    A_log = Sfitted[0]
                    B_log = Sfitted[1]
                    y_predStandards_log = plateMapLinear(np.log(Nno0), A_log, B_log)

                    # print(Nno0)
                    # print(Sno0)

                    rsquared_log = plateMapRsquared(Nno0, Sno0, y_predStandards_log)
                    r2['log'] = rsquared_log


            # if best fit, find higheset rsquared
            if form_calibration_curve == 'best_fit':
                bestFitMethod = max(r2.items(), key=operator.itemgetter(1))[0]
                use_calibration_curve = bestFitMethod
            else:
                use_calibration_curve = form_calibration_curve

            if number_standard_values_excluding_0 < 4 and use_calibration_curve in ['log', 'logistic4', 'logistic4a0', 'logistic4f']:
                use_calibration_curve = 'linear'
                special_note_when_excluding_0_and_curve_change_needed = " IMPORTANT: Not enough standard concentrations for log or logistic."

            # do not move this into a place that it happens before selection of best fit!
            if use_calibration_curve in ['log', 'logistic4', 'logistic4a0', 'logistic4f']:
                use_form_min = Nno0[0]

            # make an array of Ns so that there will be 100ish fitted points on the graph
            # some fitting methods will get their 0 popped off
            theTop = use_form_max-use_form_min
            # print("theTop ",theTop)
            step = theTop/100.0
            # print("step ", step)

            N100x = [None] * 100;
            for i in range(0, 100):
                N100x[i] = i*step
                i = i + 1

            # 1D numpy array HANDY
            N100 = np.asarray(N100x)
            # 2D numpy array
            # N100 = np.array(N100x).reshape(-1, 1)

            if use_calibration_curve == 'linear':
                y_predStandards100 = plateMapLinear(N100, A_linear, B_linear)

                icept_linear = A_linear
                slope_linear = B_linear
                icept = sandrasGeneralFormatNumberFunction(A_linear)
                slope = sandrasGeneralFormatNumberFunction(B_linear)

                rsquared = '{:.5f}'.format(rsquared_linear)
                # equation = "Sample Fitted = (Adjusted Raw - (" + str(icept) + "))/" + str(slope)
                # equation = "Fitted = (Adjusted Signal - A)/B"
                #  (s = B*n + A)
                equation = "signal = B*concentration + A"

                dict_of_parameter_labels_linear = (
                    {'p1': 'Intercept (A)', 'p2': 'Slope (B)', 'p3': '-', 'p4': '-', 'p5': '-'})
                dict_of_parameter_values_linear = (
                    {'p1': icept, 'p2': slope, 'p3': 0, 'p4': 0, 'p5': 0})

                dict_of_curve_info_linear = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve})
                dict_of_standard_info_linear = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_linear
                dict_of_parameter_values = dict_of_parameter_values_linear
                dict_of_curve_info = dict_of_curve_info_linear
                dict_of_standard_info = dict_of_standard_info_linear

            elif use_calibration_curve == 'logistic4':
                if N100[0] == 0:
                    N100no0 = np.delete(N100, 0)
                else:
                    N100no0 = N100

                y_predStandards100 = plateMapLogistic4(N100no0, A4, B4, C4, D4)

                A_logistic4 = sandrasGeneralFormatNumberFunction(A4)
                B_logistic4 = sandrasGeneralFormatNumberFunction(B4)
                C_logistic4 = sandrasGeneralFormatNumberFunction(C4)
                D_logistic4 = sandrasGeneralFormatNumberFunction(D4)
                # print("&& A, B, C, D ", str(A_logistic4)," " , str(B_logistic4)," ", str(C_logistic4)," ", str(D_logistic4)," ")

                rsquared = '{:.5f}'.format(rsquared_logistic4)
                # equation = ftv = C4 * ( ( (A4 - D4)/( araw - D4) ) - 1 )**(1/B4)
                # equation = "Sample Fitted = " + C_logistic4 + " * { [ ( " + A_logistic4 + " - " + D_logistic4 + " ) / ( signal - " + D_logistic4 + " ) ] - 1 } ^ ( 1/" + B_logistic4 + " )"
                # (s = ((A-D) / (1.0 + ((n / C) ** B))) + D)
                equation = "signal = (A-D)/(1.0 + {[concentration/C]**B}) + D"

                dict_of_parameter_labels_logistic4 = (
                    {'p1': 'Theoretical response at zero concentration (A)', 'p2': 'Slope factor (B)', 'p3': 'Mid-range concentration (inflection point) (C)', 'p4': 'Theoretical response at infinite concentration (D)', 'p5': '-'})
                dict_of_parameter_values_logistic4 = (
                    {'p1': A_logistic4, 'p2': B_logistic4, 'p3': C_logistic4, 'p4': D_logistic4, 'p5': 0})

                dict_of_curve_info_logistic4 = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve })
                dict_of_standard_info_logistic4 = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_logistic4
                dict_of_parameter_values = dict_of_parameter_values_logistic4
                dict_of_curve_info = dict_of_curve_info_logistic4
                dict_of_standard_info = dict_of_standard_info_logistic4

                # print("A, B, C, D ", str(A4), " ", str(B4), " ", str(C4), " ", str(D4), " ")
                # print("(A4 - D4) ", str(A4 - D4))
                # print("(araw - D4) ", str(araw - D4))
                # print("(1 / B4) ", str(1 / B4))
                # print("(((A4 - D4) / (araw - D4)) - 1) ", str(((A4 - D4) / (araw - D4)) - 1))

            elif use_calibration_curve == 'logistic4a0':
                if N100[0] == 0:
                    N100no0 = np.delete(N100, 0)
                else:
                    N100no0 = N100

                y_predStandards100 = plateMapLogistic4a0(N100no0, A4a0, B4a0, C4a0, D4a0)

                A_logistic4a0 = sandrasGeneralFormatNumberFunction(A4a0)
                B_logistic4a0 = sandrasGeneralFormatNumberFunction(B4a0)
                C_logistic4a0 = sandrasGeneralFormatNumberFunction(C4a0)
                D_logistic4a0 = sandrasGeneralFormatNumberFunction(D4a0)

                rsquared = '{:.5f}'.format(rsquared_logistic4a0)
                equation = "signal = (0-D)/(1.0 + {[concentration/C]**B}) + D"

                dict_of_parameter_labels_logistic4a0 = (
                    {'p1': 'Theoretical response at zero concentration (A)', 'p2': 'Slope factor (B)', 'p3': 'Mid-range concentration (inflection point) (C)', 'p4': 'Theoretical response at infinite concentration (D)', 'p5': '-'})
                dict_of_parameter_values_logistic4a0 = (
                    {'p1': A_logistic4a0, 'p2': B_logistic4a0, 'p3': C_logistic4a0, 'p4': D_logistic4a0, 'p5': 0})

                dict_of_curve_info_logistic4a0 = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve })
                dict_of_standard_info_logistic4a0 = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_logistic4a0
                dict_of_parameter_values = dict_of_parameter_values_logistic4a0
                dict_of_curve_info = dict_of_curve_info_logistic4a0
                dict_of_standard_info = dict_of_standard_info_logistic4a0

            elif use_calibration_curve == 'logistic4f':
                if N100[0] == 0:
                    N100no0 = np.delete(N100, 0)
                else:
                    N100no0 = N100

                y_predStandards100 = plateMapLogistic4f(N100no0, A4f, B4f, C4f, D4f)

                A_logistic4f = sandrasGeneralFormatNumberFunction(A4f)
                B_logistic4f = sandrasGeneralFormatNumberFunction(B4f)
                C_logistic4f = sandrasGeneralFormatNumberFunction(C4f)
                D_logistic4f = sandrasGeneralFormatNumberFunction(D4f)

                rsquared = '{:.5f}'.format(rsquared_logistic4f)
                equation = "signal = (A-D)/(1.0 + {[concentration/C]**B}) + D"

                dict_of_parameter_labels_logistic4f = (
                    {'p1': 'Theoretical response at zero concentration (A)', 'p2': 'Slope factor (B)', 'p3': 'Mid-range concentration (inflection point) (C)', 'p4': 'Theoretical response at infinite concentration (D)', 'p5': '-'})
                dict_of_parameter_values_logistic4f = (
                    {'p1': A_logistic4f, 'p2': B_logistic4f, 'p3': C_logistic4f, 'p4': D_logistic4f, 'p5': 0})

                dict_of_curve_info_logistic4f = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve })
                dict_of_standard_info_logistic4f = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_logistic4f
                dict_of_parameter_values = dict_of_parameter_values_logistic4f
                dict_of_curve_info = dict_of_curve_info_logistic4f
                dict_of_standard_info = dict_of_standard_info_logistic4f

            elif use_calibration_curve == 'log':
                if N100[0] == 0:
                    N100no0 = np.delete(N100, 0)
                else:
                    N100no0 = N100

                y_predStandards100 = plateMapLinear(np.log(N100no0), A_log, B_log)

                A_logs = sandrasGeneralFormatNumberFunction(A_log)
                B_logs = sandrasGeneralFormatNumberFunction(B_log)

                rsquared = '{:.5f}'.format(rsquared_log)
                # equation = ftv = exp((s-A)/B)
                # equation = "Sample Fitted = exp((signal-" + A_logs + ")/"+ B_logs +")"
                #  (s = B*ln(n) + A)
                equation = "signal = B*ln(concentration) + A"

                dict_of_parameter_labels_log = (
                    {'p1': 'constant (A)', 'p2': 'coefficient of ln (B)', 'p3': '-', 'p4': '-', 'p5': '-'})
                dict_of_parameter_values_log = (
                    {'p1': A_logs, 'p2': B_logs, 'p3': 0, 'p4': 0, 'p5': 0})

                dict_of_curve_info_log = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve })
                dict_of_standard_info_log = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_log
                dict_of_parameter_values = dict_of_parameter_values_log
                dict_of_curve_info = dict_of_curve_info_log
                dict_of_standard_info = dict_of_standard_info_log

            elif use_calibration_curve == 'poly2':
                y_predStandards100 = plateMapPoly2(N100, A_poly2, B_poly2, C_poly2, D_poly2)

                A_poly2s = sandrasGeneralFormatNumberFunction(A_poly2)
                B_poly2s = sandrasGeneralFormatNumberFunction(B_poly2)
                C_poly2s = sandrasGeneralFormatNumberFunction(C_poly2)
                D_poly2s = sandrasGeneralFormatNumberFunction(D_poly2)

                rsquared = '{:.5f}'.format(rsquared_poly2)
                # equation = ftv = ( (-1*B_poly2) + ( (B_poly2**2) - (4*C_poly2*A_poly2) )**(1/2) ) / (2*C_poly2)
                # equation = "Sample Fitted = ( (-1*" + B_poly2s + ") +- ( (" + B_poly2s + "**2) - (4*" + C_poly2s + "*(" + A_poly2s + "-r)) )**(1/2) ) / (2*" + C_poly2s + ")"
                #  (s = C*n**2 + B*n + A)
                equation = "signal = C*n**2 + B*n + A"

                dict_of_parameter_labels_poly2 = (
                    {'p1': 'coefficient (A)', 'p2': 'coefficient of concentration (B)', 'p3': 'coefficient of concentration**2 (C)', 'p4': '-', 'p5': '-'})
                dict_of_parameter_values_poly2 = (
                    {'p1': A_poly2s, 'p2': B_poly2s, 'p3': C_poly2s, 'p4': 0, 'p5': 0})
                # print('A_poly2s ',A_poly2s)
                # print('B_poly2s ', B_poly2s)
                # print('C_poly2s ', C_poly2s)

                dict_of_curve_info_poly2 = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve })
                dict_of_standard_info_poly2 = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_poly2
                dict_of_parameter_values = dict_of_parameter_values_poly2
                dict_of_curve_info = dict_of_curve_info_poly2
                dict_of_standard_info = dict_of_standard_info_poly2

                # print(dict_of_parameter_labels)
                # print(dict_of_parameter_values)
                # print(dict_of_curve_info)
                # print(dict_of_standard_info)

            else:
                # use_calibration_curve == 'linear0':
                y_predStandards100 = plateMapLinear0(N100, A_linear0, B_linear0)

                icept_linear0 = A_linear0
                slope_linear0 = B_linear0
                icept = sandrasGeneralFormatNumberFunction(A_linear0)
                slope = sandrasGeneralFormatNumberFunction(B_linear0)

                rsquared = '{:.5f}'.format(rsquared_linear0)
                # equation = "Sample Fitted = (Adjusted Raw - 0)/" + str(slope)
                # equation = "Sample Fitted = (Adjusted Signal - A)/B"
                #  (s = B*n)
                equation = "signal = B*concentration"

                dict_of_parameter_labels_linear0 = (
                    {'p1': 'Intercept (A)', 'p2': 'Slope (B)', 'p3': '-', 'p4': '-', 'p5': '-'})
                dict_of_parameter_values_linear0 = (
                    {'p1': icept, 'p2': slope, 'p3': 0, 'p4': 0, 'p5': 0})

                dict_of_curve_info_linear0 = (
                    {'method': CALIBRATION_CURVE_MASTER_DICT.get(use_calibration_curve), 'equation': equation, 'rsquared': rsquared, 'used_curve': use_calibration_curve})
                dict_of_standard_info_linear0 = (
                    {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
                     'blankaverage': sample_blank_average})

                dict_of_parameter_labels = dict_of_parameter_labels_linear0
                dict_of_parameter_values = dict_of_parameter_values_linear0
                dict_of_curve_info = dict_of_curve_info_linear0
                dict_of_standard_info = dict_of_standard_info_linear0

            if use_calibration_curve == 'log' or use_calibration_curve == 'logistic4' or use_calibration_curve == 'logistic4a0' or use_calibration_curve == 'logistic4f':
                i = 0
                for each in N100no0:
                    this_row = {}
                    this_row.update({'Concentration': N100no0[i]})
                    this_row.update({'Observed Signal': None})
                    # FYI when using 2D numpy array....y_predStandards100[i] returns an array of 1
                    # when using 2D numpy array .... this_row.update({'Predicted Signal': y_predStandards100[i][0]})
                    this_row.update({'Predicted Signal': y_predStandards100[i]})
                    list_of_dicts_of_each_standard_row_curve.append(this_row)
                    i = i + 1

                con_mid = N100no0[50]

            else:
                i = 0
                for each in N100:
                    this_row = {}
                    this_row.update({'Concentration': N100[i]})
                    this_row.update({'Observed Signal': None})
                    # FYI when using 2D numpy array....y_predStandards100[i] returns an array of 1
                    # when using 2D numpy array .... this_row.update({'Predicted Signal': y_predStandards100[i][0]})
                    this_row.update({'Predicted Signal': y_predStandards100[i]})
                    list_of_dicts_of_each_standard_row_curve.append(this_row)
                    i = i + 1

                con_mid = N100[50]

            adj_mid = y_predStandards100[50]

            p = 0
            for each in list_of_dicts_of_each_standard_row_ave_points:
                CONC = each['Concentration']
                # print(p , "   ",CONC)
                if use_calibration_curve == 'linear':
                    myFit = plateMapLinear(CONC, A_linear, B_linear)
                elif use_calibration_curve == 'linear0':
                    myFit = plateMapLinear(CONC, A_linear0, B_linear0)
                elif use_calibration_curve == 'logistic4':
                    if CONC == 0:
                        myFit = ''
                    else:
                        myFit = plateMapLogistic4(CONC, A4, B4, C4, D4)
                elif use_calibration_curve == 'logistic4a0':
                    if CONC == 0:
                        myFit = ''
                    else:
                        myFit = plateMapLogistic4a0(CONC, A4a0, B4a0, C4a0, D4a0)
                elif use_calibration_curve == 'logistic4f':
                    if CONC == 0:
                        myFit = ''
                    else:
                        myFit = plateMapLogistic4f(CONC, A4f, B4f, C4f, D4f)
                elif use_calibration_curve == 'log':
                    if CONC == 0:
                        myFit = ''
                    else:
                        myFit = plateMapLinear(np.log(CONC), A_log, B_log)
                elif use_calibration_curve == 'poly2':
                    myFit = plateMapPoly2(CONC, A_poly2, B_poly2, C_poly2, D_poly2)
                else:
                    # 20201104 - changed the error message so it does not scare the user
                    err_msg = "Error - missing a calibration method."
                    print(err_msg)

                # print(p, "   ", myFit)
                each['Fitted Signal'] = myFit
                p = p + 1

            # load up the standards (points) row dictionary
            for each in mystandardsAll:
                this_row = {}
                this_row.update({'Concentration': each[0]})
                this_row.update({'Adjusted Observed Signal': each[1]})
                this_row.update({'Observed Signal': each[2]})
                # what would the fitted concentration be at this signal?
                araw = each[1]
                fitted_ftv_pdv_flags_sendFitStandardsMessage = plate_map_sub_return_the_fitted_and_other_info(
                    araw, df, cv, ct, caution_flag, notes, omits, sendFitStandardsMessage, standardunitCellsStart, unitCellsStart,
                    yes_to_calibrate, use_calibration_curve, multiplier, use_form_max, use_form_min,
                    slope_linear, icept_linear,
                    slope_linear0, icept_linear0,
                    A4, B4, C4, D4,
                    A4a0, B4a0, C4a0, D4a0,
                    A4f, B4f, C4f, D4f,
                    A_log, B_log,
                    A_poly2, B_poly2, C_poly2,
                    adj_mid, con_mid)
                # [ftv, pdv, caution_flag, sendFitStandardsMessage]
                ftv = fitted_ftv_pdv_flags_sendFitStandardsMessage[0]
                # print("ftv ",ftv)
                this_row.update({'Fitted Concentration': ftv})
                list_of_dicts_of_each_standard_row_points.append(this_row)

        # END EXTRA FOR CALIBRATION

    if yes_to_continue == 'yes':
        # same for all rows
        cross_reference = "Plate Reader Tool"
        subtarget = 'none'
        a_space = ' '

        # get info to load up the sample row dictionary
        with connection.cursor() as cursor:
            # 0, 1, 2, 3, 4
            sqls = "SELECT assays_AssayPlateReaderMapItem.plate_index"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.dilution_factor"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.location_id"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.matrix_item_id"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.collection_volume"
            # 5, 6, 7, 8, 9
            sqls = sqls + ", assays_AssayPlateReaderMapItem.collection_time"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.name"
            sqls = sqls + ", assays_AssayPlateReaderMapItem.well_use"
            sqls = sqls + ", assays_AssayPlateReaderMapItemValue.time"
            sqls = sqls + ", assays_AssayPlateReaderMapItemValue.raw_value"
            # 10, 11
            sqls = sqls + ", assays_AssaySampleLocation.name"
            sqls = sqls + ", assays_AssayMatrixItem.name"
            # 12 adjusted value(sample_blank_average will be 0 if not adjusting by sample blank
            # could also be overwritten with the standard blank average depending on selected blank handling
            # so do not need an if conditions here)
            sqls = sqls + ", (assays_AssayPlateReaderMapItemValue.raw_value"
            sqls = sqls + "-" + str(sample_blank_average) + ")"

            sqls = sqls + " FROM ((( assays_AssayPlateReaderMapItem "
            sqls = sqls + " INNER JOIN assays_AssayPlateReaderMapItemValue ON "
            sqls = sqls + " assays_AssayPlateReaderMapItem.id="
            sqls = sqls + " assays_AssayPlateReaderMapItemValue.assayplatereadermapitem_id) "
            sqls = sqls + " INNER JOIN assays_AssayMatrixItem ON "
            sqls = sqls + " assays_AssayPlateReaderMapItem.matrix_item_id=assays_AssayMatrixItem.id) "
            sqls = sqls + " INNER JOIN assays_AssaySampleLocation ON "
            sqls = sqls + " assays_AssayPlateReaderMapItem.location_id=assays_AssaySampleLocation.id) "

            # get this plate map, the samples, the selected (at the top) File/Block
            sqls = sqls + " WHERE assays_AssayPlateReaderMapItemValue.assayplatereadermap_id = "
            sqls = sqls + str(pk_platemap) + " "
            sqls = sqls + " and assays_AssayPlateReaderMapItem.well_use = 'sample' "
            sqls = sqls + " and assays_AssayPlateReaderMapItemValue.assayplatereadermapdatafileblock_id = "
            sqls = sqls + str(pk_data_block) + " "

            # need to order to find the replicates - use the key fields
            sqls = sqls + " ORDER by assays_AssayPlateReaderMapItem.well_use "
            sqls = sqls + " , assays_AssayPlateReaderMapItem.matrix_item_id "
            sqls = sqls + " , assays_AssayPlateReaderMapItemValue.time"
            sqls = sqls + " , assays_AssayPlateReaderMapItem.location_id"
            sqls = sqls + " , assays_AssayMatrixItem.name"

            # print("4770 sqls ", sqls)
            cursor.execute(sqls)
            # cursor.fetchone() or cursor.fetchall()
            myquery = cursor.fetchall()

            # print(myquery)

            # this will be a message for each row - so far, sendFitStandardsMessage is empty 20200530
            # sendFitStandardsMessage = sendFitStandardsMessage + "Fitting method: " + use_calibration_curve + ";  Standard minimum: " + str(use_form_min) + ";  Standard maximum: " + str(use_form_max) + ";  "
            sendFitStandardsMessage = "Fitting method: " + use_calibration_curve + ";  Standard minimum: " + str(use_form_min) + ";  Standard maximum: " + str(use_form_max) + ";  "

        # need the string info to get the notes and true/false if omit box is checked
        # need whenever processing, but only need to use if called when the replicate handling is average
        # which means, the user made changes to the Each table manually, then clicked the button to average
        # these lists index should be the plate index
        average_notes_list = []
        average_omits_list = []
        # split strings into lists - these are by plate map index (could all be empty, but that's okay)
        average_notes_list = user_notes.split("|")
        average_omits_list = user_omits.split("|")

        # print("len(average_notes_list) ", len(average_notes_list))
        # print("len(average_omits_list) ", len(average_omits_list))

        if use_plate_size != len(average_notes_list) or use_plate_size != len(average_omits_list):
            err_msg = "There is a very bad error - lengths of notes or omits are not the same as plate size."
            print(err_msg)

        # print('average_notes_list')
        # print(average_notes_list)
        # print('average_omits_list')
        # print(average_omits_list)

        # start for EACH, will always be 1 for average
        replicate = 1

        ######## s REPLICATES-GROUPING
        # set some previous of the key fields to use for first look at grouping
        # the key fields for determining a replicate (these should only be samples)
        # these are reset AFTER the group changes
        prevMxii = -1
        prevMxin = ""
        prevSt = -1
        prevLoci = -1
        prevLocn = ""
        prevWelln = ""
        # these are recalulated for each row and, when needed reset after the group changes
        cumNotes = ''
        cumWelln = ''
        cumCautionFlag = ''
        omitsFalseSum = 0
        valueSum = 0
        valueCount = 1

        # omitsFalseSum - what if all the replicates are marked for omit?
        # and/or, if there are not replicates but the one was marked for omit
        ####### e REPLICATES-GROUPING

        # For EACH row in the EACH table
        number_rows = len(myquery)
        row_counter = 1
        for each in myquery:
            # fields coming directly for sql queries
            pi = each[0]
            df = each[1]
            loci = each[2]
            mxii = each[3]
            cv = each[4]
            ct = each[5]
            welln = each[6]
            wellu = each[7]
            st = each[8]
            raw = each[9]
            locn = each[10]
            mxin = each[11]
            # adjusted raw value
            araw = each[12]

            # get for this row
            ftv = 0
            pdv = 0
            caution_flag = ''
            sendSampleProcessingMessage = ''
            notes = ''
            omits = 'false'
            notesPassed = 0
            omitsPassed = 0

            # process data (fitted and final value) for each row
            fitted_ftv_pdv_flags_sendmessage = plate_map_sub_return_the_fitted_and_other_info(
                araw, df, cv, ct, caution_flag, notes, omits, sendSampleProcessingMessage, standardunitCellsStart, unitCellsStart,
                yes_to_calibrate, use_calibration_curve, multiplier, use_form_max, use_form_min,
                slope_linear, icept_linear,
                slope_linear0, icept_linear0,
                A4, B4, C4, D4,
                A4a0, B4a0, C4a0, D4a0,
                A4f, B4f, C4f, D4f,
                A_log, B_log,
                A_poly2, B_poly2, C_poly2,
                adj_mid, con_mid)

            # [ftv, pdv, caution_flag, sendmessage]
            ftv = fitted_ftv_pdv_flags_sendmessage[0]
            pdv = fitted_ftv_pdv_flags_sendmessage[1]
            caution_flag = fitted_ftv_pdv_flags_sendmessage[2]
            sendSampleProcessingMessage = fitted_ftv_pdv_flags_sendmessage[3]
            notes = fitted_ftv_pdv_flags_sendmessage[4]
            omits = fitted_ftv_pdv_flags_sendmessage[5]

            notesPassed = average_notes_list[pi]
            omitsPassed = average_omits_list[pi]

            # print ("~~~~  ", pi, a_space,  df, a_space,  loci, a_space,  mxii, a_space,  cv, a_space,  ct, a_space,  welln)
            # print(wellu, a_space,  st, a_space,  raw, a_space,  locn, a_space,  mxin, a_space,  araw, a_space,  locn, a_space,  mxin, a_space,  araw)
            # print (ftv, a_space,  pdv, a_space,  caution_flag, a_space,  sendSampleProcessingMessage, a_space,  notes, a_space,  omits, a_space, notesPassed, a_space, omitsPassed)

            # print('---pi ', pi)
            # print('notes       ', notes)
            # print('notesPassed ', notesPassed)
            # print('omits       ', omits)
            # print('omitsPassed ', omitsPassed)

            if called_from == 'change_average' or called_from == 'form_save':
                # the user input (in memory from page or in form field from from save)
                # needs to overwrite what was just calculated (notes or omits)
                notes = notesPassed
                omits = omitsPassed

            # when doing EACH sample, get the replicate number right
            if prevMxii == mxii and prevSt == st and prevLoci == loci:
                # this is a replicate of the previous
                replicate = replicate + 1
            else:
                replicate = 1

            this_row_each = sub_to_load_processed_data_to_dict(
                replicate,
                mxii, mxin, loci, locn, st,
                welln, notes, omits, pdv,
                pi, df, cv, ct,
                raw, araw, ftv,
                cross_reference, subtarget, a_space,
                wellu, use_calibration_curve, time_unit, target, plate_name, method,
                standard_unit, sample_blank_average, volume_unit, multiplier,
                unit, caution_flag, sendFitStandardsMessage+sendSampleProcessingMessage
            )
            # add the dictionary to the list for each
            list_of_dicts_of_each_sample_row_each.append(this_row_each)

            ######## Note about Replicates-Grouping
            # I considered using a string_agg for the postgres tables, BUT, the problem is,
            # the manually entered notes and the manually changed omit check box
            # 1: are not saved in table, and 2: even if they were saved in the table,
            # they would not have been saved yet when being called from the web page.
            # So, used the old stand-bye of accumulating the fields as we go.
            # I don't love it because it is error prone.

            ######## s REPLICATES-GROUPING
            # print("Cumulating")
            # print("-----replicate number ", replicate)
            # print("prevMxii ",prevMxii, "  # current mxii ", mxii)
            # print("prevMxin ",prevMxin, "  # current mxin ", mxin)
            # print("prevSt ", prevSt, "  # current st ", st)
            # print("prevLoci ", prevLoci, "  # current loci ", loci)
            # print("prevLocn ", prevLocn, "  # current locn ", locn)
            # print("prevWelln ", prevWelln, "  # current welln ", welln)
            # print("cumNotes ", cumNotes, "  # currents notes ", notes)
            # print("cumCautionFlag ", cumCautionFlag, "  # current caution_flag ",caution_flag )
            # print('omitsFalseSum ', omitsFalseSum, "  # current omits ", omits)
            # print("current value ", pdv)
            # print("valueSum ", valueSum)
            # print("valueCount ", valueCount)

            if prevMxii == mxii and prevSt == st and prevLoci == loci:
                # print("this is a replicate of the previous")
                # if it is included, continue

                if omits == 'false':
                    # for the last row in the table,
                    # need to know if ANY in this group were unchecked (to include)
                    # keep track with this variable
                    omitsFalseSum = omitsFalseSum + 1

                    # is the current caution flag already in the string?
                    # only add if not in the string already
                    if cumCautionFlag.find(caution_flag) < 0:
                        cumCautionFlag = cumCautionFlag + caution_flag

                    # add the well name to the string A2 B2 etc
                    cumWelln = welln + " " + cumWelln

                    if len(notes.strip()) > 0:
                        cumNotes = cumNotes + ' | ' + notes.strip()

                    valueSum = valueSum + pdv
                    valueCount = valueCount + 1

            else:
                # print("this is the row AFTER the last in a replicate or last when no replicate")
                # print('omitsFalseSum ', omitsFalseSum)
                # where ANY in this group we are working with included? (eg not omitted)
                if omitsFalseSum > 0:
                    # at least one row in group was to be included
                    this_row_average = sub_to_load_processed_data_to_dict_limited(
                        1,
                        prevMxin, prevLocn, prevSt,
                        cumWelln, cumNotes, valueSum/valueCount,
                        cross_reference, subtarget, a_space,
                        time_unit, target, plate_name, method,
                        unit, cumCautionFlag, sendFitStandardsMessage+sendSampleProcessingMessage
                    )
                    # add the dictionary to the list for average
                    list_of_dicts_of_each_sample_row_average.append(this_row_average)
                # else:
                #     .print("omitsFalseSum not > 0")

                # IF this is NOT the last row, reset to start for NEXT loop through
                # in the SAME group as sitting on, or a complete different group if no replicates of one sitting on
                # If the last row, want to keep the last settings
                if (row_counter < number_rows):
                    if (omits == 'false'):
                        # the point we are sitting on WILL be included, so set with this points info
                        cumNotes = notes
                        cumWelln = welln
                        cumCautionFlag = caution_flag
                        omitsFalseSum = 1
                        valueSum = pdv
                        valueCount = 1

                    else:
                        # the point we are sitting on will NOT be included, so do not set its info
                        cumNotes = ''
                        cumWelln = ''
                        cumCautionFlag = ''
                        omitsFalseSum = 0
                        valueSum = 0
                        valueCount = 0

            # always reset the previous key fields for determining a replicate (these should only be samples)
            prevMxii = mxii
            prevSt = st
            prevLoci = loci
            prevWelln = welln
            prevLocn = locn
            prevMxin = mxin
            row_counter = row_counter + 1

        # Now, out of the loop of rows.
        # Need to add information, multiple conditions:
        # - last row was last in a replicate group
        # --there could be none that are included in the group, so don't write
        # --there could be some included, but not this one, write
        # --there could be none but this one included, write
        # --this one is include, but none others, write
        # - an individual row, not part of a replicte group
        # --if included, write
        # --if not included, don't write
        # in all cases where writing is required, omitsFalseSum > 0
        # print("on last record, what is omitsFalseSum: ", omitsFalseSum)
        if omitsFalseSum > 0:
            this_row_average = sub_to_load_processed_data_to_dict_limited(
                1,
                mxin, locn, st,
                cumWelln, cumNotes, valueSum / valueCount,
                cross_reference, subtarget, a_space,
                time_unit, target, plate_name, method,
                unit, cumCautionFlag, sendFitStandardsMessage+sendSampleProcessingMessage
            )
            # print("sum > 0 last row average ", this_row_average)
            # add the dictionary to the list for average
            list_of_dicts_of_each_sample_row_average.append(this_row_average)
        ######## s REPLICATES-GROUPING - what started in the loop ends here

        # print('***list_of_dicts_of_each_sample_row_each going back to ajax')
        # print(list_of_dicts_of_each_sample_row_each)
        # print('***list_of_dicts_of_each_standard_row_ave_points')
        # print(list_of_dicts_of_each_standard_row_ave_points)
        # print("list_of_dicts_of_each_sample_row_average ")
        # print(list_of_dicts_of_each_sample_row_average)

    # if failed one or more of QC, only the sendGeneralQcErrorMessage should be populated
    return [sendGeneralQcErrorMessage + special_note_when_excluding_0_and_curve_change_needed,
            list_of_dicts_of_each_sample_row_each,
            list_of_dicts_of_each_standard_row_points,
            list_of_dicts_of_each_standard_row_ave_points,
            list_of_dicts_of_each_standard_row_curve,
            dict_of_parameter_labels,
            dict_of_parameter_values,
            dict_of_curve_info,
            dict_of_standard_info,
            list_of_dicts_of_each_sample_row_average]


# sck
def sub_to_load_processed_data_to_dict(
        replicate,
        mxii, mxin, loci, locn, st,
        welln, notes, omits, pdv,
        pi, df, cv, ct,
        raw, araw, ftv,
        cross_reference, subtarget, a_space,
        wellu, use_calibration_curve, time_unit, target, plate_name, method,
        standard_unit, sample_blank_average, volume_unit, multiplier,
        unit, caution_flag, sendmessage
        ):
    # print('notes- ', notes)
    # print('omits- ', omits)
    # pi = str(each[0])
    # df = str(each[1])
    # loci = str(each[2])
    # mxii = str(each[3])
    # cv = str(each[4])
    # ct = str(each[5])
    # welln = str(each[6])
    # wellu = str(each[7])
    # st = str(each[8])
    # raw = str(each[9])
    # locn = str(each[10])
    # mxin = str(each[11])
    # # adjusted raw value
    # araw = str(each[12])
    # ftv = str(ftv)
    # pdv = str(pdv)

    pi = str(pi)
    df = str(df)
    loci = str(loci)
    mxii = str(mxii)
    cv = str(cv)
    ct = str(ct)
    welln = str(welln)
    wellu = str(wellu)
    st = str(st)
    raw = str(raw)
    locn = str(locn)
    mxin = str(mxin)
    araw = str(araw)
    ftv = str(ftv)
    # print("pdv before string ",pdv)
    pdv = str(pdv)
    multiplier = str(multiplier)

    # print("multiplier ", multiplier)

    this_row = {}
    # for each - do every time
    # 0,1,2,3
    this_row.update({'plate_index'              : pi                    })
    this_row.update({'matrix_item_name'         : mxin                  })
    this_row.update({'matrix_item_id'           : mxii                  })
    this_row.update({'cross_reference'          : cross_reference       })
    # 4,5,6
    this_row.update({'plate_name'               : plate_name            })
    this_row.update({'well_name'                : welln                 })
    this_row.update({'well_use'                 : wellu                  })
    # 7,8,9
    if (time_unit == 'Day' or time_unit == 'day'):
        this_row.update({'day'                  : st                    })
        this_row.update({'hour': '0'     })
        this_row.update({'minute': '0'     })
    elif (time_unit == 'Hour' or time_unit == 'hour'):
        this_row.update({'day': '0'})
        this_row.update({'hour'                 : st                    })
        this_row.update({'minute': '0'     })
    else:
        this_row.update({'day': '0'     })
        this_row.update({'hour': '0'     })
        this_row.update({'minute'               : st                    })
    # 10,11,12,13,14
    this_row.update({'target'                   : target                })
    this_row.update({'subtarget'                : subtarget             })
    this_row.update({'method'                   : method                })
    this_row.update({'location_name'            : locn                  })
    this_row.update({'location_id'              : loci                  })
    # 15,16,17
    this_row.update({'raw_value'                : raw                   })
    this_row.update({'standard_unit'            : standard_unit         })
    this_row.update({'average_blank'            : sample_blank_average  })
    # 18,19
    if use_calibration_curve == 'no_calibration':
        this_row.update({'adjusted_raw'             : a_space           })
        this_row.update({'fitted_value'             : a_space           })
    else:
        this_row.update({'adjusted_raw'             : araw              })
        this_row.update({'fitted_value'             : ftv               })
    # 20,21,22,23
    this_row.update({'dilution_factor'          : df                    })
    this_row.update({'collection_volume'        : cv                    })
    this_row.update({'volume_unit'              : volume_unit           })
    this_row.update({'collection_time'          : ct                    })
    # 24,25,26,27
    # need to string the multiplier because, if it is small, it will show as 0
    this_row.update({'multiplier'               : multiplier            })
    this_row.update({'processed_value'          : pdv                   })
    this_row.update({'unit'                     : unit                  })
    this_row.update({'replicate'                : replicate             })
    # 28,29,30,31
    this_row.update({'caution_flag'             : caution_flag          })
    this_row.update({'exclude'                  : a_space               })
    this_row.update({'notes'                    : notes                 })
    this_row.update({'sendmessage'              : sendmessage           })
    this_row.update({'omits'                    : omits                 })
    return this_row


# sck
# 1,
# mxin, locn, st,
# cumWelln, cumNotes, valueSum / valueCount,
# cross_reference, subtarget, a_space,
# time_unit, target, plate_name, method,
# unit, cumCautionFlag, sendFitStandardsMessage
# search term MIFC - if MIFC changes, this will need changed
def sub_to_load_processed_data_to_dict_limited(
        replicate,
        mxin, locn, st,
        welln, notes, pdv,
        cross_reference, subtarget, a_space,
        time_unit, target, plate_name, method,
        unit, caution_flag, sendmessage
        ):
    # print('notes- ', notes)
    # print('omits- ', omits)
    # pi = str(each[0])
    # df = str(each[1])
    # loci = str(each[2])
    # mxii = str(each[3])
    # cv = str(each[4])
    # ct = str(each[5])
    # welln = str(each[6])
    # wellu = str(each[7])
    # st = str(each[8])
    # raw = str(each[9])
    # locn = str(each[10])
    # mxin = str(each[11])
    # # adjusted raw value
    # araw = str(each[12])
    # ftv = str(ftv)
    # pdv = str(pdv)

    welln = str(welln)
    st = str(st)
    locn = str(locn)
    mxin = str(mxin)
    pdv = str(pdv)

    this_row = {}
    # for each - do every time
    # 0,1,2,3
    # this_row.update({'plate_index'              : pi                    })
    this_row.update({'matrix_item_name'         : mxin                  })
    # this_row.update({'matrix_item_id'           : mxii                  })
    this_row.update({'cross_reference'          : cross_reference       })
    # 4,5,6
    this_row.update({'plate_name'               : plate_name            })
    this_row.update({'well_name'                : welln                 })
    # this_row.update({'well_use'                 : wellu                  })
    # 7,8,9
    if (time_unit == 'Day' or time_unit == 'day'):
        this_row.update({'day'                  : st                    })
        this_row.update({'hour': '0'     })
        this_row.update({'minute': '0'     })
    elif (time_unit == 'Hour' or time_unit == 'hour'):
        this_row.update({'day': '0'})
        this_row.update({'hour'                 : st                    })
        this_row.update({'minute': '0'     })
    else:
        this_row.update({'day': '0'     })
        this_row.update({'hour': '0'     })
        this_row.update({'minute'               : st                    })
    # 10,11,12,13,14
    this_row.update({'target'                   : target                })
    this_row.update({'subtarget'                : subtarget             })
    this_row.update({'method'                   : method                })
    this_row.update({'location_name'            : locn                  })
    # this_row.update({'location_id'              : loci                  })
    # 15,16,17
    # this_row.update({'raw_value'                : raw                   })
    # this_row.update({'standard_unit'            : standard_unit         })
    # this_row.update({'average_blank'            : sample_blank_average  })
    # 18,19
    # if use_calibration_curve == 'no_calibration':
    #     this_row.update({'adjusted_raw'             : a_space           })
    #     this_row.update({'fitted_value'             : a_space           })
    # else:
    #     this_row.update({'adjusted_raw'             : araw              })
    #     this_row.update({'fitted_value'             : ftv               })
    # 20,21,22,23
    # this_row.update({'dilution_factor'          : df                    })
    # this_row.update({'collection_volume'        : cv                    })
    # this_row.update({'volume_unit'              : volume_unit           })
    # this_row.update({'collection_time'          : ct                    })
    # 24,25,26,27
    # this_row.update({'multiplier'               : multiplier            })
    this_row.update({'processed_value'          : pdv                   })
    this_row.update({'unit'                     : unit                  })
    this_row.update({'replicate'                : replicate             })
    # 28,29,30,31
    this_row.update({'caution_flag'             : caution_flag          })
    this_row.update({'exclude'                  : a_space               })
    this_row.update({'notes'                    : notes                 })
    this_row.update({'sendmessage'              : sendmessage           })
    # this_row.update({'omits'                    : omits                 })
    return this_row


# sck
def plate_map_sub_return_the_fitted_and_other_info(
    araw, df, cv, ct, caution_flag, notes, omits, sendmessage, standardunitCellsStart, unitCellsStart,
    yes_to_calibrate, use_calibration_curve, multiplier, use_form_max, use_form_min,
    slope_linear, icept_linear,
    slope_linear0, icept_linear0,
    A4, B4, C4, D4,
    A4a0, B4a0, C4a0, D4a0,
    A4f, B4f, C4f, D4f,
    A_log, B_log,
    A_poly2, B_poly2, C_poly2,
    adj_mid, con_mid):

    ftv = araw

    if yes_to_calibrate == 'no' or use_calibration_curve == 'no_calibration':
        ftv = araw

    elif use_calibration_curve == 'linear':
        if slope_linear == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " Slope is 0. Cannot calculate fitted value."
        else:
            ftv = (araw - icept_linear) / slope_linear

    elif use_calibration_curve == 'logistic4':
        if araw - D4 == 0 or B4 == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " A denominator is 0. Cannot calculate fitted value."
        else:
            try:
                ftv = C4 * (((A4 - D4) / (araw - D4)) - 1) ** (1 / B4)
                if str(ftv).lower().strip() == 'nan':

                    if araw < A4:
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Sample value too small to calculate."
                        # here here if change their mind and want the theoretical response at 0
                        # ftv = A4
                        # caution_flag = 'e'
                        # sendmessage = sendmessage + " Sample value too small to calculate; set to theoretical response at zero concentration (A)."
                    else:
                        # print("araw,    A,    B,    C,    D ")
                        # print(str(araw), " ", str(A4), " ", str(B4), " ", str(C4), " ", str(D4))
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Cannot calculate fitted value."
            except:
                ftv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Cannot calculate fitted value. Likely due to very large exponent."

    elif use_calibration_curve == 'logistic4a0':
        if araw - D4a0 == 0 or B4a0 == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " A denominator is 0. Cannot calculate fitted value."
        else:
            try:
                ftv = C4a0 * (((A4a0 - D4a0) / (araw - D4a0)) - 1) ** (1 / B4a0)
                if str(ftv).lower().strip() == 'nan':

                    if araw < A4a0:
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Sample value too small to calculate."
                        # here here if change their mind and want the theoretical response at 0
                        # ftv = A4a0
                        # caution_flag = 'e'
                        # sendmessage = sendmessage + " Sample value too small to calculate; set to theoretical response at zero concentration (A)."
                    else:
                        # print("araw,    A,    B,    C,    D ")
                        # print(str(araw), " ", str(A4a0), " ", str(B4a0), " ", str(C4a0), " ", str(D4a0))
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Cannot calculate fitted value."
            except:
                ftv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Cannot calculate fitted value. Likely due to very large exponent."

    elif use_calibration_curve == 'logistic4f':
        if araw - D4f == 0 or B4f == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " A denominator is 0. Cannot calculate fitted value."
        else:
            try:
                ftv = C4f * (((A4f - D4f) / (araw - D4f)) - 1) ** (1 / B4f)
                if str(ftv).lower().strip() == 'nan':

                    if araw < A4f:
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Sample value too small to calculate."
                        # here here if change their mind and want the theoretical response at 0
                        # ftv = A4f
                        # caution_flag = 'e'
                        # sendmessage = sendmessage + " Sample value too small to calculate; set to theoretical response at zero concentration (A)."
                    else:
                        # print("araw,    A,    B,    C,    D ")
                        # print(str(araw), " ", str(A4f), " ", str(B4f), " ", str(C4f), " ", str(D4f))
                        ftv = " "
                        caution_flag = 'F'
                        sendmessage = sendmessage + " Cannot calculate fitted value."
            except:
                ftv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Cannot calculate fitted value. Likely due to very large exponent."

    elif use_calibration_curve == 'log':
        if B_log == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " A denominator is 0. Cannot calculate fitted value."
        else:
            try:
                ftv = math.exp((araw - A_log) / B_log)
            except:
                ftv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Cannot calculate fitted value. Likely due to very large exponent."

    elif use_calibration_curve == 'poly2':
        # print("araw ",araw)
        # because I want the runtime warning to be trapped in this specific case

        if C_poly2 == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " A denominator is 0. Cannot calculate fitted value."
        else:
            warnings.filterwarnings("error")
            try:
                ftv1 = ((-1 * B_poly2) + ((B_poly2 ** 2) - (4 * C_poly2 * (A_poly2 - araw))) ** (1 / 2)) / (2 * C_poly2)
            except RuntimeWarning:
                ftv1 = None
            try:
                ftv2 = ((-1 * B_poly2) - ((B_poly2 ** 2) - (4 * C_poly2 * (A_poly2 - araw))) ** (1 / 2)) / (2 * C_poly2)
            except RuntimeWarning:
                ftv2 = None
            warnings.filterwarnings("default")

            # if ftv1 >= 0:
            #     ftv = ftv1
            #     # print("one")
            # else:
            #     ftv = ftv2
            #     # print("two")
            #
            # print("ftv1 ", ftv1)
            # print("ftv2 ", ftv2)
            #
            # # always pick the positive root
            # ftv = ftv1

            # how to pick the root
            if ftv1 is None and ftv2 is None:
                ftv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Cannot calculate fitted value."
            elif ftv1 is None:
                ftv = ftv2
            elif ftv2 is None:
                ftv = ftv1
            elif (araw <= adj_mid and ftv1 <= con_mid) or (araw > adj_mid and ftv1 > con_mid):
                ftv = ftv1
            elif (araw <= adj_mid and ftv2 <= con_mid) or (araw > adj_mid and ftv2 > con_mid):
                ftv = ftv2
            else:
                ftv = ftv1

    else:
        # elif use_calibration_curve == 'linear0':
        if slope_linear0 == 0:
            ftv = " "
            caution_flag = 'F'
            sendmessage = sendmessage + " Slope is 0. Cannot calculate fitted value."
        else:
            ftv = araw / slope_linear0

    # WATCH if change this above, will not work here!! Be careful.
    if ftv != " ":
        # adjust by normalization
        if standardunitCellsStart == None and unitCellsStart != None:
            if (cv == 0 or ct == 0):
                pdv = " "
                caution_flag = 'F'
                sendmessage = sendmessage + " Collection volume or collection time = 0.;"
            else:
                pdv = ftv * multiplier * df * cv / ct
        else:
            pdv = ftv * multiplier * df

        if yes_to_calibrate == 'yes':
            if ftv > use_form_max:
                caution_flag = 'E'
            if ftv < use_form_min:
                caution_flag = 'E'
    else:
        pdv = " "

    if len(caution_flag) > 0:
        omits = 'true'
    else:
        omits = 'false'
    return [ftv, pdv, caution_flag, sendmessage, notes, omits]


# sck
# Find the R Squared
def plateMapRsquared(N, S, y_predStandards):

    # y is Signal S     x is concentration N
    # print("N ", N)
    # print("S ", S)

    yAve = sum(S) / len(S)
    # print("yAve  ", yAve)

    y_obs_minus_fitted = [None] * len(N)
    y_obs_minus_ave = [None] * len(N)

    y_obs_minus_fitted_s = [None] * len(N)
    y_obs_minus_ave_s = [None] * len(N)

    # xAve = sum(N) / len(N)

    i = 0
    for n in N:
        y_obs_minus_fitted[i] = S[i] - y_predStandards[i]
        # print("y_obs_minus_fitted[i] ",y_obs_minus_fitted[i])
        y_obs_minus_ave[i] = S[i] - yAve
        # print("y_obs_minus_ave[i] ", y_obs_minus_ave[i])

        y_obs_minus_fitted_s[i] = (y_obs_minus_fitted[i]) ** 2
        # print("y_obs_minus_fitted_s[i] ", y_obs_minus_fitted_s[i])
        y_obs_minus_ave_s[i] = (y_obs_minus_ave[i]) ** 2
        # print("y_obs_minus_ave_s[i] ", y_obs_minus_ave_s[i])

        i = i + 1

    # https://medium.com/@erika.dauria/looking-at-r-squared-721252709098
    rsquared = 1 - sum(y_obs_minus_fitted_s) / sum(y_obs_minus_ave_s)

    # http://ww2.tnstate.edu/ganter/BIO%20311%20Ch%2012%20Regression.html
    return rsquared


# sck
# Logistic 4 Parameter Set of Functions
# https://people.duke.edu/~ccc14/pcfb/analysis.html
# equations sck using for fitting in plate reader calibration
#  n is concentration, returns Signal
# when this is called with the leastsq wrapper, r is the signal array, n is the concentration array
# these come down in the wrapper
# s  [ 0.0125  0.0425  1.0475  2.4975  4.9975 10.1475]
# n  [  31.3   62.5  125.   250.   500.  1000. ]
# r  [ 0.0125  0.0425  1.0475  2.4975  4.9975 10.1475]
def plateMapLogistic4(n, A, B, C, D):
    """4PL logistic equation."""
    # print("A, B, C, D ", str(A), " ", str(B), " ", str(C), " ", str(D), " ")
    # print("(A - D) ", str(A - D) )
    # print("(1 / B) ", str(1 / B) )
    # print("(n / C) ", str( (n / C) ) )
    # print("(1.0+((n/C)**B))) ", str(1.0+((n/C)**B)) )

    # print("n, A, B, C, D ", str(n), " ", str(A)," " , str(B)," ", str(C)," ", str(D)," ")
    # print("logistic4 n ", n)
    signal = ((A-D)/(1.0+((n/C)**B))) + D
    # print(signal)
    return signal


# sck
def plateMapResidualsLogistic4(p, r, n):
    """Deviations of data from fitted 4PL curve"""
    A, B, C, D = p
    err = r - plateMapLogistic4(n, A, B, C, D)
    return err

# sck
# # takes concentration and returns signal
# def plateMap_pevalLogistic4(n, p):
#     """Evaluated value (signal) at concentration n with current parameters."""
#     A, B, C, D = p
#     return plateMapLogistic4(n, A, B, C, D)

# Logistic 4a0 Parameter Set of Functions
def plateMapLogistic4a0(n, A, B, C, D):
    """4PL logistic equation."""
    signal = ((0-D)/(1.0+((n/C)**B))) + D
    return signal


# sck
def plateMapResidualsLogistic4a0(p, r, n):
    """Deviations of data from fitted 4PL curve"""
    A, B, C, D = p
    err = r - plateMapLogistic4a0(n, 0, B, C, D)
    return err

# sck
# def plateMap_pevalLogistic4a0(n, p):
#     """Evaluated value (signal) at concentration n with current parameters."""
#     A, B, C, D = p
#     return plateMapLogistic4a0(n, 0, B, C, D)

# NOTE: def plateMapLogistic4f(n, A, B, C, D): was moved to an inner function so could pass different variables inside


# sck
# Power Set of Functions
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
def plateMapPoly2(n, A, B, C, D):
    signal = C*n**2 + B*n + A
    return signal


# sck
def plateMapResidualsPoly2(p, r, n):
    A, B, C, D = p
    err = r-plateMapPoly2(n, A, B, C, D)
    return err


# sck
# def plateMap_pevalPoly2(n, p):
#     A, B, C, D = p
#     return plateMapPoly2(n, A, B, C, D)


# sck
# Linear0 Set of Functions
# B is SLOPE!!!
def plateMapLinear0(n, A, B):
    signal = B * n
    return signal


# sck
def plateMapResidualsLinear0(p, r, n):
    A, B = p
    err = r - plateMapLinear0(n, A, B)
    return err

# def plateMap_pevalLinear0(n, p):
#     A, B = p
#     return plateMapLinear0(n, A, B)


# sck
# Linear Set of Functions
# and Log Set of Functions when talk log before sending (base determined outside of the fitting
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
# A is INTERCEPT!!!!!
# B is SLOPE!!!
def plateMapLinear(n, A, B):
    signal = (B*n) + A
    return signal


# sck
def plateMapResidualsLinear(p, r, n):
    A, B = p
    err = r-plateMapLinear(n, A, B)
    return err

# def plateMap_pevalLinear(n, p):
#     A, B = p
#     return plateMapLinear(n, A, B)

# START - save for now in case change mind and go back to this way.
# using a different fitting method
# to work in fitting, need to be a reshaped numpy array
# NN = np.array(N).reshape(-1, 1)
# RR = np.array(R).reshape(-1, 1)
#
# print("NN")
# print(NN)
# print("RR")
# print(RR)
#
# https://towardsdatascience.com/a-beginners-guide-to-linear-regression-in-python-with-scikit-learn-83a8f7ae2b4f
# Used other way for consistency, but this way was probably better.
# if form_calibration_curve in ['linear']:
#     # fit the intercept
#     regressor_linear = LinearRegression(fit_intercept=True)
#     regressor_linear.fit(NN, RR)
#     slope_linear = regressor_linear.coef_[0][0]
#     icept_linear = regressor_linear.intercept_[0]
#     rsquared_linear = regressor_linear.score(NN, RR)
#     slope = sandrasGeneralFormatNumberFunction(slope_linear)
#     icept = sandrasGeneralFormatNumberFunction(icept_linear)
#     rsquared = sandrasGeneralFormatNumberFunction(rsquared_linear)
#     equation = "Sample Fitted = (Adjusted Raw - (" + str(icept) + "))/" + str(slope)
#     r2['linear'] = rsquared
#
#     # MAE = metrics.mean_absolute_error(RR, y_pred)
#     # MSE = metrics.mean_squared_error(RR, y_pred)
#     # RSME = np.sqrt(metrics.mean_squared_error(RR, y_pred))
#
#     dict_of_parameter_labels_linear = (
#         {'p1': 'slope', 'p2': 'Intercept', 'p3': '-', 'p4': '-', 'p5': '-'})
#     dict_of_parameter_values_linear = (
#         {'p1': slope, 'p2': icept, 'p3': 9876543210, 'p4': 9876543210, 'p5': 9876543210})
#
#     dict_of_curve_info_linear = (
#         {'method': 'Linear w/fitted intercept', 'equation': equation,
#          'rsquared': str(rsquared) + " (calculated using python sklearn LinearRegression .score)"})
#     dict_of_standard_info_linear = (
#         {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
#          'blankaverage': sample_blank_average})
#
#     dict_of_parameter_labels = dict_of_parameter_labels_linear
#     dict_of_parameter_values = dict_of_parameter_values_linear
#     dict_of_curve_info = dict_of_curve_info_linear
#     dict_of_standard_info = dict_of_standard_info_linear
#
# if form_calibration_curve in ['linear0']:
#     # force through 0
#     regressor_linear0 = LinearRegression(fit_intercept=False)
#     regressor_linear0.fit(NN, RR)
#     slope_linear0 = regressor_linear0.coef_[0][0]
#     icept_linear0 = 0
#     rsquared_linear0 = regressor_linear0.score(NN, RR)
#     slope = sandrasGeneralFormatNumberFunction(slope_linear0)
#     icept = sandrasGeneralFormatNumberFunction(icept_linear0)
#     rsquared = sandrasGeneralFormatNumberFunction(rsquared_linear0)
#     equation = "Sample Fitted = (Adjusted Raw - 0)/" + str(slope)
#     r2['linear0'] = rsquared
#
#     dict_of_parameter_labels_linear0 = (
#         {'p1': 'slope', 'p2': 'Intercept', 'p3': '-', 'p4': '-', 'p5': '-'})
#     dict_of_parameter_values_linear0 = (
#         {'p1': slope, 'p2': icept, 'p3': 9876543210, 'p4': 9876543210, 'p5': 9876543210})
#
#     dict_of_curve_info_linear0 = (
#         {'method': 'Linear w/intercept = 0', 'equation': equation,
#          'rsquared': str(rsquared) + " (calculated using python sklearn LinearRegression .score)"})
#     dict_of_standard_info_linear0 = (
#         {'min': use_form_min, 'max': use_form_max, 'standard0average': standard_blank_average,
#          'blankaverage': sample_blank_average})
#
#     dict_of_parameter_labels = dict_of_parameter_labels_linear0
#     dict_of_parameter_values = dict_of_parameter_values_linear0
#     dict_of_curve_info = dict_of_curve_info_linear0
#     dict_of_standard_info = dict_of_standard_info_linear0
#
#
# some more of the other way of fitting (I think), save for now incase go back
# if form_calibration_curve == 'linear':
#     y_predStandards100 = regressor_linear.predict(NN)
# elif form_calibration_curve == 'linear0':
#     y_predStandards100 = regressor_linear0.predict(NN)
# else:
#     y_predStandards100 = regressor_linear0.predict(NN)
#
# # FYI y_predStandards100[i] returns an array of 1
# i = 0
# for each in N:
#     this_row = {}
#     this_row.update({'Average Concentration': N[i]})
#     this_row.update({'Observed Signal': S[i]})
#     this_row.update({'Predicted Signal': y_predStandards100[i][0]})
#     list_of_dicts_of_each_standard_row_curve.append(this_row)
#     i = i + 1
# END save for now in case go back


# sck - the main function for processing data - pass to a utils.py funciton
def sandrasGeneralFormatNumberFunction(this_number_in):
        # https://pyformat.info/
        # '{:06.2f}'.format(3.141592653589793)
        # Output 003.14
        # https://stackoverflow.com/questions/6913532/display-a-decimal-in-scientific-notation
        # x = Decimal('40800000000.00000000000000')
        # '{:.2e}'.format(x)
        formatted_number = 0
        x = float(this_number_in)
        if x == 0:
            formatted_number = '{:.0f}'.format(x)
        elif x < 0.00001:
            formatted_number = '{:.4e}'.format(x)
            #formatted_number = '{:.8f}'.format(x)
        elif x < 0.0001:
            formatted_number = '{:.4e}'.format(x)
            # formatted_number = '{:.5f}'.format(x)
        elif x < 0.001:
            formatted_number = '{:.5f}'.format(x)
        elif x < 0.01:
            formatted_number = '{:.3f}'.format(x)
        elif x < 0.1:
            formatted_number = '{:.3f}'.format(x)
        elif x < 1.0:
            formatted_number = '{:.3f}'.format(x)
        elif x < 10:
            formatted_number = '{:.1f}'.format(x)
        elif x < 30:
            formatted_number = '{:.1f}'.format(x)
        elif x < 100:
            formatted_number = '{:.0f}'.format(x)
        elif x < 1000:
            formatted_number = '{:,.0f}'.format(x)
        elif x < 10000:
            formatted_number = '{:,.0f}'.format(x)
        elif x < 100000:
            formatted_number = '{:,.0f}'.format(x)
        elif x < 1000000:
            formatted_number = '{:,.0f}'.format(x)
        else:
            formatted_number = '{:.3e}'.format(x)

        return formatted_number



# sck called from forms.py when save and
# change omic data file in GUI via an ajax function
# fetch_omics_data_for_upload_preview_prep;
# js function get_data_for_this_file_ready_for_preview
def omic_data_file_process_data(save, study_id, omic_data_file_id, data_file, file_extension,
                                          called_from, data_type, analysis_method):
    """
    Assay Omics Data File Add or Change the file (utility).
    """

    # when called from ajax, this is what is used for the preview (Quinn's)
    # the preview is ONLY called/available when the file is changed (not on load for the saved file)
    # the dictionary that is returned can have extra stuff
    # but must the stuff that matches with what Quinn's preview is expecting
    # when called from the form clean and save, this makes the list of rows that will go into the data points table(s)
    # note: there is a table for compare (two group) data and a table for counts data
    # this is because the metadata for the compare data is stored in the table with the upload file
    # but the metadata for the counts data is stored in a separate table and a requires pk foreign key to the sample metadata
    # to be stored with the count value

    # set the defaults
    continue_outer_if_true = True
    # if there is more than one Excel sheet, will need a loop, check for number of sheets.
    looper = 1
    sheet_index = 0
    workbook = None
    # construct here so can use this name anywhere
    df = pd.DataFrame(columns=['one'])
    # if there are multiple sheets, they can all be added to one bulk file
    # that means only need one list_of_instances for all the sheets
    list_of_instances = []
    instance_counter = 0
    analysis_target_name_to_pk_dict = {}
    analysis_target_pk_to_sc_target_pk_dict = {}
    sc_target_pk_to_name_dict = {}
    omic_target_text_header_list = []
    # data_dicts is all about the preview from the upload page
    data_dicts = {'data': {}, 'file_id_to_name': {}, 'table': {}}
    joint_name = 'New/Changed File Preview'
    data_dicts['data'][joint_name] = {}
    data_dicts['file_id_to_name'][1] = joint_name
    data_dicts['table'][joint_name] = ['Preview Chosen File', omic_data_file_id]
    data_dicts['target_name_to_id'] = {}
    error_message = ''
    data_dicts['error_message'] = ''
    # todo-sck need to coordinate with Quinn for the counts data preview - what need and in what format?


    # Was asked to build a check to autofind the file type
    # this is complicated because there could be multiple sheets
    # But, if go back and do it later....
    # MAKE ASSUMPTION: in the AssayOmicAnalysisTarget table, only the log 2 fold change headers will match the Input File Headers
    # THUS, there will never by a header in a file that = normcounts or rawcounts
    # might need to start looking at the sheets, then, if error out due to finding log2fc header
    # go back, reset the defaults, and cycle through again with the new data_type, but it be complicated, so wait until base function works before implimenting this whistle
    # data_dicts['new_data_type'] = 'data_type'
    # reset_defaults = False
    # for each in list_of_relevant_headers_in_file:
    #     if each in omic_target_text_header_list:
    #         # must be log2fc
    #         if data_type != 'log2fc':
    #             new_data_type = 'log2fc'
    #             break


    if continue_outer_if_true:
        # Think good for all log2fc and counts data

        # fill omic_target_text_header_list = [] and target_pk_list = []
        # pull from the AssayOmicAnalysisTarget
        # where file_header is true and data_type matches data_type and analysis_method matches analysis_method
        # HANDY combine filters with commas in queryset
        target_matches = AssayOmicAnalysisTarget.objects.filter(
            data_type=data_type,
            method=analysis_method
        )
        analysis_target_name_to_pk_dict = {target.name: target.id for target in target_matches}
        analysis_target_pk_to_sc_target_pk_dict = {target.id: target.target_id for target in target_matches}
        if len(analysis_target_name_to_pk_dict) == 0:
            error_message = error_message + 'No option for this combination of data type and analysis method has been programmed. Contact the MPS Database Admins (AssayOmicAnalysisTargets not found).'
            raise forms.ValidationError(error_message)
            continue_outer_if_true = False
        else:
            omic_target_text_header_list = list(analysis_target_name_to_pk_dict.keys())
            sc_target_pk_header_list = list(analysis_target_pk_to_sc_target_pk_dict.values())
            sc_target_matches = AssayTarget.objects.filter(
                id__in=sc_target_pk_header_list
            )
            sc_target_pk_to_name_dict = {target.id: target.name for target in sc_target_matches}

    # print("~dict ",analysis_target_name_to_pk_dict)
    # {'padj': 1, 'baseMean': 2, 'lfcSE': 3, 'stat': 4, 'log2FoldChange': 5, 'pvalue': 6}
    # print("~text ",omic_target_text_header_list)

    if continue_outer_if_true:
        # get the number of sheets need to loop through and check to see if valid
        if file_extension in ['.xls', '.xlsx']:
            try:
                file_data = data_file.read()
                workbook = xlrd.open_workbook(file_contents=file_data)
                looper = len(workbook.sheet_names())
            except:
                continue_outer_if_true = False
                error_message = error_message + 'Has and Excel extension but file could not be opened.'
                raise forms.ValidationError(error_message)

    if continue_outer_if_true:
        # each sheet will be checked for data
        # not all sheets need to be valid, a sheet can be skipped and others imported
        while sheet_index < looper:
            matrix_item_pk_list = []

            # Guts of opening the file or sheet and find and return the dataframe
            # same for all data import types - no splitting by data type is needed
            find_dataframe = data_file_to_data_frame(data_file, file_extension, workbook, sheet_index)
            continue_this_sheet_if_true = find_dataframe[0]
            error_message = error_message + find_dataframe[1]
            data_dicts['error_message'] = error_message
            df = find_dataframe[2]
            # avoid problems with leading or trailing spaces
            df.columns = df.columns.str.strip()
            # save these in a list, because, need for some data (headers are chip ID names, sample names, group names)
            df_column_headers_stripped = df.columns
            # does the file have a column named 'gene' or 'name'?
            gene_id_field_header_plus = omic_determine_if_field_with_header_for_gene(df_column_headers_stripped)
            continue_this_sheet_if_true = gene_id_field_header_plus[0]
            gene_id_field_header = gene_id_field_header_plus[1]

            # print("~gene ",gene_id_field_header)

            if continue_this_sheet_if_true:
                # Guts of the QC for the omics data point file
                # functions should return continue and error message (and other stuff if needed for data type)
                #  todo-sck need to see what file headers are being pulled - did have a function to pull them but not sure if current...check it
                qc_each_file_or_worksheet_level = omic_qc_data_file(df, omic_target_text_header_list, data_type)
                continue_this_sheet_if_true = qc_each_file_or_worksheet_level[0]
                error_message = error_message + qc_each_file_or_worksheet_level[1]
                data_dicts['error_message'] = error_message
                list_of_relevant_headers_in_file = qc_each_file_or_worksheet_level[2]

                # print("~match headers ",list_of_relevant_headers_in_file)
                # to be compatible with the graphing, need this dict
                data_dicts['target_name_to_id'] = {y: analysis_target_name_to_pk_dict[y] for y in list_of_relevant_headers_in_file}

            if continue_this_sheet_if_true:
                parameter_list = [
                    list_of_instances, instance_counter, df,
                    study_id, omic_data_file_id, analysis_target_name_to_pk_dict,
                    sc_target_pk_to_name_dict, analysis_target_pk_to_sc_target_pk_dict,
                    list_of_relevant_headers_in_file, called_from, gene_id_field_header,
                    data_dicts['data'][joint_name]
                ]
                # Guts of data loading for omic data file
                # functions should return continue, error message, and a list of instances and an instance counter
                if data_type == 'log2fc':
                    data_loaded_to_list_of_instances = omic_two_group_data_to_list_of_instances(
                        list_of_instances, instance_counter, df,
                        study_id, omic_data_file_id, analysis_target_name_to_pk_dict,
                        sc_target_pk_to_name_dict, analysis_target_pk_to_sc_target_pk_dict,
                        list_of_relevant_headers_in_file, called_from, gene_id_field_header,
                        data_dicts['data'][joint_name]
                        )
                    continue_this_sheet_if_true = data_loaded_to_list_of_instances[0]
                elif data_type == 'normcounts' or data_type == 'rawcounts':
                    data_loaded_to_list_of_instances = omic_count_data_to_list_of_instances(
                        list_of_instances, instance_counter, df,
                        study_id, omic_data_file_id, analysis_target_name_to_pk_dict,
                        sc_target_pk_to_name_dict, analysis_target_pk_to_sc_target_pk_dict,
                        list_of_relevant_headers_in_file, called_from, gene_id_field_header,
                        data_dicts['data'][joint_name]
                        )
                    continue_this_sheet_if_true = data_loaded_to_list_of_instances[0]
                else:
                    continue_this_sheet_if_true = False

                if continue_this_sheet_if_true:
                    error_message = error_message + data_loaded_to_list_of_instances[1]
                    data_dicts['error_message'] = error_message
                    list_of_instances = data_loaded_to_list_of_instances[2]
                    instance_counter = data_loaded_to_list_of_instances[3]
                    data_dicts['data'][joint_name] = data_loaded_to_list_of_instances[4]
                    data_dicts['error_message'] = error_message
                    # todo-sck need to coordinate with Quinn for the counts data preview - what need and in what format?

            sheet_index = sheet_index + 1

    if instance_counter == 0:
        error_message = error_message + 'There were no records in the file to upload. '
        raise forms.ValidationError(error_message)
        continue_outer_if_true = False

    # called_from will only be == save when it is called from the form save
    if called_from == 'save' and continue_outer_if_true:
        if data_type == 'log2fc':
            omic_compare_data_upload_remove_and_add(omic_data_file_id, list_of_instances, error_message)
        else:
            omic_count_data_upload_remove_and_add(omic_data_file_id, list_of_instances, error_message)

    # the returned is ONLY used for the preview on the upload page
    # can change it to whatever is needed for the graph preview
    # print(data_dicts)
    return data_dicts


# sck sub here
def omic_determine_if_field_with_header_for_gene(df_column_headers_stripped):
    continue_this_sheet_if_true = True
    # may need other options here (eg probe_id, refseq name, etc), but these will do for now
    gene_id_field_name = ''
    if 'gene' in df_column_headers_stripped:
        gene_id_field_name = 'gene'
    elif 'name' in df_column_headers_stripped:
        gene_id_field_name = 'name'
    elif 'gene reference' in df_column_headers_stripped:
        gene_id_field_name = 'gene reference'
    else:
        # for this sheet or file, the HEADER for the target field could not be found, skip this sheet
        continue_this_sheet_if_true = False
    return [continue_this_sheet_if_true, gene_id_field_name]


# sck form save qc of omics upload file
def omic_qc_data_file(df, omic_target_text_header_list, data_type):
    error_message = ''
    continue_this_sheet_if_true = True

    list_of_relevant_headers_in_file = []
    found_foldchange_true = False
    for file_header in df.columns:
        if file_header in omic_target_text_header_list:
            list_of_relevant_headers_in_file.append(file_header)
        # only required field is the fold change field - if not found, ignore this sheet
        if data_type == 'log2fc':
            if file_header.find('fc') >= 0 or file_header.find('fold') >= 0 or file_header.find(
                    'FC') >= 0 or file_header.find('Fold') >= 0:
                found_foldchange_true = True

    if data_type == 'log2fc':
        if found_foldchange_true:
            pass
        else:
            continue_this_sheet_if_true = False
            error_message = error_message + ' Required header containing "fc" or "fold" or "FC" or "Fold" is missing. '
    else:
        pass
        # todo-sck need build for counts data - not that the head list would be normcounts or rawcounts, not the sample headers

    return [continue_this_sheet_if_true, error_message, list_of_relevant_headers_in_file]


# sck sub here in utils.py
# two group data only
def omic_two_group_data_to_list_of_instances(
    list_of_instances, instance_counter, df,
    study_id, omic_data_file_id, analysis_target_name_to_pk_dict,
    sc_target_pk_to_name_dict, analysis_target_pk_to_sc_target_pk_dict,
    list_of_relevant_headers_in_file, called_from, gene_id_field_header,
    data_dict):

    error_message = ''
    continue_this_sheet_if_true = True

    # these are for the preview and might not be needed...checking with Quinn to see if needed
    # max_fold_change_r = -999.0
    # max_pvalue_r = -999.0
    # max_fold_change = -999.0
    # max_pvalue = -999.0
    # min_fold_change_r = 9999999.0
    # min_pvalue_r = 9999999.0
    # min_fold_change = 9999999.0
    # min_pvalue = 9999999.0

    for index, row in df.iterrows():
        name = row[gene_id_field_header]
        # for the preview of the graphs
        # testing
        # if name.find('MZ') >= 0:
        if 0 == 0:
            data_dict[name] = {}
            for each in list_of_relevant_headers_in_file:
                target_pk = analysis_target_name_to_pk_dict[each]
                value = row[each]
                if np.isnan(value):
                    value = None
                else:
                    value = float(value)

                # if value != None:
                #
                #     if each.find('val') >= 0:
                #         if value > max_pvalue:
                #             max_pvalue = value
                #         if value < min_pvalue:
                #             min_pvalue = value
                #
                #     if each.find('fold') >= 0 or each.find('fc') >= 0 or each.find('FC') >= 0 or each.find('Fold') >= 0:
                #         if value > max_fold_change:
                #             max_fold_change = value
                #         if value < min_fold_change:
                #             min_fold_change = value

                # print("instance_counter ",instance_counter)
                # print("~each ", each)
                # print("~target_pk ", target_pk)
                # print("~value ", value)

                # creating an instance causes an error in the clean since there is no pk for this file on the add form
                # but we want the rest to go through the save AND we want to make sure instances are being counted in the clean
                if called_from == 'save':
                    instance = AssayOmicDataPoint(
                        study_id=study_id,
                        omic_data_file_id=omic_data_file_id,
                        name=name,
                        analysis_target_id=target_pk,
                        value=value
                    )
                    # add this list to the list of lists
                    list_of_instances.append(instance)
                else:
                    # this will be for the preview on the page when the file is changed
                    # gene name, analysis target pk, header,
                    # study component target pk, study component target name, value
                    # sc_target_pk = analysis_target_pk_to_sc_target_pk_dict.get(target_pk)
                    # sc_target_name = sc_target_pk_to_name_dict.get(sc_target_pk)
                    # listance = [name, target_pk, each, sc_target_pk, sc_target_name, value]
                    # list_of_instances.append(listance)

                    # This if for the graph preview on the upload page
                     data_dict[name][target_pk] = value

                instance_counter = instance_counter + 1

        # max_fold_change_r = max_fold_change
        # max_pvalue_r = max_pvalue
        # min_fold_change_r = min_fold_change
        # min_pvalue_r = min_pvalue

    # return [continue_this_sheet_if_true, error_message, list_of_instances, instance_counter, data_dict, max_fold_change_r, max_pvalue_r, min_fold_change_r, min_pvalue_r]
    return [continue_this_sheet_if_true, error_message, list_of_instances, instance_counter, data_dict]


# sck sub here in utils.py
# count data only
def omic_count_data_to_list_of_instances(
    list_of_instances, instance_counter, df,
    study_id, omic_data_file_id, analysis_target_name_to_pk_dict,
    sc_target_pk_to_name_dict, analysis_target_pk_to_sc_target_pk_dict,
    list_of_relevant_headers_in_file, called_from, gene_id_field_header,
    data_dict):
    # todo-sck, going to need to pass through the pk for the meta data file!

    error_message = ''
    continue_this_sheet_if_true = True

    for index, row in df.iterrows():
        name = row[gene_id_field_header]
        # for the preview of the graphs
        # testing
        # if name.find('MZ') >= 0:
        if 0 == 0:
            data_dict[name] = {}
            for each in list_of_relevant_headers_in_file:
                target_pk = analysis_target_name_to_pk_dict[each]
                value = row[each]
                if np.isnan(value):
                    value = None
                else:
                    value = float(value)

                # creating an instance causes an error in the clean since there is no pk for this file on the add form
                # but we want the rest to go through the save AND we want to make sure instances are being counted in the clean
                if called_from == 'save':
                    instance = AssayOmicDataPoint(
                        study_id=study_id,
                        omic_data_file_id=omic_data_file_id,
                        name=name,
                        analysis_target_id=target_pk,
                        value=value
                    )
                    # add this list to the list of lists
                    list_of_instances.append(instance)
                else:
                    # todo-sck update when coordinate with Quinn
                    # this will be for the preview on the page when the file is changed
                    # gene name, analysis target pk, header,
                    # study component target pk, study component target name, value
                    # sc_target_pk = analysis_target_pk_to_sc_target_pk_dict.get(target_pk)
                    # sc_target_name = sc_target_pk_to_name_dict.get(sc_target_pk)
                    # listance = [name, target_pk, each, sc_target_pk, sc_target_name, value]
                    # list_of_instances.append(listance)

                    # This if for the graph preview on the upload page
                     data_dict[name][target_pk] = value

                instance_counter = instance_counter + 1

    return [continue_this_sheet_if_true, error_message, list_of_instances, instance_counter, data_dict]


# sck
# one group data only
def omic_metadata_data_to_list_of_instances(
    list_of_instances, instance_counter, df,
    study_id, omic_data_file_id, target_pk_list,
    matrix_item_pk_list, called_from, gene_id_field_name_if_app
    ):
    # TODO-sck fix this it is part of the sample metadata, not part of the upload...it will be moved, but might want for QC ...


    error_message = ''
    continue_this_sheet_if_true = True

    if len(matrix_item_pk_list) != len(df.columns):
        error_message = 'There is a problem with finding the list of matrix items. Notify the MPS Database Admins.'
        continue_this_sheet_if_true = False
        print(error_message)
    else:
        target = int(target_pk_list[0])
        data_cols = []
        i = 0
        for each in df.columns:
            if i > 0:
                data_cols.append(each)
            i = i + 1

        for index, row in df.iterrows():

            # assume for now there will be only one header row and it was row 0 and we specified a header row so it is not called here
            # if there are additional header rows, deal with them here ....

            name = row[gene_id_field_name_if_app]
            # print('name for this row ',name)
            c = 0

            while c < len(data_cols):
                # print('c ', c, ' data_cols[c] ', data_cols[c])
                value = row[data_cols[c]]
                # note the +1 because the first one was not popped off as the data_cols was
                this_matrix_item = int(matrix_item_pk_list[c + 1])
                # print('index ',index,'  instance_counter ', instance_counter ,'  i ',i,'  name ',name,'  target ',target, '  value ',value)

                # creating an instance causes an error in the clean since there is no pk for this file on the add form
                # but we want the rest to go through the save AND we want to make sure instances are being counted in the clean

                if called_from == 'save' and this_matrix_item > 0:
                    instance = AssayOmicDataPoint(
                        study_id=study_id,
                        omic_data_file_id=omic_data_file_id,
                        name=name,
                        target_id=target,
                        value=value
                        # , matrix_item_id=this_matrix_item
                        #     may want a group id or a cross reference, depends on what team decides
                    )
                    # add this list to the list of lists
                    list_of_instances.append(instance)
                else:
                    # this will be for the preview on the page when the file is changed
                    listance = [name, target, value]
                    list_of_instances.append(listance)

                instance_counter = instance_counter + 1
                c = c + 1

    return [continue_this_sheet_if_true, error_message, list_of_instances, instance_counter]


# sck
def omic_compare_data_upload_remove_and_add(data_file_pk, list_of_instances, error_message):
    # Guts of removing old and saving the data to the DataPoint Table of compare data.
    # double check that there are data ready to add to the DataPoint table before continuing
    if len(list_of_instances) > 0:
        try:
            # if there are data in the omic data point table related to this file, remove them all
            instance = AssayOmicDataPoint.objects.filter(omic_data_file=data_file_pk)
            instance.delete()
        except:
            # if found none
            pass
        # Add the data to the omic data point table
        AssayOmicDataPoint.objects.bulk_create(list_of_instances)
    else:
        # This should not happen - should be screened out in the clean - here just in case
        error_message = error_message + ' During the save, found no records in the file to upload. Should have received and error message during data cleaning. '
        raise forms.ValidationError(error_message)


# sck
def omic_count_data_upload_remove_and_add(data_file_pk, list_of_instances, error_message):
    # todo-sck completely change this for the count data!
    # Guts of removing old and saving the data to the DataPoint Table of compare data.
    # double check that there are data ready to add to the DataPoint table before continuing
    if len(list_of_instances) > 0:
        try:
            # if there are data in the omic data point table related to this file, remove them all
            instance = AssayOmicDataPoint.objects.filter(omic_data_file=data_file_pk)
            instance.delete()
        except:
            # if found none
            pass
        # Add the data to the omic data point table
        AssayOmicDataPoint.objects.bulk_create(list_of_instances)
    else:
        # This should not happen - should be screened out in the clean - here just in case
        error_message = error_message + ' During the save, found no records in the file to upload. Should have received and error message during data cleaning. '
        raise forms.ValidationError(error_message)


# sck
def data_file_to_data_frame(data_file, file_extension, workbook=None, sheet_index=None):
    # should be able to use this for all data to data frame

    # being called for each text file or each workbook sheet
    # make a default data frame
    df = pd.DataFrame(columns=['one'])

    # print("df empty")
    # print(df)

    try_again = False
    true_if_dataframe_found = True
    error_message = ''

    if file_extension == '.csv':
        try:
            df = pd.read_csv(data_file, header=0)
        except:
            try_again = True
    elif file_extension == '.tsv':
        try:
            df = pd.read_csv(data_file, sep='\t', header=0)
        except:
            try_again = True
    elif file_extension in ['.xls', '.xlsx']:
        try:
            df = pd.read_excel(workbook, sheet_name=sheet_index)
        except:
            try_again = True
    else:
        try_again = True

    if try_again:
        # try the python file type sniffer
        try:
            df = pd.read_csv(data_file, header=0)
        except:
            error_message = 'ERROR - file was not in a recognized format.'
            true_if_dataframe_found = False

    # print("df loaded")
    # print(df)

    return [true_if_dataframe_found, error_message, df]


# sck for form clean for omic file upload
def data_quality_clean_check_for_omic_file_upload(self, data, data_file_pk):
    # fields that would cause a change in data pull
    # 'omic_data_file' in self.changed_data or
    # 'analysis_method' in self.changed_data or
    # 'data_type' in self.changed_data or

    true_to_continue = True
    file_name = data.get('omic_data_file').name

    if true_to_continue and 'omic_data_file' in self.changed_data:

        # check for valid file extension
        file_extension = os.path.splitext(data.get('omic_data_file').name)[1]
        if file_extension not in ['.csv', '.tsv', '.txt', '.xls', '.xlsx']:
            true_to_continue = False
            validation_message = 'Invalid file extension - must be in csv, tsv, txt, xls, or xlsx.'
            validation_message = validation_message + "  " + file_name
            raise ValidationError(validation_message, code='invalid')

    if true_to_continue and 'omic_data_file' in self.changed_data:
        true_to_continue = this_file_is_the_same_hash_as_another_in_this_study(self, data, data_file_pk)

    if true_to_continue:
        # todo-sck ONGOING - add to the list with all data types that are two groups required
        if data['data_type'] in ['log2fc']:
            true_to_continue = qc_for_compare_omic_upload(self, data, data_file_pk)
        elif data['data_type'] in ['normcounts', 'rawcounts']:
            true_to_continue = qc_for_count_omic_upload(self, data, data_file_pk)
        else:
            pass

    return true_to_continue


# sck sub here in utils.py
def qc_for_compare_omic_upload(self, data, data_file_pk):
    true_to_continue = True
    file_name = data.get('omic_data_file').name

    if data['group_1'] is None or data['group_2'] is None:
        true_to_continue = False
        validation_message = 'For data type that compares two groups, both groups must be selected.'
        validation_message = validation_message + "  " + file_name
        raise ValidationError(validation_message, code='invalid')
    if data['group_1'] == data['group_2'] and data['time_1'] == data['time_2'] and data['location_1'] == data['location_2']:
        true_to_continue = False
        validation_message = 'For data type that compares two groups, the combination of the group, sample location, and sample time must be different.'
        validation_message = validation_message + "  " + file_name
        raise ValidationError(validation_message, code='invalid')
    if data['location_1'] is None or data['location_2'] is None:
        true_to_continue = False
        validation_message = 'Sample locations are required for this data type.'
        validation_message = validation_message + "  " + file_name
        raise ValidationError(validation_message, code='invalid')
    if data['time_1'] is None or data['time_2'] is None:
        true_to_continue = False
        validation_message = 'Sample times are required for this data type.'
        validation_message = validation_message + "  " + file_name
        raise ValidationError(validation_message, code='invalid')

    if true_to_continue:

        # print('-', self.instance.study.id)
        # print('-', data['analysis_method'])
        # print('-', data['group_1'])
        # print('-', data['group_2'])
        # print('-', data['location_1'])
        # print('-', data['location_2'])
        # print('-', data['time_1'])
        # print('-', data['time_2'])

        if ('analysis_method' in self.changed_data or
                'group_1' in self.changed_data or
                'group_2' in self.changed_data or
                'location_1' in self.changed_data or
                'location_2' in self.changed_data or
                'time_1' in self.changed_data or
                'time_2' in self.changed_data):
            # is there a combination of group1+location1+time1+group2+location2+time2 already in study
            # in as group 1 and group 2
            group_keys_combos_left = AssayOmicDataFileUpload.objects.filter(
                study_id=self.instance.study.id,
                analysis_method_id=data['analysis_method'],
                group_1=data['group_1'],
                group_2=data['group_2'],
                location_1=data['location_1'],
                location_2=data['location_2'],
                time_1=data['time_1'],
                time_2=data['time_2']
            )
            # in as group 2 and group 1
            group_keys_combos_right = AssayOmicDataFileUpload.objects.filter(
                study_id=self.instance.study.id,
                analysis_method_id=data['analysis_method'],
                group_1=data['group_2'],
                group_2=data['group_1'],
                location_1=data['location_2'],
                location_2=data['location_1'],
                time_1=data['time_2'],
                time_2=data['time_1']
            )

            # group_keys_combos_left = (f for f in group_keys_combos_left if f.filename() == file_name)
            # group_keys_combos_right = (f for f in group_keys_combos_right if f.filename() == file_name)

            # print('-------')
            # print('group_keys_combos_left ', group_keys_combos_left)
            # print('group_keys_combos_right ', group_keys_combos_right)
            #
            # print('group_keys_combos_left-len ', len(group_keys_combos_left))
            # print('group_keys_combos_right-len ', len(group_keys_combos_right))

            files_left_list = []
            files_right_list = []

            for each in group_keys_combos_left:
                fame = each.omic_data_file.name
                if each.id != data_file_pk:
                    file_name2 = ''
                    file_name2_as_list = []
                    if fame.find('/') >= 0:
                        file_name2_as_list = fame.split('/')
                    else:
                        file_name2_as_list = fame.split('\\')

                    file_name2 = file_name2_as_list[len(file_name2_as_list) - 1]
                    true_to_continue = False
                    files_left_list.append(file_name2)

            for each in group_keys_combos_right:
                fame = each.omic_data_file.name
                if each.id != data_file_pk:
                    file_name2 = ''
                    file_name2_as_list = []
                    if fame.find('/') >= 0:
                        file_name2_as_list = fame.split('/')
                    else:
                        file_name2_as_list = fame.split('\\')

                    file_name2 = file_name2_as_list[len(file_name2_as_list) - 1]
                    true_to_continue = False
                    files_right_list.append(file_name2)

            files_left_list_str = ', '.join(files_left_list)
            files_right_list_str = ', '.join(files_right_list)

            if len(files_left_list) > 0 or len(files_right_list) > 0:
                if len(files_left_list) > 0 and len(files_right_list) > 0:
                    files_list_str = files_left_list_str + ', ' + files_right_list_str
                elif len(files_left_list) > 0:
                    files_list_str = files_left_list_str
                else:
                    files_list_str = files_right_list_str
                true_to_continue = False
                validation_message = 'The combination of assay, groups, locations, and times selected have ALREADY BEEN USED in this study. '
                validation_message = validation_message + 'The combination was used in files: ' + files_list_str + '. '
                validation_message = validation_message + 'You must use a different combination for the file you just tried to upload: ' + file_name
                raise ValidationError(validation_message, code='invalid')

    return true_to_continue


# sck sub here in utils.py
def qc_for_count_omic_upload(self, data, data_file_pk):
    # todo-sck update this all for counts data
    true_to_continue = True
    file_name = data.get('omic_data_file').name

    # change for missing headers in the sample metadata
    # example of how to send error messages
    # if data['group_1'] is None or data['group_2'] is None:
    #     true_to_continue = False
    #     validation_message = 'For data type that compares two groups, both groups must be selected.'
    #     validation_message = validation_message + "  " + file_name
    #     raise ValidationError(validation_message, code='invalid')
    return true_to_continue


# sck sub here in utils.py
def this_file_is_the_same_hash_as_another_in_this_study(self, data, data_file_pk):
    true_to_continue = True
    message = ''
    file_name = ''
    file_name_as_list = []
    if data.get('omic_data_file').name.find('/') >= 0:
        file_name_as_list = data.get('omic_data_file').name.split('/')
    else:
        file_name_as_list = data.get('omic_data_file').name.split('\\')

    file_name = file_name_as_list[len(file_name_as_list)-1]
    study_id = self.instance.study.id
    this_file_hash = hashlib.sha1(data.get('omic_data_file').read()).hexdigest()
    data.get('omic_data_file').seek(0)

    # https://stackoverflow.com/questions/15885201/django-uploads-discard-uploaded-duplicates-use-existing-file-md5-based-check
    # https://josephmosby.com/2015/05/13/preventing-file-dupes-in-django.html
    files_in_study = AssayOmicDataFileUpload.objects.filter(
        study_id=study_id
    )
    potential_dup_list = []

    # print("\nfile_name ", file_name, "  hash ", this_file_hash)
    for each in files_in_study:
        fame = each.omic_data_file.name
        # print("fame ", fame)
        each_file_hash = hashlib.sha1(each.omic_data_file.read()).hexdigest()
        # print("each hash  ", each_file_hash)
        each.omic_data_file.seek(0)

        if this_file_hash == each_file_hash:
            if each.id != data_file_pk:
                file_name2 = ''
                file_name2_as_list = []
                if fame.find('/') >= 0:
                    file_name2_as_list = fame.split('/')
                else:
                    file_name2_as_list = fame.split('\\')

                file_name2 = file_name2_as_list[len(file_name2_as_list) - 1]

                true_to_continue = False
                potential_dup_list.append(file_name2)

    if not true_to_continue:
        potential_dup_string = ', '.join(potential_dup_list)
        message = 'This file ' + file_name + ' appears to be a duplicate of ' + potential_dup_string + '. To change the metadata for this file, exit this page select to Edit ' + potential_dup_string + '.'
        validation_message = message
        raise ValidationError(validation_message, code='invalid')

    return true_to_continue


# sck
# this is called from the ajax.py to pick up the subs as needed
def this_file_same_as_another_in_this_study(omic_data_file, study_id, data_file_pk):
    # 'same' is determined here by what subs are called
    true_to_continue = True
    message = ''

    if true_to_continue:
        similar = this_file_name_is_similar_to_another_in_this_study(omic_data_file, study_id, data_file_pk)
        true_to_continue = similar[0]
        message = message + " " + similar[1]

    return [true_to_continue, message]


# sck - sub here in utils.py
def this_file_name_is_similar_to_another_in_this_study(omic_data_file, study_id, data_file_pk):
    true_to_continue = True
    message = ''
    file_name = ''
    file_name_as_list = []
    if omic_data_file.find('/') >= 0:
        file_name_as_list = omic_data_file.split('/')
    else:
        file_name_as_list = omic_data_file.split('\\')

    file_name = file_name_as_list[len(file_name_as_list)-1]

    file_name_as_list_2 = file_name.split('.')
    # file_name_as_list_2 = file_name_as_list_2[:len(file_name_as_list_2)-1]
    file_name_as_list_2 = file_name_as_list_2[:-1]
    # NOTE: Attempt to deal with spaces by converting to underscores
    file_name_no_extension = '.'.join(file_name_as_list_2).replace(' ', '_')
    files_in_study = AssayOmicDataFileUpload.objects.filter(
        study_id=study_id
    )
    potential_dup_list = []

    for each in files_in_study:
        fame = each.omic_data_file.name
        if file_name_no_extension in fame:
            if each.id != data_file_pk:
                file_name2 = ''
                file_name2_as_list = []
                if fame.find('/') >= 0:
                    file_name2_as_list = fame.split('/')
                else:
                    file_name2_as_list = fame.split('\\')

                file_name2 = file_name2_as_list[len(file_name2_as_list) - 1]

                true_to_continue = False
                potential_dup_list.append(file_name2)

    if not true_to_continue:
        potential_dup_string = ', '.join(potential_dup_list)
        message = 'Similar file names already in this study [' + potential_dup_string + ']. Make sure you are uploading the correct file.'

    return [true_to_continue, message]

omic_metadata_collection_indy_list_of_column_labels = [
    'Chip/Well Name',
    'Sample Location',
    'Sample Time (Day)',
    'Sample Time (Hour)',
    'Sample Time (Minute)',
    'Sample Label',
    'Data Attached',
    'matrix_item_pk',
    'sample_location_pk',
    'sample_metadata_pk'
]

omic_metadata_collection_indy_list_of_column_labels_show_hide = [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0
]

# sck forms.py - will load for previous submit
def find_the_labels_needed_for_the_indy_omic_table(called_from, study_id):
    # todo-sck get all this loaded correctly after get the save done
    # todo-sck for demo, get the add to work correctly (instead of defaults)
    # todo-sck this will mean autofilling the sample label - use the default pattern, they must fix replicates

    indy_omic_table = {}
    indy_list_of_column_labels = []
    indy_list_of_column_labels_show_hide = []
    indy_list_of_dicts_of_table_rows = []

    # decide how to do this - maybe if all are zeros when extracted, hide, else, show
    # for now, day is default on the form DHM 234
    indy_list_time_units_to_include_initially = ['day']
    indy_dict_time_units_to_table_column = {'day': 2, 'hour': 3, 'minute': 4}

    # for development, use find_defaults to get a table to work with
    # else, if there is metadata for this study, pull it in the correct format
    # else, if there is none, pull one for each chip in the study

    # note: the ROW for the apply button is completely handled in the js file
    # see the js file for changing the option to add the row of apply to column buttons
    # note: the COLUMN for the apply to row buttons COULD be added here in the column headers
    # note: if the sample id (hence, the pk for the record in the study) is in one or more of the data points
    # if the sample id has been used (the pk is in the data point file), do not allow the user to edit the sample id
    # but allow the user to change the chip, sample time, and sample location for the sample label

    indy_list_of_column_labels = omic_metadata_collection_indy_list_of_column_labels
    indy_list_of_column_labels_show_hide = omic_metadata_collection_indy_list_of_column_labels_show_hide

    # does this study have any sample metadata in the table
    sample_metadata_rows = AssayOmicSampleMetadata.objects.filter(study_id=study_id)
    sample_metadata_row_count = len(sample_metadata_rows)

    # set the find_defaults is just for development - it must be True once saves and pulls are working
    find_defaults = False

    indy_add_or_update = 'update'
    if sample_metadata_row_count == 0:
        indy_add_or_update = 'add'

        if find_defaults:
            indy_list_of_dicts_of_table_rows = for_development_of_omic_counts_get_some_defaults()
        else:
            # get the queryset of matrix items in this study
            matrix_item_queryset = AssayMatrixItem.objects.filter(study_id=study_id).order_by('name', )
            for index, each in enumerate(matrix_item_queryset):
                list_of_defaults1 = []
                dict1 = {}
                list_of_defaults1 = [
                    each.name,
                    '',
                    '0',
                    '0',
                    '0',
                    each.name + '-',
                    'no',
                    each.id,
                    '',
                    ''
                ]
                # this is an add form, will give a list of chips in the study
                for index, each in enumerate(indy_list_of_column_labels):
                    dict1[each] = list_of_defaults1[index]
                indy_list_of_dicts_of_table_rows.append(dict1)
    else:
        # need to get from the tables
        if find_defaults:
            indy_list_of_dicts_of_table_rows = for_development_of_omic_counts_get_some_defaults(indy_list_of_column_labels)
        else:
            # todo-sck need to get the data when update or review, make sure, for update, that sample labels are marked as y if there is a data point assigned to it
            pass
            # need something like this
            # if self.instance.time_1:
            #     time_1_instance = self.instance.time_1
            #     times_1 = get_split_times(time_1_instance)
            #     self.fields['time_1_day'].initial = times_1.get('day')
            #     self.fields['time_1_hour'].initial = times_1.get('hour')
            #     self.fields['time_1_minute'].initial = times_1.get('minute')

    # print("indy_list_of_dicts_of_table_rows")
    # print(indy_list_of_dicts_of_table_rows)

    indy_omic_table['indy_list_of_column_labels'] = indy_list_of_column_labels
    indy_omic_table['indy_list_of_column_labels_show_hide'] = indy_list_of_column_labels_show_hide
    indy_omic_table['indy_list_time_units_to_include_initially'] = indy_list_time_units_to_include_initially
    indy_omic_table['indy_dict_time_units_to_table_column'] = indy_dict_time_units_to_table_column
    indy_omic_table['indy_add_or_update'] = indy_add_or_update

    # sort here so that the table does not need to be sorted by default - which makes it rearrange when stuff is replaced
    r_counter = 0
    new_indy_list_of_dicts_of_table_rows = sorted(indy_list_of_dicts_of_table_rows,
                                                  key=sortkeypicker([indy_list_of_column_labels[0],
                                                                     indy_list_of_column_labels[1],
                                                                     indy_list_of_column_labels[2],
                                                                     indy_list_of_column_labels[3],
                                                                     indy_list_of_column_labels[4],
                                                                     indy_list_of_column_labels[5]
                                                                     ]))
    indy_omic_table['indy_list_of_dicts_of_table_rows'] = new_indy_list_of_dicts_of_table_rows
    # print("indy_omic_table")
    # print(indy_omic_table)

    return indy_omic_table


# sub to here in utils.py
def for_development_of_omic_counts_get_some_defaults():
    indy_list_of_column_labels = omic_metadata_collection_indy_list_of_column_labels

    indy_list_of_dicts_of_table_rows = []

    list_of_defaults1 = []
    list_of_defaults2 = []
    list_of_defaults3 = []
    list_of_defaults4 = []
    list_of_defaults5 = []

    dict1 = {}
    dict2 = {}
    dict3 = {}
    dict4 = {}
    dict5 = {}

    list_of_defaults1 = [
        'chip1',
        'efflux',
        '2',
        '0',
        '1',
        'sample20201105-05',
        'n',
        '5',
        '6',
        '1'
    ]
    list_of_defaults2 = [
        'chip2',
        'efflux',
        '1',
        '0',
        '1',
        'sample20201105-02',
        'n',
        '7',
        '9',
        '2'
    ]
    list_of_defaults3 = [
        'chip3',
        'efflux',
        '5',
        '0',
        '1',
        'sample20201105-03',
        'n',
        '9',
        '9',
        '3'
    ]
    list_of_defaults4 = [
        'chip5',
        'efflux',
        '5',
        '0',
        '1',
        'Chip5-10mL-a',
        'y',
        '9',
        '9',
        '4'
    ]
    list_of_defaults5 = [
        'chip5',
        'efflux',
        '5',
        '0',
        '1',
        'Chip5-10mL-b',
        'n',
        '9',
        '9',
        '5'
    ]

    # make a default dict
    # if this is an edit form, these lists will need initialized with what was previously saved
    for index, each in enumerate(indy_list_of_column_labels):
        dict1[each] = list_of_defaults1[index]
        dict2[each] = list_of_defaults2[index]
        dict3[each] = list_of_defaults3[index]
        dict4[each] = list_of_defaults4[index]
        dict5[each] = list_of_defaults5[index]
    indy_list_of_dicts_of_table_rows.append(dict1)
    indy_list_of_dicts_of_table_rows.append(dict2)
    indy_list_of_dicts_of_table_rows.append(dict3)
    indy_list_of_dicts_of_table_rows.append(dict4)
    indy_list_of_dicts_of_table_rows.append(dict5)

    return indy_list_of_dicts_of_table_rows


# sck sub here in utils.py - not using right not, but keep in case need later
def omic_find_sets_of_prefixes_and_numbers_for_well_names(header_list):
    prefix_long = []
    number_long = {}
    # todo-sck make these all UPPER case!!
    for str in header_list:
        if not (str == 'gene' or str == 'gene reference' or str == 'name'):
            # loop to iterating characters
            index = len(str)-1
            while index >= 0:

                # checking if character is numeric,
                # saving index
                if str[index].isdigit():
                    index = index - 1
                else:
                    break

            prefix_long.append(str[:index+1])
            # todo-sck - do want to make it a number or leave as a string?
            # if number it, it will not match a recombination of the two, which could be a problem
            # number_long.append(int(str[index+1:]))
            thisStr = str[index+1:]
            if thisStr is None or len(thisStr) == 0:
                number_long[987654321] = None
            else:
                thisKey = int(thisStr)
                number_long[thisStr] = thisKey

    # Just stored here for example...used after this function in a different one ...
    # uni_list = copy.deepcopy(data_dicts.get('indy_file_column_header_list'))
    # for item in df_column_headers_stripped:
    #     if item not in uni_list:
    #         uni_list.append(item)

    return [long_list_to_unique_list(prefix_long), number_long]


# sck
# function to get unique values
def long_list_to_unique_list(long_list):
    unique_list = []

    for each in long_list:
        if each not in unique_list:
            unique_list.append(each)

    return unique_list


# sck called for ajax.py
def function_to_make_a_model_location_dictionary(this_model_pk):
    location_dict = {}

    qs_locations = OrganModelLocation.objects.filter(
        organ_model_id=this_model_pk
    ).prefetch_related(
        'sample_location'
    )
    if len(qs_locations) > 0:
        for each in qs_locations:
            location_dict[each.sample_location.id] = each.sample_location.name
    else:
        qs_locations = AssaySampleLocation.objects.all()
        for each in qs_locations:
            if each.name.lower() == 'na' or each.name.lower() == 'unspecified':
                pass
            else:
                location_dict[each.id] = each.name

    # print('location_dict ', location_dict)
    # location_dict {31: 'Well', 30: 'Media'}
    return location_dict


# sck
# time unit for display and store (when giving as a unit and a time, not in DD HH MM (then use the other function)
def convert_time_from_mintues_to_unit_given(tvalue, unit_given):
    if unit_given == 'day':
        ctime = (tvalue/24.0)/60.0
    elif unit_given == 'hour':
        ctime = tvalue / 60.0
    else:
        ctime = tvalue
    return ctime


# sck
# time unit for display and store (when giving as a unit and a time, not in DD HH MM (then use the other function)
def convert_time_unit_given_to_minutes(tvalue, unit_given):
    if unit_given == 'day':
        ctime = tvalue*24.0*60.0
    elif unit_given == 'hour':
        ctime = tvalue*60.0
    else:
        ctime = tvalue
    return ctime


# sck sub in utils.py
# from https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-keys-in-python
# call like this a = sorted(b, key=sortkeypicker(['-Total_Points', 'TOT_PTS_Misc']))
# where b is the list of dictionaries
def sortkeypicker(keynames):
    negate = set()
    for i, k in enumerate(keynames):
        if k[:1] == '-':
            keynames[i] = k[1:]
            negate.add(k[1:])
    def getit(adict):
       composite = [adict[k] for k in keynames]
       for i, (k, v) in enumerate(zip(keynames, composite)):
           if k in negate:
               composite[i] = -v
       return composite
    return getit


# sck forms.py - qc for indy omic count metadata
def data_quality_clean_check_for_omic_metadata_gui(self, data):
    # only comes here if something was changed in the metadata table
    # print('in qc ')
    true_to_continue = True
    study_id = self.instance.id
    # print('data ', data)
    list_of_dicts = json.loads(self.data.get('indy_list_of_dicts_of_table_rows', '[]'))
    # print('list_of_dicts ', list_of_dicts)
    indy_list_of_column_labels = omic_metadata_collection_indy_list_of_column_labels

    list_of_sample_labels = []

    # could be these conditions:
    # 1 The list - has a dict that has a pk match to the Table (previous save)
    # 2 The list - has a dict that has a null pk (new rows)
    # 3 The existing table - has a pk that is not longer in the list of dicts (removed)
    for dict in list_of_dicts:

        for key, value in dict.items():
            # print(key, '->'+str(value)+'<')

            if key == 'matrix_item_pk' and len(str(value)) == 0:
                true_to_continue = False
                validation_message = 'One or more chip or well names is blank in the table.'
                validation_message = validation_message
                raise ValidationError(validation_message, code='invalid')
            if key == 'sample_location_pk' and len(str(value)) == 0:
                true_to_continue = False
                validation_message = 'One or more sample locations is blank in the table.'
                validation_message = validation_message
                raise ValidationError(validation_message, code='invalid')
            if key == 'Sample Label' and value in list_of_sample_labels:
                true_to_continue = False
                validation_message = 'It looks like a Sample Label is used more than once. Make Sample Labels unique.'
                validation_message = validation_message
                raise ValidationError(validation_message, code='invalid')
            else:
                list_of_sample_labels.append(value)

    return true_to_continue


# sck forms.py - qc for indy omic count metadata
def process_the_omic_metadata(self, data):
    true_to_continue = True
    study_id = self.instance.id
    # print('data ', data)
    list_of_dicts = json.loads(self.data.get('indy_list_of_dicts_of_table_rows', '[]'))
    # print('list_of_dicts ', list_of_dicts)
    indy_list_of_column_labels = omic_metadata_collection_indy_list_of_column_labels

    # could be these conditions:
    # 1 The list - has a dict that has a pk match to the Table (previous save)
    # 2 The list - has a dict that has a null pk (new rows)
    # 3 The existing table - has a pk that is not longer in the list of dicts (removed)
    for dict in list_of_dicts:

        for key, value in dict.items():
            print(key, '->'+str(value)+'<')
        #     sample_label_queryset = AssayOmicSampleMetadata.objects.filter(
        #         study_id=study_id,
        #     )
        #     sample_to_pk_dictionary = {}
        #
        #     for index, each in enumerate(sample_label_queryset):
        #         sample_to_pk_dictionary[each.name] = each.id
        #
        # list_of_sample_labels = AssayOmicSampleMetadata.objects.filter(
        #     study_id=study_id,
        # ).values_list('sample_name', flat=True)

    return true_to_continue
