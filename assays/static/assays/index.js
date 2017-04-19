// DEPRECATED: Index and Study List now have the same content
$(document).ready(function() {
    $('#studies').DataTable( {
        "iDisplayLength": 50,
        fixedHeader: {headerOffset: 50},
        responsive: true,
        // Initially sort on start date (descending), not ID
        "order": [ 3, "desc" ],
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
