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

        var table = exist ? "<table class='layout-table' style='width: 99.5%;background: #7FFF00'><tbody>":"<table class='layout-table' style='width: 99.5%;'><tbody>";

        for (var i in lines) {
            table += i==0 && !exist ? "<tr style='background: #FF2400'>" : "<tr>";
            table += "<th><br>" + lines[i][0] + "<br></th>";
            table += "<th><br>" + lines[i][1] + "<br></th>";
            table += "<th><br>" + lines[i][2] + "<br></th>";
            table += "</tr>";
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);
    };

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var id = getReadoutValue();

    var add = "<table class='layout-table' style='width: 99.5%;'><tbody>" +
            "<tr style='background: #FF2400'><th>Time</th><th>Field</th><th>Raw Data</th></tr>" +
            "<tr><th><br><br></th><th><br><br></th><th><br><br></th>" +
            "</tr><tr><th><br><br></th><th><br><br></th><th><br><br></th></tr>" +
            "</tbody></table>";

    if ($('#assaychipreadout_form')[0] != undefined) {
        $('<div id="csv_table" align="center" style="margin-top: 10px;margin-bottom: 10px;">').appendTo('body').html(add);
        $("#csv_table").insertBefore($(".module")[3]);
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

