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

    function addChart(id,name) {

        $('<div id="chart' + id + '" align="right" style="width: 50%;float: right;margin-right: 5%;margin-left: -100%px;">')
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
                            text: 'Time',
                            position: 'outer-center'
                        }
                    },
                    y: {
                        label: {
                            text: name,
                            position: 'outer-middle'
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

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: id,

                // Evil hack to get the CSRF middleware token
                // Always pass the CSRF middleware token with every AJAX call

                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                parseAndReplace(json.csv,true);
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
        parseAndReplace(fileString,false);
    };

    var parseAndReplace = function (csv,exist) {
        if (!csv) {
            $('#csv_table').html(add);
            return;
        }

        // Update headers
        headers = Math.floor($('#id_headers').val());

        // Crash if the first time is not numeric
        if (isNaN(headers)) {
            alert("Please make sure you choose a valid number for number of header rows.");
            return;
        }

        var all = csv.split('\n');
        var lines = [];

        for (var index in all) {
            if (all[index].indexOf(",") > -1) {
                lines.push(all[index].split(','));
            }
        }

        all = null;

        //Make table
        var table = exist ? "<table class='layout-table' style='width: 100%;background: #7FFF00'><tbody>" : "<table class='layout-table' style='width: 100%;'><tbody>";

        table += exist ? "<tr style='background: #FF2400'><th>Time</th><th>Time Unit</th><th>Assay</th><th>Object</th><th>Value</th><th>Value Unit</th></tr>" : "";

        for (var i in lines) {
            var every = lines[i].every(isTrue);

            if ((i < headers && !exist) || !every) {
                table += "<tr style='background: #FF2400'>";
            }
            else if (lines[i][4] == 'None') {
                table += "<tr style='background: #606060'>";
            }
            else {
                table += "<tr>";
            }

            for (var j=0; j<6; j++) {
                table += "<th>" + lines[i][j] + "</th>";
            }
            table += "</tr>";
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);

        //Make chart
        var assays = {};

        for (var i in lines) {

            // Crash if the time or value are not numeric
            if (isNaN(lines[headers][0]) || isNaN(lines[headers][4])) {
                alert("Improperly Configured: Please check your file and the number of header rows selected.");
                return;
            }

            if (!lines[i][0] || !lines[i][2] || !lines[i][3] || (i < headers && !exist)) {
                continue;
            }

            if (!assays[lines[i][2]]) {
                assays[lines[i][2]] = {};
            }

            if (lines[i][3] && lines[i][3] != 'None' && !assays[lines[i][2]][lines[i][3]]) {
                assays[lines[i][2]][lines[i][3]] = {'time':[], 'data':[]};
            }

            if (assays[lines[i][2]][lines[i][3]] && lines[i][4] && lines[i][4] != 'None') {
                assays[lines[i][2]][lines[i][3]].time.push(lines[i][0]);
                assays[lines[i][2]][lines[i][3]].data.push(lines[i][4]);
            }
        }

        var chart = 0;
        for (var assay in assays) {
            addChart(chart,assay);

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
                        assays[assay][object].time,
                    ]
                });

                num += 1;
            }
            chart += 1;
        }
    };

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var id = getReadoutValue();

    var headers = +$('#id_headers').val();

    var add = "<table class='layout-table' style='width: 100%;'><tbody>" +
            "<tr style='background: #FF2400'><th>Time</th><th>Time Unit</th><th>Assay</th><th>Object</th><th>Value</th><th>Value Unit</th></tr>" +
            "<tr>" + repeat('<th><br><br></th>',6) + "</tr>" +
            "<tr>" + repeat('<th><br><br></th>',6) + "</tr>" +
            "</tbody></table>";

    if ($('#assaychipreadoutassay_set-group')[0] != undefined) {
        $('<div id="extra" align="center" style="margin-top: 10px;margin-bottom: 10px;width: 99%;overflow: hidden;">')
            .appendTo('body');
        $("#extra").insertAfter($("#assaychipreadoutassay_set-group")[0]);

        $('<div id="csv_table" style="width: 30%;float: left;margin-left: 5%;">')
            .appendTo('#extra').html(add);

        var charts = [];
    }

    if (id) {
        getReadout();
    }

    $('#id_file').change(function(evt) {
        resetChart();
        var file = $('#id_file')[0].files[0];
        if (file) {
            getText(file);
        }
        else{
            if (id) {
               getReadout()
            }
            else {
                $('#csv_table').html(add);
            }
        }
    });
});



