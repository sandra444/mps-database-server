# coding=utf-8

import json
import os
import hashlib
import random

from pandas import *
from django.db import connection

from mps.settings import MEDIA_ROOT


"""

unit_table

Convert and standardize units to a common value

"""

unit_table = {

    'nM': 10 ** -9,
    'uM': 10 ** -6,
    's': 1,
    '%': 1,
    'mg/dL': 1,
    'g': 1,
    'mg': 10 ** -3,
    'ug.mL-1': 10 ** -6

}


def query_to_frequencylist(query):
    result = {}

    for q in query:
        element = ''.join(q)
        if element:
            if element in result:
                frequency = result.get(element)
                frequency += 1
                result.update({element: frequency})
            else:
                result.update({element: 1})

    result_list = []

    for key, value in result.iteritems():
        result_list.append([key, value])

    return result_list


def normalize(value, units):
    """

    Convert units imported from the CHEMBL data store into standard units,
    or else return null or an error message as the result.

    :param value: initial value to be converted
    :param units: initial units to use for conversion

    """

    try:
        # select the function from the dictionary
        value *= unit_table[units]

    # If all else fails, handle the error message
    except KeyError:
        # DEBUG: '{} {}'.format('ERROR ... ', units)
        return 0, 'ERROR'

    else:
        return round(value, 12), units


def generate_table():
    cursor = connection.cursor()

    cursor.execute(
        'SELECT compounds_compound.name, '
        'bioactivities_target.name, '
        'bioactivities_bioactivity.bioactivity_type, '
        'bioactivities_bioactivity.value, '
        'bioactivities_bioactivity.units '
        'FROM bioactivities_bioactivity '
        'INNER JOIN compounds_compound '
        'ON bioactivities_bioactivity.compound_id=compounds_compound.id '
        'INNER JOIN bioactivities_target '
        'ON bioactivities_bioactivity.target_id=bioactivities_target.id;'
    )

    # bioactivity is a tuple:
    # (compound name, target name, the bioactivity, value, units)
    # (0            , 1          , 2              , 3    , 4    )
    query = cursor.fetchall()

    result = []

    for q in query:

        normalized_value, normalized_units = normalize(q[3], q[4])

        # DEBUG: print out errors in units
        if 'ERROR' in normalized_units:
            continue

        result.append({
            'compound': q[0],
            'target': q[1],
            'bioactivity': q[2],
            'value': normalized_value,
            'units': normalized_units,
        })

    cursor.close()

    return result


def generate_list_of_all_bioactivities_in_bioactivities():
    cursor = connection.cursor()

    cursor.execute(
        'SELECT bioactivities_bioactivity.bioactivity_type '
        'FROM bioactivities_bioactivity;'
    )

    result = query_to_frequencylist(cursor.fetchall())
    cursor.close()

    return result


def generate_list_of_all_targets_in_bioactivities():
    cursor = connection.cursor()

    cursor.execute(
        " SELECT bioactivities_target.name "
        " FROM bioactivities_bioactivity "

        " INNER JOIN bioactivities_target "
        " ON bioactivities_bioactivity.target_id=bioactivities_target.id "

        " WHERE bioactivities_target.organism='Homo sapiens' "
        " AND bioactivities_target.target_type='SINGLE PROTEIN' "
    )

    result = query_to_frequencylist(cursor.fetchall())
    cursor.close()

    return result


def generate_list_of_all_compounds_in_bioactivities():
    cursor = connection.cursor()

    cursor.execute(
        'SELECT compounds_compound.name '
        'FROM bioactivities_bioactivity '
        'INNER JOIN compounds_compound '
        'ON bioactivities_bioactivity.compound_id=compounds_compound.id;'
    )

    result = query_to_frequencylist(cursor.fetchall())
    cursor.close()

    return result


