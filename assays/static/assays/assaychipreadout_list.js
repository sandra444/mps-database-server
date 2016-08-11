$(document).ready(function() {
    $('#readouts').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: true,
        responsive: true,
        "iDisplayLength": 50,
        // Initially sort on setup not arbitrary ID
        "order": [[5, "desc"], [2, "asc"] ,[3, "asc"]],
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
