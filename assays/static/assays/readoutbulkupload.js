// This script allows previews to be shown for bulk uploads
// CURRENTLY ONLY CHIP PREVIEWS ARE SHOWN
// TODO CONSOLIDATE CODE WITH ASSAYRUN SUMMARY (DRY)
$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(get_readouts);

    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    var current_key = 'chip';
    // Do not convert to percent control at the moment
    var percent_control = '';

    var radio_buttons_display = $('#radio_buttons');

    function get_readouts() {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readouts',
                study: study_id,
                // TODO SET UP A WAY TO SWITCH BETWEEN CHIP AND COMPOUND
                key: current_key,
                // Tells whether to convert to percent Control
                percent_control: percent_control,
                // TODO REVISE
                include_all: $('#show_all').val(),
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                // Show radio_buttons if there is data
                if (Object.keys(json).length > 0) {
                    radio_buttons_display.show();
                }

                window.CHARTS.prepare_side_by_side_charts(json, 'current_charts');
                window.CHARTS.make_charts(json, 'current_charts');
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Please note that bulk upload does not currently allow changing QC or notes
    // Before permitting this, ensure that the update_number numbers are accurate!
    function validate_bulk_file() {
        var formData = new FormData();
        formData.append('bulk_file', $("#id_bulk_file")[0].files[0]);
        formData.append('overwrite_option', $("#id_overwrite_option").val());
        formData.append('call', 'validate_bulk_file');
        formData.append('study', study_id);
        formData.append('percent_control', percent_control);
        // Always include all for previews
        formData.append('include_all', 'True');
        formData.append('csrfmiddlewaretoken', middleware_token);
        formData.append('key', current_key);
        if ($("#id_bulk_file")[0].files[0]) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                cache: false,
                contentType: false,
                processData: false,
//                data: {
//                    // Function to call within the view is defined by `call:`
//                    call: 'validate_bulk_file',
//                    study: study_id,
//                    key: current_key,
//                    // Tells whether to convert to percent Control
//                    percent_control: percent_control,
//                    include_all: 'True',
//                    bulk_file: bulk_file,
//                    csrfmiddlewaretoken: middleware_token
//                },
                data: formData,
                success: function (json) {
                    // console.log(json);
                    if (json.errors) {
                        // Display errors
                        alert(json.errors);
                        // Remove file selection
                        $('#id_bulk_file').val('');
                        $('#new_charts').empty();
                    }
                    else {
                        alert('Success! Please see "New Chip Data" below for preview.');
                        window.CHARTS.prepare_side_by_side_charts(json, 'new_charts');
                        window.CHARTS.make_charts(json, 'new_charts');
                    }
                },
                error: function (xhr, errmsg, err) {
                    alert('An unknown error has occurred.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_bulk_file').val('');
                    $('#new_charts').empty();
                }
            });
        }
    }

    // Initial data (by device)
    // get_readouts();

    // Validate file if file selected
    $('#id_bulk_file').change(function() {
        validate_bulk_file();
    });

    // Trigger on change in show all (TO BE REVISED)
    $('#show_all').click(function() {
        if (this.value) {
            this.value = '';
            $(this).text('Show All');
        }
        else {
            this.value = 'True';
            $(this).text('Show Unmarked Only');
        }
        get_readouts();
    });
});

