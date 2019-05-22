$(document).ready(function () {
    var group_selector = $('#id_group');
    var center_name_selector = $('#center_name');
    var image_selector = $('#id_image');
    var image_display_selector = $('#image_display');
    var current_image_display_selector = $('#current_display');

    var organ_model = $('#id_organ_model');
    var protocol = $('#id_organ_model_protocol');

    window.organ_model = organ_model;
    window.organ_model_protocol = protocol;

    // FULL DATA
    var current_setup_data = [];

    // DATA FOR THE VERSION
    var current_setup = {};

    // The different components of a setup
    var prefixes = [
        'cell',
        'compound',
        'setting',
    ];

    var time_prefixes = [
        'addition_time',
        'duration'
    ]

    // SOMEWHAT TASTELESS USE OF VARIABLES TO TRACK WHAT IS BEING EDITED
    var current_prefix = '';
    var current_setup_index = 0;
    var current_row_index = null;
    var current_column_index = null;

    // CREATE DIALOGS
    $.each(prefixes, function(index, prefix) {
        var current_dialog = $('#' + prefix + '_dialog');
        current_dialog.dialog({
            width: 825,
            open: function() {
                $.ui.dialog.prototype.options.open();
                // BAD
                setTimeout(function() {
                    // Blur all
                    $('.ui-dialog').find('input, select, button').blur();
                }, 250);

                // Populate the fields
                var current_data = $.extend({}, current_setup_data[current_row_index][current_prefix][current_column_index]);

                console.log(current_setup_data);

                var this_popup = $(this);

                this_popup.find('input').each(function() {
                    if ($(this).attr('name')) {
                        console.log($(this).attr('name'), current_data[$(this).attr('name').replace(current_prefix + '_', '')]);
                        $(this).val(current_data[$(this).attr('name').replace(current_prefix + '_', '')]);
                    }
                });

                this_popup.find('select').each(function() {
                    if ($(this).attr('name')) {
                        console.log($(this).attr('name'), current_data[$(this).attr('name').replace(current_prefix + '_', '') + '_id']);
                        this.selectize.setValue(current_data[$(this).attr('name').replace(current_prefix + '_', '') + '_id']);
                    }
                });

                // TODO SPECIAL EXCEPTION FOR CELL SAMPLE
                this_popup.find('input[name="' + prefix + '_cell_sample"]').val(
                    current_data['cell_sample_id']
                );

                // TODO SPECIAL EXCEPTION FOR TIMES
                $.each(time_prefixes, function(index, current_time_prefix) {
                    var split_time = window.SPLIT_TIME.get_split_time(
                        current_data[current_time_prefix],
                    );

                    console.log(split_time);

                    $.each(split_time, function(time_name, time_value) {
                        console.log(prefix + '_' + current_time_prefix + '_' + time_name);
                        this_popup.find('input[name="' + prefix + '_' + current_time_prefix + '_' + time_name + '"]').val(time_value);
                    });
                });

                console.log(current_data);
            },
            buttons: [
            {
                text: 'Apply',
                click: function() {
                    // ACTUALLY MAKE THE CHANGE TO THE RESPECTIVE ENTITY
                    // TODO TODO TODO
                    var current_data = {};

                    $(this).find('input').each(function() {
                        console.log($(this).attr('name'), $(this).val());
                        if ($(this).attr('name')) {
                            current_data[$(this).attr('name').replace(current_prefix + '_', '')] = $(this).val();
                        }
                    });

                    $(this).find('select').each(function() {
                        console.log($(this).attr('name'), $(this).val());
                        if ($(this).attr('name')) {
                            current_data[$(this).attr('name').replace(current_prefix + '_', '') + '_id'] = $(this).val();
                        }
                    });

                    // SLOPPY
                    $.each(time_prefixes, function(index, current_time_prefix) {
                        if (current_data[current_time_prefix + '_minute'] !== undefined) {
                            current_data[current_time_prefix] = window.SPLIT_TIME.get_minutes(
                                    current_data[current_time_prefix + '_day'],
                                    current_data[current_time_prefix + '_hour'],
                                    current_data[current_time_prefix + '_minute']
                            );
                            $.each(window.SPLIT_TIME.time_conversions, function(key, value) {
                                delete current_data[current_time_prefix + '_' + key];
                            });
                        }
                    });

                    // Special exception for cell_sample
                    if ($(this).find('input[name="' + prefix + '_cell_sample"]')[0]) {
                        current_data['cell_sample_id'] = $(this).find('input[name="' + prefix + '_cell_sample"]').val();
                        delete current_data['cell_sample'];
                    }

                    console.log(current_data);

                    // current_setup_data[current_row_index][current_prefix][current_column_index] = $.extend({}, current_data);
                    modify_setup_data(current_prefix, $.extend({}, current_data), current_row_index, current_column_index);

                    var html_contents = get_content_display(current_prefix, current_row_index, current_column_index, current_data);

                    $('a[data-edit-button="true"][data-row="' + current_row_index +'"][data-column="' + current_column_index +'"][data-prefix="' + current_prefix + '"]').parent().html(html_contents);

                    $(this).dialog("close");
                }
            },
            {
                text: 'Cancel',
                click: function() {
                   $(this).dialog("close");
                }
            }]
        });
        current_dialog.removeProp('hidden');
    });

    // TODO NEEDS MAJOR REVISION
    function get_content_display(prefix, row_index, column_index, content) {
        var html_contents = [
            create_edit_button(prefix, row_index, column_index)
        ];

        if (content) {
            $.each(content, function(key, value) {
                html_contents.push(key + ': ' + value);
            });
        }

        html_contents = html_contents.join('<br>');

        return html_contents;
    }

    function get_center_id() {
        if (group_selector.val()) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                data: {
                    call: 'fetch_center_id',
                    id: group_selector.val(),
                    csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
                },
                success: function (json) {
                    center_name_selector.html(json.name + ' (' + json.center_id + ')');
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            center_name_selector.html('');
        }
    }

    // Need to have condition for adding vs. changing data
    get_center_id();

    // Needs an AJAX call to get centerID
    group_selector.change(function (evt) {
        get_center_id();
    });

    // Change image preview as necessary
    image_selector.change(function() {
        IMAGES.display_image(image_selector, image_display_selector, current_image_display_selector);
    });

    var number_of_columns = {
        'cell': 0,
        'compound': 0,
        'setting': 0,
    };

    // Table vars
    var study_setup_table = $('#study_setup_table');
    var study_setup_head = study_setup_table.find('thead').find('tr');
    var study_setup_body = study_setup_table.find('tbody');

    var setup_data_selector = $('#id_setup_data');

    function create_edit_button(prefix, row_index, column_index) {
        return '<a data-edit-button="true" data-row="' + row_index + '" data-prefix="' + prefix + '" data-column="' + column_index + '" role="button" class="btn btn-primary">Edit</a>';
    }

    function create_delete_button(prefix, index) {
        if (prefix === 'row') {
            return '<a data-delete-row-button="true" data-row="' + index + '" role="button" class="btn btn-danger">Delete</a>';
        }
        else {
            return '<a data-delete-column-button="true" data-column="' + index + '" data-prefix="' + prefix + '" role="button" class="btn btn-danger">Delete</a>';
        }
    }

    function create_clone_button(index) {
        return '<a data-clone-row-button="true" data-row="' + index + '" role="button" class="btn btn-info">Clone</a>';
    }

    function modify_setup_data(prefix, content, setup_index, object_index) {
        if (object_index) {
            current_setup_data[setup_index][prefix][object_index] = content;
        }
        else {
            current_setup_data[setup_index][prefix] = content;
        }

        setup_data_selector.val(JSON.stringify(current_setup_data));
    }

    function spawn_column(prefix) {
        var column_index = number_of_columns[prefix];
        // UGLY
        study_setup_head.find('.' + prefix + '_start').last().after('<th class="' + prefix + '_start' + '">' + prefix + ' ' + column_index + '<br>' + create_delete_button(prefix, column_index) +'</th>');

        // ADD TO EXISTING ROWS AS EMPTY
        study_setup_body.find('tr').each(function(row_index) {
            $(this).find('.' + prefix + '_start').last().after('<td class="' + prefix + '_start' + '">' + create_edit_button(prefix, row_index, column_index) + '</td>');
        });

        number_of_columns[prefix] += 1;
    }

    function populate_table_cell(prefix, content, setup_index, object_index) {

    }

    // JUST USES DEFAULT PROTOCOL FOR NOW
    function spawn_row() {
        var new_row = $('<tr>');

        var row_index = study_setup_body.find('tr').length;

        new_row.append(
            $('<td>').html(
                create_clone_button(row_index) + create_delete_button('row', row_index)
            ).append(
                $('#id_number_of_items').clone().removeAttr('id')
            )
        );

        new_row.append(
            $('<td>').append(
                $('#id_test_type').clone().removeAttr('id').removeAttr('style')
            )
        );

        $.each(prefixes, function(index, prefix) {
            var content_set = current_setup[prefix];
            if (!content_set) {
                if (!number_of_columns[prefix]) {
                    new_row.append(
                        $('<td>')
                            .attr('hidden', 'hidden')
                            .addClass(prefix + '_start')
                    );
                }
                else {
                    for (var i = 0; i < number_of_columns[prefix]; i++) {
                        new_row.append(
                            $('<td>')
                                .html(create_edit_button(prefix, row_index, i))
                                .addClass(prefix + '_start')
                        );
                    }
                }
            }
            else {
                while (number_of_columns[prefix] < content_set.length) {
                    spawn_column(prefix);
                }

                for (var i = 0; i < number_of_columns[prefix]; i++) {
                    // var html_contents = [
                    //     create_edit_button(prefix, row_index, i)
                    // ];
                    //
                    // var content = content_set[i];
                    // if (content) {
                    //     $.each(content, function(key, value) {
                    //         html_contents.push(key + ': ' + value);
                    //     });
                    // }
                    //
                    // html_contents = html_contents.join('<br>')
                    var html_contents = get_content_display(prefix, row_index, i, content_set[i]);

                    new_row.append(
                        $('<td>')
                            .html(html_contents)
                            .addClass(prefix + '_start')
                    );
                }
            }
        });

        study_setup_body.append(new_row);

        current_setup_data.push(
            $.extend({}, current_setup)
        );
        setup_data_selector.val(JSON.stringify(current_setup_data));
    }

    $(document).on('change', '.test-type', function() {
        console.log('test_type', $(this).val());
        modify_setup_data('test_type', $(this).val(), $(this).attr('setup_index'));
    });

    $(document).on('change', '.number-of-items', function() {
        console.log('test_type', $(this).val());
        modify_setup_data('number_of_items', $(this).val(), $(this).attr('setup_index'));
    });

    $(document).on('click', 'a[data-edit-button="true"]', function() {
        console.log(this);
        current_prefix = $(this).attr('data-prefix');
        current_row_index = $(this).attr('data-row');
        current_column_index = $(this).attr('data-column');
        $('#' + $(this).attr('data-prefix') + '_dialog').dialog('open');
    });

    $('a[data-add-new-button="true"]').click(function() {
        spawn_column($(this).attr('data-prefix'));
    });

    $('#add_group_button').click(function() {
        spawn_row();
    });

    // function apply_protocol_setup_to_row() {
    //
    // }

    // Handling Device flow
    // Make sure global var exists before continuing
    if (window.get_organ_models) {
        organ_model.change(function() {
            // Get and display correct protocol options
            window.get_protocols(organ_model.val());
        });

        window.get_protocols(organ_model.val());

        // NOTE THAT THIS IS TRIGGERED ON LOAD
        protocol.change(function() {
            // Start SPINNING
            window.spinner.spin(
                document.getElementById("spinner")
            );

            console.log(protocol.val());

            if (protocol.val()) {
              $.ajax({
                  url: "/assays_ajax/",
                  type: "POST",
                  dataType: "json",
                  data: {
                      call: 'fetch_organ_model_protocol_setup',
                      organ_model_protocol_id: protocol.val(),
                      csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
                  },
                  success: function (json) {
                      // Stop spinner
                      window.spinner.stop();

                      console.log(json);
                      current_setup = $.extend({}, json);

                      // GET RID OF ANYTHING IN THE TABLE
                      study_setup_body.empty();
                      current_setup_data = [];

                      spawn_row();
                  },
                  error: function (xhr, errmsg, err) {
                      first_run = false;

                      // Stop spinner
                      window.spinner.stop();

                      console.log(xhr.status + ": " + xhr.responseText);
                  }
              });
            }
            else {
                window.spinner.stop();
            }
        }).trigger('change');
    }
});
