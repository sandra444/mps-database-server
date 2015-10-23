$(document).ready(function() {
    $('#microdevices').DataTable({
        "iDisplayLength": 200,
        "sDom": '<T<"clear">t>',
        "order": [[ 1, "asc" ]],
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
    $('#models').DataTable({
        "iDisplayLength": 200,
        "sDom": '<T<"clear">t>',
        "order": [[ 1, "asc" ]],
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
});
