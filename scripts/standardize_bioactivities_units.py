# begin django environment imports
import sys
import os
import types

# sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mps.settings'
# end django environment imports

# import database driver
from django.db import connection
from mps import settings


def standardize_concentration(
        bioactivity_to_convert,
        unit_to_convert,
        value_to_convert):
    print('standardizing concentrations')

    print(
        'bioactivity to convert: ' + str(bioactivity_to_convert) +
        ' original units: ' + str(unit_to_convert) +
        ' original values: ' + str(value_to_convert)
    )

    final_unit = 'uM'

    concentration_units = {
        'pM': 10**-6,
        'nM': 10**-3,
        'uM': 10**0,
        'mM': 10**3,
        'M': 10**6
    }

    multiplier = concentration_units.get(unit_to_convert)

    if not isinstance(multiplier, types.NoneType):
        new_val = value_to_convert * multiplier
    else:
        new_val = 0
        final_unit = 'ERROR'

    return final_unit, new_val


def get_truth_dict():
    result_dict = {}
    with open(
            os.path.join(
                settings.PROJECT_ROOT,
                '..',
                'scripts/bioactivities_truth_table.txt'
            ),
            'r'
    ) as datafile:
        for line in datafile:
            (key, value) = line.split(sep=',')
            assert key.__len__() > 0
            assert value.__len__() > 0
            result_dict[str(key)] = value
    assert result_dict.__len__() > 0
    return result_dict


def save_bioactivity(bioactivity_id, standard_unit, standard_value):
    print(
        'bioactivity id: ' + str(bioactivity_id) +
        ' new units: ' + str(standard_unit) +
        ' new value: ' + str(standard_value)
    )

    return


cursor = connection.cursor()

# q[n]:
# n=0: bioactivities record id (integer)
# n=1: compound name (string)
# n=2: bioactivity name (string)
# n=3: units before standardization (string)
# n=4: values before standardization (float)

cursor.execute(
    " SELECT    bioactivities_bioactivity.id,  "
    "      	    compounds_compound.name, "
    "           bioactivities_bioactivity.bioactivity_type,   "
    "           bioactivities_bioactivity.units,  "
    "           bioactivities_bioactivity.value  "
    " FROM bioactivities_bioactivity   "
    " INNER JOIN compounds_compound   "
    " ON bioactivities_bioactivity.compound_id=compounds_compound.id;  "
)

query = cursor.fetchall()

result = []

for q in query:

    # our query response will be a list of tuples
    # we will iterate over every tuple and process the elements of each
    # tuple such that the index of each respective element of the tuple
    # is always predictable

    original_bioactivity_id = q[0]
    original_compound_name = q[1]
    original_bioactivity = q[2]
    original_unit = q[3]
    original_value = q[4]

    # we will not perform any operations if any single field is missing data
    if not (q[0] and q[1] and q[2] and q[3] and q[4]):
        continue

    bioactivities_truth_dict = get_truth_dict()

    if original_bioactivity in bioactivities_truth_dict:

        print('bioactivity match found!')
        print(
            'bioactivity: ' + str(original_bioactivity) +
            ' bioactivity id: ' + str(original_bioactivity_id)
        )

        standardizing_function = bioactivities_truth_dict[original_bioactivity]

        new_unit, new_value = getattr(
            sys.modules[__name__],
            standardizing_function
        )(
            bioactivity_to_convert=original_bioactivity,
            unit_to_convert=original_unit,
            value_to_convert=original_value
        )
        print(
            'preparing to save bioactivity: ' + str(original_bioactivity) +
            ' for compound: ' + str(original_compound_name)
        )

        save_bioactivity(
            bioactivity_id=original_bioactivity_id,
            standard_unit=new_unit,
            standard_value=new_value
        )

        # print a blank line
        print('')

cursor.close()

