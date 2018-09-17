$(document).ready(function() {
    window.TABLE = $('#units-table').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[0, "asc"]],
    });

    // Prevent "pop in".
    $("#units").css("display", "block");
});
