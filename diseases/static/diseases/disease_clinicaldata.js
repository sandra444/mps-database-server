$(document).ready(function() {
    window.TABLE = $('#trials').DataTable({
        "iDisplayLength": 100,
        "sDom": '<<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[2, "asc"]],
        "aoColumnDefs": [
            {
                "width": "5%",
                "targets": [1, 2, 3]
            }
        ]
    });
});
