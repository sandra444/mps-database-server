$(document).ready(function () {

    var getText = function (readFile) {
        var reader = new FileReader();
        reader.readAsText(readFile, "UTF-8");
        reader.onload = loaded;
    };

    var loaded = function (evt) {
        var fileString = evt.target.result;
        parseAndReplace(fileString);
    };

    var parseAndReplace = function (csv) {
        var all = csv.split('\n');
        var lines = [];

        for (i in all) {
            lines.push(all[i].split(','));
        }

        all = null;

        table = "<table class='layout-table' style='width: 99.5%;'><tbody>";

        for (i in lines) {
            table += "<tr>";
            table += "<th><br>" + lines[i][0] + "<br></th>";
            table += "<th><br>" + lines[i][1] + "<br></th>";
            table += "<th><br>" + lines[i][2] + "<br></th>";
            table += "</tr>";
        }

        table += "</tbody></table>";
        $('#csv_table').html(table);
    };

    if ($('#assaychipreadout_form')[0] != undefined) {
        var add = "<table class='layout-table' style='width: 99.5%;'><tbody>" +
            "<tr><th>Time</th><th>Field</th><th>Raw Data</th></tr>" +
            "<tr><th><br><br></th><th><br><br></th><th><br><br></th>" +
            "</tr><tr><th><br><br></th><th><br><br></th><th><br><br></th></tr>" +
            "</tbody></table>";
        $('<div id="csv_table" align="center" style="margin-top: 10px;margin-bottom: 10px;">').appendTo('body').html(add);
        $("#csv_table").insertBefore($(".module")[3]);
    }

    if ($('.file-upload').find($('a')).attr('href') != undefined) {
        $.get($('.file-upload').find($('a')).attr('href'), function(data) { parseAndReplace(data); });
    }

    $('#id_file').change(function(evt) {
        var file = $('#id_file')[0].files[0];
        getText(file);
    });

});

