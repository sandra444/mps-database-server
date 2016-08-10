$(document).ready(function() {
    var ids = [
        '#setups',
        '#plate_setups',
        '#readouts',
        '#plate_readouts',
        '#results',
        '#plate_results'
    ];

    $.each(ids, function(index, table_id) {
        if ($(table_id)[0]) {
            $(table_id).DataTable({
                "iDisplayLength": 400,
                dom: 'rt',
                fixedHeader: true,
                responsive: true,
                // Initially sort on start date (descending), not ID
                "order": [[1, "asc"], [2, "desc"]],
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
        }
    });
});
