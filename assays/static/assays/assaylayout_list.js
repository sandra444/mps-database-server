$(document).ready(function() {
    $('#layouts').DataTable( {
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on start date (descending), not ID
        "order": [ 2, "asc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
