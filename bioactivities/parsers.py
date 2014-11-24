# coding=utf-8

import json
import os
import hashlib
import csv

from pandas import *
from django.db import connection

from mps.settings import MEDIA_ROOT

import scipy.spatial
import scipy.cluster
import numpy as np

def generate_record_frequency_data(query):
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

def generate_list_of_all_data_in_bioactivities(organisms, targets):
    bioactivities_data = generate_list_of_all_bioactivities_in_bioactivities()
    compounds_data = generate_list_of_all_compounds_in_bioactivities()
    targets_data = generate_list_of_all_targets_in_bioactivities(organisms, targets)

    result = {'bioactivities':bioactivities_data,
              'compounds':compounds_data,
              'targets':targets_data
            }

    return result

def generate_list_of_all_bioactivities_in_bioactivities():
    cursor = connection.cursor()

    cursor.execute(
        'SELECT bioactivities_bioactivity.standard_name '
        'FROM bioactivities_bioactivity '
        'WHERE bioactivities_bioactivity.standardized_value>0;'
    )

    result = generate_record_frequency_data(cursor.fetchall())
    cursor.close()

    return result


def generate_list_of_all_targets_in_bioactivities(organisms, targets):

    cursor = connection.cursor()


    where_clause = " WHERE ( "
    organisms_clause = ""

    if not organisms or not targets:
        return

    if len(organisms) is 1:
        organisms_clause = "   LOWER(bioactivities_target.organism)=LOWER('{}') ".format(''.join(organisms))
    else:
        for organism in organisms:
            organisms_clause += "OR LOWER(bioactivities_target.organism)=LOWER('{}') ".format(''.join(organism))

    where_clause += organisms_clause[2:]  # remove the first 'OR'

    where_clause += ") AND ("

    targets_clause = ""

    if len(targets) is 1:
        targets_clause = "   LOWER(bioactivities_target.target_type)=LOWER('{}') ".format(''.join(targets))
    else:
        for target in targets:
            targets_clause += "OR LOWER(bioactivities_target.target_type)=LOWER('{}') ".format(''.join(target))

    where_clause += targets_clause[2:]  # remove the first 'OR'
    where_clause += ");"

    cursor.execute(
        " SELECT bioactivities_target.name " +
        " FROM bioactivities_bioactivity " +
        " INNER JOIN bioactivities_target " +
        " ON bioactivities_bioactivity.target_id=bioactivities_target.id " +
        where_clause
    )

    result = generate_record_frequency_data(cursor.fetchall())
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

    result = generate_record_frequency_data(cursor.fetchall())
    cursor.close()

    return result


def fetch_all_standard_bioactivities_data(
        desired_compounds,
        desired_targets,
        desired_bioactivities,
        normalized
):
    # using values for now, FUTURE: use standardized_values
    #Appears to be using standardized_values now
    cursor = connection.cursor()

    cursor.execute(
        'SELECT compound,target,tbl.bioactivity,AVG(value) as value,units,'
        'AVG(norm_value) as norm_value,organism,target_type '
        'FROM ( '
        'SELECT compounds_compound.name as compound, '
        'bioactivities_target.name as target, '
        'bioactivities_bioactivity.standard_name as bioactivity, '
        'bioactivities_bioactivity.standardized_value as value,bioactivities_bioactivity.standardized_units as units, '
        'bioactivities_target.organism, '
        'bioactivities_target.target_type,'
        'CASE WHEN agg_tbl.max_value-agg_tbl.min_value <> 0 '
        'THEN (standardized_value-agg_tbl.min_value)/(agg_tbl.max_value-agg_tbl.min_value) ELSE 1 END as norm_value '
        'FROM bioactivities_bioactivity '
        'INNER JOIN compounds_compound '
        'ON bioactivities_bioactivity.compound_id=compounds_compound.id '
        'INNER JOIN bioactivities_target '
        'ON bioactivities_bioactivity.target_id=bioactivities_target.id '
        'INNER JOIN '
        '(SELECT bioactivities_bioactivity.standard_name ,'
        'MAX(standardized_value) as max_value,MIN(standardized_value) as min_value '
        'FROM bioactivities_bioactivity '
        'GROUP BY bioactivities_bioactivity.standard_name '
        ') as agg_tbl ON bioactivities_bioactivity.standard_name = agg_tbl.standard_name '
        ') as tbl '
        ' GROUP BY compound,target,tbl.bioactivity,units,organism,target_type '
        'HAVING AVG(value) IS NOT NULL ;'
    )

    # bioactivity is a tuple:
    # (compound name, target name, the bioactivity, value, units, norm_value,organism,target_type)
    # (0            , 1          , 2              , 3 ,  4, 5, 6, 7   )
    query = cursor.fetchall()

    result = []

    norm = 3

    if normalized:
        norm = 5

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
                'value': q[norm]
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
        return {'error': 'empty request body'}

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

    normalized = request_filter.get('normalize_bioactivities')

    all_std_bioactivities = fetch_all_standard_bioactivities_data(
        desired_compounds,
        desired_targets,
        desired_bioactivities,
        normalized
    )

    if not all_std_bioactivities:
        return {'error': 'no standard bioactivities'}
    if len(all_std_bioactivities) == 0:
        return {'error': 'standard bioactivities zero length'}

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

    unwound_data = pivoted_data.unstack().reset_index(name='value').dropna()

    unwound_data['target_bioactivity_pair'] = \
        unwound_data['target'] + '_ ' + unwound_data['bioactivity']

    del unwound_data['target']
    del unwound_data['bioactivity']

    data_order = ['compound', 'target_bioactivity_pair', 'value']
    rearranged_data = unwound_data[data_order]

    # try to make heatmap folder and ignore the exception if the folder exists
    try:
        os.makedirs(os.path.join(MEDIA_ROOT, 'heatmap'))
    except OSError:
        pass

    # generate a unique full path for data and rows and columns information

    data_hash = hashlib.sha512(
        str(rearranged_data)
    ).hexdigest()[:10]

    fullpath_without_extension = os.path.join(
        MEDIA_ROOT,
        'heatmap',
        data_hash
    )

    # string representation of the respective full full paths
    data_csv_fullpath = fullpath_without_extension + '_data.csv'

    # generate file handles for the csv writer
    data_csv_filehandle = open(data_csv_fullpath, "w")

    # generate csv writers for each file handle
    data_csv_writer = csv.writer(data_csv_filehandle)

    # write out our data lists into csv format
    data_csv_writer.writerow(['compound', 'bioactivity', 'value'])
    data_csv_writer.writerows(rearranged_data.values.tolist())

    # close the csv files that we have written so far
    data_csv_filehandle.close()

    heatmap_url_prefix = '/media/heatmap/'

    data_csv_relpath = heatmap_url_prefix + os.path.basename(
        data_csv_fullpath
    )

    # return the paths to each respective filetype as a JSON
    return {
        # csv filepath for the data
        'data_csv': data_csv_relpath
    }

