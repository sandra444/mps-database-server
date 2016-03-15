# coding=utf-8

from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
import ujson as json
from .models import *
from assays.models import AssayChipRawData

from bioservices import ChEMBL as ChEMBLdb

from bioactivities.models import Assay, Target

from bs4 import BeautifulSoup
import requests
import re

# Calling main is and always will be indicative of an error condition.
# ajax.py is strictly for AJAX requests

# Ajax requests are sent to ajax(request) and funneled into the correct
# handler function using a simulated Python switch routing function


def main(request):
    return render_to_response('ajax_error.html',
                              context_instance=RequestContext(request))


def fetch_compound_name(request):
    data = {}

    data.update(
        {'name': Compound.objects.get(id=request.POST['compound_id']).name})

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def chembl_error(error):
    data = {}
    data.update({'error': error})

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_chemblid_data(request):
    chemblid = request.POST['chemblid']
    selector = request.POST['selector']

    if not chemblid or not selector:
        return main(request)

    element = {
        'compound': Compound.objects.filter(chemblid=chemblid),
        'assay': Assay.objects.filter(chemblid=chemblid),
        'target': Target.objects.filter(chemblid=chemblid),
    }[selector]

    if chemblid.startswith('CHEMBL') and chemblid[6:].isdigit():

        if element:
            return chembl_error(
                '"{}" is already in the database.'.format(chemblid)
            )

        else:

            try:
                if 'compound' == selector:
                    data = ChEMBLdb().get_compounds_by_chemblId(str(chemblid))
                elif 'assay' == selector:
                    data = ChEMBLdb().get_assay_by_chemblId(str(chemblid))
                elif 'target' == selector:
                    data = ChEMBLdb().get_target_by_chemblId(str(chemblid))

            except Exception:
                return chembl_error(
                    '"{}" did not match any compound records.'.format(chemblid)
                )
    else:
        return chembl_error(
            '"{}" is not a valid ChEMBL id.'.format(chemblid)
        )

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# TODO NEEDS REVISION: SWITCH TO ACD CALCULATED LOGP ETC
def fetch_compound_report(request):
    summary_types = (
        'Pre-clinical Findings',
        'Clinical Findings',
        # Recently added
        'PK/Metabolism',
    )
    property_types = (
        'Dose (xCmax)',
        'cLogP',
    )

    compounds_request = json.loads(request.POST.get('compounds'))

    data = {}

    compounds = Compound.objects.filter(name__in=compounds_request)

    for compound in compounds:
        data.update(
            {compound.name: {
                'table': {
                    'id': compound.id,
                    'preclinical': compound.preclinical,
                    'clinical': compound.clinical,
                    'pk_metabolism': compound.pk_metabolism,
                    'post_marketing': compound.post_marketing,
                    'logP': compound.logp,
                    'max_time': {}
                },
                'plot': {}
            }}
        )

    # Acquire AssayChipRawData and store based on compound-assay (and convert to minutes?)
    # Make sure that the quality IS THE EMPTY STRING (anything in the quality field qualifies as invalid)
    readouts = AssayChipRawData.objects.filter(
        assay_chip_id__chip_setup__compound__in=compounds,
        assay_id__readout_unit__unit='%Control',
        quality=u'',
    ).select_related(
        'assay_chip_id__chip_setup__compound',
        'assay_chip_id__chip_setup__unit',
        'assay_chip_id__timeunit'
    )

    for readout in readouts:
        compound = readout.assay_chip_id.chip_setup.compound.name
        plot = data.get(compound).get('plot')
        assay = readout.assay_id.assay_id.assay_short_name
        if not assay in plot:
            plot[assay] = {}
        concentration = unicode(
            readout.assay_chip_id.chip_setup.concentration
        ) + u'_' + readout.assay_chip_id.chip_setup.unit.unit
        # Replace unicode characters
        # This may pose problems should more unicode characters appear
        # I may want to employ a sort of ASCII heuristic table to deal with this issue
        # Otherwise I would want to just avoid passing unicode where it shouldn't be (in HTML IDs and so on)
        # concentration = concentration.replace(u'µ', u'u')
        if not concentration in plot[assay]:
            plot[assay][concentration] = {}
        entry = plot[assay][concentration]

        # Convert all times to days for now
        # Get the conversion unit
        scale = readout.assay_chip_id.timeunit.scale_factor
        readout_time = "{0:.2f}".format((scale/1440.0) * readout.elapsed_time)
        readout_time = readout_time.rstrip('0').rstrip('.') if '.' in readout_time else readout_time

        if readout_time not in entry:
            entry.update({readout_time: [readout.value]})
        else:
            entry.get(readout_time).append(readout.value)

    # Average out the values
    for compound in data:
        plot = data.get(compound).get('plot')
        for assay in plot:
            for concentration in plot[assay]:
                entry = plot[assay][concentration]
                averaged_plot = {}
                for time in entry:
                    averaged_plot.update({time: float(sum(entry.get(time)))/len(entry.get(time))})
                # Add maximum
                times = [float(t) for t in entry.keys()]
                if assay not in data[compound]['table']['max_time'] or max(times) > data[compound]['table']['max_time'][assay]:
                    data[compound]['table']['max_time'].update({assay: max(times)})
                # Switch to averaged values
                plot[assay][concentration] = averaged_plot

    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_compound_list(request):
    """This function just gets a list of compounds and returns it as JSON"""
    # Why does this function exist? To have compound search suggestions without violating SOC
    data = [compound.name for compound in Compound.objects.all()]
    return HttpResponse(json.dumps(data),
                        content_type="application/json")


