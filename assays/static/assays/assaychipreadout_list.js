$(document).ready(function() {
    $('#readouts').DataTable( {
        dom: 'B<"row">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on setup not arbitrary ID
        "order": [[ 3, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            },
            {
                "width": "10%",
                "targets": [0]
            }
        ]
    });
});
