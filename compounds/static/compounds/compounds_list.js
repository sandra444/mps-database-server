$(document).ready(function() {
    $('#compounds').DataTable({
        dom: 'T<"clear">lfrtip',
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0,1,10]
            },
            {
                "targets": [4],
                "visible": false,
                "searchable": true
            },
            {
                "width": "10%",
                "targets": [0]
            }
        ],
        "iDisplayLength": 25
    });
});
