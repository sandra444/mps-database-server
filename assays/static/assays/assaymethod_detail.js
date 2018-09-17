$(document).ready(function() {
    window.TABLE1 = $('#assays-table').DataTable({
        "iDisplayLength": 10,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[0, "asc"]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [2]
            },
        ]
    });
    window.TABLE2 = $('#studies-table').DataTable({
        "iDisplayLength": 10,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[0, "asc"]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [3]
            },
        ]
    });

    // Prevent "pop in".
    $("#assays").css("display", "block");
    $("#studies").css("display", "block");
});
