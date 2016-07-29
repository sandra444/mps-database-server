$(document).ready(function() {
    $('#cellsamples').DataTable({
        dom: 'B<"row">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on receipt date
        "order": [ 2, "desc" ],
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
