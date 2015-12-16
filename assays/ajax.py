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

# TODO OPTIMIZE DATABASE HITS


def main(request):
    return HttpResponseServerError()


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
        layout = AssayPlateSetup.objects.get(id=id).assay_layout

    elif model == 'assay_device_readout':
        layout = AssayPlateReadout.objects.get(id=id).setup.assay_layout

    data = defaultdict(dict)

    # Fetch compounds
    compounds = AssayWellCompound.objects.filter(assay_layout=layout).prefetch_related(
        'assay_layout', 'compound', 'concentration_unit').order_by('compound__name')

    for compound in compounds:
        well = compound.row + '_' + compound.column
        if not 'compounds' in data[well]:
            data[well]['compounds'] = []
        data[well]['compounds'].append({
            'name': compound.compound.name,
            'id': compound.compound_id,
            'concentration': compound.concentration,
            'concentration_unit_id': compound.concentration_unit_id,
            'concentration_unit': compound.concentration_unit.unit
            #'well': well
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
    types = AssayWell.objects.filter(assay_layout=layout).prefetch_related('assay_layout', 'well_type')

    for type in types:
        well = type.row + '_' + type.column
        data[well].update({
            'type': type.well_type.well_type,
            'type_id': type.well_type_id,
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
        current_readout_id = AssayPlateReadout.objects.get(id=id)

    elif model == 'assay_plate_test_results':
        current_readout_id = AssayPlateTestResult.objects.get(id=id).readout

    # data = defaultdict(list)
    data = []

    readouts = AssayReadout.objects.filter(assay_device_readout=current_readout_id)\
        .prefetch_related('assay_device_readout', 'assay').order_by('assay','elapsed_time')

    time_unit = AssayPlateReadout.objects.filter(id=current_readout_id.id)[0].timeunit.unit

    for readout in readouts:
        data.append({
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
        layout = AssayPlateSetup.objects.get(id=id).assay_layout.device

    elif model == 'assay_device_readout':
        layout = AssayPlateReadout.objects.get(id=id).setup.assay_layout.device

    data = {}

    if layout.column_labels and layout.row_labels:
        column_labels = layout.column_labels.split()
        row_labels = layout.row_labels.split()
    # Contrived way to deal with models without labels
    else:
        column_labels = None
        row_labels = None

    data.update({
        'id': layout.id,
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


#Fetches and displays assay layout from plate readout
def fetch_plate_info(request):
    """Returns dynamic info for plate assays"""

    assay_id = request.POST.get('id')

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

    chip_data = AssayChipRawData.objects.prefetch_related(
        'assay_id'
    ).filter(
        assay_chip_id=chip_id
    ).order_by(
        'assay_id',
        'elapsed_time'
    )

    readout = AssayChipReadout.objects.filter(id=chip_id)[0]
    time_unit = readout.timeunit
    chip_name = readout.chip_setup.assay_chip_id

    csv = ""

    for raw in chip_data:
        csv += str(chip_name) + ','
        csv += str(raw.elapsed_time) + ','
        # Add time unit
        csv += str(time_unit) + ','
        csv += str(raw.assay_id.assay_id.assay_short_name) + ','
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
        csv += str(raw.assay_id.readout_unit) + ','
        # End with the quality
        csv += str(raw.quality) + '\n'

    data = {}

    data.update({
        'csv': csv,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# TODO REQUIRES MAJOR REVISION
# TODO NEED TO AVERAGE REPEAT VALUES
# TODO NEED TO CONFIRM UNITS ARE THE SAME (ELSE CONVERSION)
# TODO ONLY USE FIELD WHEN NECESSARY
def fetch_readouts(request):
    assays = {}

    study = request.POST.get('study')
    key = request.POST.get('key')

    # Get chip readouts
    readouts = AssayChipReadout.objects.filter(chip_setup__assay_run_id_id=study)

    if key == 'compound':
        raw_data = AssayChipRawData.objects.filter(
            assay_chip_id=readouts
        ).prefetch_related(
            'assay_id',
            'assay_chip_id'
        ).select_related(
            'assay_chip_id__chip_setup',
            'assay_chip_id__chip_setup__compound',
            'assay_chip_id__chip_setup__unit',
            'assay_id__assay_id',
            'assay_id__readout_unit'
        )

    else:
        raw_data = AssayChipRawData.objects.filter(
            assay_chip_id=readouts
        ).prefetch_related(
            'assay_id',
            'assay_chip_id'
        ).select_related(
            'assay_chip_id__chip_setup',
            'assay_id__assay_id',
            'assay_id__readout_unit'
        )

    for raw in raw_data:
        assay = raw.assay_id.assay_id.assay_short_name
        unit = raw.assay_id.readout_unit.unit
        assay_label = assay + '  (' + unit + ')'

        field = raw.field_id
        value = raw.value
        time = raw.elapsed_time
        quality = raw.quality

        if not quality:
            if key == 'compound':
                if raw.assay_chip_id.chip_setup.compound:
                    tag = raw.assay_chip_id.chip_setup.compound.name
                    tag += '_' + str(raw.assay_chip_id.chip_setup.concentration)
                    tag += '_' + raw.assay_chip_id.chip_setup.unit.unit
                else:
                    tag = 'Control'
            else:
                tag = raw.assay_chip_id.chip_setup.assay_chip_id

            current_key = tag + '_' + field

            if assay_label not in assays:
                assays.update({assay_label: {}})

            current_assay = assays.get(assay_label)
            if current_key not in current_assay:
                current_assay.update({
                    current_key: {
                        'time': [],
                        'values': [current_key]
                    }
                })

            current_values = current_assay.get(current_key)

            current_values.get('time').append(time)
            current_values.get('values').append(value)

    data = {
        'assays': assays,
    }

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# Should these be refactored just to use fetch_context instead?
def fetch_organ_models(request):
    context = u'<option value="">---------</option>'

    device = request.POST.get('device')

    findings = OrganModel.objects.filter(device_id=device).prefetch_related('device')

    for finding in findings:
        # match value to the desired subject ID
        value = str(finding.id)
        context += u'<option value="' + value + '">' + unicode(finding) + '</option>'

    data = {}

    data.update({
        'context': context,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_protocols(request):
    context = u'<option value="">---------</option>'

    organ_model = request.POST.get('organ_model')

    # Order should be from newest to oldest
    findings = OrganModelProtocol.objects.filter(
        organ_model_id=organ_model
    ).prefetch_related(
        'organ_model'
    ).order_by('-version')

    # Default to first finding
    if len(findings) >= 1:
        finding = findings[0]
        value = str(finding.id)
        context += u'<option selected value="' + value + '">' + unicode(finding) + '</option>'

    if len(findings) > 1:
        # Add the other protocols
        for finding in findings[1:]:
            # match value to the desired subject ID
            value = str(finding.id)
            context += u'<option value="' + value + '">' + unicode(finding) + '</option>'

    data = {}

    data.update({
        'context': context,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_protocol(request):
    data = {}

    protocol_id = request.POST.get('protocol')

    protocol = OrganModelProtocol.objects.filter(pk=protocol_id)

    if protocol:
        protocol_file = protocol[0].file
        file_name = '/'.join(protocol_file.name.split('/')[1:])
        href = '/media/' + protocol_file.name
        data.update({
            'file_name': file_name,
            'href': href
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

def fetch_context(request):
    """Acquires context for whittling down number of dropdown"""

    context = '<option value="">---------</option>'

    # the model who's dropdown you want to whittle down
    models = {
        'AssayChipReadout': AssayChipReadout,
        'AssayChipSetup': AssayChipSetup,
        'AssayRun': AssayRun,
        'AssayChipReadoutAssay': AssayChipReadoutAssay,
        'AssayPlateReadoutAssay': AssayPlateReadoutAssay
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

    findings = subject.objects.filter(**{master: master_id})

    if next_model and next_filter:
        next_model = models.get(next_model)
        original = list(findings)
        findings = []

        for item in original:
            findings.extend(next_model.objects.filter(**{next_filter: item}))

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
    'fetch_plate_info': fetch_plate_info,
    'fetch_center_id': fetch_center_id,
    'fetch_chip_readout': fetch_chip_readout,
    'fetch_readouts': fetch_readouts,
    'fetch_context': fetch_context,
    'fetch_organ_models': fetch_organ_models,
    'fetch_protocols': fetch_protocols,
    'fetch_protocol': fetch_protocol,
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
