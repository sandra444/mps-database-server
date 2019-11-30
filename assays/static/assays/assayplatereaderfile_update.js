$(document).ready(function () {
    // # id, . class

    // set global variables


    // set based on add or update and if the plate map has been assigned to a file-block
    let global_plate_number_file_block_sets = 0;
    try {
        // this should happen if the file-block has been assigned
        global_plate_number_file_block_sets = document.getElementById("id_number_blocks").value;
    }
    catch(err) {
    }

    // set the tooltips
    let global_plate_file_upload_tooltip = "Data from file will be copied and displayed for review. Note: the file will not be loaded to the database.";
    $('#file_upload_tooltip').next().html($('#file_upload_tooltip').next().html() + make_escaped_tooltip(global_plate_file_upload_tooltip));




    // // get the copy of the empty formsets (the "extra" in the forms.py), then remove the empty
    // let first_item_form = $('#formset').find('.inline').first()[0].outerHTML;
    // if ($('#formset').find('.inline').length === 1 && $("#check_load").html() === 'add') {
    //     $('#formset').find('.inline').first().remove();
    // }
    // let first_line_form = $('#line_formset').find('.inline').first()[0].outerHTML;
    // if ($('#line_formset').find('.inline').length === 1 && $("#check_load").html() === 'add') {
    //     $('#line_formset').find('.inline').first().remove();
    // }
    //
    // //Make sure to do these every time add a formset back! watch the index, they might be different!
    // $('#formset').append(first_item_form.replace(/-0-/g, '-' + formsetidx + '-'));
    // $('#id_assayplatereadermapdatafileblock_set-TOTAL_FORMS').val(formsetidx + 1);
    // $('#line_formset').append(first_value_form.replace(/-0-/g, '-' + formsetidx + '-'));
    // $('#id_assayplatereadermapdatafileline_set-TOTAL_FORMS').val(formsetidx + 1);


    // when loading, what and how to load the plate
    if ($("#check_load").html() === 'add') {

    } else {

    }

    // Upload file to the line table when click button
    // No changing file will be allowed, only adds and deletes  (only edit Name and/or Description of this file data set)
    $('#id_plate_reader_file').change(function() {
        upload_plate_reader_file();
    });
    $('#id_plate_reader_file').click(function() {
        upload_plate_reader_file();
    });

    function upload_plate_reader_file() {
        // var charts_name = 'new_charts';
        // var charts_name = 'charts';

        // var dynamic_quality = $.extend(true, {}, dynamic_quality_current, dynamic_quality_new);
        console.log("in upload")
        var data = {
            // see ajax file !!!
            call: 'upload_plate_reader_data_file',
            study: $('#this_study_id').val(),
            //criteria: JSON.stringify(window.GROUPING.group_criteria),
            //post_filter: JSON.stringify(window.GROUPING.current_post_filter),
            //csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        //    dynamic_quality: JSON.stringify(dynamic_quality),
        //    include_table: include_table
        };

       // window.CHARTS.global_options = window.CHARTS.prepare_chart_options();
        //var options = window.CHARTS.global_options.ajax_data;

        data = $.extend(data);
        //data = $.extend(data, options);

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
            // Show spinner
            window.spinner.spin(
                document.getElementById("spinner")
            );

            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                cache: false,
                contentType: false,
                processData: false,
                data: formData,
                success: function (json) {
                    // Stop spinner
                    window.spinner.stop();
                    if (json.errors) {
                        // Display errors
                        alert(json.errors);
                        // Remove file selection
                        $('#id_bulk_file').val('');
                    }
                    else {
                        alert('Success!' +
                            '\n\nPlease note that changes will not be made until you press the "Submit" button at the bottom of the page.');
                    }
                },
                error: function (xhr, errmsg, err) {
                    // Stop spinner
                    window.spinner.stop();
                    alert('An unknown error has occurred. \nIf you have the file open, you may need to close it.');
                    console.log(xhr.status + ": " + xhr.responseText);
                    // Remove file selection
                    $('#id_bulk_file').val('');
                }
            });
        }
    }

    // functions for the tooltips
    function escapeHtml(html) {
        return $('<div>').text(html).html();
    }
    function make_escaped_tooltip(title_text) {
        let new_span = $('<div>').append($('<span>')
            .attr('data-toggle', "tooltip")
            .attr('data-title', escapeHtml(title_text))
            .addClass("glyphicon glyphicon-question-sign pull-left")
            .attr('aria-hidden', "true")
            .attr('data-placement', "bottom"));
        return new_span.html();
    }
    // function to purge previous formsets when adding a page and changing plate size
    function removeFormsets() {
        // get rid of previous formsets before try to add more or the indexes get all messed up
        while ($('#formset').find('.inline').length > 0 ) {
            $('#formset').find('.inline').first().remove();
        }
        $('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(0);
    }
});
