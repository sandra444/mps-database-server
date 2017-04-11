$(document).ready(function () {
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

    // The data in question as a Sample Location pairing 'time|time_unit|assay|sample_location|value_unit|replicate
    // var data = {};

    // Tracks the quality of data to indicate whether to exclude or include in plots
    var dynamic_quality_current = {};
    var dynamic_quality_new = {};

    var readout_id = get_readout_value();

    // Indicates whether the data exists in the database or not
    var exist = false;

    // Deprecated
    // var headers = 0;
    //
    // if ($('#id_headers')[0]) {
    //     headers = Math.floor($('#id_headers').val());
    // }

    // var charts = [];

    // Load the Visualization API and the corechart package.
    google.charts.load('current', {'packages':['corechart']});

    // Set a callback to run when the Google Visualization API is loaded.
    google.charts.setOnLoadCallback(get_readout);

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

    // function addChart(id, name, timeUnits, valueUnits) {
    //     $('<div>')
    //         .attr('id', 'chart' + id)
    //         .attr('align', 'right')
    //         .addClass('chart-container single-chip-chart')
    //         .appendTo('#extra');
    //
    //     charts.push(
    //         c3.generate({
    //             bindto: '#chart'+id,
    //
    //             data: {
    //                 columns: []
    //             },
    //             axis: {
    //                 x: {
    //                     label: {
    //                         text: 'Time (' + timeUnits + ')',
    //                         position: 'outer-center'
    //                     }
    //                 },
    //                 y: {
    //                     label: {
    //                         text: valueUnits,
    //                         position: 'outer-middle'
    //                     },
    //                     tick: {
    //                         format: data_format
    //                     }
    //                 }
    //             },
    //             title: {
    //                 text: name
    //             },
    //             tooltip: {
    //                 format: {
    //                     value: function (value, ratio, id) {
    //                         var format = value % 1 === 0 ? d3.format(',d') : d3.format(',.2f');
    //                         return format(value);
    //                     }
    //                 }
    //             },
    //             padding: {
    //                 right: 10
    //             },
    //             // TODO this is not optimal
    //             // manually reposition axis label
    //             onrendered: function() {
    //                 $('.c3-axis-x-label').attr('dy', '35px');
    //             }
    //         })
    //     );
    // }
    //
    // function resetChart() {
    //     for (var i in charts) {
    //         $('#chart'+i).remove();
    //     }
    //     charts = [];
    // }

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
        var serializedData = $('form').serializeArray();
        var formData = new FormData();
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        formData.append('file', $('#id_file')[0].files[0]);
        if (readout_id) {
            formData.append('readout', readout_id);
        }
        else {
            formData.append('study', Math.floor(window.location.href.split('/')[4]));
        }
        formData.append('include_table', include_table);
        formData.append('dynamic_quality', JSON.stringify(dynamic_quality));
        formData.append('call', 'validate_individual_chip_file');
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
                    make_charts(json.charts, 'charts');
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

    // var getText = function (readFile) {
    //     var reader = new FileReader();
    //     reader.readAsText(readFile, "UTF-8");
    //     reader.onload = loaded;
    // };
    //
    // var loaded = function (evt) {
    //     var fileString = evt.target.result;
    //     exist = false;
    //     parseAndReplace(fileString);
    // };

    // function get_index_for_value(chip_id, sample_location_id, time, assay_instance_id, replicate, update_number) {
    //     var full_index = {
    //         // Chip ID added for future proofing (maybe we will have study-wide changes to quality)
    //         'chip_id': chip_id,
    //         'sample_location_id': sample_location_id,
    //         'time': time,
    //         'assay_instance_id': assay_instance_id,
    //         // 'value_unit': value_unit,
    //         'replicate': replicate,
    //         'update_number': update_number
    //     };
    //
    //     return JSON.stringify(full_index);
    // }

    var process_data = function (json) {
        var table_body = $('#table_body');

        // Do not empty entire table, only delete new values
        // table_body.empty();
        clear_new_data();

        if (!json) {
            return;
        }

        // Check if headers exists (it doesn't in detail)
        // if ($('#id_headers')[0]) {
        //     // Update headers
        //     headers = Math.floor($('#id_headers').val());
        // }

        // Crash if the first time is not numeric
        // if (isNaN(headers)) {
        //     alert("Please make sure you choose a valid number for number of header rows.");
        //     return;
        // }

        // var lines = parse_csv(csv);

        // If this is in the database
//        if(exist) {
//            table_body.addClass('bg-success');
//        }
//        else {
//            table_body.removeClass('bg-success')
//        }

        // table += exist ? "<tr class='bg-info'>" + header + "</tr>" : "";
        // table += "<tr class='bg-info'>" + header + "</tr>";

        // Current index for saving QC values
        var current_index = 0;

        // var table = '';

        var data_points = json.data_points;
        var assay_instances = json.assay_instances;
        var sample_locations = json.sample_locations;

        for (var i in data_points) {
            // Based on csv method, using JSON now
            // var line = lines[i];
            //
            // var chip_id = line[0];
            //
            // var assay_plate_id = line[1];
            // var assay_well_id = line[2];
            //
            // var day = Math.floor(line[3]);
            // var hour = Math.floor(line[4]);
            // var minute = Math.floor(line[5]);
            //
            // // Just convert to day for now
            // var time = day + hour / 24 + minute / 1440;
            //
            // var target = line[6];
            // var method = line[7];
            //
            // // var time = line[1];
            // // var time_unit = line[2];
            // // var assay = line[3];
            // var sample_location = line[8];
            // var value = line[9];
            // var value_unit = line[10];
            //
            // var quality = $.trim(line[11]);
            // var notes = $.trim(line[12]);
            // var replicate = $.trim(line[13]);
            // var update_number = $.trim(line[14]);

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

            // Index in data
            // TODO FIX!
            // var index = get_index_for_value(
            //     chip_id,
            //     sample_location_id,
            //     time_in_minutes,
            //     assay_instance_id,
            //     replicate,
            //     update_number
            // );
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

            // var col_assay_plate_id = $('<td>').text(assay_plate_id);
            // var col_assay_well_id = $('<td>').text(assay_well_id);

            // var col_day = $('<td>').text(day);
            // var col_hour = $('<td>').text(hour);
            // var col_minute = $('<td>').text(minute);
            var col_time = $('<td>').text('D' + day + ' H' + hour + ' M' + minute);

            var col_target = $('<td>').text(target_name);
            var col_method = $('<td>').text(method_name);
            // var col_time = $('<td>').text(time);
            // var col_time_unit = $('<td>').text(time_unit);
            // var col_assay = $('<td>').text(assay);
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
                // col_assay_plate_id,
                // col_assay_well_id,
                col_time,
                // col_day,
                // col_hour,
                // col_minute,
                col_target,
                col_method,
                // col_time,
                // col_time_unit,
                // col_assay,
                col_sample_location,
                col_value,
                col_value_unit,
                col_quality,
                col_notes
            );
            table_body.append(new_row);
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
            // dynamic_quality[joined_index] = this.value;

            // console.log(dynamic_quality);

            // data[index]['quality'] = this.value;
            // plot();

            // Validate again if there is a file
            if ($('#id_file').val()) {
                validate_readout_file('');
            }
            else {
                plot_existing_data();
            }
        });

        // TODO FIX PLOT
        // plot();
    };

    function plot_existing_data() {
        var dynamic_quality = $.extend({}, dynamic_quality_current, dynamic_quality_new);
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readouts',
                readout: readout_id,
                // study: study_id,
                // TODO CONTRIVED, DEVICE FOR NOW
                key: 'device',
                dynamic_quality: JSON.stringify(dynamic_quality),
                // Tells whether to convert to percent Control
                // percent_control: percent_control,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                make_charts(json, 'charts');
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // TODO Copy-pasting is irresponsible, please refrain from doing so in the future
    function make_charts(json, charts) {
        // Clear existing charts
        var charts_id = $('#' + charts);
        charts_id.empty();

//        var assay_to_id = {};
//        var assay_ids = {};

        // Show radio_buttons if there is data
        // if (Object.keys(json).length > 0) {
        //     radio_buttons_display.show();
        // }

        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        var previous = null;
        for (var index in sorted_assays) {
            // var assay_unit = sorted_assays[index];

            // var current_chart_id = assay_unit.replace(/\W/g,'_');

//            if (!assay_ids[assay_id]) {
//                assay_ids[assay_id] = true;
//                assay_to_id[assay] = assay_id;
//            }
//            else {
//                var assay_number = 2;
//
//                while (assay_ids[assay_id + '_' + assay_number]) {
//                    assay_number += 1;
//                }
//
//                assay_id = assay_id + '_' + assay_number;
//
//                assay_ids[assay_id] = true;
//                assay_to_id[assay] = assay_id;
//            }

            $('<div>')
                .attr('id', charts + '_' + index)
                .attr('align', 'right')
                .addClass('chart-container')
                .appendTo('#charts');
        }

        for (index in sorted_assays) {
            var assay_unit = sorted_assays[index];
            var assay = assay_unit.split('\n')[0];
            var unit = assay_unit.split('\n')[1];
            var current_chart_id = assay_unit.replace(/\W/g, '_');
            // var add_to_bar_charts = true;

            // var data = google.visualization.arrayToDataTable([
            //     ['Year', 'Sales', 'Expenses'],
            //     ['2004', 1000, 400],
            //     ['2005', 1170, 460],
            //     ['2006', 660, 1120],
            //     ['2007', 1030, 540]
            // ]);

            var data = google.visualization.arrayToDataTable(assays[index]);

            var options = {
                title: assay,
                titleTextStyle: {
                    fontSize: 18,
                    bold: true,
                    underline: true
                },
                // curveType: 'function',
                legend: {
                    position: 'top',
                    maxLines: 5,
                    textStyle: {
                        // fontSize: 8,
                        bold: true
                    }
                },
                hAxis: {
                    title: 'Time (Days)',
                    textStyle: {bold: true},
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    }
                    // baselineColor: 'none',
                    // ticks: []
                },
                vAxis: {
                    title: unit,
                    format: 'short',
                    textStyle: {bold: true},
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    }
                    // baselineColor: 'none',
                    // ticks: []
                },
                pointSize: 5,
                chartArea: {
                    // Slight change in width
                    width: '78%',
                    height: '65%'
                },
                height:400,
                focusTarget: 'category',
                intervals: { style: 'bars' }
            };

            // Find out whether to shrink text
            $.each(assays[index][0], function(index, column_header) {
                if (column_header.length > 12) {
                    options.legend.textStyle.fontSize = 8;
                }
            });

            var chart = null;

            if (assays[index].length > 4) {
                chart = new google.visualization.LineChart(document.getElementById(charts + '_' + index));
            }
            else if (assays[index].length > 1) {
                // Convert to categories
                data.insertColumn(0, 'string', data.getColumnLabel(0));
                // copy values from column 1 (old column 0) to column 0, converted to numbers
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    var val = data.getValue(i, 1);
                    if (val != null) {
                        data.setValue(i, 0, val + ''.valueOf());
                    }
                }
                // remove column 1 (the old column 0)
                data.removeColumn(1);

                chart = new google.visualization.ColumnChart(document.getElementById(charts + '_' + index));
            }

            if (chart) {
                var dataView = new google.visualization.DataView(data);

                // Change interval columns to intervals
                var interval_setter = [0];

                i = 1;
                while (i < data.getNumberOfColumns()) {
                    interval_setter.push(i);
                    if (i+2 < data.getNumberOfColumns() && assays[index][0][i+1].indexOf('_i1') > -1) {
                        interval_setter.push({sourceColumn: i + 1, role: 'interval'});
                        interval_setter.push({sourceColumn: i + 2, role: 'interval'});
                        i += 2;
                    }
                    i += 1;
                }
                dataView.setColumns(interval_setter);

                chart.draw(dataView, options);
            }
        }
    }

