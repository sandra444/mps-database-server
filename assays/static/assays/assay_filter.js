$(document).ready(function() {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});

    var filters = {
        'organ_models': {},
        'groups': {},
        'compounds': {},
        'targets': {}
    };

    var group_criteria = {};
    var grouping_checkbox_selector = $('.grouping-checkbox');

    // Odd ID
    // var submit_button_selector = $('#submit');
    var submit_buttons_selector = $('.submit-button');
    var charts_button_selector = $('#charts_submit');
    var repro_button_selector = $('#repro_submit');
    // var back_button_selector = ;

    var number_of_points_selector = $('#number_of_points');
    var number_of_points_container_selector = $('#number_of_points_container');
    var select_user_group_message_selector = $('#select_user_group_message');

    var charts_name = 'charts';

    function show_plots() {
        // THIS IS A CRUDE WAY TO TEST THE GROUPING
        // Reset the criteria
        group_criteria = {};
        grouping_checkbox_selector.each(function() {
            if (this.checked) {
                if (!group_criteria[$(this).attr('data-group-relation')]) {
                    group_criteria[$(this).attr('data-group-relation')] = [];
                }
                group_criteria[$(this).attr('data-group-relation')].push(
                    $(this).attr('data-group')
                );
            }
        });

        var data = {
            // TODO TODO TODO CHANGE CALL
            call: 'fetch_data_points_from_filters',
            intention: 'charting',
            filters: JSON.stringify(filters),
            criteria: JSON.stringify(group_criteria),
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
        number_of_points_container_selector.removeClass('text-success text-danger');
        number_of_points_container_selector.addClass('text-warning');
        number_of_points_selector.html('Calculating, Please Wait');

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
                number_of_points_selector.html(json.number_of_points);
                if (json.number_of_points > 0) {
                    number_of_points_container_selector.removeClass('text-warning text-danger');
                    number_of_points_container_selector.addClass('text-success');
                    submit_buttons_selector.removeAttr('disabled');
                }
                else {
                    number_of_points_container_selector.removeClass('text-warning text-success');
                    number_of_points_container_selector.addClass('text-danger');
                    submit_buttons_selector.attr('disabled', 'disabled');
                }

                // Test if this is an "initial" query
                if (_.isEmpty(json.filters.groups)) {
                    select_user_group_message_selector.show();
                    submit_buttons_selector.attr('disabled', 'disabled');
                }
                else {
                    select_user_group_message_selector.hide();
                }

                $.each(json.filters, function (filter, contents) {
                    // Do not refresh current
                    if (filter === parent_filter) {
                        return true;
                    }

                    // Do not refresh MPS Model if you don't have to
                    // Crude, obviously
                    if (filter === 'organ_models' && _.keys(filters['organ_models']).length) {
                        return true;
                    }

                    var current_table = $('#filter_' + filter);
                    var current_body = current_table.find('tbody');

                    current_table.DataTable().clear();
                    current_table.DataTable().destroy();
                    current_body.empty();

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

                // Recalculate fixed headers
                $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
            },
            error: function (xhr, errmsg, err) {
                number_of_points_container_selector.removeClass('text-warning text-success');
                number_of_points_container_selector.addClass('text-danger');
                number_of_points_selector.html('An Error has Occurred');
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

    // TODO TODO TODO REPRO STUFF
    // TODO: UGLY
    var cv_tooltip = '<span data-toggle="tooltip" title="The CV is calculated for each time point and the value reported is the max CV across time points, or the CV if a single time point is present.  The reproducibility status is excellent if Max CV/CV < 5% (Excellent (CV)), acceptable if Max CV/CV < 15% (Acceptable (CV)), and poor if CV > 15% for a single time point (Poor (CV))" class="glyphicon glyphicon-question-sign" aria-hidden="true" data-placement="bottom"></span>';
    var icc_tooltip = '<span data-toggle="tooltip" title="The ICC Absolute Agreement of the measurements across multiple time points is a correlation coefficient that ranges from -1 to 1 with values closer to 1 being more correlated.  When the Max CV > 15%, the reproducibility status is reported to be excellent if > 0.8 (Excellent (ICC), acceptable if > 0.2 (Acceptable (ICC)), and poor if < 0.2 (Poor (ICC))" class="glyphicon glyphicon-question-sign" aria-hidden="true" data-placement="bottom"></span>';
    var repro_tooltip = '<span data-toggle="tooltip" title="Our classification of this grouping\'s reproducibility (Excellent > Acceptable > Poor/NA). If Max CV < 15% then the status is based on the  Max CV criteria, otherwise the status is based on the ICC criteria" class="glyphicon glyphicon-question-sign" aria-hidden="true" data-placement="bottom"></span>';
    var missing_tooltip = '<span data-toggle="tooltip" title="Quantity of data values whose values were missing from the data provided and were interpolated by the average of the data values at the same time point" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    var mad_tooltip = '<span data-toggle="tooltip" title="Median Absolute Deviation (MAD) scores of all chip measurement population at every time point.  A score > 3.5 or < -3.5 indicates that the chip is an outlier relative to the median of chip measurement population at a that time point" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    var comp_tooltip = '<span data-toggle="tooltip" title="The ICC is calculated for each chip relative to the median of all of the chips." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';

    // For making the table
    var repro_table_data = null;
    // For making the charts
    var chart_data = null;
    // For getting info on treatment groups
    var data_groups = null;
    var header_keys = null;

    // Table for the broad results
    var repro_table = null;

    var repro_set_info = $('#repro_set_info');

    function show_repro() {
        $('#filter').hide();
        $('#inter_repro').show();

        // Define what the legend is
        // TODO TODO TODO CONTRIVED FOR NOW
        var legend_key = 'Centers';
        if (false) {
            legend_key = 'Studies';
        }

        repro_table = $('#repro_table').DataTable({
            ajax: {
                url: '/assays_ajax/',
                data: {
                    // TODO TODO TODO THIS DEPENDS ON THE INTERFACE
                    call: 'fetch_data_points_from_filters',
                    intention: 'inter_repro',
                    filters: JSON.stringify(filters),
                    criteria: JSON.stringify(group_criteria),
                    csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
                },
                type: 'POST',
                dataSrc: function (json) {
                    repro_table_data = json.repro_table_data;
                    chart_data = json.chart_data;
                    data_groups = json.data_groups;
                    header_keys = json.header_keys;
                    treatment_groups = json.treatment_groups;

                    console.log(repro_table_data);
                    console.log(chart_data);
                    console.log(data_groups);
                    console.log(header_keys);
                    console.log(treatment_groups);

                    return repro_table_data;
                }
            },
            columns: [
                {
                    title: "Show Details",
                    "render": function (data, type, row) {
                        if (type === 'display' && row[1] === '') {
                            // var groupNum = row[10];
                            return '<input type="checkbox" class="big-checkbox repro-checkbox" data-repro-set="' + row[0] + '">';
                        }
                        return '';
                    },
                    "className": "dt-body-center",
                    "createdCell": function (td, cellData, rowData, row, col) {
                        if (cellData) {
                            $(td).css('vertical-align', 'middle')
                        }
                    },
                    "sortable": false
                },
                {
                    title: "Set",
                    type: "brute-numeric",
                    "render": function (data, type, row) {
                            return '<span class="badge badge-primary repro-set-info">' + row[0] + '</span>';
                    }
                },
                {
                    title: "Interpolation",
                    "render": function (data, type, row) {
                        if (type === 'display' && row[1] !== '') {
                            // var groupNum = row[10];
                            return '<input type="checkbox" class="repro-chart-checkbox"> ' + row[1];
                        }
                        return '';
                    }
                },
                {title: "Max Interpolated", data: '2'},
                {title: legend_key, data: '3'},
                {title: "# of Overlapping Time Points", data: '4'},
                {title: "<span style='white-space: nowrap;'>Max CV<br>or CV " + cv_tooltip + "</span>", data: '5'},
                {title: "<span style='white-space: nowrap;'>ICC " + icc_tooltip + "</span>", data: '6'},
                {title: "ANOVA P-Value", data: '7'},
                {
                    title: "Reproducibility<br>Status " + repro_tooltip,
                    data: '8',
                    render: function (data, type, row, meta) {
                        if (data == "Excellent (ICC)" || data == "Excellent (CV)") {
                            return '<td><span class="hidden">3</span>' + data + '</td>';
                        } else if (data == "Acceptable (ICC)" || data == "Acceptable (CV)") {
                            return '<td><span class="hidden">2</span>' + data + '</td>';
                        } else if (data == "Poor (ICC)" || data == "Poor (CV)") {
                            return '<td><span class="hidden">1</span>' + data + '</td>';
                        } else {
                            return '<td><span class="hidden">0</span>' + data + '<span data-toggle="tooltip" title="' + row[9] + '" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></td>';
                        }
                    }
                }
            ],
            "order": [[9, 'desc'], [ 1, "asc" ]],
            "createdRow": function(row, data, dataIndex) {
                if (data[8][0] === "E") {
                    $(row).find('td:eq(9)').css("background-color", "#74ff5b").css("font-weight", "bold");
                }
                else if (data[8][0] === "A") {
                    $(row).find('td:eq(9)').css("background-color", "#fcfa8d").css("font-weight", "bold");
                }
                else if (data[8][0] === "P") {
                    $(row).find('td:eq(9)').css("background-color", "#ff7863").css("font-weight", "bold");
                }
                else {
                    $(row).find('td:eq(9)').css("background-color", "Grey").css("font-weight", "bold");
                }
            },
            "responsive": true,
            dom: 'B<"row">lfrtip',
            fixedHeader: {headerOffset: 50},
            deferRender: true,
            initComplete: function () {
                // TODO TODO TODO
                // Draw necessary sections below
                console.log('Hello');
                draw_subsections();
            },
            drawCallback: function () {
                // Make sure tooltips displayed properly
                // TODO TODO TODO
                $('[data-toggle="tooltip"]').tooltip({container: "body"});
            }
        });

        // On reorder
        repro_table.on('order.dt', function () {
            var set_order = [];
            repro_table.column(1, {search:'applied'}).data().each(function(value, index) {
                set_order.push(value);
            });
            order_info(set_order);
        });
    }

    function draw_subsections() {
        var item_to_copy = $("#clone_container").find('[data-id="repro-data"]');
        var copy_to = $("#expanded_data");
        repro_table.rows().every(function() {
            var data = this.data();
            var group = data[0];
            var method = data[1];
            if (!method) {
                var icc_status = data[8];
                var current_clone = item_to_copy.first().clone(true);
                current_clone.addClass('repro-'+group);
                var repro_title = current_clone.find('[data-id="repro-title"]');
                var repro_status = current_clone.find('[data-id="repro-status"]');
                var data_table = current_clone.find('[data-id="data-table"]');

                repro_title.html('Set ' + group);

                if (icc_status[0] === 'E'){
                    repro_status.html('<em>'+icc_status+'</em>').css("background-color", "#74ff5b");
                } else if (icc_status[0] === 'A'){
                    repro_status.html('<em>'+icc_status+'</em>').css("background-color", "#fcfa8d");
                } else if (icc_status[0] === 'P'){
                    repro_status.html('<em>'+icc_status+'</em>').css("background-color", "#ff7863");
                } else {
                    repro_status.html('<em>'+icc_status+'</em><small style="color: black;"><span data-toggle="tooltip" title="'+data[13]+'" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></small>').css("background-color", "Grey");
                }

                populate_table(group, data_table);

                copy_to.append(current_clone);
            }
        });
    }

    function populate_table(set, current_table) {
        var current_body = current_table.find('tbody');

        var rows = [];

        $.each(header_keys['data'], function(index, key) {
            rows.push(
                '<tr><th>' + key + '</th><td>' + data_groups[set][index] + '</td></tr>'
            );
        });

        var current_treatment_group = data_groups[set][data_groups[set].length - 1];

        $.each(header_keys['treatment'], function(index, key) {
            rows.push(
                '<tr><th>' + key + '</th><td>' + treatment_groups[current_treatment_group][key] + '</td></tr>'
            );
        });

        rows = rows.join('');
        current_body.html(rows);
    }

    function draw_charts(set) {
        var chart_content_types = [
            'item',
            'average',
            'trimmed',
            'nearest',
            'linear',
            'quadratic',
            'cubic'
        ];

        $.each(chart_content_types, function(index, content_type) {
            var values = chart_data[set][content_type];
            if (values == null) {
                return true;
            }
            var all_null = true;
            for (var i = 1; i < values.length; i++) {
                for (var j = 1; j < values[i].length; j++) {
                    if (values[i][j] === "") {
                        values[i][j] = null;
                    } else {
                        all_null = false;
                    }
                }
            }
            if (all_null) {
                return false;
            }
            var data = google.visualization.arrayToDataTable(values);
            var options = {
                title: content_type,
                interpolateNulls: true,
                titleTextStyle: {
                    fontSize: 18,
                    bold: true,
                    underline: true
                },
                legend: {
                    position: 'top',
                    maxLines: 5,
                    textStyle: {
                        // fontSize: 8,
                        bold: true
                    }
                },
                hAxis: {
                    title: 'Time (Days)',
                    textStyle: {
                        bold: true
                    },
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    }
                },
                vAxis: {
                    title: 'VALUE UNIT HERE',
                    format: 'short',
                    textStyle: {
                        bold: true
                    },
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    },
                    minValue: 0,
                    viewWindowMode: 'explicit'
                },
                pointSize: 5,
                'chartArea': {
                    'width': '80%',
                    'height': '75%'
                },
                'height': 400,
                // 'width': 450,
                // Individual point tooltips, not aggregate
                focusTarget: 'datum',
                // Use an HTML tooltip.
                tooltip: {isHtml: true},
                intervals: {
                    style: 'sticks'
                }
            };

            // CONTRIVANCE FOR NOW
            if (content_type !== 'item') {
                chart = new google.visualization.LineChart(
                    $('.repro-' + set).find(
                        '[data-id="' + content_type + '_chart"]'
                    ).first()[0]);
            }
            else {
                chart = new google.visualization.ScatterChart(
                    $('.repro-' + set).find(
                        '[data-id="' + content_type + '_chart"]'
                    ).first()[0]);
            }


            if (chart) {
                var dataView = new google.visualization.DataView(data);

                // Change interval columns to intervals
                // ALSO CHANGES ROLE FOR STYLE COLUMNS
                var interval_setter = [0];

                i = 1;
                while (i < data.getNumberOfColumns()) {
                    interval_setter.push(i);
                    if (i + 2 < data.getNumberOfColumns() && values[0][i + 1].indexOf('~@i1') > -1) {
                        interval_setter.push({sourceColumn: i + 1, role: 'interval'});
                        interval_setter.push({sourceColumn: i + 2, role: 'interval'});
                        i += 2;
                    }
                    else if (i + 1 < data.getNumberOfColumns() && values[0][i + 1].indexOf('~@s') > -1) {
                        interval_setter.push({sourceColumn: i + 1, type: 'string', role: 'style'});
                        i += 1;
                    }
                    i += 1;
                }
                dataView.setColumns(interval_setter);

                chart.draw(dataView, options);
            }
        });
    }

    function generate_data_point_tooltip(time, value, chip_id) {
        return '<div style="padding:5px 5px 5px 5px;">' +
        '<table class="table">' +
        '<tr>' +
        '<td><b>' + time + '</b></td>' +
        '</tr>' +
        '<tr>' +
        '<td><b>Value</b></td>' +
        '<td>' + value + '</td>' +
        '</tr>' +
        '<tr>' +
        '<td><b>Item</b></td>' +
        '<td>' + chip_id + '</td>' +
        '</tr>' +
        '</table>' +
        '</div>';
    }

    function build_group_table(group_id) {
        var content = '';
        return content;
    }

    function build_cv_icc(cv, icc){
        content = '<tr><th>CV(%)</th><th>ICC-Absolute Agreement</th></tr><tr><td>'+cv+'</td><td>'+icc+'</td></tr>';
        return content;
    }

    //Checkbox click event
    $(document).on("click", ".repro-checkbox", function() {
        var checkbox = $(this);
        var number = checkbox.attr('data-repro-set');
        var current_repro = $('.repro-' + number);
        if (checkbox.is(':checked')) {
            current_repro.removeClass('hidden');

            draw_charts(number);
        } else {
            current_repro.addClass('hidden')
        }
        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body"});
    });

    $(document).on('mouseover', '.repro-info-box', function() {
        var current_group = Math.floor($(this).html());

    });

    $(document).on('mouseout', '.repro-info-box', function() {
        var current_group = Math.floor($(this).html());

    });

    function order_info(orderList){
        for (var i=0; i < orderList.length; i++) {
            $('#clone-container .repro-'+orderList[i]).appendTo('#clone-container');
        }
    }
    // TODO TODO TODO END REPRO STUFF

    // TODO, THESE TRIGGERS SHOULD BE BASED ON THE ANCHOR, NOT BUTTON CLICKS
    charts_button_selector.click(function() {
        show_plots();
    });

    repro_button_selector.click(function() {
        show_repro();
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

    // NAIVE FOR NOW
    $('#' + charts_name + 'refresh_plots').click(function() {
        show_plots();
    });
});
