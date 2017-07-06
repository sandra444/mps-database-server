$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(get_readout);

    // Get the middleware token
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value') ?
            $('[name=csrfmiddlewaretoken]').attr('value'):
            getCookie('csrftoken');

    // Get the quality indicators
    // var quality_indicators = [];
    // $.ajax({
    //     url: "/assays_ajax/",
    //     type: "POST",
    //     dataType: "json",
    //     data: {
    //         call: 'fetch_quality_indicators',
    //         csrfmiddlewaretoken: middleware_token
    //     },
    //     success: function (json) {
    //         quality_indicators = json;
    //     },
    //     error: function (xhr, errmsg, err) {
    //         console.log(xhr.status + ": " + xhr.responseText);
    //     }
    // });

    // Tracks the quality of data to indicate whether to exclude or include in plots
    var dynamic_quality_current = {};
    var dynamic_quality_new = {};

    var readout_id = get_readout_value();
    var study_id = get_study_id();

    // Name for the charts for binding events etc
    var charts_name = 'charts';

    var changes_to_chart_options = {
        chartArea: {
            // Slight change in width
            width: '78%',
            height: '65%'
        }
    };

    function is_true(element, index, array) {
        if (!element && element !== 0) {
            return false;
        }
        else {
            return true;
        }
    }

    function data_format(value, ratio, id) {
        var format = d3.format(',.2f');
        if (Math.abs(value) > 100000) {
            format = d3.format('.2e');
        }
        else if (value % 1 === 0) {
            format = d3.format(',d');
        }
        return format(value);
    }

    function get_study_id() {
        var study_id = Math.floor(window.location.href.split('/')[4]);
        if (study_id) {
            return study_id
        }
        else {
            return ''
        }
    }

    function get_readout_value() {
        // Admin (check by looking for content-main ID)
        // Deprecated
        if ($('#content-main')[0]) {
            try {
                return Math.floor($('.historylink').attr('href').split('/')[4]);
            }
            catch (err) {
                return null;
            }
        }
        // Frontend
        else {
            // Details does not have access to CSRF on its own
            middleware_token = getCookie('csrftoken');
            var current_id = Math.floor(window.location.href.split('/')[5]);

            if (!current_id) {
                current_id = '';
            }

            return current_id;
        }
    }

    function get_readout() {
        if (readout_id) {
            // Get the table
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_chip_readout',
                    id: readout_id,
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    exist = true;
                    process_data(json, exist);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
            // Get the plots
            plot_existing_data();
        }
    }

    function clear_new_data() {
        $('.new-value').each(function() {
            // Delete this value from data
            // delete data[$(this).attr('data-chart-index')];
            // Remove the row itself
            $(this).remove();
        });
    }

    function validate_readout_file(include_table) {
        // Purge dynamic_quality_new if table if being reset
        if (include_table) {
            dynamic_quality_new = {};
        }

        var dynamic_quality = $.extend({}, dynamic_quality_current, dynamic_quality_new);

        var data = {
            call: 'validate_individual_chip_file',
            study: study_id,
            readout: readout_id,
            csrfmiddlewaretoken: middleware_token,
            dynamic_quality: JSON.stringify(dynamic_quality),
            include_table: include_table
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        var serializedData = $('form').serializeArray();
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        formData.append('file', $('#id_file')[0].files[0]);

        $.each(data, function(index, contents) {
            formData.append(index, contents);
        });

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
                    $('#id_file').val('');
                    // $('#table_body').empty();
                    clear_new_data();
                    // plot();
                    plot_existing_data();
                }
                else {
                    exist = false;
                    alert('Success! Please see "New Chip Data" below for preview.');

                    if (json.number_of_conflicting_entries) {
                        alert('***Submitting this file will replace ' + json.number_of_conflicting_entries + ' point(s).***')
                    }

                    if (include_table) {
                       process_data(json.table, exist);
                    }

                    window.CHARTS.prepare_charts_by_table(json.charts, charts_name);
                    window.CHARTS.make_charts(json.charts, charts_name, changes_to_chart_options);
                }
            },
            error: function (xhr, errmsg, err) {
                alert('An unknown error has occurred. \nIf you have the file open, you may need to close it.');
                console.log(xhr.status + ": " + xhr.responseText);
                // Remove file selection
                $('#id_file').val('');
                // $('#table_body').empty();
                clear_new_data();
                // plot();
                plot_existing_data();
            }
        });
    }

    var process_data = function (json, exist) {
        var table_body = $('#table_body');

        // Do not empty entire table, only delete new values
        // table_body.empty();
        clear_new_data();

        if (!json) {
            return;
        }

        // Current index for saving QC values
        var current_index = 0;

        // var table = '';

        // PLEASE NOTE THAT THE DATA POINTS ARE REVERSED
        var data_points = json.data_points.reverse();
        var assay_instances = json.assay_instances;
        var sample_locations = json.sample_locations;

        for (var i in data_points) {
            var data_point = data_points[i];

            var chip_id = data_point.chip_id;

            var assay_plate_id = data_point.assay_plate_id;
            var assay_well_id = data_point.assay_well_id;

            var day = Math.floor(data_point.day);
            var hour = Math.floor(data_point.hour);
            var minute = Math.floor(data_point.minute);

            // Just convert to day for now
            var time_in_minutes = data_point.time_in_minutes;
            var time_in_days = time_in_minutes / 1440.0;

            var assay_instance_id = data_point.assay_instance_id;
            var target_name = assay_instances[assay_instance_id].target_name;
            var method_name = assay_instances[assay_instance_id].method_name;

            var sample_location_id = data_point.sample_location_id;
            var sample_location_name = sample_locations[sample_location_id].name;

            var value = data_point.value;
            var value_unit = assay_instances[assay_instance_id].unit;

            var caution_flag = data_point.caution_flag;
            var quality = data_point.quality;

            var notes = data_point.notes;
            var replicate = data_point.replicate;
            var update_number = data_point.update_number;

            var data_upload_url = data_point.data_upload_url;
            var data_upload_name = data_point.data_upload_name;

            // If there is an R, continue
            if (quality.indexOf('R') > -1) {
                continue;
            }

            // Add update_number to notes if this is an update (i.e. update_number > 0)
            // if (update_number && update_number != 0) {
            //     notes += '\nUpdate #' + update_number;
            // }

            // Add replicate to notes if replicate is specified
            // if (replicate) {
            //     notes += '\nReplicate ' + replicate;
            // }

            var index = {
                // Chip ID added for future proofing (maybe we will have study-wide changes to quality)
                'chip_id': chip_id,
                'assay_plate_id': assay_plate_id,
                'assay_well_id': assay_well_id,
                'assay_instance_id': assay_instance_id,
                'sample_location_id': sample_location_id,
                'time': time_in_minutes,
                // 'value_unit': value_unit,
                'replicate': replicate,
                'update_number': update_number
            };

            index = JSON.stringify(index);

            var new_row = $('<tr>');
            //     .attr('data-chart-index', index);

            // Need to take a slice to avoid treating missing QC as invalid
            // Allow QC changes for NULL value row
            var every = [chip_id, time_in_minutes, assay_instance_id, sample_location_id].every(is_true);

            if (exist) {
                new_row.addClass('bg-success');
            }

            else {
                new_row.addClass('new-value');
            }

            if (!exist && !every) {
                new_row.addClass('bg-danger');
            }

            else if (value === null || value === '') {
                new_row.css('background', '#606060');
            }

            else if (quality) {
                new_row.addClass('bg-danger');
            }

            else if (caution_flag) {
                new_row.addClass('bg-warning');
            }

            var col_chip_id = $('<td>').text(chip_id);

            var col_time = $('<td>').text('D' + day + ' H' + hour + ' M' + minute);

            var col_target = $('<td>').text(target_name);
            var col_method = $('<td>').text(method_name);
            var col_sample_location = $('<td>').text(sample_location_name);
            var col_value = $('<td>').text(value ? data_format(value) : value);
            var col_value_unit = $('<td>').text(value_unit);

            var col_caution_flag = $('<td>').text(caution_flag);

            var col_quality = $('<td>');

            var quality_box = $('<input>')
                .attr('type', 'checkbox')
                // .attr('id', i)
                .css('width', 50)
                .addClass('quality');

            var quality_input = $('<input>')
                .css('visibility', 'hidden')
                .attr('name', index)
                .addClass('quality-input');

            if (quality) {
                quality_box.prop('checked', true);
                quality_input.val(quality);
            }

            if (exist || every) {
                col_quality.append(
                    quality_box,
                    quality_input
                );
            }

            var col_notes = $('<td>').text(notes);
            // var col_notes = $('<td>');
            // if (notes) {
            //     col_notes.append(
            //         $('<span>')
            //             .addClass('glyphicon glyphicon-info-sign')
            //             .attr('title', notes)
            //     );
            // }

            var col_data_upload = $('<td>').append(
                $('<a>')
                    .text(data_upload_name)
                    .attr('href', data_upload_url)
            );

            new_row.append(
                col_chip_id,
                col_time,
                col_target,
                col_method,
                col_sample_location,
                col_value,
                col_value_unit,
                col_caution_flag
            );

            // Technically a magic value SUBJECT TO CHANGE
            // Finds if there is a column to put exclude into
            if ($('#id_exclude_header')[0]) {
                new_row.append(col_quality)
            }

            new_row.append(
                col_notes,
                col_data_upload
            );

            // If there is an X, hide and mark
            if (quality.indexOf('X') > -1) {
                new_row.addClass('initially-excluded')
            }

            table_body.prepend(new_row);
        }

        // Refresh exclusions
        toggle_excluded();

        var all_qualities = null;

        if (exist) {
            all_qualities = $('.quality');
        }
        else {
            all_qualities = $('.new-value').find('.quality');
        }

        // Bind change event to quality
        all_qualities.change(function() {
            var current_value = $(this).prop('checked');
            var current_row = $(this).parent().parent();
            var current_input = $(this).parent().find('.quality-input');

            // Make sure that the value is empty string rather than boolean
            if (!current_value) {
                current_value = '';
                current_input.val('');
            }
            else {
                current_input.val('X');
            }

            var index = JSON.parse(current_input.attr('name'));
            index = [
                index.chip_id,
                index.assay_plate_id,
                index.assay_well_id,
                ''+index.assay_instance_id,
                ''+index.sample_location_id,
                ''+index.time,
                index.replicate,
                ''+index.update_number
            ];

            var joined_index = index.join('~');

            // Change color of parent if there is input
            if (current_value) {
                current_row.addClass('bg-danger');
                current_row.removeClass('unexcluded');
            }
            else if (!current_value && current_row.hasClass('initially-excluded')) {
                current_row.addClass('bg-info');
                current_row.addClass('unexcluded');
                current_row.removeClass('bg-success bg-danger');
            }
            else {
                current_row.removeClass('bg-danger');
            }

            if (exist) {
                dynamic_quality_current[joined_index] = current_value;
            }
            else {
                dynamic_quality_new[joined_index] = current_value;
            }

            // Validate again if there is a file
            // Only affects charts
            refresh_chart_only();
        });
    };

    function plot_existing_data() {
        var dynamic_quality = $.extend({}, dynamic_quality_current, dynamic_quality_new);

        var data = {
            call: 'fetch_readouts',
            study: study_id,
            readout: readout_id,
            csrfmiddlewaretoken: middleware_token,
            dynamic_quality: JSON.stringify(dynamic_quality)
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: data,
            success: function (json) {
                window.CHARTS.prepare_charts_by_table(json, charts_name);
                window.CHARTS.make_charts(json, charts_name, changes_to_chart_options);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    var refresh_table_and_charts = function() {
        if ($('#id_file')[0] && $('#id_file')[0].files[0]) {
            // resetChart();
            validate_readout_file('True');
            // getText(file);
        }
        else {
            plot_existing_data();
        }

        toggle_excluded();
    };

    var refresh_chart_only = function() {
        if ($('#id_file')[0] && $('#id_file')[0].files[0]) {
            // resetChart();
            validate_readout_file('');
            // getText(file);
        }
        else {
            plot_existing_data();
        }

        toggle_excluded();
    };

    function toggle_excluded() {
        // Stop gap: magic string
        var include_all = $('#chartsinclude_all').prop('checked');

        if (include_all) {
            $('.initially-excluded').show();
        }
        else {
            $('.initially-excluded').hide();
        }

        // Show initially-excluded items that have had their exclusion removed
        $('.unexcluded').show();
    }

    // Refresh on file change
    $('#id_file').change(function(evt) {
        refresh_table_and_charts();
    });

    // Refresh on change in overwrite option NEED REPLCATE TO BE ACCURATE
    $('#id_overwrite_option').change(function() {
        refresh_table_and_charts();
    });

    // Datepicker superfluous on admin, use this check to apply only in frontend
    if ($('#fluid-content')[0]) {
        // Setup date picker
        var date = $("#id_readout_start_time");
        var curr_date = date.val();
        date.datepicker();
        date.datepicker("option", "dateFormat", "yy-mm-dd");
        date.datepicker("setDate", curr_date);
    }

    // Setup triggers
    $('#' + charts_name + 'chart_options').find('input').change(function() {
        refresh_chart_only();
    });
});
