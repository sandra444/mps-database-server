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
    var quality_indicators = [];
    $.ajax({
        url: "/assays_ajax/",
        type: "POST",
        dataType: "json",
        data: {
            call: 'fetch_quality_indicators',
            csrfmiddlewaretoken: middleware_token
        },
        success: function (json) {
            quality_indicators = json;
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });

    // Tracks the quality of data to indicate whether to exclude or include in plots
    var dynamic_quality_current = {};
    var dynamic_quality_new = {};

    var readout_id = get_readout_value();
    var study_id = get_study_id();

    // Name for the charts for binding events etc
    var charts_name = 'charts';

    // Indicates whether the data exists in the database or not
    var exist = false;

    var changes_to_chart_options = {
        chartArea: {
            // Slight change in width
            width: '78%',
            height: '65%'
        }
    };

    function is_true(element, index, array) {
        if (!element) {
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
            return Math.floor(window.location.href.split('/')[5]);
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
                    process_data(json);
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
                    if (include_table) {
                       process_data(json.table);
                    }
                    window.CHARTS.prepare_charts_by_table(json.charts, charts_name);
                    window.CHARTS.make_charts(json.charts, charts_name, changes_to_chart_options);
                }
            },
            error: function (xhr, errmsg, err) {
                alert('An unknown error has occurred.');
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

    var process_data = function (json) {
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

            var quality = data_point.quality;
            var notes = data_point.notes;
            var replicate = data_point.replicate;
            var update_number = data_point.update_number;

            // Add update_number to notes if this is an update (i.e. update_number > 0)
            if (update_number && update_number != 0) {
                notes += '\nUpdate #' + update_number;
            }

            // Add replicate to notes if this is a replicate (i.e. replicate > 0)
            if (replicate && replicate != 0) {
                notes += '\nReplicate ' + update_number;
            }

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
            var every = [chip_id, time_in_minutes, assay_instance_id, sample_location_id, value].every(is_true);

            if (exist) {
                new_row.addClass('bg-success');
            }

            else {
                new_row.addClass('new-value');
            }

            if (!exist && !every) {
                new_row.addClass('bg-danger');
            }

            else if (value === null) {
                new_row.css('background', '#606060');
            }

            else if (quality) {
                new_row.addClass('bg-warning');
            }

            var col_chip_id = $('<td>').text(chip_id);

            var col_time = $('<td>').text('D' + day + ' H' + hour + ' M' + minute);

            var col_target = $('<td>').text(target_name);
            var col_method = $('<td>').text(method_name);
            var col_sample_location = $('<td>').text(sample_location_name);
            var col_value = $('<td>').text(value ? data_format(value) : value);
            var col_value_unit = $('<td>').text(value_unit);

            var col_quality = $('<td>');

            var quality_input = $('<input>')
                .attr('name', index)
                // .attr('id', i)
                .css('width', 50)
                .addClass('text-danger quality')
                .val(quality);

            if (exist || every) {
                col_quality.append(quality_input);
            }

            var col_notes = $('<td>');
            if (notes) {
                col_notes.append(
                    $('<span>')
                        .addClass('glyphicon glyphicon-info-sign')
                        .attr('title', notes)
                );
            }

            new_row.append(
                col_chip_id,
                col_time,
                col_target,
                col_method,
                col_sample_location,
                col_value,
                col_value_unit,
                col_quality,
                col_notes
            );
            table_body.prepend(new_row);
        }

        var all_qualities = null;

        if (exist) {
            all_qualities = $('.quality');
        }
        else {
            all_qualities = $('.new-value').find('.quality');
        }

        // Bind click event to quality
        all_qualities.click(function() {
            // Remove other tables to avoid quirk when jumping from quality to quality
            $('.quality-indicator-table').remove();

            var current_quality = $(this);

            var table_container = $('<div>')
                .css('width', '180px')
                .css('background-color', '#FDFEFD')
                .addClass('quality-indicator-table');

            var indicator_table = $('<table>')
                .css('width', '100%')
                .attr('align', 'center')
                .addClass('table table-striped table-bordered table-hover table-condensed');

            $.each(quality_indicators, function(index, indicator) {
                var prechecked = false;

                // ASSUMES SINGLE CHARACTER CODES
                if (current_quality.val().indexOf(indicator.code) > -1) {
                    prechecked = true;
                }

                var new_row = $('<tr>');
                var name = $('<td>').text(indicator.name + ' ');

                // Add the description
                name.append(
                    $('<span>')
                        .addClass('glyphicon glyphicon-question-sign')
                        .attr('title', indicator.description)
                );

                var code = $('<td>')
                    .text(indicator.code)
                    .addClass('lead');

                var select = $('<td>')
                    .append($('<input>')
                        .attr('type', 'checkbox')
                        .val(indicator.code)
                        .prop('checked', prechecked)
                        .addClass('quality-indicator')
                        .click(function() {
                            var current_quality_value = current_quality.val();

                            // If it is being checked
                            if ($(this).prop('checked') == true) {
                                if (current_quality_value.indexOf($(this).val()) < 0) {
                                    current_quality.val(current_quality_value + $(this).val());
                                }
                            }
                            else {
                                // Otherwise get rid of flag
                                current_quality.val(current_quality_value.replace($(this).val(), ''));
                            }

                            current_quality.focus();
                            current_quality.trigger('change');
                        }));
                new_row.append(name, code, select);
                indicator_table.append(new_row);
            });

            table_container.append(indicator_table);

            $('body').append(table_container);

            table_container.position({
              of: current_quality,
              my: 'left-125 top',
              at: 'left bottom'
            });
        });

        // Bind unfocus event to qualities
        all_qualities.focusout(function(event) {
            var related_target = $(event.relatedTarget);
            // Remove any quality indicator tables if not quality-indicator-table or quality
            if (!related_target.hasClass('quality-indicator')) {
                $('.quality-indicator-table').remove();
            }
        });

        // Bind change event to quality
        all_qualities.change(function() {
            // Change color of parent if there is input
            if (this.value) {
                $(this).parent().parent().addClass('bg-warning');
            }
            else {
                $(this).parent().parent().removeClass('bg-warning');
            }
            var index = JSON.parse(this.name);
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

            if (exist) {
                dynamic_quality_current[joined_index] = this.value;
            }
            else {
                dynamic_quality_new[joined_index] = this.value;
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
        var file = $('#id_file')[0].files[0];
        if (file) {
            // resetChart();
            validate_readout_file('True');
            // getText(file);
        }
        else {
            plot_existing_data();
        }
    };

    var refresh_chart_only = function() {
        var file = $('#id_file')[0].files[0];
        if (file) {
            // resetChart();
            validate_readout_file('');
            // getText(file);
        }
        else {
            plot_existing_data();
        }
    };

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
