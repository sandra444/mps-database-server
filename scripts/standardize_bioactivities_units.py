from django.db import connection


def standardize_concentration():
    pass

bioactivity_truth_table = {
    'AC50': standardize_concentration,
    'ID50': standardize_concentration
}


if __name__ == "main":

    cursor = connection.cursor()

    # SQL query goes in here
    cursor.execute(
        ''
    )

    query = cursor.fetchall()

    result = []

    for q in query:

        # our query response will be a list of tuples
        # we will iterate over every tuple and process the elements of each
        # tuple such that the index of each respective element of the tuple
        # is always predictable

        original_bioactivity = q[3]
        original_unit = q[4]
        original_value = q[5]

        try:
            # select the function from the dictionary
            new_value = bioactivity_truth_table[original_bioactivity](
                bioactivity_to_convert=original_bioactivity,
                unit_to_convert=original_unit,
                value_to_convert=original_value
            )

        # If all else fails, handle the error message
        except KeyError:
            print(
                "Could not find a function to handle " +
                original_bioactivity
            )

    cursor.close()

