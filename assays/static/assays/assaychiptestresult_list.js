$(document).ready(function() {
    $('#results').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "iDisplayLength": 50,
        // Initially sort on study not arbitrary ID
        "order": [[2, "asc"], [3, "asc"]],
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
