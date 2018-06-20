$(document).ready(function() {
    var  data_table = $('#studies').DataTable( {
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
                "targets": [5, 6]
            },
            {
                'className': 'none',
                'targets': [7]
            }
        ]
    });
});
