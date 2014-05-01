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

    print(
        'about to fix concentrations for: ' + bioactivity_to_convert +
        ' original units: ' + unit_to_convert +
        ' original values: ' + value_to_convert
    )

    return

bioactivity_truth_table = {
    'AC50': standardize_concentration,
    'ID50': standardize_concentration
}


def save_bioactivity(bioactivity_id, standard_unit, standard_value):

    print(
        'saving bioactivity id: ' + bioactivity_id +
        ' new units: ' + standard_unit +
        ' new value: ' + standard_value
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
    " SELECT 	bioactivities_bioactivity.id,  "
    " 		compounds_compound.name, "
    "       bioactivities_bioactivity.bioactivity_type,   "
    " 		bioactivities_bioactivity.units,  "
    " 		bioactivities_bioactivity.value  "
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

    if original_bioactivity in bioactivity_truth_table:
        new_unit, new_value = bioactivity_truth_table[original_bioactivity](
            bioactivity_to_convert=original_bioactivity,
            unit_to_convert=original_unit,
            value_to_convert=original_value
        )
        print(
            'saving bioactivity: ' + original_bioactivity +
            ' compound: ' + original_compound_name)
        save_bioactivity(
            bioactivity_id=original_bioactivity_id,
            standard_unit=new_unit,
            standard_value=new_value
        )

cursor.close()

