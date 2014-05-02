# coding=utf-8

from pandas import *

import json
from django.db import connection
import networkx

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
    )

    # dropna thresh --> require at least N valid entries per axis
    result = bioactivities_data.pivot_table(
        rows='compound',
        cols=['target', 'bioactivity'],
        values='value'
    )

    # reindex our data frame
    df1 = result.reindex()

    # remove redundant columns
    df2 = df1.groupby(axis=1, level=0).sum()

    # reshape our rectangular table into a square matrix
    df3 = pandas.concat([df2, df2.T]).fillna(0)

    # construct a networkx graph from our pandas dataframe
    graph = networkx.from_numpy_matrix(df3.values)

    # construct an adjacency matrix using labeled nodes
    named_graph = networkx.relabel_nodes(
        graph,
        dict(enumerate(df3.columns))
    )

    # construct a network of edges
    #
    # links: [ {"source" : ____ , "target" : ____ , "value" : ____ } , ... ]
    # ======================================================================
    #
    #            VALUE
    # SOURCE -------------> TARGET
    #
    # SOURCE:  A single bioactivity, drugtrial, or assay
    # TARGET:  A single compound
    # VALUE:   The value of the bioactivity, drugtrial, or assay
    #
    # (Keep everything standardized to specific units per measurement type)
    #
    # Please let me know if you have any suggestions, comments, or concerns.
    #
    # Each colored cell represents two bioactivities, drugtrials,
    # or assays that evoked a response in the same drug
    #
    # Darker cells indicate bioactivities, drugtrials, or assays that
    # co-occurred more frequently
    #
    # build node table
    #
    # nodes: [ {"name" : ____ , "group" : ____ } , ... ]
    # ==================================================
    #
    # NAME:  a bioactivity type name, a drugtrial name,
    #        or an MPS assay test name
    #
    # GROUP: the ID number of the drug in our database
    #        which resulted in a response of any sort

    links = []
    nodes_dict = {}

    for item in named_graph.adj.iteritems():
        for key, value in item[1].iteritems():
            source = item[0]
            target = key
            weight = value.get('weight')
            if (source in desired_targets) \
                    and (target in desired_compounds):

                # {"source" : ____ , "target" : ____ , "value" : ____ } , ...
                links.append(
                    {
                        "source": desired_targets.index(source),
                        "target": desired_compounds.index(target),
                        "value": weight
                    }
                )

                # {"name" : ____ , "group" : ____ } , ...
                nodes_dict.update(
                    {
                        source: desired_compounds.index(target)
                    }
                )

    nodes = []

    for key, value in nodes_dict.iteritems():
        nodes.append({'name': key, 'group': value})

    d3_json = {
        'nodes': nodes,
        'links': links
    }

    # The result data for the adjacency matrix must be in
    # the following format:
    #
    # {
    #   nodes: [ ... see below ...] ,
    #   links: [ ... see below ...]
    # }

    return d3_json
