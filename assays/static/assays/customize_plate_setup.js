// This script is for displaying the layout for setups
// TODO NEEDS REFACTOR
// TODO PREFERABLY CONSOLIDATE THESE DISPLAY FUNCTIONS (DO NOT REPEAT YOURSELF)

// Global variables are in poor taste
var id = null;

function search(elem) {
    id = elem.id.replace(/\D/g,'');
    $("#dialog").dialog('open');
    // Remove focus
    $('.ui-dialog :button').blur();
}

$(document).ready(function () {

    var layout = $('#id_assay_layout');
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    // Get layout
    function get_device_layout() {
        var layout_id = layout.val();
        if (layout_id) {
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_layout_format_labels',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: layout_id,

                    model: 'assay_layout',

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    var row_labels = json.row_labels;
                    var column_labels = json.column_labels;
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

        get_layout_data(layout.val());
    }

    function get_layout_data(layout_id) {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_assay_layout_content',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: layout_id,

                model: 'assay_layout',

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
    }

    // On layout change, acquire labels and build table
    layout.change( function() {
        get_device_layout();
    });

    // If a layout is initially chosen
    // (implies the setup is saved)
    if (layout.val()) {
        get_device_layout();
    }

    // Datepicker superfluous on admin, use this check to apply only in frontend
    if ($('#fluid-content')[0]) {
        // Add datepicker
        var date = $("#id_setup_date");
        var curr_date = date.val();
        date.datepicker();
        date.datepicker("option", "dateFormat", "yy-mm-dd");
        date.datepicker("setDate", curr_date);
    }

    // Operations for the frontend only
    if ($('#dialog')[0]) {
        // Open and then close dialog so it doesn't get placed in window itself
        var dialog = $('#dialog');
        dialog.dialog({
            width: 825,
            height: 500,
            closeOnEscape: true,
            autoOpen: false,
            close: function() {
                $('body').removeClass('stop-scrolling');
            },
            open: function() {
                $('body').addClass('stop-scrolling');
            }
        });
        dialog.removeProp('hidden');

        $('.cellsample').click(function (evt) {
            var cellsampleId = this.id;
            var selectedInput = $('#id_assayplatecells_set-' + id + '-cell_sample');
            selectedInput.prop('value', cellsampleId);
            var cellsampleName = this.attributes["name"].value;
            var selectedLabel = $('#id_assayplatecells_set-' + id + '-cell_sample_label');
            selectedLabel.text(cellsampleName);
            $('#dialog').dialog('close');
        });

        $('#cellsamples').DataTable({
            "iDisplayLength": 50,
            // Initially sort on receipt date
            "order": [ 0, "desc" ],
            // If one wants to display top and bottom
            "sDom": '<"wrapper"fti>'
        });

        // Move filter to left
        $('.dataTables_filter').css('float', 'left');

        // This code should populate cell labels when data is already given
        var current_id = 0;
        var current_input = $('#id_assayplatecells_set-' + current_id + '-cell_sample');
        while(current_input[0]) {
            if(current_input.val()) {
                var cell_name = $('#' + current_input.val()).attr('name');
                $('#id_assayplatecells_set-' + current_id + '-cell_sample_label').text(cell_name);
            }
            current_id += 1;
            current_input = $('#id_assayplatecells_set-' + current_id + '-cell_sample');
        }

        // This will clear a cell sample when the button is pressed
        $('#clear_cell_sample').click(function() {
            var selectedInput = $('#id_assayplatecells_set-' + id + '-cell_sample');
            selectedInput.prop('value', '');
            var selectedLabel = $('#id_assayplatecells_set-' + id + '-cell_sample_label');
            selectedLabel.text('');
            $('#dialog').dialog('close');
        });
    }
});
