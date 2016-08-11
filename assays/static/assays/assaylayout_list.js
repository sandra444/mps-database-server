$(document).ready(function() {
    $('#layouts').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: true,
        responsive: true,
        "iDisplayLength": 50,
        // Initially sort on start date (descending), not ID
        "order": [[1, "asc"], [2, "asc"]],
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
