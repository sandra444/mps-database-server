# coding=utf-8
import ujson as json
from collections import defaultdict
# TODO STOP USING WILDCARD IMPORTS
from django.http import *
from .models import *
from microdevices.models import MicrophysiologyCenter, Microdevice

# from mps.settings import TEMPLATE_VALIDATION_STARTING_COLUMN_INDEX
from .forms import (
    AssayChipReadoutForm,
    AssayPlateReadoutForm,
    AssayChipReadoutInlineFormset,
    AssayPlateReadoutInlineFormset
)

from .utils import number_to_label, TIME_CONVERSIONS, DEFAULT_CSV_HEADER, CHIP_DATA_PREFETCH

import csv
from StringIO import StringIO

# from.utils import(
#     valid_chip_row,
#     stringify_excel_value,
#     unicode_csv_reader,
#     get_row_and_column,
#     process_readout_value,
#     get_sheet_type
# )
# import xlrd

# TODO FIX SPAGHETTI CODE
from .forms import ReadoutBulkUploadForm
from django.forms.models import inlineformset_factory

# from django.utils import timezone

import logging
logger = logging.getLogger(__name__)

# Calling main is and always will be indicative of an error condition.
# ajax.py is strictly for AJAX requests

# Ajax requests are sent to ajax(request) and funneled into the correct
# handler function using a simulated Python switch routing function

# TODO OPTIMIZE DATABASE HITS


def main(request):
    """Default to server error"""
    return HttpResponseServerError()


