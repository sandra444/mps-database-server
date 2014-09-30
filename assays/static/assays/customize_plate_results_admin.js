$(document).ready(function () {

    var assay_layout_id;
    var base_layout_id;
    var readout_table;
    var readout_id;

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    function getReadouts(data) {
        // select the first table in the form (the one we want)
        var table = $('#layout_table')[0];

        // `cells` is current column starting with 0
        // `rows` is current row starting with 0

        for (var key in data) {
            var row = data[key][0].row;
            var column = data[key][0].column;
            var value = data[key][0].value;

            ++row;
            ++column;

            currentCell = table.rows[row].cells[column];

            $(currentCell).append(
                '<div style="text-align: center; color: blue;"><p><b>' +
                    value +
                    '</b></p></div>'
            );

        }

    }

    function fillLayout(request) {

        readout_table = request;

        var stampCounter = 0;

        $.each(request, function (well, content) {

            var list = $('#' + well + '_list');

            $.each(content, function (index, data) {

                var stamp = well + '_time', tp = data.timepoint, text, li, info;

                if (tp > 0 && $('#' + stamp).length == 0) {
                    text = 'Time: ' + tp + ' min';
                    li = $('<li>')
                        .attr('id', stamp)
                        .text(text);

                    li.append($('<input>')
                        .attr('type', 'hidden')
                        .attr('name', stamp)
                        .attr('value', tp));
                    list.prepend(li);
                }

                if (data.cellsample) {

                    var cellsample_id = data.cellsample;
                    var density = data.density;
                    var density_unit = data.density_unit;

                    text = data.name +
                        ' (' +
                        density +
                        ' ' +
                        density_unit +
                        ')';

                    li = $('<li>')
                        .text(text)
                        .attr('cellsample', cellsample_id);

                    info =
                        'well="' + well + '"'
                            + ',cellsample=' + cellsample_id
                            + ',density=' + density
                            + ',density_unit="' + density_unit + '"';

                    stampCounter++;
                    li.append($('<input>')
                        .attr('type', 'hidden')
                        .attr('name', 'well_' + stampCounter)
                        .attr('value', info));
                    list.append(li);

                }
                if (data.compound) {

                    compound_id = data.compound;
                    concentration = data.concentration;
                    concentration_unit = data.concentration_unit;

                    text = data.name +
                        ' (' +
                        concentration +
                        ' ' +
                        concentration_unit +
                        ')';

                    li = $('<li>')
                        .text(text)
                        .attr('compound', compound_id);

                    info =
                        'well="' + well + '"'
                            + ',compound=' + compound_id
                            + ',concentration=' + concentration
                            + ',concentration_unit="' + concentration_unit +
                            '"';

                    stampCounter++;
                    li.append($('<input>')
                        .attr('type', 'hidden')
                        .attr('name', 'well_' + stampCounter)
                        .attr('value', info));
                    list.append(li);

                }

            });
        });

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readout',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                current_readout_id: readout_id,

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                getReadouts(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function createBaseTableLayout(data) {

        $('#layout_div').remove();
        $('#controls').remove();

        $('fieldset').first()
            .after($('<div>')
                .attr('id', 'layout_div')
                .addClass('module inline'));

        var table = $('<table>')
            .css('width', '100%')
            .addClass('layout-table')
            .attr('id', 'layout_table')
            .appendTo($('#layout_div'));


        // make the first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(data.format.column_labels, function (index, value) {
            row.append($('<th>').text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(data.format.row_labels, function (r, rval) {
            var row = $('<tr>');
            row.append($('<th>').text(rval));
            $.each(data.format.column_labels, function (c, cval) {
                row.append($('<td>').attr('id', rval + '_' + cval));
            });
            table.append(row);

        });

        // fill in well colors
        $.each(data.wells, function (k, v) {
            $('#' + k)
                .css('background-color', v[1])
                .append($('<div>')
                    .css('text-align', 'center')
                    .append($('<b>').text(v[0])))
                .append($('<ul>')
                    .attr('id', k + '_list')
                    .addClass('layout-list'));
        });

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                assay_layout_id: assay_layout_id,

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fillLayout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

    }

    function setBaseLayout(data) {

        base_layout_id = data.base_layout_id;

        console.log('Current Base Layout ID: ' + base_layout_id);

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_base_layout_info',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: base_layout_id,

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                createBaseTableLayout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function fetchBaseLayout() {
        //assay_layout_id = assay_layout.val();
        console.log('Current Assay Layout: ' + assay_layout_id);

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_baseid',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                current_layout_id: assay_layout_id,

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                setBaseLayout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function getReadoutData() {

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_plate_info',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: $('#id_assay_device_id').val(),

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                console.log(json);
                assay_layout_id = json.assay_layout_id;
                readout_id = $('#id_assay_device_id').val();
                fetchBaseLayout();
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

    }

    function checkAssayLayoutValidity() {

        var previous = $('#layout_div');

        if(previous){
            previous.remove();
        }

        var assay_readout = $('#id_assay_device_id');

        if (assay_readout.val()) {
            getReadoutData();
        }
    }

    checkAssayLayoutValidity();


    $('#id_assay_device_id').change( function () {
            checkAssayLayoutValidity();
    });


});
