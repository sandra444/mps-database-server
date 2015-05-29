$(document).ready(function () {

    // Build table
    function build_table() {
        var column_labels = $('#id_column_labels').val().split(' ');
        var row_labels = $('#id_row_labels').val().split(' ');

        if (column_labels && row_labels) {
            // Remove old
            $('#layout_table').remove();

            // Choice of inserting after fieldset is contrived; for admin
            var table = $('<table>').css('width',
                '100%').addClass('layout-table').attr('id',
                'layout_table').insertAfter($('fieldset')[2]);

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
                // Note that the "lists" are added here
                $.each(column_labels, function (column_index, column_value) {
                    row.append($('<td>'));
                });
                table.append(row);
            });
        }
    }

    // This pulled function turns numbers into letters
    // Very convenient for handling things like moving from "Z" to "AA" automatically
    function toLetters(num) {
        "use strict";
        var mod = num % 26,
            pow = num / 26 | 0,
            out = mod ? String.fromCharCode(64 + mod) : (--pow, 'Z');
        return pow ? toLetters(pow) + out : out;
    }

    $('#id_number_of_rows').change( function() {
        var rows = $('#id_number_of_rows').val();
        var labels = '';
        // All but the final row
        for (var i=1; i<rows; i++) {
            labels += toLetters(i) + ' ';
        }
        // The final row
        labels += toLetters(rows);

        // Insert into row labels
        $('#id_row_labels').val(labels);

        build_table()
    });

    $('#id_number_of_columns').change( function() {
        var columns = $('#id_number_of_columns').val();
        var labels = '';
        // All but the final row
        for (var i=1; i<columns; i++) {
            labels += i + ' ';
        }
        // The final row
        labels += columns;

        // Insert into row labels
        $('#id_column_labels').val(labels);

        build_table()
    });

    $('#id_row_labels').change( function() {
        build_table();
    });
    $('#id_column_labels').change( function() {
        build_table()
    });

    // Attempt to build initial table
    build_table()
});
