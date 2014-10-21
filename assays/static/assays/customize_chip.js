$(document).ready(function () {

    function getReadoutValue() {
        try {
            return Math.floor($('.historylink').attr('href').split('/')[4]);
        }
        catch(err) {
            return null;
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

        table += exist ? "<tr style='background: #FF2400'><th>Time</th><th>Field</th><th>Raw Data</th></tr>" : "";

        for (var i in lines) {
            if (i == 0 && !exist || (!lines[i][0] && !lines[i][1] && !lines[i][2])){
                table += "<tr style='background: #FF2400'>";
            }
            else if (i > 0 && lines[i][2] == 'None'){
                table += "<tr style='background: #606060'>";
            }
            else{
                table += "<tr>";
            }
            table += "<th><br>" + lines[i][0] + "<br></th>";
            table += "<th><br>" + lines[i][1] + "<br></th>";
            table += "<th><br>" + lines[i][2] + "<br></th>";
            table += "</tr>";
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);

        //Make chart
        var objects = {};

        for (var i in lines) {
            if (!lines[i][1] || (i == 0 && !exist)) {
                continue;
            }

            if (!objects[lines[i][1]]){
                objects[lines[i][1]] = {'time':[], 'data':[]};
            }

            if (lines[i][2] && lines[i][2] != 'None') {
                objects[lines[i][1]].time.push(lines[i][0]);
                objects[lines[i][1]].data.push(lines[i][2]);
            }
        }

        //console.log(objects);

        var xs = {};

        var num = 1;
        for (var object in objects) {
            //console.log(object);
            object = '' + object;

            xs[object] = 'x' + num;

            console.log(xs);

            objects[object].data.unshift(object);
            objects[object].time.unshift('x' + num);

            console.log(objects[object].data);
            console.log(objects[object].time);

            chart.load({
                xs: xs,

                columns: [
                    objects[object].data,
                    objects[object].time,
                ]
            });

            num += 1;
        }
    };

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var id = getReadoutValue();

    var add = "<table class='layout-table' style='width: 100%;'><tbody>" +
            "<tr style='background: #FF2400'><th>Time</th><th>Field</th><th>Raw Data</th></tr>" +
            "<tr><th><br><br></th><th><br><br></th><th><br><br></th>" +
            "</tr><tr><th><br><br></th><th><br><br></th><th><br><br></th></tr>" +
            "</tbody></table>";

    if ($('#assaychipreadout_form')[0] != undefined) {
        $('<div id="extra" align="center" style="margin-top: 10px;margin-bottom: 10px;width: 99%">').appendTo('body');
        $("#extra").insertBefore($(".module")[2]);

        $('<div id="csv_table" style="width: 20%;float: left;">')
            .appendTo('#extra').html(add);

        $('<div id="chart" style="width: 80%;float: left;">')
            .appendTo('#extra');

        var chart = c3.generate({
            bindto: '#chart',

            data: {
                columns: []
            },
            axis: {
                x: {
                    label: 'Time'
                },
                y: {
                    label: 'Value'
                }
            }
        });
    }

    if (id) {
        getReadout();
    }

    $('#id_file').change(function(evt) {
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



