// Define a custom sorting order
// Note that special characters must be escaped
$(document).ready(function() {
    var show_mps = $('#show_mps');
    var show_epa = $('#show_epa');
    var show_unassigned = $('#show_unassigned');

    var filters = {
        'MPS': true,
        'EPA': true,
        'Unassigned': true
    };

    // This function filters the dataTable rows
    $.fn.dataTableExt.afnFiltering.push(function(oSettings, aData, iDataIndex) {
        for (var filter in filters) {
            if (filters[filter] && aData[11].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    $.fn.dataTable.ext.type.order['frequency-range-pre'] = function (d) {
        switch (d) {
            case '&lt; 0.01%':         return 1;
            case '0.01 - &lt; 0.1%':   return 2;
            case '0.1 - &lt; 1%':      return 3;
            case '1 - &lt; 10%':       return 4;
            case '&gt;= 10%':          return 5;
        }
        return 0;
    };

    var drug_trials = $('#drugtrials').DataTable({
        dom: 'B<"row">lfrtip',
        "iDisplayLength": 50,
        "deferRender": true,
        // Initially sort on compound, not arbitrary ID
        "order": [[ 2, "asc" ], [ 1, "asc"]],
        // Apply custom sorting priorities to frequency column
        "columnDefs": [{
            "type": "frequency-range",
            "targets": 8
        }],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            },
            {
                "width": "10%",
                "targets": [0]
            },
            {
                "targets": [11],
                "visible": false,
                "searchable": true
            }
        ]
    });

    $('.table-filter').click(function() {
        filters['MPS'] = show_mps.prop('checked');
        filters['EPA'] = show_epa.prop('checked');
        filters['Unassigned'] = show_unassigned.prop('checked');

        // Redraw the table
        drug_trials.draw();
    });
});
