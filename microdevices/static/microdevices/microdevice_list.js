$(document).ready(function() {
    $('#microdevices').DataTable({
        "iDisplayLength": 200,
        "sDom": '<T<"clear">t>',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1]
            },
            {
                "width": "10%",
                "targets": [0]
            }
        ]
    });
    $('#models').DataTable({
        "iDisplayLength": 200,
        "sDom": '<T<"clear">t>',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1]
            },
            {
                'sortable': true,
                'visible': false,
                'targets': [6]
            },
            {
                "width": "10%",
                "targets": [0, 1]
            }
        ]
    });
});
