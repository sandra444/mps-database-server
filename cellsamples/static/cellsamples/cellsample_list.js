$(document).ready(function() {
    $('#cellsamples').DataTable({
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on receipt date
        "order": [ 2, "desc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
