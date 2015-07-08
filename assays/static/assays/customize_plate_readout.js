// This script is for displaying the layout for readouts and filling in the table with readout values
// NOTE THAT UNLIKE LAYOUT THIS DOES NOT RELY ON HIDDEN INPUTS AND INSTEAD IS BASED ON THE UPLOADED FILE
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {

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
    var feature_select = $('#feature_select');
    // Data toggle for heatmap
    var data_toggle = $('#data_toggle');
    // This will contain the min, max, and median values for a feature (for the heatmap)
    //var feature_parameters = {};
    // This contains all values for a feature
    var feature_values = {};

    // This will contain the respective colors for each feature on a well to well basis
    var heatmaps = {};

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

    function heatmap_options(features) {
        // Clear old features
        feature_select.empty();

        $.each(features, function (index, feature) {
                // Prepend 'f' to avoid invalid class name; remove all invalid characters
                var feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');
                var option = $('<option>')
                    .attr('value', feature_class)
                    .text(feature);
                feature_select.append(option);
            });
            $('#heatmap_options').show();
            feature_select.trigger('change');
    }

    function build_heatmap(feature_values) {
        // For each feature
        $.each(feature_values, function(feature, values) {
            // Start the heatmap for this feature
            heatmaps[feature] = {};

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
                heatmaps[feature][well] = value ? color_scale(value) : '#606060';
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

        // Whether or not the upload should fail
        var failed = false;
        // Whether to read the file as tabular or block
        var upload_type = $('#id_upload_type').val();
        // Get a list of features
        var features = {};
        // Get a unique array of features
        var unique_features = [];

        // Get all values in a dict with features as keys
        feature_values = {};

        if (upload_type == 'Block') {
            // Current feature
            // NOTE THAT FEATURES ARE NOW USED IN LIEU OF ASSAYS
            var feature = undefined;
            // Current unit
            var value_unit = undefined;
            // Current time
            var time = undefined;
            // Current units
            var time_unit = undefined;

            var number_of_features = 0;
            var number_of_data_blocks = 0;

            // TODO FIX CLIENT-SIDE VALIDATION
            // TODO
            $.each(lines, function (row_index, row) {
                // If the first value is 'feature', identify the line as a header
                if ($.trim(row[0].toLowerCase()) == 'feature') {

                    feature = row[1];
                    value_unit = row[3];
                    time = row[5];
                    time_unit = row[7];

                    // Add feature to features (keeping it unique)
                    if (unique_features.indexOf(feature) < 0) {
                        unique_features.push(feature);
                    }

                    // Add time and time unit for multiple readings
                    if (time) {
                        feature += '_' + time + '_' + time_unit;
                    }

                    // Add feature for drop down feature list
                    features[feature] = feature;

                    // Add feature to feature_values
                    var feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');
                    feature_values[feature_class] = {};

                    if (!feature || !value_unit || (time && !time_unit)) {
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

                                // FOR THE PREVIEW I MAY JUST USE FEATURE FOR NOW

                                // Prepend 'f' to avoid invalid class name; remove all invalid characters
                                feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g, '');

                                // If value is not a number
                                if (isNaN(value)) {
                                    // Fail the file
                                    failed += 'non-numeric';
                                }

                                // Consider adding lead if people demand a larger font
                                var readout = $('<p>')
                                    .addClass('value ' + feature_class)
                                    .text(value);

                                $(well_id).append(readout);

                                // Add value to feature_values
                                feature_values[feature_class][well_id] = parseFloat(value);
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
            lines = _.filter(lines, function(list){
                return _.some(list, function (val) {
                    return $.trim(val)
                })
            });

            // Indicates whether time was specified
            var time_specified = false;

            // The header should be the first line
            var header = lines[0];
            if ($.trim(header[1].toLowerCase()) == 'time') {
                // Header WITH TIME should be [WellName, Time, Time Unit, Feature1, Feature2, ...]
                unique_features = header.slice(3);
                time_specified = true;
            }
            else {
                // Header WITHOUT TIME should be: [WellName, Feature1, Feature2, ...]
                unique_features = header.slice(1);
            }
            // Exclude the header for iteration later
            var data = lines.slice(1);

            // Fail if this appears to be block data
            if ($.trim(header[0].toLowerCase()) == 'feature') {
                failed += 'block';
            }

            // Fail if no features
            else if (unique_features.length < 1 || !_.some(unique_features)) {
                failed += 'headers';
            }

            // TODO working with times
            // Continue if successful
            else {
                $.each(data, function (row_index, row) {
                    // Unchanged well
                    var well = row[0];
                    // Split the well into alphabetical and numeric and then merge again (gets rid of leading zeroes)
                    var split_well = well.match(/(\d+|[^\d]+)/g);
                    // Merge back together for ID
                    var well_id = '#' + split_well[0] + '_' + parseInt(split_well[1]);

                    var values = null;
                    var time = 0;
                    var time_unit = null;

                    // If TIME specified
                    if (time_specified) {
                        values = row.slice(3);
                        time = row[1];
                        time_unit = row[2];
                    }
                    // If NO TIME specified
                    else {
                        values = row.slice(1);
                    }


                    $.each(values, function (column_index, value) {
                        feature = unique_features[column_index];

                        if (time) {
                            feature += '_' + time + '_' + time_unit;
                        }

                        if (!features[feature]) {
                            features[feature] = feature;
                        }

                        // Prepend 'f' to avoid invalid class name; remove all invalid characters
                        var feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g, '');

                        // If value is not a number
                        if (isNaN(value)) {
                            // Fail the file
                            failed += 'non-numeric';
                        }

                        var readout = $('<p>')
                            .addClass('value ' + feature_class)
                            .text(value);

                        $(well_id).append(readout);

                        // If feature not in feature_values, add it
                        // Otherwise tack on the value
                        if (feature_values[feature_class]) {
                            feature_values[feature_class][well_id] = parseFloat(value);
                        }
                        else {
                            feature_values[feature_class] = {};
                            feature_values[feature_class][well_id] = parseFloat(value);
                        }
                    });
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
            $('#id_file').val('');
        }

        // TODO
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
                            .change( function() {
                                var feature_name = $('#' + this.id + '-name').val();
                                var selected_index = this.value;
                                $('#id_assayplatereadoutassay_set-' + selected_index + '-feature').val(feature_name);
                            })
                        ));
                $('#binding_table').append(row);
            });
            $('#binding').show();

            build_heatmap(feature_values);
            // Heatmap dialog
            heatmap_options(features);

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

        var features = {};

        $.each(data, function(index, well_data) {
            var value = well_data.value;

            // TODO
            // HOW WILL THESE BE DISPLAYED?
            var value_unit = well_data.value_unit;
            var time = well_data.time;
            var time_unit = well_data.time_unit;
            var assay = well_data.assay;

            var row_label = row_labels[well_data.row];
            var column_label = column_labels[well_data.column];
            var well_id = '#' + row_label + '_' + column_label;

            var feature = well_data.feature;

            // Add time and time unit for multiple readings
            if (time) {
                feature += '_' + time + '_' + time_unit;
            }

            // Add feature to features
            features[feature] = feature;

            // Prepend 'f' to avoid invalid class name; remove all invalid characters
            var feature_class = 'f' + feature.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');

            // Consider adding lead if people demand a larger font
            var readout = $('<p>')
                .addClass('value ' + feature_class)
                .text(value);

            $(well_id).append(readout);

            // If feature not in feature_values, add it
            // Otherwise tack on the value
            if (feature_values[feature_class]) {
                feature_values[feature_class][well_id] = parseFloat(value);
            }
            else {
                feature_values[feature_class] = {};
                feature_values[feature_class][well_id] = parseFloat(value);
            }
        });

        // Convert features to an array
        features = _.values(features);

        build_heatmap(feature_values);
        heatmap_options(features);
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

    // When the feature_select changes, get the correct values
    feature_select.change( function() {
        var current_feature = feature_select.val();

        // Hide all values
        $('.value').hide();

        // console.log(heatmaps);

        // Use heatmaps to get the respective colors
        var well_colors = heatmaps[current_feature];
        $.each(well_colors, function(well, color) {
           $(well).css('background-color', color);
        });

        // Show this feature's values
        $('.' + current_feature).show();
    });

    // When the 'toggle data only' button is clicked
    data_toggle.click( function() {
         $('.layout-list').toggle();
    });
});
