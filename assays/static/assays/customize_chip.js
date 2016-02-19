$(document).ready(function () {

    // Add commas to number
    // Special thanks to stack overflow
    function number_with_commas(x) {
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return parts.join(".");
    }

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

    function addChart(id,name,timeUnits,valueUnits) {

        $('<div id="chart' + id + '" align="right" style="width: 50%;float: right;margin-right: 2.5%;margin-left: -100%px;">')
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
                            text: name + ' (' + valueUnits + ')',
                            position: 'outer-middle'
                        }
                    }
                },
                tooltip: {
                    format: {
                        value: function (value, ratio, id) {
                            var format = value % 1 === 0 ? d3.format(',d') : d3.format(',.2f');
                            return format(value);
                        }
                    }
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
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_chip_readout',
                id: id,
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

        var all = csv.split('\n');
        lines = [];

        for (var index in all) {
            if (all[index].indexOf(",") > -1) {
                lines.push(all[index].split(','));
            }
        }

        all = null;

        //Make table
        var table = exist ? "<table class='layout-table' style='width: 100%;background: #7FFF00'><tbody>" : "<table class='layout-table' style='width: 100%;'><tbody>";

        table += exist ? "<tr style='background: #FF2400'>" + header + "</tr>" : "";

        // Current index for saving QC values
        var current_index = 0;

        for (var i in lines) {
            var line = lines[i];

            // Need to take a slice to avoid treating missing QC as invalid
            var every = line.slice(0,7).every(isTrue);

            var value = line[5];

            // If the row will be excluded (highlighted red)
            if ((i < headers && !exist) || !every) {
                table += "<tr style='background: #FF2400'>";
            }

            // If the row has no value (residue code, may be used later)
            else if (value == 'None') {
                table += "<tr style='background: #606060'>";
            }

            else {
                table += "<tr>";
            }

            // DO NOT ADD COMMAS TO CHIP ID
            if (line[0]) {
                table += "<th>" + line[0] + "</th>";
            }

            for (var j=1; j<7; j++) {
                if (line[j]) {
                    table += "<th>" + number_with_commas(line[j]) + "</th>";
                }
                else {
                    table += "<th></th>";
                }
            }

            // Just add text if this is a header row for QC OR if this row is invalid
            // (QC status of an ignored row does not really matter)
            if (i < headers && !exist || !every) {
                if (line[7]) {
                    table += "<th>" + line[7] + "</th>";
                }
                else {
                    table += "<th></th>";
                }
            }
            // Add an input for the QC if this isn't a header
            // QC inputs NAME begin with "QC_"
            // QC input IDS are the row index (for plotting accurately)
            else {
                table += "<th><input size='4' class='quality text-danger' id='" + i + "' name='QC_" + current_index + "' value='" + line[7] + "'></th>";
                // Increment the current index
                current_index += 1;
            }

            table += "</tr>";
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);

        // Bind change event to quality
        $('.quality').change(function() {
            var index = +this.id;
            lines[index][7] = this.value;
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

        for (var i in lines) {
            var line = lines[i];

            // Need to take a slice to avoid treating missing QC as invalid
            var every = line.slice(0,7).every(isTrue);

            if (!every || (i < headers && !exist)) {
                continue;
            }

            var time = line[1];
            var time_unit = line[2];
            var assay = line[3];
            var object = line[4];
            var value = line[5];
            var value_unit = line[6];

            var quality = $.trim(line[7]);

            // Crash if the time or value are not numeric
            if (isNaN(time) || isNaN(value)) {
                alert("Improperly Configured: Please check your file and the number of header rows selected.");
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
        for (var assay in assays) {
            addChart(chart,assay,timeUnits[assay],valueUnits[assay]);

            var xs = {};
            var num = 1;
            for (var object in assays[assay]) {
                object = '' + object;

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
            chart += 1;
        }
    }

    var refresh = function() {
        resetChart();
        var file = $('#id_file')[0].files[0];
        if (file) {
            getText(file);
        }
        else {
            if (id) {
               getReadout()
            }
            else {
                $('#csv_table').html(add);
            }
        }
    };

    // The data in question
    var lines = [];

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var id = getReadoutValue();

    // Indicates whether the data exists in the database or not
    var exist = false;

    var headers = 0;
    var header = "<th>Chip ID</th><th>Time</th><th>Time Unit</th><th>Assay</th><th>Object</th><th>Value</th><th>Value Unit</th><th>QC Status</th>";

    if ($('#id_headers')[0]) {
        headers = Math.floor($('#id_headers').val());
    }

    var add = "<table class='layout-table' style='width: 100%;'><tbody>" +
        "<tr style='background: #FF2400'>" + header + "</tr>" +
        "<tr>" + repeat('<th><br><br></th>',8) + "</tr>" +
        "<tr>" + repeat('<th><br><br></th>',8) + "</tr>" +
        "</tbody></table>";

    if ($('#assaychipreadoutassay_set-group')[0] != undefined) {
        $('<div id="extra" align="center" style="margin-top: 10px;margin-bottom: 10px;min-width: 975px;overflow: hidden;">')
            .appendTo('body');
        $("#extra").insertAfter($("#assaychipreadoutassay_set-group")[0]);

        $('<div id="csv_table" style="width: 30%;float: left;margin-left: 2.5%;">')
            .appendTo('#extra').html(add);

        var charts = [];
    }

    if (id) {
        getReadout();
    }

    $('#id_file').change(function(evt) {
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



