$(document).ready(function() {
    window.TABLE = $('#assays-table').DataTable({
        "iDisplayLength": 10,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[0, "asc"]]
    });
    window.TABLE = $('#studies-table').DataTable({
        "iDisplayLength": 10,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[0, "asc"]]
    });
    $("#assays").css("display", "block");
    $("#studies").css("display", "block");
});
