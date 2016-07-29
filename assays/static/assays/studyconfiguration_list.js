$(document).ready(function() {
    $('#studyconfigurations').DataTable( {
        dom: 'B<"row">lfrtip',
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
