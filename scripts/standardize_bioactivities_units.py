# begin django environment imports
import sys
import os

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mps.settings'
# end django environment imports

# import database driver
from django.db import connection


def standardize_concentration(
        bioactivity_to_convert,
        unit_to_convert,
        value_to_convert):
    print('standardizing concentrations')

    print(
        'original units: ' + str(unit_to_convert) +
        ' original values: ' + str(value_to_convert)
    )

    return unit_to_convert, value_to_convert


bioactivity_truth_table = {
    'AC50': standardize_concentration,
    'IC50': standardize_concentration
}


def save_bioactivity(bioactivity_id, standard_unit, standard_value):
    print(
        'new units: ' + str(standard_unit) +
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

    if original_bioactivity in bioactivity_truth_table:

        print('bioactivity match found!')
        print(
            'bioactivity: ' + str(original_bioactivity) +
            ' bioactivity id: ' + str(original_bioactivity_id)
        )

        new_unit, new_value = bioactivity_truth_table[original_bioactivity](
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

