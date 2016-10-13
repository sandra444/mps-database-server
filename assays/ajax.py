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

    readouts = AssayReadout.objects.filter(assay_device_readout=current_readout_id)\
        .prefetch_related('assay_device_readout', 'assay').order_by('assay', 'elapsed_time')

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
def get_chip_readout_data_as_csv(chip_ids):
    """Returns readout data as a csv in the form of a string"""

    # PLEASE NOTE: THIS AFFECTS PROCESSING OF QC
    # DO NOT MODIFY THIS WITHOUT ALSO CHANGING modify_qc_status_chip
    chip_data = AssayChipRawData.objects.prefetch_related(
        'assay_id',
        'assay_chip_id__chip_setup'
    ).filter(
        assay_chip_id__in=chip_ids
    ).order_by(
        'assay_chip_id__chip_setup__assay_chip_id',
        'assay_id__assay_id__assay_short_name',
        'elapsed_time'
    )

    csv = ''

    for raw in chip_data:
        if ',' in raw.assay_chip_id.chip_setup.assay_chip_id:
            csv += '"' + unicode(raw.assay_chip_id.chip_setup.assay_chip_id) + '"' + ','
        else:
            csv += raw.assay_chip_id.chip_setup.assay_chip_id + ','
        csv += unicode(raw.elapsed_time) + ','
        # Add time unit
        csv += unicode(raw.assay_chip_id.timeunit) + ','
        csv += unicode(raw.assay_id.assay_id.assay_short_name) + ','
        if ',' in raw.field_id:
            csv += '"' + unicode(raw.field_id) + '"' + ','
        else:
            csv += unicode(raw.field_id) + ','
        # Format to two decimal places
        value = raw.value
        # Check if None first before format
        if value is not None:
            value = '%.2f' % raw.value
        else:
            value = unicode(value)
        # Get rid of trailing zero and decimal if necessary
        value = value.rstrip('0').rstrip('.') if '.' in value else value
        csv += value + ','
        # Add value unit
        csv += unicode(raw.assay_id.readout_unit) + ','
        # End with the quality
        if ',' in raw.quality:
            csv += '"' + unicode(raw.quality) + '"' + '\n'
        else:
            csv += unicode(raw.quality) + '\n'

    return csv


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

    data = {}

    csv = get_chip_readout_data_as_csv([chip_id])

    data.update({
        'csv': csv,
    })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# TODO REQUIRES REVISION
# TODO NEED TO CONFIRM UNITS ARE THE SAME (ELSE CONVERSION)
def fetch_readouts(request):
    """Get all readouts for a given study for Study Summary

    Receives the following from POST:
    study -- the study to acquire readouts from
    key -- specifies whether to split readouts by compound or device
    """
    study = request.POST.get('study', '')
    key = request.POST.get('key', '')
    percent_control = request.POST.get('percent_control', '')

    if percent_control == 'true':
        percent_control = True
    else:
        percent_control = False

    # Get chip readouts
    readouts = AssayChipReadout.objects.filter(chip_setup__assay_run_id_id=study).prefetch_related(
        'chip_setup',
        'chip_setup__assay_run_id_id'
    )

    if key == 'compound':
        raw_data = AssayChipRawData.objects.filter(
            assay_chip_id=readouts
        ).prefetch_related(
            'assay_id',
            'assay_chip_id',
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
            'assay_chip_id',
            'assay_chip_id__chip_setup',
            'assay_id__assay_id',
            'assay_id__readout_unit'
        )

    # TODO ACCOUNT FOR CASE WHERE ASSAY HAS TWO DIFFERENT UNITS?
    # TODO MAY FORBID THIS CASE, MUST ASK FIRST
    # Organization is assay -> unit -> compound/tag -> field -> time -> value
    assays = {}
    initial_data = {}
    averaged_data = {}
    controls = {}

    for raw in raw_data:
        assay = raw.assay_id.assay_id.assay_short_name
        unit = raw.assay_id.readout_unit.unit
        field = raw.field_id
        value = raw.value

        # Convert all times to days for now
        # Get the conversion unit
        scale = raw.assay_chip_id.timeunit.scale_factor
        time = '{0:.2f}'.format((scale/1440.0) * raw.elapsed_time)

        quality = raw.quality

        if not quality:
            # Get tag for data point
            # If by compound
            if key == 'compound':
                if raw.assay_chip_id.chip_setup.compound:
                    tag = raw.assay_chip_id.chip_setup.compound.name
                    tag += ' ' + str(raw.assay_chip_id.chip_setup.concentration)
                    tag += ' ' + raw.assay_chip_id.chip_setup.unit.unit
                else:
                    tag = 'Control'
            # If by device
            else:
                tag = raw.assay_chip_id.chip_setup.assay_chip_id

                # Specifically add to consolidated control if this is a device-by-device control
                if percent_control and raw.assay_chip_id.chip_setup.chip_test_type == 'control':
                    initial_data.setdefault(assay, {}).setdefault(unit, {}).setdefault('Control', {}).setdefault(field, {}).setdefault(time, []).append(value)

             # Set data in nested monstrosity that is initial_data
            initial_data.setdefault(assay, {}).setdefault(unit, {}).setdefault(tag, {}).setdefault(field, {}).setdefault(time, []).append(value)

    for assay, units in initial_data.items():
        for unit, tags in units.items():
            for tag, fields in tags.items():
                for field, time_values in fields.items():
                    for time, values in time_values.items():
                        if percent_control and tag == 'Control':
                            controls.update({(assay, unit, field, time): sum(values) / float(len(values))})
                        # Add to averaged data if this isn't a average control value for device-by-device
                        if not (tag == 'Control' and key != 'compound'):
                            averaged_data.setdefault(assay, {}).setdefault(unit, {}).setdefault(tag, {}).setdefault(field, {}).update({
                                time: sum(values) / float(len(values))
                            })

    for assay, units in averaged_data.items():
        for unit, tags in units.items():
            accomadate_units = len(units) > 1
            for tag, fields in tags.items():
                accomadate_field = len(fields) > 1
                for field, time_values in fields.items():
                    for time, value in time_values.items():
                        if not percent_control:
                            # Not converted to percent control
                            assay_label = assay + '  (' + unit + ')'

                            if accomadate_field:
                                current_key = tag + ' ' + field
                            else:
                                current_key = tag

                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('time', []).append(time)
                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('values', []).append(value)

                        elif controls.get((assay, unit, field, time), False):
                            control_value = controls.get((assay, unit, field, time))
                            # Convert to percent control
                            if accomadate_units:
                                current_unit = '%Control [' + unit + ']'
                            else:
                                current_unit = '%Control'

                            assay_label = assay + '  (' + current_unit + ')'

                            if accomadate_field:
                                current_key = tag + ' ' + field
                            else:
                                current_key = tag

                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('time', []).append(time)
                            # Perform conversion
                            assays.setdefault(assay_label, {}).setdefault(current_key, {}).setdefault('values', []).append((value / control_value) * 100)

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
