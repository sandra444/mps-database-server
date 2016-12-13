// This script is for displaying the layout for readouts and filling in the table with readout values
// Injected inputs are used to indicate QC status
// NOTE THAT QC STATUS IS DEPENDENT ON TIME BUT NOT FEATURE
// TODO DEFINING STYLE IN JS IS IN POOR TASTE
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {
    if (!$('#flag')[0]) {
        alert('Sorry, plate readout uploads are not currently available in the admin.');
    }

    // The setup
    var setup = $('#id_setup');

    // The file
    var file = $('#id_file');

    //  TODO REFACTOR
    // Specify that the location for the table is different
    window.LAYOUT.insert_after = $('.inline-group');

    // gets the id of existing readout object from the delete link (admin)
    var delete_link = $('.deletelink');
    if (delete_link.length > 0) {
        window.LAYOUT.models['assay_device_readout'] = delete_link.first().attr('href').split('/')[4];
    }
    // Otherwise, if this is the frontend, get the id from the URL
    else {
        window.LAYOUT.models['assay_device_readout'] = Math.floor(window.location.href.split('/')[5]);
    }

    // Get preview from AJAX file validation
    function validate_readout_file() {
        var current_file = $('#id_file')[0].files[0];
        var serializedData = $('form').serializeArray();
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        formData.append('file', current_file);
        if (window.LAYOUT.models['assay_device_readout']) {
            formData.append('readout', window.LAYOUT.models['assay_device_readout']);
        }
        else {
            formData.append('study', Math.floor(window.location.href.split('/')[4]));
        }
        formData.append('call', 'validate_individual_plate_file');
        if (current_file) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                cache: false,
                contentType: false,
                processData: false,
                data: formData,
                success: function (json) {
                    // console.log(json);
                    if (json.errors) {
                        // Display errors
                        alert(json.errors);
                        // Remove file selection
                        $('#id_file').val('');
                    }
                    else {
                        alert('Success! Please see "New Chip Data" below for preview.');
                        // Fill heatmap
                        window.LAYOUT.fill_readout_from_existing(json);
                    }
                },
                error: function (xhr, errmsg, err) {
                    alert('An unknown error has occurred.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_file').val('');
                }
            });
        }
    }

    // On setup change, acquire labels and build table
    setup.change(function() {
        window.LAYOUT.get_device_layout(setup.val(), 'assay_device_setup', false);
    });

    // (implies readout exists)
    if (window.LAYOUT.models['assay_device_readout']) {
        // Initial table and so on
        window.LAYOUT.get_device_layout(window.LAYOUT.models['assay_device_readout'], 'assay_device_readout', false);
    }
    // If a setup is initially chosen
    else if (setup.val()) {
        window.LAYOUT.get_device_layout(setup.val(), 'assay_device_setup', false);
    }

    // If the file changes
    file.change(function () {
        validate_readout_file();
    });

    // TODO AVOID MAGIC CALLS TO DOM
    // Refresh on change in overwrite option NEED REPLCATE TO BE ACCURATE
    $('#id_overwrite_option').change(function() {
        validate_readout_file();
    });

    // Datepicker superfluous on admin, use this check to apply only in frontend
    if ($('#fluid-content')[0]) {
        // Add datepicker
        var date = $("#id_readout_start_time");
        var curr_date = date.val();
        date.datepicker();
        date.datepicker("option", "dateFormat", "yy-mm-dd");
        date.datepicker("setDate", curr_date);
    }
});