# TODO ADD BASE LAYOUT CONTENT TO ASSAY LAYOUT
def fetch_assay_layout_content(request):
    """Return compounds in a layout

    Receives the following from POST:
    id -- the id of the model of interest
    model -- the model of interest
    """

    current_id = request.POST.get('id', '')
    model = request.POST.get('model', '')

    if not model and current_id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'assay_layout':
        layout = AssayLayout.objects.get(id=current_id)

    elif model == 'assay_device_setup':
        layout = AssayPlateSetup.objects.get(id=current_id).assay_layout

    elif model == 'assay_device_readout':
        layout = AssayPlateReadout.objects.get(id=current_id).setup.assay_layout

    data = defaultdict(dict)

    # Fetch compounds
    compounds = AssayWellCompound.objects.filter(assay_layout=layout).prefetch_related(
        'assay_layout',
        'assay_compound_instance__compound_instance__compound',
        'assay_compound_instance__compound_instance__supplier',
        'assay_compound_instance__concentration_unit'
    ).order_by('compound__name')

    for compound in compounds:
        well = compound.row + '_' + compound.column
        if not 'compounds' in data[well]:
            data[well]['compounds'] = []
        receipt_date = ''
        if compound.assay_compound_instance.compound_instance.receipt_date:
            receipt_date = compound.assay_compound_instance.compound_instance.receipt_date.isoformat()
        data[well]['compounds'].append({
            'name': compound.assay_compound_instance.compound_instance.compound.name,
            'id': compound.assay_compound_instance.compound_instance.compound_id,
            'concentration': compound.assay_compound_instance.concentration,
            'concentration_unit_id': compound.assay_compound_instance.concentration_unit_id,
            'concentration_unit': compound.assay_compound_instance.concentration_unit.unit,
            'supplier': compound.assay_compound_instance.compound_instance.supplier.name,
            'lot': compound.assay_compound_instance.compound_instance.lot,
            'receipt_date': receipt_date,
            'addition_time': compound.assay_compound_instance.addition_time,
            'duration': compound.assay_compound_instance.duration
            # 'well': well
        })

    # Fetch timepoints
    timepoints = AssayWellTimepoint.objects.filter(assay_layout=layout).prefetch_related('assay_layout')

    for timepoint in timepoints:
        well = timepoint.row + '_' + timepoint.column
        data[well].update({'timepoint': timepoint.timepoint})

    # Fetch labels
    labels = AssayWellLabel.objects.filter(assay_layout=layout).prefetch_related('assay_layout')

    for label in labels:
        well = label.row + '_' + label.column
        data[well].update({'label': label.label})

    # Fetch types
    current_types = AssayWell.objects.filter(assay_layout=layout).prefetch_related('assay_layout', 'well_type')

    for current_type in current_types:
        well = current_type.row + '_' + current_type.column
        data[well].update({
            'type': current_type.well_type.well_type,
            'type_id': current_type.well_type_id,
            'color': current_type.well_type.background_color
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_readout(request):
    """Get the current plate readout data

    From POST:
    current_id - the current ID
    model - what model the ID is for
    """
    current_id = request.POST.get('id', '')
    model = request.POST.get('model', '')

    if not model and current_id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'assay_device_readout':
        current_readout_id = AssayPlateReadout.objects.get(id=current_id)

    elif model == 'assay_plate_test_results':
        current_readout_id = AssayPlateTestResult.objects.get(id=current_id).readout

    # data = defaultdict(list)
    data = []

    # TODO NOTE THAT THIS DOES NOT ORDER THE ROWS AND COLUMNS CORRECTLY
    # TODO PLEASE NOTE THIS IS A STOP GAP; CHANGE AFTER REVISING ROW AND COLUMN
    readouts = AssayReadout.objects.filter(
        assay_device_readout=current_readout_id
    ).prefetch_related(
        'assay_device_readout__setup__assay_run_id',
        'assay__assay_id',
        'assay__readout_unit'
    ).order_by(
        'assay',
        'row',
        'column',
        'elapsed_time',
        'update_number',
        'quality'
    )

    time_unit = AssayPlateReadout.objects.filter(id=current_readout_id.id)[0].timeunit.unit

    for readout in readouts:
        # TODO DRY DICTATES THAT I SHOULDN'T JUST COPY THIS TO UTILS
        notes = readout.notes
        if readout.update_number:
            notes = notes + '\nUpdate #' + unicode(readout.update_number)

        data.append({
            'plate_id': readout.assay_device_readout.setup.assay_plate_id,
            'row': readout.row,
            'column': readout.column,
            'value': readout.value,
            'assay': readout.assay.assay_id.assay_short_name,
            'time': readout.elapsed_time,
            # TODO SOMEWHAT FRIVOLOUS CONSIDER REVISING
            'time_unit': time_unit,
            'value_unit': readout.assay.readout_unit.unit,
            'feature': readout.assay.feature,
            'quality': readout.quality,
            'notes': notes,
            'update_number': readout.update_number
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_layout_format_labels(request):
    """Return layout format labels

    Receives the following from POST:
    id -- the id of the model of interest
    model -- the model of interest
    """

    current_id = request.POST.get('id', '')
    model = request.POST.get('model', '')

    if not model and current_id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'device':
        layout = Microdevice.objects.get(id=current_id)

    elif model == 'assay_layout':
        layout = AssayLayout.objects.get(id=current_id).device

    elif model == 'assay_device_setup':
        layout = AssayPlateSetup.objects.get(id=current_id).assay_layout.device

    elif model == 'assay_device_readout':
        layout = AssayPlateReadout.objects.get(id=current_id).setup.assay_layout.device

    data = {}

    # if layout.column_labels and layout.row_labels:
    #     column_labels = layout.column_labels.split()
    #     row_labels = layout.row_labels.split()
    # # Contrived way to deal with models without labels
    # else:
    #     column_labels = None
    #     row_labels = None

    column_labels = []
    row_labels = []

    if layout.number_of_columns:
        for x in range(layout.number_of_columns):
            column_labels.append(x + 1)

    if layout.number_of_rows:
        for x in range(layout.number_of_rows):
            row_labels.append(number_to_label(x + 1))

    data.update({
        'id': layout.id,
        'column_labels': column_labels,
        'row_labels': row_labels,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_well_types(request):
    """Return well type ids and colors"""

    data = {}

    for well_type in AssayWellType.objects.all():
        data.update(
            {
                well_type.id: {
                    'name': well_type.well_type,
                    'color': well_type.background_color
                }
            }
        )

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# Fetches and displays assay layout from plate readout
def fetch_plate_info(request):
    """Returns dynamic info for plate assays

    Receives the following from POST:
    id -- the ID of the Assay Plate Readout of interest
    """

    assay_id = request.POST.get('id', '')

    if not assay_id:
        logger.error('assay id not present in request to fetch_assay_info')
        return HttpResponseServerError()

    assay = AssayPlateReadout.objects.get(id=assay_id)

    data = {}

    data.update({
        'assay_layout_id': assay.assay_layout_id,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_center_id(request):
    """Returns center ID for dynamic run form

    Receives the following from POST:
    id -- the ID of the Microphysiology Center of interest
    """

    group = request.POST.get('id', '')

    if not group:
        logger.error('center not present in request to fetch_assay_info')
        return HttpResponseServerError()

    data = {}

    try:
        center_data = MicrophysiologyCenter.objects.filter(groups__id=group)[0]

        data.update({
            'center_id': center_data.center_id,
            'center_name': center_data.center_name,
        })

    except:
        data.update({
            'center_id': '',
            'center_name': '',
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# TODO THIS WAS A STRING TO BE EXPEDIENT WRT TO THE JAVSCRIPT IN READOUT ADD, BUT SHOULD BE REVISED
# def get_chip_readout_data_as_csv(chip_ids, chip_data=None, both_assay_names=False):
#     """Returns readout data as a csv in the form of a string
#
#     Params:
#     chip_ids - Readout IDs to use to acquire chip data (if data not provided)
#     chip_data - Readout raw data, optional, acquired with chip_ids if not provided
#     both_assay_names - Indicates that both assay names should be returned (not currently used)
#     """
#
#     # PLEASE NOTE: THIS AFFECTS PROCESSING OF QC
#     # DO NOT MODIFY THIS WITHOUT ALSO CHANGING modify_qc_status_chip
#     if not chip_data:
#         chip_data = AssayChipRawData.objects.prefetch_related(
#             'assay_id__assay_id',
#             'assay_chip_id__chip_setup'
#         ).filter(
#             assay_chip_id__in=chip_ids
#         ).order_by(
#             'assay_chip_id__chip_setup__assay_chip_id',
#             'assay_id__assay_id__assay_short_name',
#             'time',
#             'quality',
#             'update_number'
#         )
#
#     csv = ''
#
#     for raw in chip_data:
#         if ',' in raw.assay_chip_id.chip_setup.assay_chip_id:
#             csv += '"' + unicode(raw.assay_chip_id.chip_setup.assay_chip_id) + '"' + ','
#         else:
#             csv += raw.assay_chip_id.chip_setup.assay_chip_id + ','
#         csv += unicode(raw.time) + ','
#         # Add time unit
#         csv += unicode(raw.assay_chip_id.timeunit) + ','
#         # Now uses full name
#         # csv += unicode(raw.assay_id.assay_id.assay_short_name) + ','
#         csv += unicode(raw.assay_id.assay_id.assay_name) + ','
#         if ',' in raw.field_id:
#             csv += '"' + unicode(raw.field_id) + '"' + ','
#         else:
#             csv += unicode(raw.field_id) + ','
#         # Format to two decimal places
#         value = raw.value
#         # Check if None first before format
#         if value is not None:
#             value = '%.2f' % value
#         else:
#             value = ''
#         # Get rid of trailing zero and decimal if necessary
#         value = value.rstrip('0').rstrip('.') if '.' in value else value
#         csv += value + ','
#         # Add value unit
#         csv += unicode(raw.assay_id.readout_unit) + ','
#         # End with the quality and notes
#         if ',' in raw.quality:
#             csv += '"' + unicode(raw.quality) + '"' + ','
#         else:
#             csv += unicode(raw.quality) + ','
#         csv += '"' + unicode(raw.notes) + '"' + ','
#         csv += '"' + unicode(raw.update_number) + '"\n'
#
#     return csv


# TODO EMPLOY THIS FUNCTION ELSEWHERE
def get_split_times(time_in_minutes):
    """Takes time_in_minutes and returns a dic with the time split into day, hour, minute"""
    times = {
        'day': 0,
        'hour': 0,
        'minute': 0
    }
    time_in_minutes_remaining = time_in_minutes
    for time_unit, conversion in TIME_CONVERSIONS.items():
        initial_time_for_current_field = int(time_in_minutes_remaining / conversion)
        if initial_time_for_current_field:
            times[time_unit] = initial_time_for_current_field
            time_in_minutes_remaining -= initial_time_for_current_field * conversion
    # Add fractions of minutes if necessary
    if time_in_minutes_remaining:
        times['minute'] += time_in_minutes_remaining

    return times


def get_chip_readout_data_as_csv(chip_ids, chip_data=None, both_assay_names=False, include_header=False):
    """Returns readout data as a csv in the form of a string

    Params:
    chip_ids - Readout IDs to use to acquire chip data (if data not provided)
    chip_data - Readout raw data, optional, acquired with chip_ids if not provided
    both_assay_names - Indicates that both assay names should be returned (not currently used)
    """
    if not chip_data:
        chip_data = AssayChipRawData.objects.prefetch_related(
            *CHIP_DATA_PREFETCH
        ).filter(
            assay_chip_id__in=chip_ids
        ).order_by(
            'assay_chip_id__chip_setup__assay_chip_id',
            'assay_instance__target__name',
            'assay_instance__method__name',
            'sample_location__name',
            'time',
            'quality',
            'update_number'
        )

    data = []

    if include_header:
        data.append(
            DEFAULT_CSV_HEADER
        )

    for data_point in chip_data:
        chip_id = data_point.assay_chip_id.chip_setup.assay_chip_id
        assay_plate_id = data_point.assay_plate_id
        assay_well_id = data_point.assay_well_id

        # Add time here
        time_in_minutes = data_point.time
        times = get_split_times(time_in_minutes)

        target = data_point.assay_instance.target.name
        method = data_point.assay_instance.method.name
        sample_location = data_point.sample_location.name
        value = data_point.value
        value_unit = data_point.assay_instance.unit.unit
        quality = data_point.quality
        # TODO ADD OTHER STUFF
        notes = data_point.notes

        data.append(
            [
                chip_id,
                assay_plate_id,
                assay_well_id,
                times.get('day'),
                times.get('hour'),
                times.get('minute'),
                target,
                method,
                sample_location,
                value,
                value_unit,
                quality,
                notes
            ]
        )

    string_io = StringIO()
    csv_writer = csv.writer(string_io)
    for one_line_of_data in data:
        csv_writer.writerow(one_line_of_data)

    return string_io.getvalue()


def get_chip_readout_data_as_json(chip_ids, chip_data=None):
    if not chip_data:
        chip_data = AssayChipRawData.objects.prefetch_related(
            *CHIP_DATA_PREFETCH
        ).filter(
            assay_chip_id__in=chip_ids
        ).order_by(
            'assay_chip_id__chip_setup__assay_chip_id',
            'assay_instance__target__name',
            'assay_instance__method__name',
            'sample_location__name',
            'time',
            'quality',
            'update_number'
        )

    data = {}

    data_points = []
    sample_locations = {}
    assay_instances = {}

    for data_point in chip_data:
        chip_id = data_point.assay_chip_id.chip_setup.assay_chip_id
        assay_plate_id = data_point.assay_plate_id
        assay_well_id = data_point.assay_well_id
        # Add time here
        time_in_minutes = data_point.time
        times = get_split_times(time_in_minutes)
        assay_instance = data_point.assay_instance
        sample_location = data_point.sample_location
        value = data_point.value
        quality = data_point.quality
        # TODO ADD OTHER STUFF
        notes = data_point.notes

        update_number = data_point.update_number
        replicate = data_point.replicate

        if sample_location.id not in sample_locations:
            sample_locations.update(
                {
                    sample_location.id: {
                        'name': sample_location.name,
                        'description': sample_location.description
                    }
                }
            )

        if assay_instance.id not in assay_instances:
            assay_instances.update(
                {
                    assay_instance.id: {
                        'target_name': assay_instance.target.name,
                        'target_short_name': assay_instance.target.short_name,
                        'method_name': assay_instance.method.name,
                        'unit': assay_instance.unit.unit,
                    }
                }
            )

        data_point_fields = {
            'chip_id': chip_id,
            'assay_plate_id': assay_plate_id,
            'assay_well_id': assay_well_id,
            'time_in_minutes': time_in_minutes,
            'day': times.get('day'),
            'hour': times.get('hour'),
            'minute': times.get('minute'),
            'assay_instance_id': assay_instance.id,
            'sample_location_id': sample_location.id,
            'value': value,
            'quality': quality.strip(),
            # TODO ADD OTHER STUFF
            'notes': notes.strip(),
            'update_number': update_number,
            'replicate': replicate.strip()
        }
        data_points.append(data_point_fields)

    data.update({
        'data_points': data_points,
        'sample_locations': sample_locations,
        'assay_instances': assay_instances
    })
    return data


# TODO Needs refactor
def fetch_chip_readout(request):
    """Returns the Raw Chip Data stored for a Chip Readout

    Receives the following from POST:
    id -- the ID of the Chip Readout of interest
    """

    chip_id = request.POST.get('id', '')

    if not chip_id:
        logger.error('chip not present in request to fetch_chip_readout')
        return HttpResponseServerError()

    data = get_chip_readout_data_as_json([chip_id])

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def get_readout_data(raw_data, related_compounds_map, key, percent_control, include_all):
    """Get all readout data for a study and return it in JSON format

    From POST:
    raw_data - the AssayChipRawData needed to create the JSON
    key - whether this data should be considered by device or by compound
    percent_control - whether to use percent control (WIP)
    include_all - whether to include all values
    """

    # TODO ACCOUNT FOR CASE WHERE ASSAY HAS TWO DIFFERENT UNITS?
    # TODO MAY FORBID THIS CASE, MUST ASK FIRST
    # TODO ACCOUNT FOR CASE WHERE STUDY HAS MORE THAN ONE COMPOUND
    # Organization is assay -> unit -> compound/tag -> field -> time -> value
    assays = {}
    initial_data = {}
    averaged_data = {}
    controls = {}

    for raw in raw_data:
        # Now uses full name
        # assay = raw.assay_id.assay_id.assay_short_name
        # Deprecated
        # assay = raw.assay_id.assay_id.assay_name
        unit = raw.assay_id.readout_unit.unit
        # Deprecated
        # field = raw.field_id
        value = raw.value

        # TODO CHANGE TO USE FOLLOWING
        assay_instance = raw.assay_instance
        target = assay_instance.target.name
        # Not currently used
        method = assay_instance.method.name

        sample_location = raw.sample_location.name

        # Convert all times to days for now
        # Get the conversion unit
        # scale = raw.assay_chip_id.timeunit.scale_factor
        # time = '{0:.2f}'.format((scale / 1440.0) * raw.time)
        # # Have time in minutes for comparing to addition_time and duration
        # time_minutes = scale * raw.time

        time_minutes = raw.time
        # Time will always be in days
        time = '{0:.2f}'.format(raw.time / 1440.0)

        quality = raw.quality

        if value is not None and (include_all or not quality):
            # Get tag for data point
            # If by compound
            if key == 'compound':
                compounds = related_compounds_map.get(raw.assay_chip_id.chip_setup_id, [])
                if compounds:
                    compounds_to_add = []

                    for compound in compounds:
                        # Previously included only compounds within duration
                        # if compound.addition_time <= time_minutes and compound.duration + compound.addition_time >= time_minutes:
                        # Everything past addition time will be listed as effected
                        if compound.addition_time <= time_minutes:
                            compounds_to_add.append(
                                compound.compound_instance.compound.name +
                                ' (' + str(compound.concentration) + ' ' + compound.concentration_unit.unit + ')'
                            )

                    if not compounds_to_add:
                        tag = '-Control-'
                    else:
                        tag = ' & '.join(sorted(compounds_to_add))
                else:
                    tag = '-Control-'
            # If by device
            else:
                tag = raw.assay_chip_id.chip_setup.assay_chip_id

                # Specifically add to consolidated control if this is a device-by-device control
                if percent_control and raw.assay_chip_id.chip_setup.chip_test_type == 'control':
                    initial_data.setdefault(target, {}).setdefault(unit, {}).setdefault('-Control-', {}).setdefault(sample_location, {}).setdefault(time, []).append(value)

            # Set data in nested monstrosity that is initial_data
            initial_data.setdefault(target, {}).setdefault(unit, {}).setdefault(tag, {}).setdefault(sample_location, {}).setdefault(time, []).append(value)

    for target, units in initial_data.items():
        for unit, tags in units.items():
            for tag, sample_locations in tags.items():
                for sample_location, time_values in sample_locations.items():
                    for time, values in time_values.items():
                        if percent_control and tag == '-Control-':
                            controls.update({(target, unit, sample_location, time): sum(values) / float(len(values))})
                        # Add to averaged data if this isn't a average control value for device-by-device
                        if not (tag == '-Control-' and key != 'compound'):
                            averaged_data.setdefault(target, {}).setdefault(unit, {}).setdefault(tag, {}).setdefault(sample_location, {}).update({
                                time: sum(values) / float(len(values))
                            })

    for target, units in averaged_data.items():
        for unit, tags in units.items():
            accomadate_units = len(units) > 1
            for tag, sample_locations in tags.items():
                accomadate_sample_location = len(sample_locations) > 1
                for sample_location, time_values in sample_locations.items():
                    for time, value in time_values.items():
                        if not percent_control:
                            # Not converted to percent control
                            # Newline is used as a delimiter
                            assay_label = target + '\n' + unit

                            if accomadate_sample_location:
                                current_key = tag + ' ' + sample_location
                            else:
                                current_key = tag

                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('time', []).append(time)
                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('values', []).append(value)

                        elif controls.get((target, unit, sample_location, time), False):
                            control_value = controls.get((target, unit, sample_location, time))
                            # Convert to percent control
                            if accomadate_units:
                                current_unit = '%Control [' + unit + ']'
                            else:
                                current_unit = '%Control'

                            # Newline is used as a delimiter
                            assay_label = target + '\n' + current_unit

                            if accomadate_sample_location:
                                current_key = tag + ' ' + sample_location
                            else:
                                current_key = tag

                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('time', []).append(time)
                            # Perform conversion
                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('values', []).append((value / control_value) * 100)

    return assays


# TODO REQUIRES REVISION
# TODO NEED TO CONFIRM UNITS ARE THE SAME (ELSE CONVERSION)
def fetch_readouts(request):
    """Get all readouts for a given study for Study Summary

    Receives the following from POST:
    study -- the study to acquire readouts from
    key -- specifies whether to split readouts by compound or device
    percent_control -- specifies whether to convert to percent control
    include_all -- specifies whether to include all data (exclude invalid if null string)
    """
    study = request.POST.get('study', '')
    key = request.POST.get('key', '')
    percent_control = request.POST.get('percent_control', '')
    include_all = request.POST.get('include_all', '')

    if percent_control == 'true':
        percent_control = True
    else:
        percent_control = False

    # Get chip readouts
    readouts = AssayChipReadout.objects.filter(
        chip_setup__assay_run_id_id=study
    ).prefetch_related(
        'chip_setup',
        'chip_setup__assay_run_id_id'
    )

    related_compounds_map = {}

    if key == 'compound':
        setups = readouts.values_list('chip_setup_id')

        raw_data = AssayChipRawData.objects.filter(
            assay_chip_id=readouts
        ).prefetch_related(
            *CHIP_DATA_PREFETCH
        )

        related_compounds = AssayCompoundInstance.objects.filter(
            chip_setup=setups
        ).prefetch_related(
            'compound_instance__compound',
            'compound_instance__supplier',
            'concentration_unit',
            'chip_setup'
        )

        for compound in related_compounds:
            related_compounds_map.setdefault(compound.chip_setup_id, []).append(compound)

    else:
        raw_data = AssayChipRawData.objects.filter(
            assay_chip_id=readouts
        ).prefetch_related(
            *CHIP_DATA_PREFETCH
        )

    assays = get_readout_data(raw_data, related_compounds_map, key, percent_control, include_all)

    data = {
        'assays': assays,
    }

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# Should these be refactored just to use fetch_dropdown instead?
def fetch_organ_models(request):
    """Gets a dropdown of organ models for Chip Setup

    Receives the following from POST:
    device -- the device to acquire organ models from
    """
    dropdown = u'<option value="">---------</option>'

    device = request.POST.get('device', '')

    findings = OrganModel.objects.filter(device_id=device).prefetch_related('device')

    for finding in findings:
        # match value to the desired subject ID
        value = str(finding.id)
        dropdown += u'<option value="' + value + '">' + unicode(finding) + '</option>'

    data = {}

    data.update({
        'dropdown': dropdown,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_protocols(request):
    """Gets a dropdown of protocols for Chip Setup

    Receives the following from POST:
    organ_model -- the organ model to acquire protocols from
    """
    dropdown = u'<option value="">---------</option>'

    organ_model = request.POST.get('organ_model', '')

    # Order should be from newest to oldest
    findings = OrganModelProtocol.objects.filter(
        organ_model_id=organ_model
    ).prefetch_related(
        'organ_model'
    ).order_by('-version')

    # We no longer default to the first protocol to prevent unexpected behavior
    # Add the protocols
    for finding in findings:
        # match value to the desired subject ID
        value = str(finding.id)
        dropdown += u'<option value="' + value + '">' + unicode(finding) + '</option>'

    data = {}

    data.update({
        'dropdown': dropdown,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_protocol(request):
    """Get the file location for a given protocol

    Receives the following from POST:
    protocol -- the ID of the protocol of interest
    """
    data = {}

    protocol_id = request.POST.get('protocol', '')

    protocol = OrganModelProtocol.objects.filter(pk=protocol_id)

    if protocol and protocol[0].organ_model.center and any(i in protocol[0].organ_model.center.groups.all() for i in request.user.groups.all()):
        protocol_file = protocol[0].file
        file_name = '/'.join(protocol_file.name.split('/')[1:])
        href = '/media/' + protocol_file.name
        data.update({
            'file_name': file_name,
            'href': href
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_dropdown(request):
    """Acquires options for whittling down number of dropdown

    Receives the following from POST:
    master -- master is what determines the subject's drop down choices
    subject -- subject is the model of interest as selected from the above dictionary
    next_model -- the next model to filter (if the subject is two FK away)
    next_filter -- second filter (if the subject is two FK away)
    """

    dropdown = '<option value="">---------</option>'

    # the model who's dropdown you want to whittle down
    all_models = {
        'AssayChipReadout': AssayChipReadout,
        'AssayChipSetup': AssayChipSetup,
        'AssayRun': AssayRun,
        'AssayChipReadoutAssay': AssayChipReadoutAssay,
        'AssayPlateReadoutAssay': AssayPlateReadoutAssay
    }

    # master is what determines the subject's drop down choices
    # master itself is a string for the filter that comes later
    master = request.POST.get('master', '')
    master_id = request.POST.get('master_id', '')

    # subject is the model of interest as selected from the above dictionary
    subject = all_models.get(request.POST.get('subject', ''))

    # filter is for additional filtering (for instance, if a subject is two FK away
    next_model = request.POST.get('next_model', '')
    next_filter = request.POST.get('next_filter', '')

    findings = subject.objects.filter(**{master: master_id})

    if next_model and next_filter:
        next_model = all_models.get(next_model)
        original = list(findings)
        findings = []

        for item in original:
            findings.extend(next_model.objects.filter(**{next_filter: item}))

    for finding in findings:
        # match value to the desired subject ID
        value = str(finding.id)
        dropdown += '<option value="' + value + '">' + str(finding) + '</option>'

    data = {}

    data.update({
        'dropdown': dropdown,
    })

    return HttpResponse(json.dumps(data),
                        content_type='application/json')


# USE THE POST DATA TO BUILD A BULKUPLOAD FORM
# DO NOT EXPLICITLY CALL VALIDATION
def validate_bulk_file(request):
    """Validates a bulk file and returns either errors or a preview of the data entered

    Receives the following from POST:
    study -- the study to acquire readouts from
    key -- specifies whether to split readouts by compound or device
    percent_control -- specifies whether to convert to percent control
    include_all -- specifies whether to include all data (exclude invalid if null string)
    """
    study = request.POST.get('study', '')
    key = request.POST.get('key', '')
    percent_control = request.POST.get('percent_control', '')
    include_all = request.POST.get('include_all', '')
    # overwrite_option = request.POST.get('overwrite_option', '')
    # bulk_file = request.FILES.get('bulk_file', None)

    this_study = AssayRun.objects.get(pk=int(study))

    form = ReadoutBulkUploadForm(request.POST, request.FILES, instance=this_study)

    if form.is_valid():
        form_data = form.cleaned_data

        preview_data = form_data.get('preview_data')

        # Only chip preview right now
        chip_raw_data = preview_data.get('chip_preview')

        # NOTE THE EMPTY DIC, RIGHT NOW BULK PREVIEW NEVER SHOWS COMPOUND JUST DEVICE
        assays = get_readout_data(chip_raw_data, {}, key, percent_control, include_all)

        data = {'assays': assays}

        return HttpResponse(json.dumps(data),
                            content_type="application/json")

    else:
        errors = ''
        if form.errors.get('__all__'):
            errors += form.errors.get('__all__').as_text()
        data = {
            'errors': errors
        }
        return HttpResponse(json.dumps(data),
                            content_type='application/json')

# TODO DUPLICATED THUS VIOLATING DRY
ACRAFormSet = inlineformset_factory(
    AssayChipReadout,
    AssayChipReadoutAssay,
    formset=AssayChipReadoutInlineFormset,
    extra=1,
    exclude=[],
)


# USE THE POST DATA TO BUILD A BULKUPLOAD FORM
# DO NOT EXPLICITLY CALL VALIDATION
def validate_individual_chip_file(request):
    """Validates a bulk file and returns either errors or a preview of the data entered

    Receives the following from POST:
    study -- the study to acquire readouts from
    key -- specifies whether to split readouts by compound or device
    percent_control -- specifies whether to convert to percent control
    include_all -- specifies whether to include all data (exclude invalid if null string)
    """
    study_id = request.POST.get('study', '')
    key = request.POST.get('key', '')
    percent_control = request.POST.get('percent_control', '')
    include_all = request.POST.get('include_all', '')
    readout_id = request.POST.get('readout', '')
    # overwrite_option = request.POST.get('overwrite_option', '')
    # bulk_file = request.FILES.get('bulk_file', None)

    if readout_id:
        readout = AssayChipReadout.objects.filter(pk=readout_id)
        if readout:
            readout = readout[0]
            setup_id = readout.chip_setup.id
            study = readout.chip_setup.assay_run_id
        else:
            setup_id = None
            study = AssayRun.objects.get(pk=int(study_id))
    else:
        setup_id = None
        study = AssayRun.objects.get(pk=int(study_id))

    form = AssayChipReadoutForm(study, setup_id, request.POST)
    formset = ACRAFormSet(request.POST, request.FILES, instance=form.instance)

    if formset.is_valid():
        # Validate form
        # form.is_valid()

        form_data = formset.forms[0].cleaned_data

        preview_data = form_data.get('preview_data')

        chip_raw_data = preview_data.get('chip_preview')

        csv = get_chip_readout_data_as_csv([readout_id], chip_data=chip_raw_data)

        data = {'csv': csv}

        return HttpResponse(json.dumps(data),
                            content_type="application/json")

    else:
        errors = ''
        if formset.non_form_errors():
            errors += formset.non_form_errors().as_text()
        if form.errors:
            errors += form.errors.as_text()
        data = {
            'errors': errors
        }
        return HttpResponse(json.dumps(data),
                            content_type='application/json')

APRAFormSet = inlineformset_factory(
    AssayPlateReadout,
    AssayPlateReadoutAssay,
    formset=AssayPlateReadoutInlineFormset,
    extra=1,
    exclude=[],
)


def validate_individual_plate_file(request):
    """Validates a bulk file and returns either errors or a preview of the data entered

    Receives the following from POST:
    study -- the study to acquire readouts from
    key -- specifies whether to split readouts by compound or device
    percent_control -- specifies whether to convert to percent control
    include_all -- specifies whether to include all data (exclude invalid if null string)
    """
    study_id = request.POST.get('study', '')
    readout_id = request.POST.get('readout', '')
    # overwrite_option = request.POST.get('overwrite_option', '')
    # bulk_file = request.FILES.get('bulk_file', None)

    if readout_id:
        readout = AssayPlateReadout.objects.filter(pk=readout_id)
        if readout:
            readout = readout[0]
            setup_id = readout.setup.id
            study = readout.setup.assay_run_id
        else:
            setup_id = None
            study = AssayRun.objects.get(pk=int(study_id))
    else:
        setup_id = None
        study = AssayRun.objects.get(pk=int(study_id))

    form = AssayPlateReadoutForm(study, setup_id, request.POST)
    formset = APRAFormSet(request.POST, request.FILES, instance=form.instance)

    if formset.is_valid():
        # Validate form
        # form.is_valid()

        form_data = formset.forms[0].cleaned_data

        preview_data = form_data.get('preview_data')

        data = preview_data.get('plate_preview')

        return HttpResponse(json.dumps(data),
                            content_type="application/json")

    else:
        errors = ''
        if formset.__dict__.get('_non_form_errors', ''):
            errors += formset.__dict__.get('_non_form_errors', '').as_text()
        if form.errors:
            errors += form.errors.as_text()
        data = {
            'errors': errors
        }
        return HttpResponse(json.dumps(data),
                            content_type='application/json')


def fetch_quality_indicators(request):
    """Returns quality indicators as JSON for populating dropdowns"""

    # The JSON data to return; initialize with an entry for None
    # data = [{
    #     'id': '',
    #     'code': '',
    #     'name': '',
    #     'description': 'No quality indicator selected'
    # }]
    data = []

    for quality_indicator in AssayQualityIndicator.objects.all().order_by('code'):
        data.append({
            'id': quality_indicator.id,
            'code': quality_indicator.code,
            'name': quality_indicator.name,
            'description': quality_indicator.description
        })

    return HttpResponse(json.dumps(data), content_type='application/json')

switch = {
    'fetch_assay_layout_content': fetch_assay_layout_content,
    'fetch_readout': fetch_readout,
    'fetch_layout_format_labels': fetch_layout_format_labels,
    'fetch_well_types': fetch_well_types,
    'fetch_plate_info': fetch_plate_info,
    'fetch_center_id': fetch_center_id,
    'fetch_chip_readout': fetch_chip_readout,
    'fetch_readouts': fetch_readouts,
    'fetch_dropdown': fetch_dropdown,
    'fetch_organ_models': fetch_organ_models,
    'fetch_protocols': fetch_protocols,
    'fetch_protocol': fetch_protocol,
    'validate_bulk_file': validate_bulk_file,
    'validate_individual_chip_file': validate_individual_chip_file,
    'validate_individual_plate_file': validate_individual_plate_file,
    'fetch_quality_indicators': fetch_quality_indicators
}


def ajax(request):
    """Switch to correct function given POST call

    Receives the following from POST:
    call -- What function to redirect to
    """
    post_call = request.POST.get('call', '')

    if not post_call:
        logger.error('post_call not present in request to ajax')
        return HttpResponseServerError

    # Abort if there is no valid call sent to us from Javascript
    if not post_call:
        return main(request)

    # Route the request to the correct handler function
    # and pass request to the functions
    try:
        # select the function from the dictionary
        procedure = switch[post_call]

    # If all else fails, handle the error message
    except KeyError:
        return main(request)

    else:
        # execute the function
        return procedure(request)
