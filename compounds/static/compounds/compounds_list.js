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
            if (filters[filter] && aData[9].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    var table = $('#compounds').DataTable({
        dom: 'T<"clear">lfrtip',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1, 10]
            },
            {
                "targets": [4, 9],
                "visible": false,
                "searchable": true
            },
            {
                "width": "10%",
                "targets": [0]
            }
        ],
        "iDisplayLength": 25
    });

    $('.table-filter').click(function() {
        filters['MPS'] = show_mps.prop('checked');
        filters['EPA'] = show_epa.prop('checked');
        filters['Unassigned'] = show_unassigned.prop('checked');

        // Redraw the table
        table.draw();
    });
});
