$(document).ready(function() {
    window.TABLE = $('#locations-table').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[ 0, "asc" ]],
        // "order": [[ 1, "asc" ]],
        // "aoColumnDefs": [
        //     {
        //         "bSortable": false,
        //         "aTargets": [0]
        //     },
        //     {
        //         "width": "10%",
        //         "targets": [0]
        //     }
        // ]
    });

    // Prevent "pop in".
    $("#locations").css("display", "block");
});
