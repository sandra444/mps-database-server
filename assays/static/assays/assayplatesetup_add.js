// This script is for displaying the layout for setups
// TODO NEEDS REFACTOR
// TODO PREFERABLY CONSOLIDATE THESE DISPLAY FUNCTIONS (DO NOT REPEAT YOURSELF)

$(document).ready(function () {
	var layout = $('#id_assay_layout');
    //  TODO REFACTOR
    // Specify that the location for the table is different
    window.LAYOUT.insert_after = $('.inline-group');

    var delete_link = $('.deletelink');
    if (delete_link.length > 0) {
        window.LAYOUT.models['assay_device_setup'] = delete_link.first().attr('href').split('/')[4];
    }
    // Otherwise, if this is the frontend, get the id from the URL
    else {
        window.LAYOUT.models['assay_device_setup'] = Math.floor(window.location.href.split('/')[5]);
    }

    // On layout change, acquire labels and build table
    layout.change( function() {
        window.LAYOUT.get_device_layout(layout.val(), 'assay_layout', false);
    });

    // (implies the setup is saved)
    if (window.LAYOUT.models['assay_device_setup']) {
        window.LAYOUT.get_device_layout(window.LAYOUT.models['assay_device_setup'], 'assay_device_setup', false);
    }
    // If a layout is initially chosen
    else if (layout.val()) {
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
});