// DEPRECATED
//    // Process a value from a readout file
//    function process_value(value, id, well_id, current_selection, current_time) {
//        // Check if the value is not a number
//        if (isNaN(value)) {
//            // Take everything after the first character
//            var sliced_value = value.slice(1);
//
//            // Check if the sliced value is not a number
//            if (isNaN(sliced_value)) {
//                return NaN
//            }
//            else {
//                window.LAYOUT.set_invalid(id, well_id, current_selection, current_time);
//                return sliced_value;
//            }
//        }
//        else {
//            return value;
//        }
//    }
//
//    function get_readout_from_file() {
//        if (!setup.val()) {
//            alert('Please select a setup first then select the file again.');
//            // This resets the file
//            $('#id_file').val('');
//            return;
//        }
//
//        var file = $('#id_file')[0].files[0];
//        if (file) {
//            get_text(file);
//        }
//    }
//
//    var get_text = function (readFile) {
//        var reader = new FileReader();
//        reader.readAsText(readFile, "UTF-8");
//        reader.onload = loaded;
//    };
//
//    var loaded = function (evt) {
//        var fileString = evt.target.result;
//        fill_readout_from_file(fileString);
//    };
//
//    function fill_readout_from_file(csv) {
//        if (!csv) {
//            alert('Error reading csv.');
//            $('#id_file').val('');
//            return;
//        }
//
//        var current_inline = 0;
//        var assay_inline = $('#id_assayplatereadoutassay_set-0-assay_id');
//        var selector = $('<select>');
//
//        selector.append($('<option>')
//            .attr('value', '')
//            .text('-----'));
//
//        while (assay_inline[0]) {
//            var currently_selected = $('#id_assayplatereadoutassay_set-' + current_inline + '-assay_id :selected').text();
//
//            selector.append($('<option>')
//                .attr('value', current_inline)
//                .text(currently_selected));
//
//            current_inline += 1;
//            assay_inline = $('#id_assayplatereadoutassay_set-' + current_inline + '-assay_id');
//        }
//
//        var lines = parse_csv(csv);
//
//        // Remove old values
//        $('.value').remove();
//        // Remove old invalid
//        $('.invalid').remove();
//        // Reset invalid
//        window.LAYOUT.invalid = {};
//        // Reset heatmaps
//        window.LAYOUT.heatmaps = {};
//
//        // Whether or not the upload should fail
//        var failed = false;
//        // Whether to read the file as tabular or block
//        var upload_type = $('#id_upload_type').val();
//        // Get a unique array of features
//        var unique_features = [];
//        window.LAYOUT.times = {};
//
//        // Get all values in a dict with features as keys
//        window.LAYOUT.assay_feature_values = {};
//
//        if (upload_type == 'Block') {
//            // Current assay
//            var assay = undefined;
//            // Current feature
//            var feature = undefined;
//            // Current unit
//            var value_unit = undefined;
//            // Current time
//            var time = undefined;
//            // Current units
//            var time_unit = undefined;
//
//            var number_of_features = 0;
//            var number_of_data_blocks = 0;
//
//            //var assay_feature_class = null;
//            var assay_feature_pair = null;
//
//            var assay_feature_selection = null;
//
//            // TODO FIX CLIENT-SIDE VALIDATION
//            // PLEASE NOTE THAT NEITHER FEATURES NOR ASSAYS ARE UNIQUE
//            // THIS MEANS THAT SITUATIONS REQUIRING UNIQUENESS MUST USE AN ASSAY-FEATURE PAIR
//            $.each(lines, function (row_index, row) {
//                // If the first value is 'Plate ID', identify the line as a header
//                if ($.trim(row[0].toUpperCase()) == 'PLATE ID') {
//                    assay = row[3];
//                    feature = row[5];
//                    value_unit = row[7];
//                    time = row[9];
//                    time_unit = row[11];
//
//                    // Set time to zero if undefined
//                    if (!time) {
//                        time = 0;
//                    }
//
//                    // Add time
//                    window.LAYOUT.times[time] = [time];
//
//                    // Add feature to features (keeping it unique)
//                    if (unique_features.indexOf(feature) < 0) {
//                        unique_features.push(feature);
//                    }
//
//                    // Assay-Feature pair and time for distinguishing values
//                    assay_feature_pair = assay + '_' + feature + '_' + time;
//
//                    // Add pair to assay_feature_values
//                    //assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');
//                    window.LAYOUT.assay_feature_values[assay_feature_pair] = {};
//
//                    assay_feature_selection = assay + '_' + feature;
//
//                    // Ensure unaltered assay and feature are available
//                    window.LAYOUT.selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};
//
//                    if (!assay || !feature || !value_unit || (time && !time_unit)) {
//                        failed += 'headers';
//                    }
//
//                    number_of_features += 1
//                }
//
//                else {
//                    // TODO NEEDS TO BE REVISED
//                    // Ignore empty lines
//                    if (!_.some(row, function (val) {
//                        return $.trim(val)
//                    })) {
//                        console.log('Ignored blank line');
//                    }
//
//
//                    else {
//                        // Register a new data block if this is the first reading
//                        // OR if the row index
//                        if (number_of_data_blocks == 0 || (row_index - number_of_features) % window.LAYOUT.row_labels.length == 0) {
//                            number_of_data_blocks += 1;
//                        }
//
//                        if (number_of_data_blocks > number_of_features) {
//                            failed += 'headers';
//                        }
//
//                        else {
//                            $.each(row, function (column_index, value) {
//
//                                // TODO REVISE
//                                // Must offset row due to headers
//                                // Employ modulo
//                                var row_label = window.LAYOUT.row_labels[(row_index - number_of_features) % window.LAYOUT.row_labels.length];
//                                var column_label = window.LAYOUT.column_labels[column_index];
//
//                                var well_id = '#' + row_label + '_' + column_label;
//                                var id = row_label + '_' + column_label;
//
//                                value = process_value(value, id, well_id, assay_feature_selection, time);
//
//                                // If value is not a number
//                                if (isNaN(value)) {
//                                    // Fail the file
//                                    failed += 'non-numeric';
//                                }
//
//                                // Consider adding lead if people demand a larger font
//                                var readout = $('<p>')
//                                    .addClass('value')
//                                    .attr('data-assay-feature-time', assay_feature_pair)
//                                    .text(number_with_commas(value));
//
//                                $(well_id).append(readout);
//
//                                // Add value to assay_feature_values
//                                window.LAYOUT.assay_feature_values[assay_feature_pair][well_id] = parseFloat(value);
//                            });
//                        }
//                    }
//                }
//            });
//        }
//
//        // TODO PLEASE NOTE THAT THE TABULAR FORMAT (ESPECIALLY WITH TIME) IS SUBJECT TO CHANGE
//        // Handle tabular data
//        else {
//            // Empty lines are useless in tabular uploads, remove them
//            lines = _.filter(lines, function(list) {
//                return _.some(list, function (val) {
//                    return $.trim(val)
//                })
//            });
//
//            // Indicates whether time was specified
//            var time_specified = false;
//
//            // The header should be the first line
//            var header = lines[0];
//            if (header[1]) {
//                // If time is specified
//                if ($.trim(header[5].toUpperCase()) == 'TIME') {
//                    time_specified = true;
//                }
//            }
//            else {
//                failed += 'headers';
//            }
//            // Exclude the header for iteration later
//            var data = lines.slice(1);
//
//            // Fail if this appears to be block data
//            if ($.trim(header[3].toUpperCase()) == 'ASSAY') {
//                failed += 'block';
//            }
//
//            // working with times
//            // Continue if successful
//            else {
//                $.each(data, function (row_index, row) {
//                    // Unchanged well
//                    var well = row[1];
//                    // Split the well into alphabetical and numeric and then merge again (gets rid of leading zeroes)
//                    var split_well = well.match(/(\d+|[^\d]+)/g);
//
//                    if (split_well.length < 2) {
//                        failed += 'well_id';
//                        return false;
//                    }
//
//                    // Merge back together for ID
//                    var well_id = '#' + split_well[0] + '_' + parseInt(split_well[1]);
//                    var id = split_well[0] + '_' + parseInt(split_well[1]);
//
//                    var assay = row[2];
//                    var feature = row[3];
//                    var val_unit = row[4];
//
//                    var value = null;
//                    var time = 0;
//                    var time_unit = null;
//                    var notes = '';
//
//                    // If TIME specified
//                    if (time_specified) {
//                        time = row[5];
//                        time_unit = row[6];
//                        value = row[7];
//                        notes = row[8];
//                    }
//                    // If NO TIME specified
//                    else {
//                        value = row[5];
//                        notes = row[6];
//                    }
//
//                    // Add time
//                    window.LAYOUT.times[time] = time;
//
//                    // Add feature to features (keeping it unique)
//                    if (unique_features.indexOf(feature) < 0) {
//                        unique_features.push(feature);
//                    }
//
//                    // Add for multiple readings
//                    var assay_feature_pair = assay + '_' + feature + '_' + time;
//
//                    // Add feature to assay_feature_values
//                    //var assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');
//
//                    var assay_feature_selection = assay + '_' + feature;
//
//                    // Ensure unaltered assay and feature are available
//                    window.LAYOUT.selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};
//
//                    value = process_value(value, id, well_id, assay_feature_selection, time);
//
//                    // If value is not a number
//                    if (isNaN(value)) {
//                        // Fail the file
//                        failed += 'non-numeric';
//                    }
//
//                    var readout = $('<p>')
//                        .addClass('value')
//                        .attr('data-assay-feature-time', assay_feature_pair)
//                        .attr('title', notes)
//                        .text(number_with_commas(value));
//
//                    $(well_id).append(readout);
//
//                    // If feature not in assay_feature_values, add it
//                    // Otherwise tack on the value
//                    if (window.LAYOUT.assay_feature_values[assay_feature_pair]) {
//                        window.LAYOUT.assay_feature_values[assay_feature_pair][well_id] = parseFloat(value);
//                    }
//                    else {
//                        window.LAYOUT.assay_feature_values[assay_feature_pair] = {};
//                        window.LAYOUT.assay_feature_values[assay_feature_pair][well_id] = parseFloat(value);
//                    }
//                });
//            }
//        }
//
//        // If the file upload has failed
//        if (failed) {
//            if (failed.indexOf('block') > -1) {
//                alert('It looks like this data has a block header; try changing "tabular" to "block."');
//            }
//            if (failed.indexOf('headers') > -1) {
//                alert('Please ensure that all data blocks have valid headers.')
//            }
//            if (failed.indexOf('non-numeric') > -1) {
//                alert('Error: This file contains non-numeric data. Please find and replace these values.');
//            }
//            if (failed.indexOf('well_id') > -1) {
//                alert('Error: Found incorrectly formatted well_id. Please make sure this is correctly formatted tabular data.');
//            }
//            $('#id_file').val('');
//        }
//
//        // If the file upload has succeeded, show the feature binding dialog and the heatmap dialog
//        else {
//            // Clear the binding table
//            $('#binding_table').empty();
//
//            $.each(unique_features, function (index, feature) {
//                var row = $('<tr>')
//                    .append($('<td>')
//                        .append($('<input>')
//                            .val(feature)
//                            .attr('readonly', 'true')
//                            .attr('id', 'feature-' + index + '-name')))
//                    .append($('<td>')
//                        // BE SURE TO CLONE THE SELECTOR
//                        .append(selector.clone()
//                            .attr('id', 'feature-' + index)
//                            // On change, add the feature name to the respective inline feature
//                            .change(function() {
//                                var feature_name = $('#' + this.id + '-name').val();
//                                var selected_index = this.value;
//                                $('#id_assayplatereadoutassay_set-' + selected_index + '-feature').val(feature_name);
//                            })
//                        ));
//                $('#binding_table').append(row);
//            });
//            $('#binding').show();
//
//            window.LAYOUT.build_heatmap();
//            window.LAYOUT.heatmap_options();
//
//            alert('Please link features to assays');
//        }
//    }
