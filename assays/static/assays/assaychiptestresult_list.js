$(document).ready(function() {
    $('#results').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: true,
        responsive: true,
        "iDisplayLength": 50,
        // Initially sort on study not arbitrary ID
        "order": [ 2, "asc" ],
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