def fetch_drugbank_data(request):
    """Get DrugBank data"""
    chembl_id = request.POST.get('chembl_id')

    data = get_drugbank_data_from_chembl_id(chembl_id)

    return HttpResponse(json.dumps(data),
                        content_type='application/json')


def get_drugbank_target_information(data, type_of_target):
    target = {
        'name': '',
        # May not be present
        'uniprot_id': '',
        'action': '',
        'pharmacological_action': '',
        'organism': '',
        'type': type_of_target
    }

    # Get name from header (table may not be present?)
    name = data.findChildren('h3')[0].findChildren('a')[0].text

    if len(name) > 150:
        name = name[:145] + '...'

    target['name'] = name

    # Loop through the p children to find info
    for p in data.findChildren('p'):
        if 'Organism: ' in p.text:
            organism = p.text.replace('Organism: ', '').strip()

            if len(organism) > 150:
                organism = organism[:145] + '...'

            target['organism'] = organism

        elif 'Pharmacological action:' in p.text:
            target['pharmacological_action'] = p.text.replace('Pharmacological action:', '').strip()

        elif 'Actions:' in p.text:
            target['action'] = p.text.replace('Actions:', '').lstrip().replace('\n        ', ', ').strip()

    # The child table contains the corresponding UniProt ID
    if data.findChildren('table') and data.findChildren('table')[0].findChildren('tbody')[0].findChildren('td'):
        target['uniprot_id'] = data.findChildren('table')[0].findChildren(
            'tbody')[0].findChildren('tr')[0].findChildren('td')[1].text.strip()

    return target


