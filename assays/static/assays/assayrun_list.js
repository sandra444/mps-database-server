$(document).ready(function() {
    $('#studies').DataTable( {
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on start date (descending), not ID
        "order": [ 4, "desc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
