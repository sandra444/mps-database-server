// This script was made to prevent redundant code in plate pages

// Namespace for layout functions
window.LAYOUT = {};

$(document).ready(function () {
    var time_conversions = [
        1,
        60,
        1440,
        10080
    ];

    var time_units = [
        'min',
        'hour',
        'days',
        'weeks'
    ];

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
    window.LAYOUT.row_labels = null;
    window.LAYOUT.column_labels = null;

    // Feature select for heatmap
    var assay_select = $('#assay_select');
    // Time select for heatmap
    var time_select = $('#time_select');
    // Data toggle for heatmap
    var data_toggle = $('#data_toggle');

    // This will contain the min, max, and median values for a feature (for the heatmap)
    //var feature_parameters = {};

    // This contains all values for a feature
    window.LAYOUT.assay_feature_values = {};

    // This contains all the times
    window.LAYOUT.times = {};

    // This matches assay_feature_pairs to their respective assay and feature
    window.LAYOUT.selection_to_assay_feature = {};

    // This will contain the respective colors for each feature on a well to well basis
    window.LAYOUT.heatmaps = {};

    // This will contain all the wells tagged invalid with assay selection -> time -> value
    window.LAYOUT.invalid = {};

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value')  ? $('[name=csrfmiddlewaretoken]').attr('value') : getCookie('csrftoken');

    // Specifies whether inputs are allowed
    window.LAYOUT.is_input = false;
    // Specifies whether to clone just a base layout
    window.LAYOUT.base_only = false;
    // Specifies the respective ids of various models
    window.LAYOUT.models = {
        'device': '',
        'assay_layout': '',
        'assay_device_setup': '',
        'assay_device_readout': ''
    };
    // Specifies where to put the table
    window.LAYOUT.insert_after = $('fieldset')[0];

    function get_best_time_index(value) {
        var index = 0;
        while (time_conversions[index + 1]
            && time_conversions[index + 1] <= value
            && (value % time_conversions[index + 1] == 0
                || value % time_conversions[index] != 0
                || (value > 1440 && index != 2))) {
            index += 1;
        }
        return index;
    }

    // Get layout
    window.LAYOUT.get_device_layout = function(current_id, current_model, is_input) {
        window.LAYOUT.is_input = is_input;
        window.LAYOUT.models[current_model] = current_id;

        if (current_id) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: current_id,

                    model: current_model,

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    window.LAYOUT.row_labels = json.row_labels;
                    window.LAYOUT.column_labels = json.column_labels;

                    if (window.LAYOUT.row_labels && window.LAYOUT.column_labels) {
                        window.LAYOUT.build_table();
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
            // Show the help
            $('#help').attr('hidden', false);
        }
    };

    // Build table
    window.LAYOUT.build_table = function () {
        // Remove old
        $('#layout_table').remove();

        // Show buttons for changing text size
        $('#change_text_size').attr('hidden', false);

        // Hide the help
        $('#help').attr('hidden', true);

        // Choice of inserting after fieldset is contrived; for admin
        var table = $('<table>')
            .css('width','100%')
            .addClass('layout-table')
            .attr('id','layout_table').insertAfter(window.LAYOUT.insert_after);

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(window.LAYOUT.column_labels, function (index, value) {
            row.append($('<th>')
                .text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(window.LAYOUT.row_labels, function (row_index, row_value) {
            var row = $('<tr>');
            row.append($('<th>')
                .text(row_value));
            // Note that the "lists" are added here
            $.each(window.LAYOUT.column_labels, function (column_index, column_value) {
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

        // make selectable
        if (!$('#id_locked').prop('checked') && window.LAYOUT.models['device']) {
            $('#layout_table').selectable({
                filter: "td",
                distance: 1,
                stop: window.LAYOUT.layout_add_content
            });
        }

        // Allow QC clicking if readout
        if (!$('#id_locked').prop('checked') && window.LAYOUT.models['assay_device_setup'] || window.LAYOUT.models['assay_device_readout']) {
            $('.plate-well').click(function() {
                var id = this.id;
                var well_id = '#' + id;
                // Check if qc mode is checked and if there is a readout value
                if ($('#qc_mode').prop('checked') && $('#' + id + ' .value')[0]) {
                    // Get the current selection
                    var current_selection = assay_select.val();

                    // Get the current time
                    var current_time = time_select.val();

                    // Make an id for the invalid input: <row>_<col>_<assay_feature_select>_<time>_QC
                    var invalid_id = get_invalid_id(id, current_selection, current_time);

                    // Check if there is already an input, if so, delete it
                    if ($('[id="'+ invalid_id + '"]')[0]) {
                        $('[id="'+ invalid_id + '"]').remove();
                        $(this).removeClass('invalid-well');

                        window.LAYOUT.invalid[current_selection][current_time] = _.without(window.LAYOUT.invalid[current_selection][current_time], '#' + id);
                        // THIS MAY CAUSE ISSUES, INVESTIGATE
                        window.LAYOUT.build_heatmap();
                    }
                    else {
                        window.LAYOUT.set_invalid(id, well_id, current_selection, current_time);
                    }
                }
            });
        }

        var current_id = null;
        var current_model = null;

        if (window.LAYOUT.models['assay_layout']) {
            current_id = window.LAYOUT.models['assay_layout'];
            current_model = 'assay_layout';
        }
        else if (window.LAYOUT.models['assay_device_setup']) {
            current_id = window.LAYOUT.models['assay_device_setup'];
            current_model = 'assay_device_setup';
        }
        else if (window.LAYOUT.models['assay_device_readout']) {
            current_id = window.LAYOUT.models['assay_device_readout'];
            current_model = 'assay_device_readout';
        }

        window.LAYOUT.get_layout_data(current_id, current_model, window.LAYOUT.base_only);
    };

    window.LAYOUT.get_layout_data = function(current_id, current_model) {
        window.LAYOUT.models[current_model] = current_id;

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                call: 'fetch_assay_layout_content',
                id: current_id,
                model: current_model,
                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                window.LAYOUT.fill_layout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    };

    window.LAYOUT.fill_layout = function(layout_data) {
        $.each(layout_data, function(well, data) {
            var list = $('#' + well + '_list');

            var stamp =  '';
            var text = '';
            var li = '';

            // Set type
            stamp = well + '_type';

            $('#' + stamp).text(data.type);

            if (window.LAYOUT.is_input) {
                $('#' + stamp)
                .append($('<input>')
                    .attr('type', 'hidden')
                    .attr('name', stamp)
                    .attr('id', stamp)
                    .attr('value', data.type_id));
            }


            if (data.color) {
                $('#' + well).css('background-color', data.color);
            }

            // Only add times, compounds, and labels if this is not a base_only clone
            if (!window.LAYOUT.base_only) {
                // Set time
                stamp = well + '_time';
                // Only display text if timepoint or compounds (timepoint of zero acceptable)
                if (data.timepoint !== undefined) {
                    // Get best units and convert
                    var best_index = get_best_time_index(data.timepoint);
                    var best_unit = time_units[best_index];
                    var converted_time = data.timepoint / time_conversions[best_index];

                    // Display time with best value
                    text = 'Time: ' + converted_time + ' ' + best_unit;

                    // Be sure to add event when necessary
                    li = $('<li>')
                        .attr('id', stamp)
                        .text(text);

                    if (window.LAYOUT.is_input) {
                        li.click(function () {
                            if(confirm('Are you sure you want to remove this time point?\n' + $(this).text())) {
                                $(this).remove();
                            }
                        })
                        .append($('<input>')
                            .attr('type', 'hidden')
                            .attr('name', stamp)
                            .attr('value', data.timepoint));
                    }

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

                        if (window.LAYOUT.is_input) {
                            li.click(function () {
                                if(confirm('Are you sure you want to remove this compound?\n' + $(this).text())) {
                                    $(this).remove();
                                }
                            });

                            var info = '{"well":"' + well + '"' +
                            ',"compound":"' + compound.id + '","concentration":"' +
                            compound.concentration + '","concentration_unit":"' +
                            compound.concentration_unit_id + '"}';

                            li.append($('<input>')
                                .attr('type', 'hidden')
                                .attr('name', 'well_' + stamp)
                                .attr('value', info));
                        }

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

                    if (window.LAYOUT.is_input) {
                        li.click(function () {
                            // Confirm the user wants to remove first
                            if(confirm('Are you sure you want to remove this label?\n' + $(this).text())) {
                                $(this).remove();
                            }
                        })
                        .append($('<input>')
                            .attr('type', 'hidden')
                            .attr('name', stamp)
                            .attr('value', data.label));
                    }

                    list.append(li);
                }
            }
        });

        if (!isNaN(window.LAYOUT.models['assay_device_readout'])) {
            get_existing_readout(window.LAYOUT.models['assay_device_readout']);
        }
    };

    function get_invalid_id(well_id, assay_feature_selection, time) {
        var split = well_id.split('_');
        var row = window.LAYOUT.row_labels.indexOf(split[0]);
        var column = window.LAYOUT.column_labels.indexOf(split[1]);
        return row + '_' + column + '_' + assay_feature_selection +  '_' + time + '_QC';
    }

    function get_invalid_name(well_id, assay_feature_selection, time) {
        var split = well_id.split('_');
        var row = window.LAYOUT.row_labels.indexOf(split[0]);
        var column = window.LAYOUT.column_labels.indexOf(split[1]);

        var assay_feature = window.LAYOUT.selection_to_assay_feature[assay_feature_selection];
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

    window.LAYOUT.set_invalid = function(id, well_id, current_selection, current_time) {
        var invalid_id = get_invalid_id(id, current_selection, current_time);
        var invalid_name = get_invalid_name(id, current_selection, current_time);

        // Make an empty object for this selection if it doesn't exist
        if (!window.LAYOUT.invalid[current_selection]) {
            window.LAYOUT.invalid[current_selection] = {};
        }

        // Make an empty array for this time if it doesn't exist
        if (!window.LAYOUT.invalid[current_selection][current_time]) {
            window.LAYOUT.invalid[current_selection][current_time] = [];
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

        window.LAYOUT.invalid[current_selection][current_time].push(well_id);

        // THIS MAY CAUSE ISSUES, INVESTIGATE
        window.LAYOUT.build_heatmap();
    };

    function refresh_invalid() {
        var current_selection = assay_select.val();
        var current_time = time_select.val();
        var current_invalid = null;

        if (window.LAYOUT.invalid[current_selection]) {
            current_invalid = window.LAYOUT.invalid[current_selection][current_time];
        }

        if ($('.plate-well')[0]) {
            $('.plate-well').removeClass('invalid-well');
        }

        if (current_invalid) {
            $.each(current_invalid, function (index, well) {
                $(well).addClass('invalid-well');
            });
        }
    }

    function get_existing_readout(readout_id) {
        $.ajax({
            url: "/assays_ajax/",
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

        window.LAYOUT.times = {};

        // Reset invalid
        window.LAYOUT.invalid = {};

        $.each(data, function(index, well_data) {
            var value = well_data.value;

            // TODO
            // HOW WILL THESE BE DISPLAYED (IF AT ALL)?
            var value_unit = well_data.value_unit;
            var time = well_data.time;
            var time_unit = well_data.time_unit;
            var assay = well_data.assay;
            var quality = well_data.quality;

            var row_label = window.LAYOUT.row_labels[well_data.row];
            var column_label = window.LAYOUT.column_labels[well_data.column];
            var well_id = '#' + row_label + '_' + column_label;

            var feature = well_data.feature;

            // Add time to times
            window.LAYOUT.times[time] = time;

            // Add for multiple readings
            var assay_feature_pair = assay + '_' + feature + '_' + time;

            // Add feature to assay_feature_values
            //var assay_feature_class = 'f_'+ assay_feature_pair.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/g,'');

            var assay_feature_selection = assay + '_' + feature;

            // Ensure unaltered assay and feature are available
            window.LAYOUT.selection_to_assay_feature[assay_feature_selection] = {'assay': assay, 'feature': feature};

            // Consider adding lead if people demand a larger font
            var readout = $('<p>')
                .addClass('value')
                .attr('data-assay-feature-time', assay_feature_pair)
                .text(number_with_commas(value));

            $(well_id).append(readout);

            // If feature not in assay_feature_values, add it
            // Otherwise tack on the value
            if (window.LAYOUT.assay_feature_values[assay_feature_pair]) {
                window.LAYOUT.assay_feature_values[assay_feature_pair][well_id] = parseFloat(value);
            }
            else {
                window.LAYOUT.assay_feature_values[assay_feature_pair] = {};
                window.LAYOUT.assay_feature_values[assay_feature_pair][well_id] = parseFloat(value);
            }

            var id = row_label + '_' + column_label;
            // Current time alias
            var current_time = time;
            // Alias for readability
            var current_selection = assay_feature_selection;

            if (quality) {
                window.LAYOUT.set_invalid(id, well_id, current_selection, current_time);
            }
        });

        window.LAYOUT.build_heatmap();
        window.LAYOUT.heatmap_options();
    }

    window.LAYOUT.build_heatmap = function() {
        // For each feature
        $.each(window.LAYOUT.assay_feature_values, function(pair, values) {
            // Start the heatmap for this assay feature (class) pair
            window.LAYOUT.heatmaps[pair] = {};

            var current_selection = pair.split('_').slice(0, -1).join('_');
            var current_time = pair.split('_').slice(-1).join('_');
            var current_invalid_wells = [];

            if (window.LAYOUT.invalid[current_selection]) {
                current_invalid_wells = window.LAYOUT.invalid[current_selection][current_time];
            }

            // Exclude invalidated wells from values
            values = _.omit(values, function(value, key, object) {return _.contains(current_invalid_wells, key);});

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
                window.LAYOUT.heatmaps[pair][well] = value != undefined ? color_scale(value) : '#606060';
            });
        });

        // If build_heatmap is being called due to a change in invalid
        if (assay_select.val()) {
            var current_assay_feature = assay_select.val() + '_' + time_select.val();
            apply_heatmap(current_assay_feature);
        }
    };

    window.LAYOUT.heatmap_options = function() {
        // Clear old features
        assay_select.empty();

        var unique_pairs = {};

        $.each(window.LAYOUT.assay_feature_values, function (pair, value) {
            var pair_without_time = pair.split('_').slice(0, -1).join('_');
            var assay_feature = window.LAYOUT.selection_to_assay_feature[pair_without_time];
            var text_display = assay_feature.assay + '-' + assay_feature.feature;
            if (!unique_pairs[pair_without_time]) {
                var option = $('<option>')
                    .attr('value', pair_without_time)
                    .text(text_display);
                assay_select.append(option);

                unique_pairs[pair_without_time] = true;
            }
        });
        // Clear old times
        time_select.empty();

        // Convert times to sorted array?
        $.each(window.LAYOUT.times, function (index, time) {
            var option = $('<option>')
                .attr('value', time)
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
    };

    function apply_heatmap(current_assay_feature) {
        // Use heatmaps to get the respective colors
        var well_colors = window.LAYOUT.heatmaps[current_assay_feature];

        if (well_colors) {
            $.each(well_colors, function (well, color) {
                $(well).css('background-color', color);
            });

            $.each(window.LAYOUT.row_labels, function (row_index, row) {
                $.each(window.LAYOUT.column_labels, function (col_index, col) {
                    var well = '#' + row + '_' + col;
                    if (!well_colors[well]) {
                        $(well).css('background-color', '#606060');
                    }
                })
            });
        }
    }

    // When the assay_select changes, get the correct values
    assay_select.change(function() {
        var current_assay_feature = assay_select.val();
        // Append the value of time_select
        current_assay_feature = current_assay_feature + '_' + time_select.val();

        // Hide all values
        $('.value').hide();

        apply_heatmap(current_assay_feature);

        // Escape periods for the sizzle selector
        current_assay_feature = current_assay_feature.replace('.', '\\.');

        // Show this feature's values
        $('p[data-assay-feature-time="' + current_assay_feature + '"]').show();
        refresh_invalid();
    });

    // Trigger feature select change on time change
    time_select.change(function() {
        assay_select.trigger('change');
    });

    // When the 'toggle data only' button is clicked
    data_toggle.click(function() {
         $('.layout-list').toggle();
    });
});
