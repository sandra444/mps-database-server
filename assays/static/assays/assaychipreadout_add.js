$(document).ready(function () {
    // Function to repeat a string num number of times
    function repeat(str, num) {
        return (new Array(num+1)).join(str);
    }

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
        $('<div id="chart' + id + '" align="right" style="width: 44.9%;float: right;margin-right: 0.1%;margin-left: -100%px;">')
            .addClass('chart-container')
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
                    $('#csv_table').html(add);
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
                resetChart();
                $('#csv_table').html(add);
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
        if (!csv) {
            $('#csv_table').html(add);
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

        //Make table
        var table = exist ? "<table class='chip-table bg-success' style='width: 100%;'><tbody>" : "<table class='chip-table' style='width: 100%;'><tbody>";

        // table += exist ? "<tr class='bg-info'>" + header + "</tr>" : "";
        table += "<tr class='bg-info'>" + header + "</tr>";

        // Current index for saving QC values
        var current_index = 0;

        for (var i in lines) {
            var line = lines[i];

            var chip_id = line[0];
            var time = line[1];
            var time_unit = line[2];
            var assay = line[3];
            var object = line[4];
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
            var index = '';

            // Need to take a slice to avoid treating missing QC as invalid
            var every = line.slice(0,5).every(isTrue) && isTrue(line[6]) && isTrue(line[9]);

            // If the row will be excluded (highlighted red)
            // if ((i < headers && !exist) || !every) {
            if (!exist && !every) {
                table += "<tr class='bg-danger'>";
            }

            // If the row has no value (residue code, may be used later)
            else if (value == 'None' || !value) {
                table += "<tr style='background: #606060'>";
            }

            // If the row is marked an outlier
            else if (line[7] && $.trim(line[7])) {
                table += "<tr class='bg-warning'>";
            }

            else {
                table += "<tr>";
            }

            // DO NOT ADD COMMAS TO CHIP ID
            if (chip_id) {
                table += "<th>" + chip_id + "</th>";
            }

            table += "<th>" + data_format(line[1]) + "</th>";

            for (var j=2; j<5; j++) {
                if (line[j]) {
                    table += "<th>" + line[j] + "</th>";
                }
                else {
                    table += "<th></th>";
                }
            }

            table += "<th>" + data_format(line[5]) + "</th>";

            table += "<th>" + line[6] + "</th>";

            // Just add text if this is a header row for QC OR if this row is invalid
            // (QC status of an ignored row does not really matter)
            // if (i < headers && !exist || !every) {
            if (!exist && !every) {
                if (quality) {
                    table += "<th>" + quality + "</th>";
                }
                else {
                    table += "<th></th>";
                }
            }
            // Add an input for the QC if this isn't a header
            // QC inputs NAME begin with "QC_"
            // QC input IDS are the row index (for plotting accurately)
            else {
                index = get_index_for_value(object, time, assay, value_unit, update_number);
                table += "<th><input size='4' class='quality text-danger' id='" + i + "' name='" + index + "' value='" + quality + "'></th>";
                // Increment the current index
                current_index += 1;
            }

            // Add notes
            if (notes) {
                table += '<th><span class="glyphicon glyphicon-info-sign" title="' + notes + '"></span></th>';
            }
            else {
                table += "<th></th>";
            }

            table += "</tr>";

            // Add to data if index
            if (index) {
                data[index] = line;
            }
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);

        // Bind change event to quality
        $('.quality').change(function() {
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
        var valueUnits = {};
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
            var object = line[4];
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

                if (object && object != 'None' && !assays[assay][object]) {
                    assays[assay][object] = {'time': [], 'data': []};
                }

                if (assays[assay][object] && value && value != 'None') {
                    assays[assay][object].time.push(time);
                    assays[assay][object].data.push(value);

                    valueUnits[assay] = value_unit;
                    timeUnits[assay] = time_unit;
                }
            }
        }

        var chart = 0;
        var bar_chart_list = [];

        for (var assay in assays) {
            var add_to_bar_charts = true;

            addChart(chart, assay, timeUnits[assay], valueUnits[assay]);

            var xs = {};
            var num = 1;

            for (var object in assays[assay]) {
                object = '' + object;

                // Add to bar charts if no time scale exceeds 3 points
                if (add_to_bar_charts && assays[assay][object].time.length > 3) {
                    add_to_bar_charts = false;
                }

                xs[object] = 'x' + num;

                assays[assay][object].data.unshift(object);
                assays[assay][object].time.unshift('x' + num);

                //Load for correct assay chart
                charts[chart].load({
                    xs: xs,

                    columns: [
                        assays[assay][object].data,
                        assays[assay][object].time
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

        // Make bar charts
        for (var index in bar_chart_list) {
            var chart_index = bar_chart_list[index];
            charts[chart_index].transform('bar');
        }
    }

    var refresh = function() {
        resetChart();
        var file = $('#id_file')[0].files[0];
        if (file) {
            validate_readout_file();
            // getText(file);
        }
        else {
            if (readout_id) {
               getReadout()
            }
            else {
                $('#csv_table').html(add);
            }
        }
    };

    // The data in question as a Object pairing 'time|time_unit|assay|object|value_unit|update_number
    var data = {};

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var readout_id = getReadoutValue();

    // Indicates whether the data exists in the database or not
    var exist = false;

    var headers = 0;
    var header = "<th>Chip ID</th>" +
        "<th>Time</th>" +
        "<th>Time Unit</th>" +
        "<th>Assay</th>" +
        "<th>Object</th>" +
        "<th>Value</th>" +
        "<th>Value Unit</th>" +
        "<th>QC Status</th>" +
        "<th></th>";

    if ($('#id_headers')[0]) {
        headers = Math.floor($('#id_headers').val());
    }

    var add = "<table class='chip-table' style='width: 100%;'><tbody>" +
        "<tr class='bg-info'>" + header + "</tr>" +
        "<tr>" + repeat('<th><br><br></th>',8) + "</tr>" +
        "<tr>" + repeat('<th><br><br></th>',8) + "</tr>" +
        "</tbody></table>";

    if ($('#assaychipreadoutassay_set-group')[0] != undefined) {
        $('<div id="extra" align="center" style="margin-top: 10px;margin-bottom: 10px;min-width: 975px;overflow: hidden;">')
            .appendTo('body');
        $("#extra").insertAfter($("#assaychipreadoutassay_set-group")[0]);

        $('<div id="csv_table" style="width: 55%;float: left;">')
            .appendTo('#extra').html(add);

        var charts = [];
    }

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
