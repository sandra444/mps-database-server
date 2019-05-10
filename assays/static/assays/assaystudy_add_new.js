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
