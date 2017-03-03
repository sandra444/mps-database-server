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
    var data = {};

    var readout_id = getReadoutValue();

    // Indicates whether the data exists in the database or not
    var exist = false;

    var headers = 0;

    if ($('#id_headers')[0]) {
        headers = Math.floor($('#id_headers').val());
    }

    var charts = [];

    function isTrue(element, index, array) {
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
        else if (value % 1 === 0){
            format = d3.format(',d');
        }
        return format(value);
    }

    function addChart(id, name, timeUnits, valueUnits) {
        $('<div>')
            .attr('id', 'chart' + id)
            .attr('align', 'right')
            .addClass('chart-container single-chip-chart')
            .appendTo('#extra');

        charts.push(
            c3.generate({
                bindto: '#chart'+id,

                data: {
                    columns: []
                },
                axis: {
                    x: {
                        label: {
                            text: 'Time (' + timeUnits + ')',
                            position: 'outer-center'
                        }
                    },
                    y: {
                        label: {
                            text: valueUnits,
                            position: 'outer-middle'
                        },
                        tick: {
                            format: data_format
                        }
                    }
                },
                title: {
                    text: name
                },
                tooltip: {
                    format: {
                        value: function (value, ratio, id) {
                            var format = value % 1 === 0 ? d3.format(',d') : d3.format(',.2f');
                            return format(value);
                        }
                    }
                },
                padding: {
                    right: 10
                },
                // TODO this is not optimal
                // manually reposition axis label
                onrendered: function() {
                    $('.c3-axis-x-label').attr('dy', '35px');
                }
            })
        );
    }

    function resetChart() {
        for (var i in charts) {
            $('#chart'+i).remove();
        }
        charts = [];
    }

    function getReadoutValue() {
        // Admin (check by looking for content-main ID)
        if($('#content-main')[0]) {
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

    function getReadout() {
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
                parseAndReplace(json.csv);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function clear_new_data() {
        $('.new-value').each(function() {
            // Delete this value from data
            delete data[$(this).attr('data-chart-index')];
            // Remove the row itself
            $(this).remove();
        });
    }

    function validate_readout_file() {
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
                    plot();
                }
                else {
                    exist = false;
                    alert('Success! Please see "New Chip Data" below for preview.');
                    resetChart();
                    parseAndReplace(json.csv);
                }
            },
            error: function (xhr, errmsg, err) {
                alert('An unknown error has occurred.');
                console.log(xhr.status + ": " + xhr.responseText);
                // Remove file selection
                $('#id_file').val('');
                // $('#table_body').empty();
                clear_new_data();
                plot();
            }
        });
    }

    var getText = function (readFile) {
        var reader = new FileReader();
        reader.readAsText(readFile, "UTF-8");
        reader.onload = loaded;
    };

    var loaded = function (evt) {
        var fileString = evt.target.result;
        exist = false;
        parseAndReplace(fileString);
    };

    function get_index_for_value(field, time, assay, value_unit, update_number) {
        var full_index = {
            'field': field,
            'time': time,
            'assay': assay,
            'value_unit': value_unit,
            'update_number': update_number
        };

        return JSON.stringify(full_index);
    }

    var parseAndReplace = function (csv) {
        var table_body = $('#table_body');

        // Do not empty entire table, only delete new values
        // table_body.empty();
        clear_new_data();

        if (!csv) {
            return;
        }

        // Check if headers exists (it doesn't in detail)
        if ($('#id_headers')[0]) {
            // Update headers
            headers = Math.floor($('#id_headers').val());
        }

        // Crash if the first time is not numeric
        if (isNaN(headers)) {
            alert("Please make sure you choose a valid number for number of header rows.");
            return;
        }

        var lines = parse_csv(csv);

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

        for (var i in lines) {
            var line = lines[i];

            var chip_id = line[0];
            var time = line[1];
            var time_unit = line[2];
            var assay = line[3];
            var sample_location = line[4];
            var value = line[5];
            var value_unit = line[6];

            var quality = $.trim(line[7]);
            var notes = $.trim(line[8]);
            var update_number = $.trim(line[9]);

            // Add update_number to notes if this is a replicate (i.e. update_number > 0)
            if (update_number && update_number != 0) {
                notes += '\nUpdate #' + update_number;
            }

            // Index in data
            var index = get_index_for_value(sample_location, time, assay, value_unit, update_number);

            // Notice attribute to assist in deleting old data
            var new_row = $('<tr>')
                .attr('data-chart-index', index);

            // Need to take a slice to avoid treating missing QC as invalid
            var every = line.slice(0,5).every(isTrue) && isTrue(line[6]) && isTrue(line[9]);

            if (exist) {
                new_row.addClass('bg-success');
            }

            else {
                new_row.addClass('new-value');
            }

            if (!exist && !every) {
                new_row.addClass('bg-danger');
            }

            else if (value == 'None' || !value) {
                new_row.css('background', '#606060');
            }

            else if (line[7] && $.trim(line[7])) {
                new_row.addClass('bg-warning');
            }

            var col_chip_id = $('<td>').text(chip_id);
            var col_time = $('<td>').text(time);
            var col_time_unit = $('<td>').text(time_unit);
            var col_assay = $('<td>').text(assay);
            var col_sample_location = $('<td>').text(sample_location);
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
                col_time_unit,
                col_assay,
                col_sample_location,
                col_value,
                col_value_unit,
                col_quality,
                col_notes
            );
            table_body.append(new_row);
//            // If the row will be excluded (highlighted red)
//            // if ((i < headers && !exist) || !every) {
//            if (!exist && !every) {
//                table += "<tr class='bg-danger'>";
//            }
//
//            // If the row has no value (residue code, may be used later)
//            else if (value === 'None' || value === '') {
//                table += "<tr style='background: #606060'>";
//            }
//
//            // If the row is marked an outlier
//            else if (line[7] && $.trim(line[7])) {
//                table += "<tr class='bg-warning'>";
//            }
//
//            else {
//                table += "<tr>";
//            }
//
//            // DO NOT ADD COMMAS TO CHIP ID
//            if (chip_id) {
//                table += "<td>" + chip_id + "</td>";
//            }
//
//            table += "<td>" + data_format(line[1]) + "</td>";
//
//            for (var j=2; j<5; j++) {
//                if (line[j]) {
//                    table += "<td>" + line[j] + "</td>";
//                }
//                else {
//                    table += "<td></td>";
//                }
//            }
//
//            if(value === 'None' || value === '') {
//                table += "<td></td>";
//            }
//            else {
//                table += "<td>" + data_format(line[5]) + "</td>";
//            }
//
//            table += "<td>" + line[6] + "</td>";
//
//            // Just add text if this is a header row for QC OR if this row is invalid
//            // (QC status of an ignored row does not really matter)
//            // if (i < headers && !exist || !every) {
//            if (!exist && !every) {
//                if (quality) {
//                    table += "<td>" + quality + "</td>";
//                }
//                else {
//                    table += "<td></td>";
//                }
//            }
//            // Add an input for the QC if this isn't a header
//            // QC inputs NAME begin with "QC_"
//            // QC input IDS are the row index (for plotting accurately)
//            else {
//                index = get_index_for_value(sample_location, time, assay, value_unit, update_number);
//                table += "<td><input size='5' class='quality text-danger' id='" + i + "' name='" + index + "' value='" + quality + "'></td>";
//                // Increment the current index
//                current_index += 1;
//            }
//
//            // Add notes
//            if (notes) {
//                table += '<td><span class="glyphicon glyphicon-info-sign" title="' + notes + '"></span></td>';
//            }
//            else {
//                table += "<td></td>";
//            }
//
//            table += "</tr>";

            // Add to data if index
            if (index) {
                data[index] = line;
            }
        }

        var all_qualities = $('.quality');

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
            var index = this.name;
            data[index][7] = this.value;
            resetChart();
            plot();
        });

        plot();
    };

    function plot() {
        //Make chart
        var assays = {};
        // var valueUnits = {};
        var timeUnits = {};

        for (var i in data) {
            var line = data[i];

            // This is done before hand now
            // Need to take a slice to avoid treating missing QC as invalid
//            var every = line.slice(0,7).every(isTrue);
//
//            // if (!every || (i < headers && !exist)) {
//            if (!every && !exist) {
//                continue;
//            }

            var time = line[1];
            var time_unit = line[2];
            var assay = line[3];
            var sample_location = line[4];
            var value = line[5];
            var value_unit = line[6];

            var quality = $.trim(line[7]);

            // Crash if the time is not numeric
            if (isNaN(time)) {
                alert("Improperly Configured: Please check the number of header rows selected and also make sure all times are numeric.");
                return;
            }

            if (!quality) {
                if (!assays[assay]) {
                    assays[assay] = {};
                }

                if (!assays[assay][value_unit]) {
                    assays[assay][value_unit] = {};
                }

                if (sample_location && sample_location != 'None' && !assays[assay][value_unit][sample_location]) {
                    assays[assay][value_unit][sample_location] = {'time': [], 'data': []};
                }

                if (assays[assay][value_unit][sample_location] && value && value != 'None') {
                    assays[assay][value_unit][sample_location].time.push(time);
                    assays[assay][value_unit][sample_location].data.push(value);

                    // valueUnits[assay] = value_unit;
                    timeUnits[assay] = time_unit;
                }
            }
        }

        var chart = 0;
        var bar_chart_list = [];

        for (var assay in assays) {
            for (var value_unit in assays[assay]) {
                var add_to_bar_charts = true;

                addChart(chart, assay, timeUnits[assay], value_unit);

                var xs = {};
                var num = 1;

                for (var sample_location in assays[assay][value_unit]) {
                    sample_location = '' + sample_location;

                    // Add to bar charts if no time scale exceeds 3 points
                    if (add_to_bar_charts && assays[assay][value_unit][sample_location].time.length > 3) {
                        add_to_bar_charts = false;
                    }

                    xs[sample_location] = 'x' + num;

                    assays[assay][value_unit][sample_location].data.unshift(sample_location);
                    assays[assay][value_unit][sample_location].time.unshift('x' + num);

                    //Load for correct assay chart
                    charts[chart].load({
                        xs: xs,

                        columns: [
                            assays[assay][value_unit][sample_location].data,
                            assays[assay][value_unit][sample_location].time
                        ]
                    });

                    num += 1;
                }
                // Add to bar charts if no time scale exceeds 3 points
                if (add_to_bar_charts) {
                    bar_chart_list.push(chart);
                }

                chart += 1;
            }
        }

        // Make bar charts
        for (var index in bar_chart_list) {
            var chart_index = bar_chart_list[index];
            charts[chart_index].transform('bar');
        }
    }

    var refresh = function() {
        var file = $('#id_file')[0].files[0];
        if (file) {
            resetChart();
            validate_readout_file();
            // getText(file);
        }
    };

    if (readout_id) {
        getReadout();
    }

    // Refresh on file change
    $('#id_file').change(function(evt) {
        refresh();
    });

    // Refresh on change in overwrite option NEED REPLCATE TO BE ACCURATE
    $('#id_overwrite_option').change(function() {
        refresh();
    });

    if ($('#id_headers')[0]) {
        $('#id_headers').change(function (evt) {
            if ($('#id_file')[0].files[0]) {
                refresh();
            }
        });
    }

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
