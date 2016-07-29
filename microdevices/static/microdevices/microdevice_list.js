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
        if (oSettings.nTable.getAttribute('id') != 'models') {
            return true;
        }

        for (var filter in filters) {
            if (filters[filter] && aData[6].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    $('#microdevices').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1]
            },
            {
                "width": "10%",
                "targets": [0]
            }
        ]
    });

    var models = $('#models').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1]
            },
            {
                'sortable': true,
                'visible': false,
                'targets': [6]
            },
            {
                "width": "10%",
                "targets": [0, 1]
            }
        ]
    });

    $('.table-filter').click(function() {
        filters['MPS'] = show_mps.prop('checked');
        filters['EPA'] = show_epa.prop('checked');
        filters['Unassigned'] = show_unassigned.prop('checked');

        // Redraw the table
        models.draw();
    });
});
