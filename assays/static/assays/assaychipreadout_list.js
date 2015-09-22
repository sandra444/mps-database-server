$(document).ready(function() {
    $('#readouts').DataTable( {
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on setup not arbitrary ID
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
