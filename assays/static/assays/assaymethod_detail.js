$(document).ready(function() {
    window.TABLE = $('#models').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[1, "asc"]]
    });
    $("#assays").css("display", "block");
});
