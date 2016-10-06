// This file contains all shared functions for filtering on project
// Uses the global value "window.TABLE" to hold the dataTable in question
$(document).ready(function() {
    // The respective checkboxes
    var show_mps = $('#show_mps');
    var show_epa = $('#show_epa');
    var show_tctc = $('#show_tctc');
    var show_unassigned = $('#show_unassigned');

    // Whether the checkbox for a filter is checked
    var filters = {
        'MPS': true,
        'EPA': true,
        'TCTC': true,
        'Unassigned': true
    };

    // This function filters the dataTable rows
    $.fn.dataTableExt.afnFiltering.push(function(oSettings, aData, iDataIndex) {
        // This is a special exception to make sure that that the results table is not filtered in Compound Report
        if (oSettings.nTable.getAttribute('id') == 'results_table') {
            return true;
        }

        // For every filter, check to see if the checkbox is checked and if the string of interest is in the project column
        for (var filter in filters) {
            if (filters[filter] && aData[aData.length-1].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    // When a filter is clicked, set the filter values and redraw the table
    $('.table-filter').click(function() {
        filters['MPS'] = show_mps.prop('checked');
        filters['EPA'] = show_epa.prop('checked');
        filters['TCTC'] = show_tctc.prop('checked');
        filters['Unassigned'] = show_unassigned.prop('checked');

        // Redraw the table
        window.TABLE.draw();
    });
});
