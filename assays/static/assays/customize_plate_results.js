// This script is for displaying the readout and everything before in plate results
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {

    // It is useful to have a list of row and column labels
    var row_labels = null;
    var column_labels = null;

    // The setup
    var readout = $('#id_readout');

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    // Get layout
    function get_device_layout() {
        var readout_id = readout.val();
        if (readout_id) {
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: readout_id,

                    model: 'assay_device_readout',

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    // Global in readout scope
                    row_labels = json.row_labels;
                    column_labels = json.column_labels;
                    if (row_labels && column_labels) {
                        build_table(row_labels, column_labels);
                    }
                    else {
                        alert('This device is not configured correctly');
                    }
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            // Remove when invalid/nonextant layout chosen
            $('#layout_table').remove();
        }
    }

    // Build table
    function build_table(row_labels, column_labels) {
        // Remove old
        $('#layout_table').remove();

        // Choice of inserting after fieldset is contrived; for admin
        var table = $('<table>')
            .css('width','100%')
            .addClass('layout-table')
            // CONTRIVED PLACE AFTER INLINE FOR ADMIN
            // TODO CHANGE
            .attr('id','layout_table').insertAfter($('.inline-group'));

        // make first row
        var row = $('<tr>');
        row.append($('<th>'));
        $.each(column_labels, function (index, value) {
            row.append($('<th>')
                .text(value));
        });
        table.append(row);

        // make rest of the rows
        $.each(row_labels, function (row_index, row_value) {
            var row = $('<tr>');
            row.append($('<th>')
                .text(row_value));
            // Note that the "lists" are added here
            $.each(column_labels, function (column_index, column_value) {
                row.append($('<td>')
                    .attr('id', row_value + '_' + column_value)
                    .append($('<div>')
                        .css('text-align','center')
                        .css('font-weight', 'bold')
                        .attr('id',row_value + '_' + column_value + '_type'))
                    .append($('<ul>')
                        .attr('id',row_value + '_' + column_value + '_list')
                        .addClass('layout-list')));
            });
            table.append(row);

        });

        get_layout_data(readout.val());
    }

    function get_layout_data(readout_id) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: readout_id,

                model: 'assay_device_readout',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_layout(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // TODO FILL_LAYOUT
    function fill_layout(layout_data) {
        window.LAYOUT.fill_layout(layout_data);

        // Attempt to acquire the readout
        // (AVOID RACE CONDITIONS AT ALL COST)
        get_existing_readout(readout.val());
    }

    function get_existing_readout(readout_id) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readout',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: readout_id,

                model: 'assay_device_readout',

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                fill_readout_from_existing(json);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function fill_readout_from_existing(data) {
        $.each(data, function(index, well_data) {
            var value = well_data.value;
            var value_unit = well_data.value_unit;
            var time = well_data.time;
            var time_unit = well_data.time_unit;
            var assay = well_data.assay;

            var row_label = row_labels[well_data.row];
            var column_label = column_labels[well_data.column];
            var well_id = '#' + row_label + '_' + column_label;

            var text = (time && time_unit) ?
                assay + ': ' + value + ' ' + value_unit +'\t(' + time + ' ' + time_unit + ') ':
                assay + ': ' + value + ' ' + value_unit;

            $(well_id).append(
                    '<div class="value" style="text-align: center; color: blue;"><p><b>' +
                    text +
                    '</b></p></div>');
        });
    }

    // On setup change, acquire labels and build table
    readout.change( function() {
        get_device_layout();
    });

    // If a setup is initially chosen
    // (implies readout exists)
    if (readout.val()) {
        // Initial table and so on
        get_device_layout();
    }

    // WHITTLE
    function getIDs() {
        var i = 0;
        var IDs = [];
        while ($('#id_assayplateresult_set-'+i+'-assay_name')[0]){
            IDs.push(i);
            i += 1;
        }
        return IDs;
    }

    function changeNew() {
        var i = Math.max.apply(null,getIDs());
        $('#id_assayplateresult_set-'+i+'-assay_name').html(inlineOptions);
    }

    function changeAll(reset) {
        var IDs = getIDs();
        var vals = [];

        if (!reset) {
            for (var i in IDs) {
                vals.push($('#id_assayplateresult_set-'+i+'-assay_name').val());
            }
        }

        for (var j in IDs) {
            $('#id_assayplateresult_set-'+j+'-assay_name').html(inlineOptions);
            if (!reset) {
                $('#id_assayplateresult_set-'+j+'-assay_name').val(vals[j]);
            }
        }
    }

    var newRow = $('.add-row').children().children();
    var inlineOptions = "";

    // Initial readout whittle
    $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
        inlineOptions = data;
        // Only reset (pass true) when you want to overwrite existing
        changeAll(false);
    });

    // Whittle when readout changes
    readout.change(function() {
        $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(true);
        });
    });

    newRow.click(function() {
        changeNew();
    });

    // This is to deal with new inline entries when on the frontend
    $("#add_button").click(function() {
        changeNew();
    });

    // Resolve deletion error frontend
    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on("click", "input[name*='DELETE']", function(event) {
        $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(false);
        });
    });
});

