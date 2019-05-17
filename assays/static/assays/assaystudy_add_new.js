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

    // SOMEWHAT TASTELESS USE OF VARIABLES TO TRACK WHAT IS BEING EDITED
    var current_prefix = '';
    var current_setup_index = 0;

    // CREATE DIALOGS
    $.each(prefixes, function(index, prefix) {
        var current_dialog = $('#' + prefix + '_dialog');
        current_dialog.dialog({
            width: 825,
            buttons: [
            {
                text: 'Apply',
                click: function() {
                    // ACTUALLY MAKE THE CHANGE TO THE RESPECTIVE ENTITY
                    // TODO TODO TODO

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

    function create_edit_button(prefix) {
        return '<a data-edit-button="true" data-row="" data-prefix="' + prefix + '" data-column="" role="button" class="btn btn-primary">Edit</a>'
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
        // UGLY
        study_setup_head.find('.' + prefix + '_start').last().after('<th class="' + prefix + '_start' + '">' + prefix + ' ' + (number_of_columns[prefix] + 1) + '</th>');

        // ADD TO EXISTING ROWS AS EMPTY
        study_setup_body.find('tr').each(function() {
            $(this).find('.' + prefix + '_start').last().after('<td class="' + prefix + '_start' + '">' + create_edit_button(prefix) + '</td>');
        });

        number_of_columns[prefix] += 1;
    }

    function populate_table_cell(prefix, content, setup_index, object_index) {

    }

    // JUST USES DEFAULT PROTOCOL FOR NOW
    function spawn_row() {
        var new_row = $('<tr>');

        new_row.append(
            // $('<td>').append(
            //     $('<input>')
            //     .addClass('number-of-items')
            //     .attr('data-setup-index', current_setup_data.length)
            // )
            $('<td>').append(
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
                                .html(create_edit_button(prefix))
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
                    var html_contents = [
                        create_edit_button(prefix)
                    ];

                    var content = content_set[i];
                    if (content) {
                        $.each(content, function(key, value) {
                            html_contents.push(key + ': ' + value);
                        });
                    }

                    html_contents = html_contents.join('<br>')

                    new_row.append(
                        $('<td>')
                            .html(html_contents)
                            .addClass(prefix + '_start')
                    );
                }
                // });
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
