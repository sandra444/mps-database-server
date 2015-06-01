# coding=utf-8
import ujson as json
from collections import defaultdict
from django.http import *
from .models import *
from microdevices.models import MicrophysiologyCenter, Microdevice
import logging
logger = logging.getLogger(__name__)

# Calling main is and always will be indicative of an error condition.
# ajax.py is strictly for AJAX requests

# Ajax requests are sent to ajax(request) and funneled into the correct
# handler function using a simulated Python switch routing function

def main(request):
    return HttpResponseServerError()

# TODO REQUIRES SERIOUS REVISION

# TODO ADD BASE LAYOUT CONTENT TO ASSAY LAYOUT
def fetch_assay_layout_content(request):
    """Return compounds in a layout."""

    id = request.POST.get('id')
    model = request.POST.get('model')

    if not model and id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'assay_layout':
        layout = AssayLayout.objects.get(id=id)

    elif model == 'assay_device_setup':
        layout = AssayDeviceSetup.objects.get(id=id).assay_layout

    elif model == 'assay_device_readout':
        layout = AssayDeviceReadout.objects.get(id=id).setup.assay_layout


    data = defaultdict(dict)

    # Fetch compounds
    compounds = AssayCompound.objects.filter(assay_layout=layout)

    for compound in compounds:
        well = compound.row + '_' + compound.column
        if not 'compounds' in data[well]:
            data[well]['compounds'] = []
        data[well]['compounds'].append({
            'name': compound.compound.name,
            'id': compound.compound.id,
            'concentration': compound.concentration,
            'concentration_unit': compound.concentration_unit,
            #'well': well
        })

    # Fetch timepoints
    timepoints = AssayTimepoint.objects.filter(assay_layout=layout)

    for timepoint in timepoints:
        well = timepoint.row + '_' + timepoint.column
        data[well].update({'timepoint': timepoint.timepoint})

    # Fetch labels
    labels = AssayWellLabel.objects.filter(assay_layout=layout)

    for label in labels:
        well = label.row + '_' + label.column
        data[well].update({'label': label.label})

    # Fetch types
    types = AssayWell.objects.filter(assay_layout=layout)

    for type in types:
        well = type.row + '_' + type.column
        data[well].update({
            'type': type.well_type.well_type,
            'type_id': type.well_type.id,
            'color': type.well_type.background_color
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_readout(request):
    id = request.POST.get('id')
    model = request.POST.get('model')

    if not model and id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'assay_device_readout':
        current_readout_id = AssayDeviceReadout.objects.get(id=id)

    elif model == 'assay_plate_test_results':
        current_readout_id = AssayPlateTestResult.objects.get(id=id).assay_device_id

    # data = defaultdict(list)
    data = []

    readouts = AssayReadout.objects.filter(assay_device_readout=current_readout_id)

    for readout in readouts:
        # well = readout.row + '_' + readout.column

        # data[well].append({
        #     'row': readout.row,
        #     'column': readout.column,
        #     'value': readout.value,
        # })

        data.append({
            'row': readout.row,
            'column': readout.column,
            'value': readout.value
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_layout_format_labels(request):
    """Return layout format labels."""

    id = request.POST.get('id')
    model = request.POST.get('model')

    if not model and id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    if model == 'device':
        layout = Microdevice.objects.get(id=id)

    elif model == 'assay_layout':
        layout = AssayLayout.objects.get(id=id).device

    elif model == 'assay_device_setup':
        layout = AssayDeviceSetup.objects.get(id=id).assay_layout.device

    elif model == 'assay_device_readout':
        layout = AssayDeviceReadout.objects.get(id=id).setup.assay_layout.device

    data = {}

    if layout.column_labels and layout.row_labels:
        column_labels = layout.column_labels.split()
        row_labels = layout.row_labels.split()
    # Contrived way to deal with models without labels
    else:
        column_labels = None
        row_labels = None

    data.update({
        'column_labels': column_labels,
        'row_labels': row_labels,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_well_types(request):
    """Return well type ids and colors."""

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


# Since the well types are already acquired via AJAX, it is somewhat excessive to grab the color separately
# def fetch_well_type_color(request):
#     """Return wells type colors."""
#
#     current_id = request.POST.get('id')
#
#     if not current_id:
#         logger.error('current_id was not sent with fetch_well_type_color')
#         return HttpResponseServerError()
#
#     data = AssayWellType.objects.get(id=current_id).background_color
#
#     return HttpResponse(json.dumps(data),
#                         content_type="application/json")


# Base Layout is now merged into Assay Layout
# def fetch_baseid(request):
#     """Return the base assay layout id for a given assay layout"""
#
#     current_layout_id = request.POST.get('current_layout_id')
#
#     if not current_layout_id:
#         logger.error('current_layout_id not present in request to fetch_baseid')
#         return HttpResponseServerError()
#
#     assay_layout = AssayLayout.objects.get(id=current_layout_id)
#
#     # known to set base_layout_id to an integer value correctly
#     base_layout_id = assay_layout.base_layout_id
#
#     data = {}
#     data.update({'base_layout_id': base_layout_id})
#
#     return HttpResponse(json.dumps(data),
#                         content_type="application/json")

# Base layout is now part of assay layout
# def fetch_base_layout_wells(request):
#     """Return wells in a base layout."""
#
#     base_id = request.POST.get('id')
#
#     if not base_id:
#         logger.error('base_id not present in request to fetch_base_layout_wells')
#         return HttpResponseServerError()
#
#     data = {}
#
#     data.update({
#         aw.row + '_' + aw.column: [aw.well_type.id, aw.well_type.well_type,
#                                    aw.well_type.background_color]
#         for aw in AssayWell.objects.filter(base_layout=base_id)
#     })
#
#     return HttpResponse(json.dumps(data),
#                         content_type="application/json")

# def fetch_base_layout_info(request):
#     """Return wells in a base layout."""
#
#     base_id = request.POST.get('id')
#
#     if not base_id:
#         logger.error('base_id not present in request to fetch_base_layout_info')
#         return HttpResponseServerError()
#
#     base = AssayBaseLayout.objects.get(id=base_id)
#
#     data = {}
#
#     data.update({
#         'format': {'row_labels': base.layout_format.row_labels.split(),
#                    'column_labels': base.layout_format.column_labels.split()},
#
#         'wells': {aw.row + '_' + aw.column: [aw.well_type.well_type,
#                                              aw.well_type.background_color]
#                   for aw in AssayWell.objects.filter(base_layout=base_id)}
#     })
#
#     return HttpResponse(json.dumps(data),
#                         content_type="application/json")

#Fetches and displays assay layout from plate readout
def fetch_plate_info(request):
    """Returns dynamic info for plate assays"""

    assay_id = request.POST.get('id')

    if not assay_id:
        logger.error('assay id not present in request to fetch_assay_info')
        return HttpResponseServerError()

    assay = AssayDeviceReadout.objects.get(id=assay_id)

    data = {}

    data.update({
        'assay_layout_id': assay.assay_layout_id,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_center_id(request):
    """Returns center ID for dynamic run form"""

    group = request.POST.get('id')

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

def fetch_chip_readout(request):
    """Returns the Raw Chip Data stored for a Chip Readout"""

    chip_id = request.POST.get('id')

    if not chip_id:
        logger.error('chip not present in request to fetch_chip_readout')
        return HttpResponseServerError()

    chip_data = AssayChipRawData.objects.filter(assay_chip_id=chip_id).order_by('assay_id','elapsed_time')

    time_unit = AssayChipReadout.objects.filter(id=chip_id)[0].timeunit

    csv = ""

    for raw in chip_data:
        csv += str(raw.elapsed_time) + ','
        # Add time unit
        csv += str(time_unit) + ','
        csv += str(raw.assay_id.assay_id.assay_name) + ','
        csv += str(raw.field_id) + ','
        # Format to two decimal places
        value = raw.value
        # Check if None first before format
        if value is not None:
            value = '%.2f' % raw.value
        else:
            value = str(value)
        # Get rid of trailing zero and decimal if necessary
        value = value.rstrip('0').rstrip('.') if '.' in value else value
        csv += value + ','
        # Add value unit
        csv += str(raw.assay_id.readout_unit) + '\n'

    data = {}

    data.update({
        'csv': csv,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

def fetch_context(request):
    """Acquires context for whittling down number of dropdown"""

    context = '<option value="">---------</option>'

    # the model who's dropdown you want to whittle down
    models = {
        'AssayChipReadout':AssayChipReadout,
        'AssayChipSetup':AssayChipSetup,
        'AssayRun':AssayRun,
        'AssayChipReadoutAssay':AssayChipReadoutAssay,
    }

    # master is what determines the subject's drop down choices
    # master itself is a string for the filter that comes later
    master = request.POST.get('master')
    master_id = request.POST.get('master_id')

    # subject is the model of interest as selected from the above dictionary
    subject = models.get(request.POST.get('subject'))

    # filter is for additional filtering (for instance, if a subject is two FK away
    next_model = request.POST.get('next_model')
    next_filter = request.POST.get('next_filter')

    findings = subject.objects.filter(**{master:master_id})

    if next_model and next_filter:
        next_model = models.get(next_model)
        original = list(findings)
        findings = []

        for item in original:
            findings.extend(next_model.objects.filter(**{next_filter:item}))

    for finding in findings:
        # match value to the desired subject ID
        value = str(finding.id)
        context += '<option value="' + value + '">' + str(finding) + '</option>'

    data = {}

    data.update({
        'context': context,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

switch = {
    'fetch_assay_layout_content': fetch_assay_layout_content,
    'fetch_readout': fetch_readout,
    'fetch_layout_format_labels': fetch_layout_format_labels,
    'fetch_well_types': fetch_well_types,
    # 'fetch_well_type_color': fetch_well_type_color,
    # 'fetch_baseid': fetch_baseid,
    # 'fetch_base_layout_wells': fetch_base_layout_wells,
    # 'fetch_base_layout_info': fetch_base_layout_info,
    'fetch_plate_info': fetch_plate_info,
    # 'fetch_chip_info': fetch_chip_info,
    'fetch_center_id': fetch_center_id,
    'fetch_chip_readout': fetch_chip_readout,
    'fetch_context': fetch_context,
}


def ajax(request):
    post_call = request.POST.get('call')

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
