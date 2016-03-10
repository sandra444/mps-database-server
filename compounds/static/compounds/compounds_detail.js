$(document).ready(function() {
    var target_table = $('#target_table');

    target_table.DataTable({
        dom: 'T<"clear">ft',
        "order": [[4, "desc"], [ 2, "asc" ], [3, "asc"], [0, "asc"]],
        "iDisplayLength": 100
    });

    target_table.show();
});
