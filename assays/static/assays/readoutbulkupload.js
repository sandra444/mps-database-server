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

    function get_readouts() {
        var charts_name = 'current_charts';

        var data = {
            call: 'fetch_readouts',
            study: study_id,
            csrfmiddlewaretoken: middleware_token
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: data,
            success: function (json) {
                window.CHARTS.prepare_side_by_side_charts(json, charts_name);
                window.CHARTS.make_charts(json, charts_name);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Please note that bulk upload does not currently allow changing QC or notes
    // Before permitting this, ensure that the update_number numbers are accurate!
    function validate_bulk_file() {
        var charts_name = 'new_charts';

        // var dynamic_quality = $.extend({}, dynamic_quality_current, dynamic_quality_new);

        var data = {
            call: 'validate_bulk_file',
            study: study_id,
            csrfmiddlewaretoken: middleware_token
        //    dynamic_quality: JSON.stringify(dynamic_quality),
        //    include_table: include_table
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        var serializedData = $('form').serializeArray();
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        formData.append('bulk_file', $('#id_bulk_file')[0].files[0]);

        $.each(data, function(index, contents) {
            formData.append(index, contents);
        });

        if ($("#id_bulk_file")[0].files[0]) {
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
                        $('#id_bulk_file').val('');
                        $('#new_charts').empty();
                    }
                    else {
                        alert('Success! Please see "New Chip Data" below for preview.');
                        window.CHARTS.prepare_side_by_side_charts(json, charts_name);
                        window.CHARTS.make_charts(json, charts_name);
                    }
                },
                error: function (xhr, errmsg, err) {
                    alert('An unknown error has occurred. \nIf you have the file open, you may need to close it.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_bulk_file').val('');
                    $('#new_charts').empty();
                }
            });
        }
    }

    // Validate file if file selected
    $('#id_bulk_file').change(function() {
        validate_bulk_file();
    });

    // NOTE MAGIC STRING HERE
    $('#new_chartschart_options').find('input').change(function() {
        validate_bulk_file();
    });

    // NOTE MAGIC STRING HERE
    $('#current_chartschart_options').find('input').change(function() {
        get_readouts();
    });
});

