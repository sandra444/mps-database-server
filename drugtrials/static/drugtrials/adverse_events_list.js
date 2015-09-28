$(document).ready(function() {
    $('#adverse_events').DataTable({
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
            }
        ]
    });
});