def get_drugbank_data_from_chembl_id(chembl_id):
    data = {}

    # Get drugbank_id or fail
    url = 'https://www.ebi.ac.uk/unichem/rest/src_compound_id/{}/1/2'.format(chembl_id)
    # Make the http request
    response = requests.get(url)
    # Get the webpage as JSON
    json_data = json.loads(response.text)

    if json_data and u'error' not in json_data:
        # Get drugbank_id
        drugbank_id = json_data[0].get('src_compound_id')

        # Get URL of target for scrape
        url = "http://www.drugbank.ca/drugs/{}".format(drugbank_id)
        # Make the http request
        response = requests.get(url)
        # Get the webpage as text
        stuff = response.text
        # Make a BeatifulSoup object
        soup = BeautifulSoup(stuff, 'html5lib')

        # Get all tables
        tables = soup.findChildren('table')
        # Get table of interest
        main_table = tables[0]
        # Get rows
        rows = main_table.findChildren('tr')

        # Regex for extracting percentages
        percent_extractor = re.compile(r'<?\>?\d*\.?\d+%')

        # Units for half life
        units = ['week', 'day', 'hour', 'minute', 'second']

        # Regex for extracting SPECIFICALLY floats
        float_extractor = re.compile(r'\d+\.\d+')
        # Regex for extracting ints (ignores anything with periods)
        integer_extractor = re.compile(r'(?<!\.)(?<!\d)\d+(?!\.)')
        # Regex for extracting ints or floats
        integer_and_float_extractor = re.compile(r'\d*\.?\d+')

        # Values found in table
        data = {
            'drugbank_id': '',
            'pubchemid': '',
            'drug_class': '',
            'protein_binding': '',
            'half_life': '',
            'clearance': '',
            'bioavailability': '',
            'absorption': '',
        }

        # Loop through the rows of the table
        # Break when all 6 table rows found
        # MAKE SURE TO IGNORE EXMPTY FIELDS
        for row in rows:
            header = row.findChildren('th')

            if header:
                header = header[0].text

                if header == 'Accession Number':
                    # The ID is in bold, so find with strong
                    # There will always be an ID
                    data['drugbank_id'] = row.findChildren('strong')[0].text

                elif header == 'Sub Class':
                    # The sub class is in the text of a link
                    # There might not be a sub class
                    if row.findChildren('a'):
                        drug_class = row.findChildren('a')[0].text.rstrip()

                        if len(drug_class) > 150:
                            drug_class = drug_class[:145] + '...'

                        data['drug_class'] = drug_class

                elif header == 'Protein binding':
                    # Trim protein binding to get just the percentage
                    # There might not be protein binding
                    protein_binding_initial = row.findChildren('td')[0].text
                    protein_binding_processed = re.findall(percent_extractor, protein_binding_initial)
                    # If there are multiple, which do I take?
                    # Taking first percent for now
                    if protein_binding_processed:
                        data['protein_binding'] = protein_binding_processed[0]

                    # If regex has failed and 'percent' is in the strings
                    elif 'percent' in protein_binding_initial:
                        protein_binding_processed = re.findall(re.compile(r'<?\>?\d*\.?\d+\spercent'), protein_binding_initial)
                        if protein_binding_processed:
                            data['protein_binding'] = protein_binding_processed[0]

                    # If +/- is in the string, the percent is likely the deviation
                    if u'+/-' in protein_binding_initial:
                        protein_binding_processed = protein_binding_initial.split(u'+/-')
                        protein_binding_processed = re.findall(integer_and_float_extractor, protein_binding_processed[0])
                        if protein_binding_processed:
                            data['protein_binding'] = protein_binding_processed[0]

                    if u'±' in protein_binding_initial:
                        protein_binding_processed = protein_binding_initial.split(u'±')
                        protein_binding_processed = re.findall(integer_and_float_extractor, protein_binding_processed[0])
                        if protein_binding_processed:
                            data['protein_binding'] = protein_binding_processed[0]

                # NOT GUARANTEED TO BE 100% ACCURATE
                elif header == 'Half life':
                    # Take full string
                    # Might not exist
                    # Be sure to decode for unicode comparisons
                    life = row.findChildren('td')[0].text

                    # Remove 't1/2' to eliminate confusion for the parser
                    life = life.replace('t1/2', '')

                    unit = ''
                    for possible_unit in units:
                        if not unit and possible_unit in life:
                            unit = possible_unit
                        # If a unit has already been selected, trim life to remove distracting units
                        elif unit and possible_unit in life:
                            life = life[life.index(possible_unit):]

                    # Special exception for min (abbreviation of minutes)
                    if not unit and 'min' in life:
                        unit = 'min'

                    if unit:
                        trimmed_life = life[:life.index(unit)]
                        found_numbers = re.findall(integer_and_float_extractor, trimmed_life)

                        # Make sure the numbers aren't jumbled (float came second and integer came first)
                        found_numbers.sort(key=float)

                        # If it is plus or minus
                        if u'+/-' in trimmed_life or u'±' in trimmed_life:
                            found_numbers = [
                                unicode(float(found_numbers[-1])-float(found_numbers[0])),
                                unicode(float(found_numbers[-1])+float(found_numbers[0]))
                            ]

                        # Take first two
                        data['half_life'] = '-'.join(found_numbers[:2]) + ' ' + unit + 's'.lstrip()

                # Be sure to trim
                elif header == 'Clearance':
                    # Might not exist
                    # Get rid of bullets with lstrip
                    clearance = row.findChildren('td')[0].text.lstrip()

                    if len(clearance) > 500:
                        clearance = clearance[:495] + '...'

                    data['clearance'] = clearance

                # Be sure to trim
                elif header == 'Absorption':
                    # Might not exist
                    absorption_initial = row.findChildren('td')[0].text

                    # Absorption is just the full text
                    absorption = absorption_initial
                    if len(absorption) > 1000:
                        absorption = absorption[:995] + '...'
                    data['absorption'] = absorption

                    # Find percent for bioavailability
                    bioavailability_initial = re.findall(percent_extractor, absorption_initial)
                    # If there are multiple, which do I take?
                    # Taking first percent for now
                    if bioavailability_initial:
                        data['bioavailability'] = bioavailability_initial[0]

        # Convert Not Available to None (for clarity)
        for key, value in data.items():
            if value == 'Not Available':
                data.update({key: ''})

        # Array of targets
        targets = []

        # Loop through all target cards
        listed_targets = soup.findChildren('div', class_='target')
        if listed_targets:
            listed_targets = listed_targets[0].findChildren('div')

            for target in listed_targets:
                targets.append(get_drugbank_target_information(target, 'Target'))

        # Loop through all enzyme cards
        listed_enzymes = soup.findChildren('div', class_='enzyme')
        if listed_enzymes:
            listed_enzymes = listed_enzymes[0].findChildren('div')

            for enzyme in listed_enzymes:
                targets.append(get_drugbank_target_information(enzyme, 'Enzyme'))

        # Loop through all transporter cards
        listed_transporters = soup.findChildren('div', class_='transporter')
        if listed_transporters:
            listed_transporters = listed_transporters[0].findChildren('div')

            for transporter in listed_transporters:
                targets.append(get_drugbank_target_information(transporter, 'Transporter'))

        # Remember that targets is a list!
        data.update({'targets': targets})

    # YES, I know that the function title is deceiving in that this is actually a PubChem ID
    # Get pubchemid from unichem too
    url = 'https://www.ebi.ac.uk/unichem/rest/src_compound_id/{}/1/22'.format(chembl_id)
    # Make the http request
    response = requests.get(url)
    # Get the webpage as JSON
    json_data = json.loads(response.text)

    if json_data and u'error' not in json_data:
        # Extract ID
        pubchemid = json_data[0].get('src_compound_id')
        data.update({'pubchemid': pubchemid})

    return data

switch = {
    'fetch_compound_name': fetch_compound_name,
    'fetch_chemblid_data': fetch_chemblid_data,
    'fetch_compound_report': fetch_compound_report,
    'fetch_compound_list': fetch_compound_list,
    'fetch_drugbank_data': fetch_drugbank_data
}


def ajax(request):
    post_call = request.POST['call']

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
