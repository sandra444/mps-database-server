// This script was made to prevent redundant code in setup pages
$(document).ready(function () {
	// The current interface (in all lowercase, set in corresponding scripts)
	var current_interface = '';
	
	// SENSITIVE AND POTENTIALLY SUBJECT TO CHANGE
	// Get interface from url
	if (window.location.href.split('/')[4] == 'assaychipsetup') {
		current_interface = 'chip';
	}
	else {
		current_interface = 'plate';
	}
	
	// The id of the current id
	current_cellsample_id = null;
	
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
    
    $(document).on('click', '.open-cellsample-dialog', function (evt) {
    	current_cellsample_id = this.id.replace(/\D/g,'');
	    $("#dialog").dialog('open');
	    // Remove focus
	    $('.ui-dialog :button').blur();
    });
    
    $('.cellsample').click(function (evt) {
        var cellsampleId = this.id;
        var selectedInput = $('#id_assay' + current_interface + 'cells_set-' + current_cellsample_id + '-cell_sample');
        selectedInput.prop('value', cellsampleId);
        var cellsampleName = this.attributes["name"].value;
        var selectedLabel = $('#id_assay' + current_interface + 'cells_set-' + current_cellsample_id + '-cell_sample_label');
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
    var current_input = $('#id_assay' + current_interface + 'cells_set-' + current_id + '-cell_sample');

    while (current_input[0]) {
        if (current_input.val()) {
            var cell_name = $('#' + current_input.val()).attr('name');
            $('#id_assay' + current_interface + 'cells_set-' + current_id + '-cell_sample_label').text(cell_name);
        }

        // Turn density into scientific notation
        var current_density = $('#id_assay' + current_interface + 'cells_set-' + current_id + '-cellsample_density');
        var current_number = Number(current_density.val());
        if (current_number) {
            current_density.val(current_number.toExponential());
        }

        current_id += 1;
        current_input = $('#id_assay' + current_interface + 'cells_set-' + current_id + '-cell_sample');
    }

    // This will clear a cell sample when the button is pressed
    $('#clear_cell_sample').click(function() {
        var selectedInput = $('#id_assay' + current_interface + 'cells_set-' + current_cellsample_id + '-cell_sample');
        selectedInput.prop('value', '');
        var selectedLabel = $('#id_assay' + current_interface + 'cells_set-' + current_cellsample_id + '-cell_sample_label');
        selectedLabel.text('');
        $('#dialog').dialog('close');
    });
});