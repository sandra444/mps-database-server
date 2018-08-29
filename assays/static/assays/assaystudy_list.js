$(document).ready(function() {
    $('#studies').DataTable( {
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "iDisplayLength": 50,
        // Initially sort on start date (descending), not ID
        "order": [ 2, "desc" ],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            },
            {
                "width": "10%",
                "targets": [0]
            },
            {
                "type": "numeric-comma",
                "targets": [5, 6, 7, 8]
            },
            {
                'visible': false,
                'targets': [7, 8, 11]
            },
            {
                'className': 'none',
                'targets': [9]
            }
        ]
    });
});
