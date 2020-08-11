$(document).ready(function() {

    let table_column_defs = [
    {"targets": [0], "visible": true,},
    {"targets": [1], "visible": true,},
    {"targets": [2], "visible": true,},
    {"targets": [3], "visible": true,},
    {"targets": [4], "visible": true,},
    {"targets": [5], "visible": false,},
    {"targets": [6], "visible": true,},
    {"targets": [7], "visible": false,},
    {"targets": [8], "visible": true,},
    {"targets": [9], "visible": true,},
    {responsivePriority: 1, targets: 0},
    {responsivePriority: 2, targets: 1},
    {responsivePriority: 3, targets: 2},
    {responsivePriority: 4, targets: 3},
    {responsivePriority: 5, targets: 4},
    {responsivePriority: 6, targets: 6},
    {responsivePriority: 7, targets: 8},
    {responsivePriority: 8, targets: 9},
    // {responsivePriority: 8, targets: 5},
    // {responsivePriority: 9, targets: 6},
    // {responsivePriority: 10, targets: 7},
    // none of these for this table.....{'sortable': false, 'targets': [30, 32]},
    //may need the following later - if pursue sorting on these fields
    //https://datatables.net/reference/option/columns.orderDataType
    //https://datatables.net/reference/option/columns.responsivePriority
    //{ "orderDataType": "dom-text", "targets": [ 30 ] },
    //{ "orderDataType": "dom-checkbox", "targets": [ 32 ] },
    ];

    $('#assayomicdatafileuploads').DataTable({
        "iDisplayLength": 25,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[4, "asc"]],
        "columnDefs": table_column_defs
    });

});
