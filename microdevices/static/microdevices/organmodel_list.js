$(document).ready(function() {
    window.TABLE = $('#models').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[3, "asc"], [2, "asc"]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1]
            },
            {
                'sortable': true,
                'visible': false,
                'targets': [7]
            },
            {
                "width": "10%",
                "targets": [0, 1]
            }
        ]
    });
});
