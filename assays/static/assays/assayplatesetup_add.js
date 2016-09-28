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
    //  TODO REFACTOR
    // Specify that the location for the table is different
    window.LAYOUT.insert_after = $('.inline-group');

    // On layout change, acquire labels and build table
    layout.change( function() {
        window.LAYOUT.get_device_layout(layout.val(), 'assay_layout', false);
    });

    // If a layout is initially chosen
    // (implies the setup is saved)
    if (layout.val()) {
        window.LAYOUT.get_device_layout(layout.val(), 'assay_layout', false);
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

            // Turn density into scientific notation
            var current_density = $('#id_assayplatecells_set-' + current_id + '-cellsample_density');
            var current_number = Number(current_density.val());
            if (current_number) {
                current_density.val(current_number.toExponential());
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