def fetch_all_standard_bioactivities_data(
        desired_compounds,
        desired_targets,
        desired_bioactivities
):
    # using values for now, FUTURE: use standardized_values
    cursor = connection.cursor()

    cursor.execute(
        'SELECT compounds_compound.name, '
        'bioactivities_target.name, '
        'bioactivities_bioactivity.bioactivity_type, '
        'bioactivities_bioactivity.value '
        'FROM bioactivities_bioactivity '
        'INNER JOIN compounds_compound '
        'ON bioactivities_bioactivity.compound_id=compounds_compound.id '
        'INNER JOIN bioactivities_target '
        'ON bioactivities_bioactivity.target_id=bioactivities_target.id;'
    )

    # bioactivity is a tuple:
    # (compound name, target name, the bioactivity, value)
    # (0            , 1          , 2              , 3    )
    query = cursor.fetchall()

    result = []

    for q in query:

        if q[0] not in desired_compounds:
            continue

        if q[1] not in desired_targets:
            continue

        if q[2] not in desired_bioactivities:
            continue

        result.append(
            {
                'compound': q[0],
                'target': q[1],
                'bioactivity': q[2],
                'value': q[3]
            }
        )

    cursor.close()

    return result


def fetch_all_standard_drugtrials_data():
    # using values for now, FUTURE: use standardized_values
    cursor = connection.cursor()

    # TODO: FIXME
    cursor.execute(
        ''
    )

    # bioactivity is a tuple:
    # (compound name, target name, the bioactivity, value)
    # (0            , 1          , 2              , 3    )
    query = cursor.fetchall()

    result = []

    for q in query:
        result.append(
            {
                'compound': q[0],
                'target': q[1],
                'bioactivity': q[2],
                'value': q[3]
            }
        )

    cursor.close()

    return result


def fetch_all_standard_mps_assay_data():
    # using values for now, FUTURE: use standardized_values
    cursor = connection.cursor()

    # TODO: FIXME
    cursor.execute(
        ''
    )

    # bioactivity is a tuple:
    # (compound name, target name, the bioactivity, value)
    # (0            , 1          , 2              , 3    )
    query = cursor.fetchall()

    result = []

    for q in query:
        result.append(
            {
                'compound': q[0],
                'target': q[1],
                'bioactivity': q[2],
                'value': q[3]
            }
        )

    cursor.close()

    return result


def heatmap(request):
    if len(request.body) == 0:
        return

    # convert data sent in request to a dict data type from a string data type

    request_filter = json.loads(request.body)

    desired_targets = [
        x.get(
            'name'
        ) for x in request_filter.get(
            'targets_filter'
        ) if x.get(
            'is_selected'
        ) is True
    ]

    desired_compounds = [
        x.get(
            'name'
        ) for x in request_filter.get(
            'compounds_filter'
        ) if x.get(
            'is_selected'
        ) is True
    ]

    desired_bioactivities = [
        x.get(
            'name'
        ) for x in request_filter.get(
            'bioactivities_filter'
        ) if x.get(
            'is_selected'
        ) is True
    ]

    all_std_bioactivities = fetch_all_standard_bioactivities_data(
        desired_compounds,
        desired_targets,
        desired_bioactivities
    )

    if not all_std_bioactivities:
        return

    if len(all_std_bioactivities) == 0:
        return

    bioactivities_data = pandas.DataFrame(
        all_std_bioactivities,
        columns=['compound', 'target', 'bioactivity', 'value']
    ).fillna(0)

    pivoted_data = pandas.pivot_table(
        bioactivities_data,
        values='value',
        cols=['target', 'bioactivity'],
        rows='compound'
    )

    data_hash = hashlib.sha512(
        str(random.random)
    ).hexdigest()[:10]

    data_filename = os.path.join(
        MEDIA_ROOT,
        'heatmap',
        data_hash + '.tsv'
    )

    unwound_data = pivoted_data.unstack().reset_index(name='value').dropna()

    unwound_data['target_bioactivity_pair'] = \
        unwound_data['target'] + ' ' + unwound_data['bioactivity']

    del unwound_data['target']
    del unwound_data['bioactivity']

    data_order = ['compound', 'target_bioactivity_pair', 'value']
    rearranged_data = unwound_data[data_order]

    rearranged_data.to_csv(
        index=False,
        path_or_buf=data_filename,
        sep="\t"
    )

    return {'tsv': data_hash}
