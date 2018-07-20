$(document).ready(function() {
    window.TABLE = $('#models').DataTable({
        "iDisplayLength": 100,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[1, "asc"]],
        "aoColumnDefs": [
            {
                "className": "dt-center",
                "targets": [0,2,4]
            },
            {
                "responsivePriority": 1,
                "bSortable": false,
                "width": '5%',
                "aTargets": [0]
            },
            {
                "responsivePriority": 1,
                "width": '15%',
                "aTargets": [1]
            },
            {
                "responsivePriority": 3,
                "width": '10%',
                "aTargets": [2]
            },
            {
                "responsivePriority": 4,
                "width": '45%',
                "aTargets": [3]
            },
            {
                "responsivePriority": 2,
                "width": '10%',
                "aTargets": [4]
            }
        ]
    });
});
