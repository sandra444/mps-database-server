$(document).ready(function() {
    var middleware_token = getCookie('csrftoken');

    window.TABLE = $('#adverse_events').DataTable({
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        iDisplayLength: 50,
        deferRender: true,
        ajax: {
            url: '/drugtrials_ajax/',
            data: {
                call: 'fetch_adverse_events_data',
                csrfmiddlewaretoken: middleware_token
            },
            type: 'POST'
        },
        columns: [
            {data: 'view', sortable:false, width: "10%"},
            {data: 'compound'},
            {data: 'event'},
            {data: 'number_of_reports'},
            {data: 'normalized_reports'},
            {data: 'estimated_usage'},
            {data: 'organ'},
            {data: 'black_box_warning'},
            {data: 'project', visible: false, searchable: true}
        ],
        "order": [[ 1, "asc" ], [ 3, "desc"]]
    });
});
