// This script was made to prevent redundant code in setup pages
$(document).ready(function () {
    // var cell_sample_search = $('#id_cell_sample_search');
    var cell_sample_search = $('.open-cell-sample-dialog');
    // var cell_sample_id_selector = cell_sample_search.parent().find('input[readonly=readonly]');
    // Defaults for matrix (irrelevant in matrix item)
    var cell_sample_id_selector = $('#id_cell_sample');
    var cell_sample_label_selector = $('#id_cell_sample_label');

    // Open and then close dialog so it doesn't get placed in window itself
    var dialog = $('#dialog');
    dialog.dialog({
        width: 900,
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

    $('#cellsamples').DataTable({
        "iDisplayLength": 50,
        // Initially sort on receipt date
        "order": [ 1, "desc" ],
        // If one wants to display top and bottom
        "sDom": '<"wrapper"fti>'
    });

    // Move filter to left
    $('.dataTables_filter').css('float', 'left');

    cell_sample_search.click(function() {
        dialog.dialog('open');
        // Get the proper selectors
        cell_sample_id_selector = $(this).parent().find('input[readonly=readonly]');
        cell_sample_label_selector = $(this).parent().find('.small');
        // Remove focus
        $('.ui-dialog :button').blur();
    });

    $('.cellsample-selector').click(function() {
        var cell_sample_id = $(this).attr('data-cell-sample-id');
        cell_sample_id_selector.prop('value', cell_sample_id);
        var cell_sample_name = this.attributes["name"].value;
        cell_sample_label_selector.text(cell_sample_name);
        $('#dialog').dialog('close');
    });

    // Display all labels(irrelevant in matrix)
    $('.cell-sample-id-field').each(function() {
        // Get label
        $(this).parent().find('label').text($('#cell_sample_' + $(this).val()).attr('name'));
        // Turn density into scientific notation
        // TODO SUBJECT TO CHANGE
        var current_density = $(this).parent().parent().find('input[name$="-density"]');
        var current_number = Number(current_density.val());
        if (current_number && current_number > 9999) {
            // TODO TODO TODO THIS DOES NOT WORK IN FIREFIX
            current_density.val(current_number.toExponential());
        }
    });
});
