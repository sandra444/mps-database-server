$(document).ready(function() {
    $('#celltypes').DataTable({
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on organ
        "order": [ 2, "asc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
