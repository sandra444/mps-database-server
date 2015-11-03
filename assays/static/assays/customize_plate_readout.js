// This script is for displaying the layout for readouts and filling in the table with readout values
// Injected inputs are used to indicate QC status
// NOTE THAT QC STATUS IS DEPENDENT ON TIME BUT NOT FEATURE
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {

    if (!$('#flag')[0]) {
        alert('Sorry, plate readout uploads are not currently available in the admin.');
    }

    // Pulled from heatmap
    var colors = [
        '#008000', '#1A8C00', '#339800', '#4DA400', '#66B000',
        '#80BC00',
        '#99C800', '#B3D400', '#CCE000', '#E6EC00', '#FFFF00',
        '#F3E600',
        '#E7CC00', '#DBB300', '#CF9900', '#C38000', '#B76600',
        '#AB4D00',
        '#9F3300', '#931A00', '#870000'
    ];

    // It is useful to have a list of row and column labels
    var row_labels = null;
    var column_labels = null;

    // The setup
    var setup = $('#id_setup');

    // The file
    var file = $('#id_file');

    // Feature select for heatmap
    var assay_select = $('#assay_select');
    // Time select for heatmap
    var time_select = $('#time_select');
    // Data toggle for heatmap
    var data_toggle = $('#data_toggle');
    // This will contain the min, max, and median values for a feature (for the heatmap)
    //var feature_parameters = {};
    // This contains all values for a feature
    var assay_feature_values = {};

    // This matches assay_feature_classes to their respective assay and feature
    var selection_to_assay_feature = {};

    // This will contain the respective colors for each feature on a well to well basis
    var heatmaps = {};

    // This will contain all the wells tagged invalid with assay selection -> time -> value
    var invalid = {};

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    // Add commas to number
    // Special thanks to stack overflow
    function number_with_commas(x) {
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return parts.join(".");
    }

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

    // TODO CHANGE ALL INVALID ID CALLS
    function get_invalid_id(well_id, assay_feature_selection, underscore_time) {
        var split = well_id.split('_');
        var row = row_labels.indexOf(split[0]);
        var column = column_labels.indexOf(split[1]);
        return row + '_' + column + '_' + assay_feature_selection +  underscore_time + '_QC';
    }

    function set_invalid(id, well_id, current_selection, current_time, invalid_id, invalid_name) {
        // Make an empty object for this selection if it doesn't exist
        if (!invalid[current_selection]) {
            invalid[current_selection] = {};
        }

        // Make an empty array for this time if it doesn't exist
        if (!invalid[current_selection][current_time]) {
            invalid[current_selection][current_time] = [];
        }

        $(well_id)
            .addClass('invalid-well')
            .append($('<input>')
                .attr('id', invalid_id)
                .attr('name', invalid_name)
                .attr('size', '7')
                .attr('readonly', 'true')
                .addClass('invalid')
                .attr('hidden', 'true')
                .val('X'));

        invalid[current_selection][current_time].push(id);
    }

    function get_invalid_name(well_id, assay_feature_selection, underscore_time) {
        var split = well_id.split('_');
        var row = row_labels.indexOf(split[0]);
        var column = column_labels.indexOf(split[1]);
        // Remove underscore
        var time = underscore_time.slice(1);

        var assay_feature = selection_to_assay_feature[assay_feature_selection];
        var assay = assay_feature.assay;
        var feature = assay_feature.feature;

        var full_object = {
            'row': row,
            'column': column,
            'time': time,
            'assay': assay,
            'feature': feature
        };

        return JSON.stringify(full_object);
    }

    function refresh_invalid() {
        var current_selection = assay_select.val();
        var current_time = time_select.val();
        var current_invalid = null;

        if (invalid[current_selection]) {
            current_invalid = invalid[current_selection][current_time];
        }

        if ($('.plate-well')[0]) {
            $('.plate-well').removeClass('invalid-well');
        }

        if (current_invalid) {
            $.each(current_invalid, function (index, well) {
                $('#' + well).addClass('invalid-well');
            });
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
                    // Add class
                    .addClass('plate-well')
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

        $('.plate-well').click(function() {
            var id = this.id;
            // Check if qc mode is checked and if there is a readout value
            if ($('#qc_mode').prop('checked') && $('#' + id + ' .value')[0]) {
                // Get the current selection
                var current_selection = assay_select.val();

                // Get the current time
                var current_time = time_select.val();

                // Make an id for the invalid input: <row>_<col>_<assay_feature_select>_<time>_QC
                var invalid_id = get_invalid_id(id, current_selection, current_time);
                var invalid_name = get_invalid_name(id, current_selection, current_time);

//                // Make an empty object for this selection if it doesn't exist
//                if (!invalid[current_selection]) {
//                    invalid[current_selection] = {};
//                }
//
//                // Make an empty array for this time if it doesn't exist
//                if (!invalid[current_selection][current_time]) {
//                    invalid[current_selection][current_time] = [];
//                }

                // Check if there is already an input, if so, delete it
                if ($('#' + invalid_id)[0]) {
                    $('#' + invalid_id).remove();
                    $(this).removeClass('invalid-well');

                    invalid[current_selection][current_time] = _.without(invalid[current_selection][current_time], id);
                }
                else {
                    set_invalid(id, this, current_selection, current_time, invalid_id, invalid_name);
//                    $(this)
//                        .addClass('invalid-well')
//                        .append($('<input>')
//                            .attr('id', invalid_id)
//                            .attr('name', invalid_name)
//                            .attr('size', '7')
//                            .attr('readonly', 'true')
//                            .addClass('invalid')
//                            .attr('hidden', 'true')
//                            .val('X'));
//
//                    invalid[current_selection][current_time].push(id);
                }
            }
            //console.log(invalid);
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
            // gets the id of existing readout object from the delete link (admin)
            var readout_id = undefined;
            var delete_link = $('.deletelink');
            if (delete_link.length > 0) {
                readout_id = delete_link.first().attr('href').split('/')[4];
                get_existing_readout(readout_id);
            }
            // Otherwise, if this is the frontend, get the id from the URL
            else {
                readout_id = Math.floor(window.location.href.split('/')[5]);
                if (!isNaN(readout_id)) {
                    get_existing_readout(readout_id);
                }
            }
        }
    }

    // TODO CHANGE SUCH THAT {{ASSAY NAME}} IS SELECTOR TEXT AND ASSAY_FEATURE_PAIR IS VALUE
    function heatmap_options(pairs, times) {
        // Clear old features
        assay_select.empty();

        var unique_pairs = {};

        $.each(pairs, function (pair, value) {
            var assay = pair.split('_')[1];
            var pair_without_time = pair.split('_').slice(0, -1).join('_');
            if (!unique_pairs[pair_without_time]) {
                var option = $('<option>')
                    .attr('value', pair_without_time)
                    .text(assay);
                assay_select.append(option);

                unique_pairs[pair_without_time] = true;
            }
        });
        // Clear old times
        time_select.empty();

        // Convert times to sorted array?
        $.each(times, function (index, time) {
            var option = $('<option>')
                .attr('value', '_' + time)
                .text(time);
            time_select.append(option);
        });

        // If the only timepoint is zero, no need to display time selection
//        if (_.size(times) == 1 && times[0] == 0) {
//            $('#time_select_row').hide();
//        }
//        else {
//            $('#time_select_row').show();
//        }

        // Always show time (?)
        $('#time_select_row').show();

        $('#heatmap_options').show();
        assay_select.trigger('change');
    }

    function build_heatmap(assay_feature_values) {
        // For each feature
        $.each(assay_feature_values, function(pair, values) {
            // Start the heatmap for this assay feature pair
            heatmaps[pair] = {};

            // Get the values list
            // Be sure to exclude null values
            var values_list = _.without(_.values(values), NaN);
            // Get the min
            var min_value = _.min(values_list);
            min_value -= min_value * 0.000001;
            // Get the max
            var max_value = _.max(values_list);
            max_value += max_value * 0.000001;
            // Get the median
            var median = d3.median(values_list);
            // Get the colorscale
            var color_scale = d3.scale.quantile()
                .domain([min_value , median, max_value])
                .range(colors);

            // For each value
            $.each(values, function(well, value) {
                heatmaps[pair][well] = value ? color_scale(value) : '#606060';
            });
        });
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

        var current_inline = 0;
        var assay_inline = $('#id_assayplatereadoutassay_set-0-assay_id');
        var selector = $('<select>');

        selector.append($('<option>')
            .attr('value', '')
            .text('-----'));

        while (assay_inline[0]) {
            var currently_selected = $('#id_assayplatereadoutassay_set-' + current_inline + '-assay_id :selected').text();

            selector.append($('<option>')
                .attr('value', current_inline)
                .text(currently_selected));

            current_inline += 1;
            assay_inline = $('#id_assayplatereadoutassay_set-' + current_inline + '-assay_id');
        }

        var all = csv.split('\n');
        var lines = [];

        for (var index in all) {
            var values = all[index].split(',');
            lines.push(values);
        }

        all = null;

        // Remove old values
        $('.value').remove();
        // Remove old invalid
        $('.invalid').remove();
        // Reset invalid
        invalid = {};

        // Whether or not the upload should fail
        var failed = false;
        // Whether to read the file as tabular or block
        var upload_type = $('#id_upload_type').val();
        // Get a unique array of features
        var unique_features = [];
        var times = {};

        // Get all values in a dict with features as keys
        assay_feature_values = {};

        if (upload_type == 'Block') {
            // Current assay
            var assay = undefined;
            // Current feature
            var feature = undefined;
            // Current unit
            var value_unit = undefined;
            // Current time
            var time = undefined;
            // Current units
            var time_unit = undefined;

            var number_of_features = 0;
            var number_of_data_blocks = 0;

            var assay_feature_class = null;

            // TODO FIX CLIENT-SIDE VALIDATION
            // PLEASE NOTE THAT NEITHER FEATURES NOR ASSAYS ARE UNIQUE
            // THIS MEANS THAT SITUATIONS REQUIRING UNIQUENESS MUST USE AN ASSAY-FEATURE PAIR
            $.each(lines, function (row_index, row) {
                // If the first value is 'assay', identify the line as a header
                if ($.trim(row[0].toUpperCase()) == 'ASSAY') {
                    assay = row[1];
                    feature = row[3];
                    value_unit = row[5];
                    time = row[7];
                    time_unit = row[9];

                    // Set time to zero if undefined
                    if (!time) {
                        time = 0;
                    }

                    // Add time
                    times[time] = [time];

                    // Add feature to features (keeping it unique)
                    if (unique_features.indexOf(feature) < 0) {
                        unique_features.push(feature);
                    }

                    // Assay-Feature pair and time for distinguishing values
                    var assay_feature_pair = assay + '_' + feature + '_' + time;

                    // Add pair to assay_feature_values
                    assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');
                    assay_feature_values[assay_feature_class] = {};

                    var assay_feature_selection = assay_feature_class.split('_').slice(0, -1).join('_');

                    // Ensure unaltered assay and feature are available
                    selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};

                    if (!assay || !feature || !value_unit || (time && !time_unit)) {
                        failed += 'headers';
                    }

                    number_of_features += 1
                }

                else {
                    // TODO NEEDS TO BE REVISED
                    // Ignore empty lines
                    if (!_.some(row, function (val) {
                        return $.trim(val)
                    })) {
                        console.log('Ignored blank line');
                    }


                    else {
                        // Register a new data block if this is the first reading
                        // OR if the row index
                        if (number_of_data_blocks == 0 || (row_index - number_of_features) % row_labels.length == 0) {
                            number_of_data_blocks += 1;
                        }

                        if (number_of_data_blocks > number_of_features) {
                            failed += 'headers';
                        }

                        else {
                            $.each(row, function (column_index, value) {

                                // TODO REVISE
                                // Must offset row due to headers
                                // Employ modulo
                                var row_label = row_labels[(row_index - number_of_features) % row_labels.length];
                                var column_label = column_labels[column_index];

                                var well_id = '#' + row_label + '_' + column_label;

                                // If value is not a number
                                if (isNaN(value)) {
                                    // Fail the file
                                    failed += 'non-numeric';
                                }

                                // Consider adding lead if people demand a larger font
                                var readout = $('<p>')
                                    .addClass('value ' + assay_feature_class)
                                    .text(number_with_commas(value));

                                $(well_id).append(readout);

                                // Add value to assay_feature_values
                                assay_feature_values[assay_feature_class][well_id] = parseFloat(value);
                            });
                        }
                    }
                }
            });
        }

        // TODO PLEASE NOTE THAT THE TABULAR FORMAT (ESPECIALLY WITH TIME) IS SUBJECT TO CHANGE
        // Handle tabular data
        else {
            // Empty lines are useless in tabular uploads, remove them
            lines = _.filter(lines, function(list) {
                return _.some(list, function (val) {
                    return $.trim(val)
                })
            });

            // Indicates whether time was specified
            var time_specified = false;

            // The header should be the first line
            var header = lines[0];
            if (header[1]) {
                // If time is specified
                if ($.trim(header[4].toUpperCase()) == 'TIME') {
                    time_specified = true;
                }
            }
            else {
                failed += 'headers';
            }
            // Exclude the header for iteration later
            var data = lines.slice(1);

            // Fail if this appears to be block data
            if ($.trim(header[0].toUpperCase()) == 'ASSAY') {
                failed += 'block';
            }

            // working with times
            // Continue if successful
            else {
                $.each(data, function (row_index, row) {
                    // Unchanged well
                    var well = row[0];
                    // Split the well into alphabetical and numeric and then merge again (gets rid of leading zeroes)
                    var split_well = well.match(/(\d+|[^\d]+)/g);

                    if (split_well.length < 2) {
                        failed += 'well_id';
                        return false;
                    }

                    // Merge back together for ID
                    var well_id = '#' + split_well[0] + '_' + parseInt(split_well[1]);

                    var assay = row[1];
                    var feature = row[2];
                    var val_unit = row[3];

                    var value = null;
                    var time = 0;
                    var time_unit = null;

                    // If TIME specified
                    if (time_specified) {
                        time = row[4];
                        time_unit = row[5];
                        value = row[6];
                    }
                    // If NO TIME specified
                    else {
                        value = row[4];
                    }

                    // If value is not a number
                    if (isNaN(value)) {
                        // Fail the file
                        failed += 'non-numeric';
                    }

                    // Add time
                    times[time] = time;

                    // Add feature to features (keeping it unique)
                    if (unique_features.indexOf(feature) < 0) {
                        unique_features.push(feature);
                    }

                    // Add for multiple readings
                    var assay_feature_pair = assay + '_' + feature + '_' + time;

                    // Add feature to assay_feature_values
                    var assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');

                    var assay_feature_selection = assay_feature_class.split('_').slice(0, -1).join('_');

                    // Ensure unaltered assay and feature are available
                    selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};

                    var readout = $('<p>')
                        .addClass('value ' + assay_feature_class)
                        .text(number_with_commas(value));

                    $(well_id).append(readout);

                    // If feature not in assay_feature_values, add it
                    // Otherwise tack on the value
                    if (assay_feature_values[assay_feature_class]) {
                        assay_feature_values[assay_feature_class][well_id] = parseFloat(value);
                    }
                    else {
                        assay_feature_values[assay_feature_class] = {};
                        assay_feature_values[assay_feature_class][well_id] = parseFloat(value);
                    }

//                    $.each(values, function (column_index, value) {
//                        feature = unique_features[column_index];
//
//                        feature += '_' + time;
//
//                        // Prepend 'f' to avoid invalid class name; remove all invalid characters
//                        var feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g, '');
//
//                        // If value is not a number
//                        if (isNaN(value)) {
//                            // Fail the file
//                            failed += 'non-numeric';
//                        }
//
//                        var readout = $('<p>')
//                            .addClass('value ' + feature_class)
//                            .text(number_with_commas(value));
//
//                        $(well_id).append(readout);
//
//                        // If feature not in assay_feature_values, add it
//                        // Otherwise tack on the value
//                        if (assay_feature_values[feature_class]) {
//                            assay_feature_values[feature_class][well_id] = parseFloat(value);
//                        }
//                        else {
//                            assay_feature_values[feature_class] = {};
//                            assay_feature_values[feature_class][well_id] = parseFloat(value);
//                        }
//                    });
                });
            }
        }

        // If the file upload has failed
        if (failed) {
            if (failed.indexOf('block') > -1) {
                alert('It looks like this data has a block header; try changing "tabular" to "block."');
            }
            if (failed.indexOf('headers') > -1) {
                alert('Please ensure that all data blocks have valid headers.')
            }
            if (failed.indexOf('non-numeric') > -1) {
                alert('Error: This file contains non-numeric data. Please find and replace these values.');
            }
            if (failed.indexOf('well_id') > -1) {
                alert('Error: Found incorrectly formatted well_id. Please make sure this is correctly formatted tabular data.');
            }
            $('#id_file').val('');
        }

        // If the file upload has succeeded, show the feature binding dialog and the heatmap dialog
        else {
            // Clear the binding table
            $('#binding_table').empty();

            $.each(unique_features, function (index, feature) {
                var row = $('<tr>')
                    .append($('<td>')
                        .append($('<input>')
                            .val(feature)
                            .attr('readonly', 'true')
                            .attr('id', 'feature-' + index + '-name')))
                    .append($('<td>')
                        // BE SURE TO CLONE THE SELECTOR
                        .append(selector.clone()
                            .attr('id', 'feature-' + index)
                            // On change, add the feature name to the respective inline feature
                            .change(function() {
                                var feature_name = $('#' + this.id + '-name').val();
                                var selected_index = this.value;
                                $('#id_assayplatereadoutassay_set-' + selected_index + '-feature').val(feature_name);
                            })
                        ));
                $('#binding_table').append(row);
            });
            $('#binding').show();

            build_heatmap(assay_feature_values);
            // Heatmap dialog
            heatmap_options(assay_feature_values, times);

            alert('Please link features to assays');
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
        $('.invalid').remove();

        var times = {};

        // Reset invalid
        invalid = {};

        $.each(data, function(index, well_data) {
            var value = well_data.value;

            // TODO
            // HOW WILL THESE BE DISPLAYED (IF AT ALL)?
            var value_unit = well_data.value_unit;
            var time = well_data.time;
            var time_unit = well_data.time_unit;
            var assay = well_data.assay;
            var quality = well_data.quality;

            var row_label = row_labels[well_data.row];
            var column_label = column_labels[well_data.column];
            var well_id = '#' + row_label + '_' + column_label;

            var feature = well_data.feature;

            // Add time to times
            times[time] = time;

            // Add for multiple readings
            var assay_feature_pair = assay + '_' + feature + '_' + time;

            // Add feature to assay_feature_values
            var assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');

            var assay_feature_selection = assay_feature_class.split('_').slice(0, -1).join('_');

            // Ensure unaltered assay and feature are available
            selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};

            // Consider adding lead if people demand a larger font
            var readout = $('<p>')
                .addClass('value ' + assay_feature_class)
                .text(number_with_commas(value));

            $(well_id).append(readout);

            // If feature not in assay_feature_values, add it
            // Otherwise tack on the value
            if (assay_feature_values[assay_feature_class]) {
                assay_feature_values[assay_feature_class][well_id] = parseFloat(value);
            }
            else {
                assay_feature_values[assay_feature_class] = {};
                assay_feature_values[assay_feature_class][well_id] = parseFloat(value);
            }

            var id = row_label + '_' + column_label;
            // Current time has an underscore for some reason, should refactor
            var current_time = '_'+ time;
            // Alias for readability
            var current_selection = assay_feature_selection;

            // Make an id for the invalid input: <row>_<col>_<assay_feature_select>_<time>_QC
            var invalid_id = get_invalid_id(id, current_selection, current_time);
            var invalid_name = get_invalid_name(id, current_selection, current_time);

//            // Make an empty object for this selection if it doesn't exist
//            if (!invalid[current_selection]) {
//                invalid[current_selection] = {};
//            }
//
//            // Make an empty array for this time if it doesn't exist
//            if (!invalid[current_selection][current_time]) {
//                invalid[current_selection][current_time] = [];
//            }

            // if (quality && !(invalid[current_selection][current_time].indexOf(id) > -1)) {
            if (quality) {
                set_invalid(id, well_id, current_selection, current_time, invalid_id, invalid_name);
//                $(well_id)
//                    .addClass('invalid-well')
//                    .append($('<input>')
//                        .attr('id', invalid_id)
//                        .attr('name', invalid_name)
//                        .attr('size', '7')
//                        .attr('readonly', 'true')
//                        .addClass('invalid')
//                        .attr('hidden', 'true')
//                        .val('X'));
//
//                // Add to invalid
//                invalid[current_selection][current_time].push(id);
            }
        });

        build_heatmap(assay_feature_values);
        heatmap_options(assay_feature_values, times);
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

    // When the assay_select changes, get the correct values
    assay_select.change(function() {
        var current_assay_feature = assay_select.val();

        // Append the value of time_select
        current_assay_feature = current_assay_feature + time_select.val();

        // Hide all values
        $('.value').hide();

        // console.log(heatmaps);

        // Use heatmaps to get the respective colors
        var well_colors = heatmaps[current_assay_feature];

        if (well_colors) {
            $.each(well_colors, function (well, color) {
                $(well).css('background-color', color);
            });

            $.each(row_labels, function (row_index, row) {
                $.each(column_labels, function (col_index, col) {
                    var well = '#' + row + '_' + col;
                    if (!well_colors[well]) {
                        $(well).css('background-color', '#606060');
                    }
                })
            });
        }

        // Show this feature's values
        $('.' + current_assay_feature).show();
        refresh_invalid();
    });

    // Trigger feature select change on time change
    time_select.change( function() {
        assay_select.trigger('change');
    });

    // When the 'toggle data only' button is clicked
    data_toggle.click( function() {
         $('.layout-list').toggle();
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
