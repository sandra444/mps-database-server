$(document).ready(function() {
    window.TABLE = $('#adverse_events').DataTable({
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        responsive: true,
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
                "targets": [6],
                "visible": false,
                "searchable": true
            }
        ]
    });
});
