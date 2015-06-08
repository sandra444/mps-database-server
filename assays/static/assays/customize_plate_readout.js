// This script is for displaying the layout for readouts and filling in the table with readout values
// NOTE THAT UNLIKE LAYOUT THIS DOES NOT RELY ON HIDDEN INPUTS AND INSTEAD IS BASED ON THE UPLOADED FILE
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {

    // It is useful to have a list of row and column labels
    var row_labels = null;
    var column_labels = null;

    // The setup
    var setup = $('#id_setup');

    // The file
    var file = $('#id_file');

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    // Get layout
    function get_device_layout() {
        var setup_id = setup.val();
        if (setup_id) {
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: setup_id,

                    model: 'assay_device_setup',

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    // Global in readout scope
                    row_labels = json.row_labels;
                    column_labels = json.column_labels;
                    if (row_labels && column_labels) {
                        build_table(row_labels, column_labels);
                    }
                    else {
                        alert('This device is not configured correctly');
                    }
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            // Remove when invalid/nonextant layout chosen
            $('#layout_table').remove();
        }
    }

    // Build table
    function build_table(row_labels, column_labels) {
        // Remove old
        $('#layout_table').remove();

        // Choice of inserting after fieldset is contrived; for admin
        var table = $('<table>')
            .css('width','100%')
            .addClass('layout-table')
            // CONTRIVED PLACE AFTER INLINE FOR ADMIN
            // TODO CHANGE
            .attr('id','layout_table').insertAfter($('.inline-group'));

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(column_labels, function (index, value) {
            row.append($('<th>')
                .text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(row_labels, function (row_index, row_value) {
            var row = $('<tr>');
            row.append($('<th>')
                .text(row_value));
            // Note that the "lists" are added here
            $.each(column_labels, function (column_index, column_value) {
                row.append($('<td>')
                    .attr('id', row_value + '_' + column_value)
                    .append($('<div>')
                        .css('text-align','center')
                        .css('font-weight', 'bold')
                        .attr('id',row_value + '_' + column_value + '_type'))
                    .append($('<ul>')
                        .attr('id',row_value + '_' + column_value + '_list')
                        .addClass('layout-list')));
            });
            table.append(row);

        });

        get_layout_data(setup.val());
    }

    function get_layout_data(setup_id) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: setup_id,

                model: 'assay_device_setup',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_layout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // TODO FILL_LAYOUT
    function fill_layout(layout_data) {
        $.each(layout_data, function(well, data) {
            var list = $('#' + well + '_list');

            var stamp =  '';
            var text = '';
            var li = '';

            // Set type

            stamp = well + '_type';

            $('#' + stamp)
                .text(data.type);

            if (data.color) {
                $('#' + well).css('background-color', data.color);
            }

            // Set time
            stamp = well + '_time';
            // Only display text if timepoint or compounds (timepoint of zero acceptable)
            if (data.timepoint !== undefined) {
                // All times should be stored as minutes
                text = 'Time: ' + data.timepoint + ' min';

                // Be sure to add event when necessary
                li = $('<li>')
                    .attr('id', stamp)
                    .text(text);

                list.prepend(li);
            }

//          // Set compounds
            if (data.compounds) {
                $.each(data.compounds, function (index, compound) {

                    // BE CERTAIN THAT STAMPS DO NOT COLLIDE
                    stamp = well + '_' + index;

                    text = compound.name + ' (' + compound.concentration +
                        ' ' + compound.concentration_unit + ')';

                    li = $('<li>')
                        .text(text)
                        .attr('compound', compound.id);

                    list.append(li);
                });
            }

            // Set label
            stamp = well + '_label';
            if (data.label) {
                // Be sure to add event when necessary
                li = $('<li>')
                    .attr('id', stamp)
                    .text(data.label);

                list.append(li);
            }
        });

        // Attempt to acquire the readout
        // (AVOID RACE CONDITIONS AT ALL COST)
        get_readout();
    }

    function get_readout() {
        if (!setup.val()) {
            alert('Please select a setup first then select the file again.');
            // This resets the file
            $('#id_file').val('');
            return;
        }

        var file = $('#id_file')[0].files[0];
        if (file) {
            get_text(file);
        }
        // If readout already exists
        else {
            // gets the id of existing readout object from the delete link
            var readout_id = undefined;
            var delete_link = $('.deletelink');
            if (delete_link.length > 0) {
                readout_id = delete_link.first().attr('href').split('/')[4];
                get_existing_readout(readout_id);
            }
            else {
                readout_id = Math.floor(window.location.href.split('/')[5]);
                get_existing_readout(readout_id);
            }
        }
    }

    var get_text = function (readFile) {
        var reader = new FileReader();
        reader.readAsText(readFile, "UTF-8");
        reader.onload = loaded;
    };

    var loaded = function (evt) {
        var fileString = evt.target.result;
        fill_readout_from_file(fileString);
    };

    function fill_readout_from_file(csv) {
        if (!csv) {
            alert('Error reading csv.');
            $('#id_file').val('');
            return;
        }

        var all = csv.split('\n');
        var lines = [];

        for (var index in all) {
            var values = all[index].split(',');
            // TODO REVISE CHECK FOR OVERFLOW
//            if (values && (values.length > column_labels.length)) {
//                alert('Error: This CSV contains too many columns.\nBe sure to match the layout.');
//                $('#id_file').val('');
//                return;
//            }
//            if (lines.length < row_labels.length) {
//                lines.push(values);
//            }
            lines.push(values);
        }

        all = null;

        $('.value').remove();

        // Whether or not the upload should fail
        var failed = false;

        // Current assay
        var assay = undefined;
        // Current unit
        var value_unit = undefined;
        // Current time
        var time = undefined;
        // Current units
        var time_unit = undefined;

        var number_of_assays = 0;
        var number_of_data_blocks = 0;

        // TODO FIX CLIENT-SIDE VALIDATION
        // TODO
        $.each(lines, function (row_index, row) {
            // If the first value is 'assay', identify the line as a header
            if ($.trim(row[0].toLowerCase()) == 'assay') {

                assay = row[1];
                value_unit = row[3];
                time = row[5];
                time_unit = row[7];

                if (!assay || !value_unit || (time && !time_unit)) {
                    failed += 'headers';
                }

                number_of_assays += 1
            }

            else {
                // TODO NEEDS TO BE REVISED
                // Ignore empty lines
                if (!_.some(row, function (val) {return $.trim(val)})) {
                    console.log('Ignored blank line');
                }


                else {
                    // Register a new data block if this is the first reading
                    // OR if the row index
                    if (number_of_data_blocks == 0 || (row_index - number_of_assays) % row_labels.length == 0) {
                        number_of_data_blocks += 1;
                    }

                    if (number_of_data_blocks > number_of_assays) {
                        failed += 'headers';
                    }

                    //console.log('assays: ' + number_of_assays);
                    //console.log('blocks: ' + number_of_data_blocks);

                    $.each(row, function (column_index, value) {

                        // TODO REVISE
                        // Must offset row due to headers
                        // Employ modulo
                        var row_label = row_labels[(row_index - number_of_assays) % row_labels.length];
                        var column_label = column_labels[column_index];

                        var well_id = '#' + row_label + '_' + column_label;

                        //console.log('well_id: ' + well_id);

                        var text = (time && time_unit) ?
                            assay + ': ' + value + ' ' + value_unit + '\t(' + time + ' ' + time_unit + ') ' :
                            assay + ': ' + value + ' ' + value_unit;

                        // If value is not a number
                        if (isNaN(value)) {
                            $(well_id).append(
                                    '<div class="value" style="text-align: center; color: red;"><p><b>' +
                                    text +
                                    '</b></p></div>');
                            // Fail the file
                            failed += 'non-numeric';
                        }

                        else {
                            $(well_id).append(
                                    '<div class="value" style="text-align: center; color: blue;"><p><b>' +
                                    text +
                                    '</b></p></div>');
                        }
                    });
                }
            }
        });

        // If the file upload has failed
        if (failed) {
            if (failed.indexOf('headers') > -1) {
                alert('Please ensure that all data blocks have valid headers')
            }
            if (failed.indexOf('non-numeric') > -1) {
                alert('Error: This file contains non-numeric data. Please see and replace the values in red and upload again.');
            }
            $('#id_file').val('');
        }
    }

    function get_existing_readout(readout_id) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readout',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: readout_id,

                model: 'assay_device_readout',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_readout_from_existing(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function fill_readout_from_existing(data) {
        // Clear any leftover values from previews
        $('.value').remove();

        $.each(data, function(index, well_data) {
            var value = well_data.value;
            var value_unit = well_data.value_unit;
            var time = well_data.time;
            var time_unit = well_data.time_unit;
            var assay = well_data.assay;

            var row_label = row_labels[well_data.row];
            var column_label = column_labels[well_data.column];
            var well_id = '#' + row_label + '_' + column_label;

            var text = (time && time_unit) ?
                assay + ': ' + value + ' ' + value_unit +'\t(' + time + ' ' + time_unit + ') ':
                assay + ': ' + value + ' ' + value_unit;

            $(well_id).append(
                    '<div class="value" style="text-align: center; color: blue;"><p><b>' +
                    text +
                    '</b></p></div>');
        });
    }

    // On setup change, acquire labels and build table
    setup.change( function() {
        get_device_layout();
    });

    // If a setup is initially chosen
    // (implies readout exists)
    if (setup.val()) {
        // Initial table and so on
        get_device_layout();
    }

    // If the file changes
    file.change( function () {
        get_readout();
    });
});