def cluster(request):

    # coding=utf-8  # Example data: gene expression
    geneExp = {'genes': ['a', 'b', 'c', 'd', 'e', 'f'],
               'exp1': [-2.2, 5.6, 0.9, -0.23, -3, 0.1],
               'exp2': [5.4, -0.5, 2.33, 3.1, 4.1, -3.2]
    }
    df = pandas.DataFrame(geneExp)

    # Determine distances (default is Euclidean)
    dataMatrix = np.array(df[['exp1', 'exp2']])
    distMat = scipy.spatial.distance.pdist(dataMatrix)

    # Cluster hierarchicaly using scipy
    clusters = scipy.cluster.hierarchy.linkage(distMat, method='single')
    T = scipy.cluster.hierarchy.to_tree(clusters, rd=False)

    # Create dictionary for labeling nodes by their IDs
    labels = list(df.genes)
    id2name = dict(zip(range(len(labels)), labels))

    # Create a nested dictionary from the ClusterNode's returned by SciPy
    def add_node(node, parent):
        # First create the new node and append it to its parent's children
        newNode = dict(node_id=node.id, children=[])
        parent["children"].append(newNode)

        # Recursively add the current node's children
        if node.left: add_node(node.left, newNode)
        if node.right: add_node(node.right, newNode)

    # Initialize nested dictionary for d3, then recursively iterate through tree
    d3Dendro = dict(children=[], name="Root1")
    add_node(T, d3Dendro)

    # Label each node with the names of each leaf in its subtree
    def label_tree(n):
        # If the node is a leaf, then we have its name
        if len(n["children"]) == 0:
            leafNames = [id2name[n["node_id"]]]

        # If not, flatten all the leaves in the node's subtree
        else:
            leafNames = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])

        # Delete the node id since we don't need it anymore and
        # it makes for cleaner JSON
        del n["node_id"]

        # Labeling convention: "-"-separated leaf names
        n["name"] = name = "-".join(sorted(map(str, leafNames)))

        return leafNames


    label_tree(d3Dendro["children"][0])

    return {
        # json filepath for the data
        'data_json': d3Dendro
    }

    # fullpath = os.path.join(
    #     MEDIA_ROOT,
    #     'heatmap',
    #     "d3-dendrogram.json"
    # )
    #
    # # Output to JSON
    # json.dump(d3Dendro, open(fullpath, "w"), sort_keys=True, indent=4)
    #
    # cluster_url_prefix = '/media/cluster/'
    #
    # data_json_relpath = cluster_url_prefix + "d3-dendrogram.json"
    #
    # # return the paths to each respective filetype as a JSON
    # return {
    #     # json filepath for the data
    #     'data_json': data_json_relpath
    # }
