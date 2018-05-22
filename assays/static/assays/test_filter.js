$(document).ready(function() {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});

    var filters = {
        'groups': {},
        'organ_models': {},
        'compounds': {},
        'targets': {}
    };

    var charts_name = 'charts';

    function show_plots() {
        var data = {
            // TODO TODO TODO CHANGE CALL
            call: 'fetch_data_points',
            filters: JSON.stringify(filters),
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: data,
            success: function (json) {
                $('#results').prop('hidden', false);
                $('#filter').prop('hidden', true);

                // HIDE THE DATATABLE HEADERS HERE
                $('.filter-table').prop('hidden', true);

                window.CHARTS.prepare_side_by_side_charts(json, charts_name);
                window.CHARTS.make_charts(json, charts_name);

                // Recalculate responsive and fixed headers
                $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
                $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function refresh_filters(parent_filter) {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                call: 'fetch_pre_submission_filters',
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
                filters: JSON.stringify(filters)
            },
            success: function (json) {
                $('#number_of_points').html(json.number_of_points);

                $.each(json.filters, function (filter, contents) {
                    // Do not refresh current
                    if (filter === parent_filter) {
                        return true;
                    }

                    var current_table = $('#filter_' + filter);
                    var current_body = current_table.find('tbody');

                    current_body.empty();
                    current_table.DataTable().clear();
                    current_table.DataTable().destroy();

                    var initial_filter = filters[filter];
                    var current_filter = {};

                    var rows_to_add = [];
                    $.each(contents, function (index, content) {
                        var content_id = content[0];
                        var content_name = content[1];
                        var checkbox = '<input class="big-checkbox filter-checkbox" data-filter="' + filter + '" type="checkbox" value="' + content_id + '">';
                        if (initial_filter[content_id]) {
                            current_filter[content_id] = true;
                            checkbox = '<input checked class="big-checkbox filter-checkbox" data-filter="' + filter + '" type="checkbox" value="' + content_id + '">';
                        }

                        rows_to_add.push(
                            '<tr>' +
                            '<td>' + checkbox + '</td>' +
                            '<td>' + content_name + '</td>' +
                            '</tr>'
                        )
                    });

                    // Swap to new filter
                    filters[filter] = current_filter;

                    current_body.html(rows_to_add.join(''));

                    // var table_ordering = [[1, 'asc']];
                    // if (_.keys(current_filter).length) {
                    //     table_ordering = [[0, "asc"], [1, 'asc']];
                    // }

                    current_table.DataTable({
                        // Cuts out extra unneeded pieces in the table
                        dom: 'lfrtip',
                        fixedHeader: {headerOffset: 50},
                        responsive: true,
                        // order: table_ordering,
                        order: [1, 'asc'],
                        // Needed to destroy old table
                        bDestroy: true,
                        columnDefs: [
                            // Treat the group column as if it were just the number
                            { "type": "dom-checkbox", "targets": 0, "width": "10%" },
                            { "className": "dt-center", "targets": 0}
                        ]
                    });
                });

                // TODO NOT DRY
                // Swap positions of filter and length selection; clarify filter
                $('.dataTables_filter').css('float', 'left').prop('title', 'Separate terms with a space to search multiple fields');
                $('.dataTables_length').css('float', 'right');

                // Recalculate responsive and fixed headers
                $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
                $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    $(document).on('change', '.filter-checkbox', function() {
        if (this.checked) {
            filters[$(this).attr('data-filter')][this.value] = true;
        }
        else {
            delete filters[$(this).attr('data-filter')][this.value];
        }
        refresh_filters($(this).attr('data-filter'));
    });
    refresh_filters();

    $('#submit').click(function() {
        show_plots();
    });

    $('#back').click(function() {
        $('#filter').prop('hidden', false);
        $('.filter-table').prop('hidden', false);
        $('#results').prop('hidden', true);
    });

    // Setup triggers
    $('#' + charts_name + 'chart_options').find('input').change(function() {
        show_plots();
    });
});
