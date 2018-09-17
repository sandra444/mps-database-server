$(document).ready(function() {
    window.TABLE = $('#models').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[1, "asc"]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            },
            {
                "width": "50%",
                "targets": [6]
            },
            {
                "className": "dt-center",
                "targets": [2,3,4,5]
            }
        ]
    });

    $("td:contains('0')").each(function() {
        $(this).html('<span hidden>0</span>');
    });
});
