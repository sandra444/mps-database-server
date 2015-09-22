$(document).ready(function() {
    $('#results').DataTable( {
        dom: 'T<"clear">lfrtip',
        "iDisplayLength": 50,
        // Initially sort on study not arbitrary ID
        "order": [ 2, "asc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });
});
