$(document).ready(function() {
    $('#setups').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: true,
        responsive: true,
        "iDisplayLength": 50,
        "order": [[ 1, "asc" ]],
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