//     function plot() {
//         //Make chart
//         var assays = {};
//         // var valueUnits = {};
//         var timeUnits = {};
//
//         for (var i in data) {
//             var line = data[i];
//
//             // This is done before hand now
//             // Need to take a slice to avoid treating missing QC as invalid
// //            var every = line.slice(0,7).every(is_true);
// //
// //            // if (!every || (i < headers && !exist)) {
// //            if (!every && !exist) {
// //                continue;
// //            }
//
//             var time = line['time'];
//             var time_unit = 'days';
//             var assay = line['target'];
//             var sample_location = line['sample_location'];
//             var value = line['value'];
//             var value_unit = line['value_unit'];
//
//             var quality = $.trim(line['quality']);
//
//             // Crash if the time is not numeric
//             if (isNaN(time)) {
//                 alert("Improperly Configured: Please check the number of header rows selected and also make sure all times are numeric.");
//                 return;
//             }
//
//             if (!quality) {
//                 if (!assays[assay]) {
//                     assays[assay] = {};
//                 }
//
//                 if (!assays[assay][value_unit]) {
//                     assays[assay][value_unit] = {};
//                 }
//
//                 if (sample_location && sample_location != 'None' && !assays[assay][value_unit][sample_location]) {
//                     assays[assay][value_unit][sample_location] = {'time': [], 'data': []};
//                 }
//
//                 if (assays[assay][value_unit][sample_location] && value && value != 'None') {
//                     assays[assay][value_unit][sample_location].time.push(time);
//                     assays[assay][value_unit][sample_location].data.push(value);
//
//                     // valueUnits[assay] = value_unit;
//                     timeUnits[assay] = time_unit;
//                 }
//             }
//         }
//
//         var chart = 0;
//         var bar_chart_list = [];
//
//         for (var assay in assays) {
//             for (var value_unit in assays[assay]) {
//                 var add_to_bar_charts = true;
//
//                 addChart(chart, assay, timeUnits[assay], value_unit);
//
//                 var xs = {};
//                 var num = 1;
//
//                 for (var sample_location in assays[assay][value_unit]) {
//                     sample_location = '' + sample_location;
//
//                     // Add to bar charts if no time scale exceeds 3 points
//                     if (add_to_bar_charts && assays[assay][value_unit][sample_location].time.length > 3) {
//                         add_to_bar_charts = false;
//                     }
//
//                     xs[sample_location] = 'x' + num;
//
//                     assays[assay][value_unit][sample_location].data.unshift(sample_location);
//                     assays[assay][value_unit][sample_location].time.unshift('x' + num);
//
//                     //Load for correct assay chart
//                     charts[chart].load({
//                         xs: xs,
//
//                         columns: [
//                             assays[assay][value_unit][sample_location].data,
//                             assays[assay][value_unit][sample_location].time
//                         ]
//                     });
//
//                     num += 1;
//                 }
//                 // Add to bar charts if no time scale exceeds 3 points
//                 if (add_to_bar_charts) {
//                     bar_chart_list.push(chart);
//                 }
//
//                 chart += 1;
//             }
//         }
//
//         // Make bar charts
//         for (var index in bar_chart_list) {
//             var chart_index = bar_chart_list[index];
//             charts[chart_index].transform('bar');
//         }
//     }

    var refresh = function() {
        var file = $('#id_file')[0].files[0];
        if (file) {
            // resetChart();
            validate_readout_file('True');
            // getText(file);
        }
    };

    // if (readout_id) {
    //     get_readout();
    // }

    // Refresh on file change
    $('#id_file').change(function(evt) {
        refresh();
    });

    // Refresh on change in overwrite option NEED REPLCATE TO BE ACCURATE
    $('#id_overwrite_option').change(function() {
        refresh();
    });

    // if ($('#id_headers')[0]) {
    //     $('#id_headers').change(function (evt) {
    //         if ($('#id_file')[0].files[0]) {
    //             refresh();
    //         }
    //     });
    // }

    // Datepicker superfluous on admin, use this check to apply only in frontend
    if ($('#fluid-content')[0]) {
        // Setup date picker
        var date = $("#id_readout_start_time");
        var curr_date = date.val();
        date.datepicker();
        date.datepicker("option", "dateFormat", "yy-mm-dd");
        date.datepicker("setDate", curr_date);
    }
});
