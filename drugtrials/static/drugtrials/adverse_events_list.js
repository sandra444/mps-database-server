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
            if (filters[filter] && aData[5].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    var adverse_events = $('#adverse_events').DataTable({
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on compound and frequency
        "order": [[ 1, "asc" ], [ 3, "desc"]],
        // Try to improve speed
        "deferRender": true,
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
                "targets": [5],
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
        adverse_events.draw();
    });
});
