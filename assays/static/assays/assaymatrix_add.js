// Functions for displaying Assay Matrices
// TODO WE MAY WANT THIS IN MULTIPLE LOCATIONS, BUT AT THE MOMENT I AM ASSUMING ADD ONLY
// TODO THIS FILE IS A MESS
$(document).ready(function () {
    // TODO TODO TODO IN THE FUTURE FILE-SCOPE VARIABLES SHOULD BE IN ALL-CAPS
    // The matrix's ID
    var matrix_id = Math.floor(window.location.href.split('/')[5]);

    // Alias for the matrix selector
    var matrix_table_selector = $('#matrix_table');
    var matrix_body_selector = $('#matrix_body');

    // Allows the matrix_table to have the draggable JQuery UI element
    matrix_table_selector.selectable({
        filter: 'td',
        distance: 1,
        stop: matrix_add_content_to_selected
    });

    // Page selector (MAY OR MAY NOT BE USED)
    var page_selector = $('#page');

    // Alias for device selector
    var device_selector = $('#id_device');

    // Alias for action selector
    var action_selector = $('#id_action');

    // Alias for representation selector
    var representation_selector = $('#id_representation');

    // Alias for number of rows/columns
    var number_of_items_selector = $('#id_number_of_items');
    var number_of_rows_selector = $('#id_number_of_rows');
    var number_of_columns_selector = $('#id_number_of_columns');

    // Not currently used, may be helpful in future
    // var initial_number_of_rows = 0;
    // var initial_number_of_columns = 0;

    // CRUDE AND BAD
    // var item_prefix = 'assaymatrixitem_set';
    // var cell_prefix = 'assaysetupcell_set';
    // var setting_prefix = 'assaysetupsetting_set';
    // var compound_prefix = 'assaysetupcompound_set';
    var item_prefix = 'item';
    var cell_prefix = 'cell';
    var setting_prefix = 'setting';
    var compound_prefix = 'compound';

    var prefixes = [
        item_prefix,
        cell_prefix,
        setting_prefix,
        compound_prefix
    ];

    var empty_item_html = $('#empty_item_html').children();
    var empty_compound_html = $('#empty_compound_html').children();
    var empty_cell_html = $('#empty_cell_html').children();
    var empty_setting_html = $('#empty_setting_html').children();

    // NO, JS ACCEPTS STRING LITERALS
    // var empty_html = {
    //     item_prefix: empty_item_html,
    //     compound_prefix: empty_compound_html,
    //     cell_prefix: empty_cell_html,
    //     setting_prefix: empty_setting_html
    // };
    var empty_html = {};
    empty_html[item_prefix] = empty_item_html;
    empty_html[compound_prefix] = empty_compound_html;
    empty_html[cell_prefix] = empty_cell_html;
    empty_html[setting_prefix] = empty_setting_html;

    // All but matrix item should be static here
    // var item_final_index = $('#id_' + item_prefix + '-TOTAL_FORMS').val() - 1;
    var item_final_index = $('.' + item_prefix).length - 1;
    var cell_final_index = $('.' + cell_prefix).length - 1;
    var setting_final_index = $('.' + setting_prefix).length - 1;
    var compound_final_index = $('.' + compound_prefix).length - 1;

    // Due to extra=1 (A SETTING WHICH SHOULD NOT CHANGE) there will always be an empty example at the end
    // I can use these to make new forms as necessary
    var empty_item_form = $('#' + item_prefix + '-' + item_final_index).html();
    var empty_setting_form = $('#' + setting_prefix + '-' + setting_final_index).html();
    var empty_cell_form = $('#' + cell_prefix + '-' + cell_final_index).html();
    var empty_compound_form = $('#' + compound_prefix + '-' + compound_final_index).html();

    // NO!
    // var empty_forms = {
    //     item_prefix: empty_item_form,
    //     compound_prefix: empty_compound_form,
    //     cell_prefix: empty_cell_form,
    //     setting_prefix: empty_setting_form
    // };
    var empty_forms = {};
    empty_forms[item_prefix] = empty_item_form;
    empty_forms[compound_prefix] = empty_compound_form;
    empty_forms[cell_prefix] = empty_cell_form;
    empty_forms[setting_prefix] = empty_setting_form;

    // For converting between times
    var time_conversions = {
        'day': 1440.0,
        'hour': 60.0,
        'minute': 1.0
    };

    function add_item_form() {
        // Can't cache this, need to check every call!
        var number_of_forms = $('.' + item_prefix).length;

        var regex_to_replace_old_index = new RegExp("/\-" + item_final_index +"\-/g");
        var new_html = empty_item_form.replace(regex_to_replace_old_index,'-' + number_of_forms + '-');
        var new_form = $('<div>')
            .html(new_html)
            .attr('id', item_prefix + '-' + number_of_forms);

        // TODO REVISE THIS, SHOULD BE APPENDED TO ITEM FORMSET
        // Just arbitrarily append to the page
        page_selector.append(new_form);

        // Make a form for each subform type
        $.each(empty_html, function(form_type, content) {
            add_sub_form(number_of_forms, form_type)
        });
    }

    // TODO JUST A TEST
    add_item_form();

    function add_sub_form(current_matrix_item_index, prefix) {
        var new_html = empty_forms[prefix];
    }

    // DEPRECATED
    // WILL PROBABLY JUST HANDLE THIS IN PYTHON
    function get_split_time(time_in_minutes) {
        var times = {
            'day': 0,
            'hour': 0,
            'minute': 0
        };

        var time_in_minutes_remaining = time_in_minutes;
        $.each(time_conversions, function(time_unit, conversion) {
            var initial_time_for_current_field = Math.floor(time_in_minutes_remaining / conversion);
            if (initial_time_for_current_field) {
                times[time_unit] = initial_time_for_current_field;
                time_in_minutes_remaining -= initial_time_for_current_field * conversion;
            }
        });

        // Add fractions of minutes if necessary
        if (time_in_minutes_remaining) {
            times['minute'] += time_in_minutes_remaining
        }

        return times
    }

    // This function turns numbers into letters
    // Very convenient for handling things like moving from "Z" to "AA" automatically
    // Though, admittedly, the case of so many rows is somewhat unlikely
    function to_letters(num) {
        "use strict";
        var mod = num % 26,
            pow = num / 26 | 0,
            out = mod ? String.fromCharCode(64 + mod) : (--pow, 'Z');
        return pow ? to_letters(pow) + out : out;
    }

    function plate_style_name_creation() {
        var current_global_name = $('#id_item_name').val();
        var current_number_of_rows = number_of_rows_selector.val();
        var current_number_of_columns = number_of_columns_selector.val();

        var largest_row_name_length = Math.pow(current_number_of_columns, 1/10);

        for (var row_id=0; row_id < current_number_of_rows; row_id++) {
            // Please note + 1
            var row_name = to_letters(row_id + 1);

            for (var column_id=0; column_id < current_number_of_columns; column_id++) {
                var current_item_id = item_prefix + '_' + row_id + '_' + column_id;

                var column_name = column_id + 1 + '';
                while (column_name.length < largest_row_name_length) {
                    column_name = '0' + column_name;
                }

                // TODO TODO TODO PERFORM THE ACTUAL APPLICATION TO THE FORMS
            }
        }

        // TODO CHANGE THE DISPLAYS BY REFERRING TO THE NEWLY CHANGED FORMS
        // TODO HAVE A FUNCTION TO DO ABOVE
    }

    // This function gets the initial dimensions of the matrix
    // Please see the corresponding AJAX call as necessary
    // TODO PLEASE ADD CHECKS TO SEE IF EXISTING DATA FALLS OUTSIDE NEW BOUNDS
    // TODO PLEASE NOTE THAT THIS GETS RUN A MILLION TIMES DO TO HOW TRIGGERS ARE SET UP
    // TODO MAKE A VARIABLE TO SEE WHETHER DATA WAS ALREADY AQUIRED
    var get_matrix_dimensions = function() {
        var current_device = device_selector.val();

        var current_number_of_rows = number_of_rows_selector.val();
        var current_number_of_columns = number_of_columns_selector.val();

        if (current_device) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                data: {
                    call: 'fetch_device_dimensions',
                    // The device may be needed to specify the dimensions
                    device_id: current_device,
                    csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
                },
                success: function (json) {
                    number_of_rows_selector.val(json.number_of_rows);
                    number_of_columns_selector.val(json.number_of_columns);
                    build_initial_matrix(
                        json.number_of_rows,
                        json.number_of_columns
                    );
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }

        if (current_number_of_rows > 200) {
            alert('Number of rows exceeds limit.');
            number_of_rows_selector.val(200);
            current_number_of_rows = 200;
        }

        if (current_number_of_columns > 200) {
            alert('Number of columns exceeds limit.');
            current_number_of_columns.val(200);
            current_number_of_columns = 200;
        }

        if (current_number_of_rows && current_number_of_columns) {
            build_initial_matrix(
                current_number_of_rows,
                current_number_of_columns
            );

            // initial_number_of_rows = current_number_of_rows;
            // initial_number_of_columns = current_number_of_columns;
        }

        // Set number of items
        number_of_items_selector.val(current_number_of_rows * current_number_of_columns)
    };

    // Makes the initial matrix
    // TODO PURGE CELLS WHEN SHRINKING
    var build_initial_matrix = function(number_of_rows, number_of_columns) {
        matrix_body_selector.empty();

        for (var row_index=0; row_index < number_of_rows; row_index++) {
            var row_id = 'row_' + row_index;
            var current_row = $('<tr>')
                .attr('id', row_id);
            // var add_row = true;
            for (var column_index=0; column_index < number_of_columns; column_index++) {
                var item_id = item_prefix + '_' + row_index + '_' + column_index;
                var new_cell = empty_item_html
                    .clone()
                    .attr('id', item_id);
                current_row.append(new_cell);
            }
            matrix_body_selector.append(current_row);
        }

        // TODO TODO TODO NEED A REAL FUNCTION FOR THIS
        refresh_all_contents_from_forms();
    };

    function get_field_name(field) {
        // To get the field name in question, I can split away everything before the terminal -
        if (field.attr('name')) {
            var field_name = field.attr('name').split('-');
            return field_name[field_name.length-1];
        }
        else {
            return false;
        }
    }

    function get_display_for_field(field, field_name, prefix) {
        // NOTE: SPECIAL EXCEPTION FOR CELL SAMPLES
        if (field_name === 'cell_sample') {
            // TODO VERY POORLY DONE
            return $('#' + field.val()).attr('name');
        }
        else {
            // Ideally, this would be cached in an object or something
            var origin = $('#id_' + prefix + '_' + field_name);

            // Get the select display if select
            if (origin.prop('tagName') === 'SELECT') {
                return origin.find('option[value="' + field.val() + '"]').text()
            }
            // Just display the thing if there is an origin
            else if (origin[0]) {
                return field.val();
            }
            // Give back null to indicate this should not be displayed
            else {
                return null;
            }
        }
    }

    // This function finds where to put the new display data
    function get_display_from_item_form(form) {
        var row_index = form.find('input[name$="row_index"]').val();
        var column_index = form.find('input[name$="column_index"]').val();
        return $('#' + item_prefix + '_' + row_index + '_' + column_index);
    }

    function get_display_id_from_subform(subform) {
        var parent_item_id = subform.find('input[name$="matrix_item"]').val();
        // console.log(parent_item_id);
        var parent_form = $('.' + item_prefix + '> input[value="' + parent_item_id + '"').parent();
        return get_display_from_item_form(parent_form);
    }

    // TODO REVISE
    function refresh_all_contents_from_forms() {
        // TODO PURGE ALL OLD DISPLAY STUFF
        // I probably can get away with purging the subdisplays, but can keep the item data

        $('.item-setup_set_section').empty();

        // Iterate over all prefixes
        $.each(prefixes, function(index, prefix) {
            // Iterate over all forms
            $('.' + prefix).each(function() {
                // Get the display to add to here TODO TODO TODO
                if (prefix === item_prefix) {
                    var display = get_display_from_item_form($(this));
                    var new_subdisplay = null;
                }
                // Generate a subdisplay if this is not item TODO TODO TODO
                // Add the subdisplay to the display
                else {
                    // console.log($(this));
                    var display = get_display_id_from_subform($(this));
                    var new_subdisplay = empty_html[prefix].clone();
                }

                // Iterate over all fields
                // Out of convenience, I can iterate over every child
                $(this).children().each(function() {
                    // I will need to think about invalid fields
                    var field_name = get_field_name($(this));
                    var field_display = get_display_for_field($(this), field_name, prefix);
                    if (!new_subdisplay) {
                        display.find('.' + prefix + '-' + field_name).html(field_display);
                    }
                    else {
                        new_subdisplay.find('.' + prefix + '-' + field_name).html(field_display);
                    }
                });

                if (new_subdisplay) {
                    display.append(new_subdisplay);
                }
            });
        });
    }

    function apply_matrix_item_contents() {

    }

    function add_to_item_fields(fields) {
        $('.ui-selected').each(function() {

        });
    }

    function chip_style_name_incrementer() {
        var original_name = $('#id_item_name').val();
        var split_name = original_name.split(/(\d+)/).filter(Boolean);

        var numeric_index = 0;
        // Increment the first number encountered
        while (!$.isNumeric(split_name[numeric_index]) && numeric_index < original_name.length) {
            numeric_index += 1;
        }

        var first_half = split_name.slice(0, numeric_index).join('');
        var second_half = split_name.slice(numeric_index + 1).join('');
        var initial_value = Math.floor(split_name[numeric_index]);

        if (isNaN(initial_value)) {
            initial_value = 1;
        }

        // Iterate over all selected
        $('.ui-selected').each(function(index) {
            var current_item_id = this.id;

            var incremented_value = index + initial_value;
            incremented_value += '';

            while (first_half.length + second_half.length + incremented_value.length < original_name.length) {
                incremented_value = '0' + incremented_value;
            }

            value = first_half + incremented_value + second_half;

            $(this).find('.item-name').html(value);
            // item_data[current_item_id]['name'] = value;
        });
    }

    function default_incrementer(current_value, increment, index, increment_type) {
        var new_value = current_value;
        var result = null;

        // Add
        if (increment_type === '+') {
            result = new_value + (index * increment);
            if (result >= 0) {
                new_value = result;
            }
            else {
                new_value = 0;
            }
        }

        // Divide
        else if(increment_type === '/') {
            result = new_value / Math.pow(increment, index);
            if (isFinite(result) && result >= 0) {
                new_value = result;
            }
            else {
                new_value = 0;
            }
        }

        // Subtract
        else if(increment_type === '-') {
            result = new_value - (index * increment);
            if (result >= 0) {
                new_value = result;
            }
            else {
                new_value = 0;
            }
        }

        // Multiply
        else {
            result = new_value * Math.pow(increment, index);
            if (result >= 0) {
                new_value = result;
            }
            else {
                new_value = 0;
            }
        }

        return new_value;
    }

    function clear_fields() {

    }

    function matrix_add_content_to_selected() {
        var action = action_selector.val();

        // PLEASE NOTE THIS IS SUBJECT TO CHANGE
        // Switch statements look pretty nice, might use more often
        switch (action) {
            case 'add_name':
                chip_style_name_incrementer();
                break;
            case 'add_date':
                add_to_item_fields(['setup_date']);
                break;
            case 'add_notes':
                add_to_item_fields([
                    'scientist',
                    'notebook',
                    'notebook_page',
                    'notes'
                ]);
                break;
            case 'add_device':
                add_to_item_fields([
                    'device',
                    'organ_model',
                    'organ_model_protocol',
                    'variance_from_organ_model_protocol'
                ]);
                break;
            case 'add_settings':
                alert('TODO');
                break;
            case 'add_compounds':
                add_compounds_to_setup();
                break;
            case 'add_cells':
                add_cells_to_setup();
                break;
            case 'copy':
                alert('TODO');
                break;
            case 'clear':
                // TODO add more options
                clear_fields();
                break;
            default:
                alert('Action not recognized')
        }
    }

    // Matrix Listeners
    // BE CAREFUL! THIS IS SUBJECT TO CHANGE!
    representation_selector.change(function() {
        var current_representation = representation_selector.val();

        // Hide all matrix sections
        $('.matrix-section').hide('fast');

        if (current_representation === 'chips') {
            $('#matrix_dimensions_section').show();
            // TODO CHANGE DEVICE TO NONE
            $('#id_setup_device option').show();
        }
        else if (current_representation === 'plate') {
            $('#matrix_device_and_model_section').show();
            // TODO FORCE SETUP DEVICE TO MATCH
        }
    }).trigger('change');

    device_selector.change(function() {
        get_matrix_dimensions();

        if (representation_selector.val() === 'plate') {
           $('#id_setup_device option[value!=' + device_selector.val() + ']').hide();
        }
    });

    // TODO TODO TODO RESTORE LATER
    // if (device_selector.val()) {
    //     device_selector.trigger('change');
    // }

    number_of_rows_selector.change(function() {
        get_matrix_dimensions();
    });

    number_of_columns_selector.change(function() {
        get_matrix_dimensions();
    });

    number_of_items_selector.change(function() {
        var number_of_items = Math.floor(number_of_items_selector.val());
        var first_estimate = Math.floor(Math.sqrt(number_of_items));

        var number_of_rows = first_estimate;
        var number_of_columns = first_estimate;

        var additional_columns = 0;

        while (Math.pow(first_estimate, 2) + additional_columns * number_of_rows < number_of_items) {
            additional_columns += 1;
        }

        number_of_rows_selector.val(number_of_rows);
        number_of_columns_selector.val(number_of_columns + additional_columns);

        get_matrix_dimensions();
    });

    // TODO TODO TODO RESTORE LATER
    // if (number_of_items_selector.val() && !device_selector.val()) {
    //     number_of_items_selector.trigger('change');
    // }

    action_selector.change(function() {
        $('.item-section').hide('fast');
        var current_section = $(this).val();
        $('#' + current_section + '_section').show('fast');
    }).trigger('change');

    // Testing SUBJECT TO CHANGE
    $('#apply_plate_names').click(function() {
       plate_style_name_creation();
    });

    // TODO TODO TODO TESTING
    get_matrix_dimensions();

    // Cell Samples
    // SOMEWHAT REDUNDANT, BUT THE OTHER INSTANCE OF CELL SAMPLE NEEDS TO WORK WITH INLINES
    // SHOULD REVISE TO USE CLASSES AND PEEK AT PARENT AND SO ON
    var cell_sample_search = $('#id_cell_sample_search');
    var cell_sample_id_selector = $('#id_cell_cell_sample');
    // var cell_sample_id_selector = $('#id_cell_sample');
    var cell_sample_label_selector = $('#id_cell_sample_label');

    // Open and then close dialog so it doesn't get placed in window itself
    var dialog = $('#dialog');
    dialog.dialog({
        width: 900,
        height: 500,
        closeOnEscape: true,
        autoOpen: false,
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            $('body').addClass('stop-scrolling');
        }
    });
    dialog.removeProp('hidden');

    $('#cellsamples').DataTable({
        "iDisplayLength": 50,
        // Initially sort on receipt date
        "order": [ 1, "desc" ],
        // If one wants to display top and bottom
        "sDom": '<"wrapper"fti>'
    });

    // Move filter to left
    $('.dataTables_filter').css('float', 'left');

    cell_sample_search.click(function() {
        dialog.dialog('open');
        // Remove focus
        $('.ui-dialog :button').blur();
    });

    $('.cellsample-selector').click(function() {
        var cell_sample_id = this.id;
        cell_sample_id_selector.prop('value', cell_sample_id);
        var cell_sample_name = this.attributes["name"].value;
        cell_sample_label_selector.text(cell_sample_name);
        $('#dialog').dialog('close');
    });

    // This will clear a cell sample when the button is pressed
    $('#clear_cell_sample').click(function() {
        cell_sample_id_selector.prop('value', '');
        cell_sample_label_selector.text('');
        $('#dialog').dialog('close');
    });
});
