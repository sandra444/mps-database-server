# coding=utf-8
import json
from collections import defaultdict
from django.http import *
from .models import *
from compounds.models import Compound
import logging
logger = logging.getLogger(__name__)

# Calling main is and always will be indicative of an error condition.
# ajax.py is strictly for AJAX requests

# Ajax requests are sent to ajax(request) and funneled into the correct
# handler function using a simulated Python switch routing function

def main(request):
    return HttpResponseServerError()


def fetch_assay_layout_content(request):
    """Return compounds in a layout."""

    assay_layout_id = request.POST.get('assay_layout_id')

    if not assay_layout_id:
        logger.error('assay_layout_id not present in request to fetch_assay_layout_content')
        return HttpResponseServerError()

    data = defaultdict(list)
    layout = AssayLayout.objects.get(id=assay_layout_id)

    # Fetch compounds
    compounds = AssayCompound.objects.filter(assay_layout=layout)

    for compound in compounds:
        well = compound.row + '_' + compound.column
        data[well].append({
            'name': compound.compound.name,
            'compound': compound.compound.id,
            'concentration': compound.concentration,
            'concentration_unit': compound.concentration_unit,
            'well': well
        })

    # Fetch timepoints
    timepoints = AssayTimepoint.objects.filter(assay_layout=layout)

    for timepoint in timepoints:
        well = timepoint.row + '_' + timepoint.column
        data[well].append({'timepoint': timepoint.timepoint})

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_readout(request):
    current_readout_id = request.POST.get('current_readout_id')

    if not current_readout_id:
        logger.error('current_readout_id not present in request to fetch_readout')
        return HttpResponseServerError()

    data = defaultdict(list)

    readouts = AssayReadout.objects.filter(
        assay_device_readout=current_readout_id
    )

    for readout in readouts:
        well = readout.row + '_' + readout.column

        data[well].append({
            'row': readout.row,
            'column': readout.column,
            'value': readout.value,
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_layout_format_labels(request):
    """Return layout format labels."""

    request_id = request.POST.get('id')

    if not request_id:
        logger.error('request_id not present in request to fetch_layout_format_labels')
        return HttpResponseServerError()

    layout = AssayLayoutFormat.objects.get(id=request_id)

    data = {}

    data.update({
        'column_labels': layout.column_labels.split(),
        'row_labels': layout.row_labels.split(),
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_well_types(request):
    """Return well type ids and colors."""

    data = {}

    for well_type in AssayWellType.objects.all():
        data.update({well_type.id: well_type.well_type})

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_well_type_color(request):
    """Return wells type colors."""

    current_id = request.POST.get('id')

    if not current_id:
        logger.error('current_id was not sent with fetch_well_type_color')
        return HttpResponseServerError()

    data = AssayWellType.objects.get(id=current_id).background_color

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_baseid(request):
    """Return the base assay layout id for a given assay layout"""

    current_layout_id = request.POST.get('current_layout_id')

    if not current_layout_id:
        logger.error('current_layout_id not present in request to fetch_baseid')
        return HttpResponseServerError()

    assay_layout = AssayLayout.objects.get(id=current_layout_id)

    # known to set base_layout_id to an integer value correctly
    base_layout_id = assay_layout.base_layout_id

    data = {}
    data.update({'base_layout_id': base_layout_id})

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_base_layout_wells(request):
    """Return wells in a base layout."""

    base_id = request.POST.get('id')

    if not base_id:
        logger.error('base_id not present in request to fetch_base_layout_wells')
        return HttpResponseServerError()

    data = {}

    data.update({
        aw.row + '_' + aw.column: [aw.well_type.id, aw.well_type.well_type,
                                   aw.well_type.background_color]
        for aw in AssayWell.objects.filter(base_layout=base_id)
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_base_layout_info(request):
    """Return wells in a base layout."""

    base_id = request.POST.get('id')

    if not base_id:
        logger.error('base_id not present in request to fetch_base_layout_info')
        return HttpResponseServerError()

    base = AssayBaseLayout.objects.get(id=base_id)

    data = {}

    data.update({
        'format': {'row_labels': base.layout_format.row_labels.split(),
                   'column_labels': base.layout_format.column_labels.split()},

        'wells': {aw.row + '_' + aw.column: [aw.well_type.well_type,
                                             aw.well_type.background_color]
                  for aw in AssayWell.objects.filter(base_layout=base_id)}
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

#More complex than Chip; need to find way to get compound
def fetch_plate_info(request):
    """Returns dynamic info for plate assays"""

    assay_id = request.POST.get('id')

    if not assay_id:
        logger.error('assay id not present in request to fetch_assay_info')
        return HttpResponseServerError()

    assay = AssayDeviceReadout.objects.get(id=assay_id).__dict__

    data = {}

    data.update({
        'compound': 1,
        'units': 2,
        'concentration':3,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

def fetch_chip_info(request):
    """Returns dynamic info for assays"""

    assay_id = request.POST.get('id')

    if not assay_id:
        logger.error('assay id not present in request to fetch_assay_info')
        return HttpResponseServerError()

    assay = AssayChipReadout.objects.get(id=assay_id).__dict__

    data = {}

    data.update({
        #Need actual data, not ID
        #str(Compound.objects.filter(id=assay.get('compound_id')).__dict__)
        'compound': str(Compound.objects.filter(id=assay.get('compound_id'))[0].__dict__),
        'unit':  assay.get('unit_id'),
        'concentration':assay.get('concentration'),
        'chip_test_type':assay.get('chip_test_type'),
        'assay':assay.get('assay_name_id'),
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

switch = {
    'fetch_assay_layout_content': fetch_assay_layout_content,
    'fetch_readout': fetch_readout,
    'fetch_layout_format_labels': fetch_layout_format_labels,
    'fetch_well_types': fetch_well_types,
    'fetch_well_type_color': fetch_well_type_color,
    'fetch_baseid': fetch_baseid,
    'fetch_base_layout_wells': fetch_base_layout_wells,
    'fetch_base_layout_info': fetch_base_layout_info,
    'fetch_plate_info': fetch_plate_info,
    'fetch_chip_info': fetch_chip_info,
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
