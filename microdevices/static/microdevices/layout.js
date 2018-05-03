// TODO add previews for images
// TODO REMOVE COLUMN_LABELS AND ROW_LABELS FIELDS
// TODO MAY WANT TO PREVENT EXTREMELY LARGE VALUES
$(document).ready(function () {
    var insert_into = $('fieldset')[2];

    if ($('#footer')[0]) {
        insert_into = $('#layout_display');
    }

    var number_of_rows = $('#id_number_of_rows');
    var number_of_columns = $('#id_number_of_columns');

    var column_labels = [];
    var row_labels = [];

    var max_number = 100;

    // Build table
    function build_table() {
        // Be sure to split the labels on the premise of a single space character
        if (column_labels.length && row_labels.length) {
            // Remove old
            $('#layout_table').remove();

            // Choice of inserting after fieldset is contrived; for admin
            var table = $('<table>')
                .css('width','100%')
                .addClass('layout-table')
                .attr('id','layout_table')
                .insertAfter(insert_into);

            // make first row
            var row = $('<tr>');
            row.append($('<th>'));
            $.each(column_labels, function (index, value) {
                row.append($('<th>').text(value));
            });
            table.append(row);

            // make rest of the rows
            $.each(row_labels, function (row_index, row_value) {
                var row = $('<tr>');
                row.append($('<th>').text(row_value));
                $.each(column_labels, function (column_index, column_value) {
                    row.append($('<td>'));
                });
                table.append(row);
            });
        }
    }

    // This pulled function turns numbers into letters
    // Very convenient for handling things like moving from "Z" to "AA" automatically
    // Though, admittedly, the case of so many rows is somewhat unlikely
    function toLetters(num) {
        "use strict";
        var mod = num % 26,
            pow = num / 26 | 0,
            out = mod ? String.fromCharCode(64 + mod) : (--pow, 'Z');
        return pow ? toLetters(pow) + out : out;
    }

    function check_rows() {
        var rows = number_of_rows.val();

        // Check if rows exceed 100, throw alert and reset if so
        if (rows > max_number) {
            alert('Too many rows: Decreasing to ' + max_number);
            rows = max_number;
            number_of_rows.val(rows);
        }

        row_labels = [];
        // All but the final row
        for (var i=1; i<=rows; i++) {
            row_labels.push(toLetters(i));
        }

        // Insert into row labels
        // $('#id_row_labels').val(labels);

        build_table();
    }

    number_of_rows.change(check_rows);
    check_rows();

    function check_columns() {
        var columns = number_of_columns.val();

        if (columns > max_number) {
            alert('Too many columns: Decreasing to ' + max_number);
            columns = max_number;
            number_of_columns.val(columns);
        }

        column_labels = [];
        // All but the final row
        for (var i=1; i<=columns; i++) {
            column_labels.push(i);
        }

        // Insert into row labels
        // $('#id_column_labels').val(labels);

        build_table();
    }

    number_of_columns.change(check_columns);
    check_columns();

    // Deprecated
    // $('#id_row_labels').change(function() {
    //     build_table();
    // });
    // $('#id_column_labels').change(function() {
    //     build_table()
    // });

    // Attempt to build initial table
    // number_of_rows.trigger('change');
    // number_of_columns.trigger('change');
    build_table()
});
