$(document).ready(function() {
    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    var current_key = 'chip';
    var percent_control = false;

    var radio_buttons_display = $('#radio_buttons');

    // Deprecated
    var pattern = [
        '#1f77b4', '#ff7f0e', '#2ca02c',
        '#d62728', '#9467bd',
        '#8c564b', '#e377c2','#7f7f7f',
        '#bcbd22', '#17becf',
        '#18F285',
        '#E6F02E',
        '#AAF514',
        '#52400B',
        '#CCCCCC'
    ];

    var ids = [
        '#setups',
        '#plate_setups'
    ];

    // Load the Visualization API and the corechart package.
    google.charts.load('current', {'packages':['corechart']});

    // Set a callback to run when the Google Visualization API is loaded.
    google.charts.setOnLoadCallback(get_readouts);

    $.each(ids, function(index, table_id) {
        if ($(table_id)[0]) {
            $(table_id).DataTable({
                "iDisplayLength": 400,
                dom: 'rt',
                fixedHeader: {headerOffset: 50},
                responsive: true,
                // Initially sort on start date (descending), not ID
                "order": [[1, "asc"], [2, "desc"]],
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
        }
    });

    // TODO Copy-pasting is irresponsible, please refrain from doing so in the future
    function make_charts(json, charts) {
        // Clear existing charts
        var charts_id = $('#' + charts);
        charts_id.empty();

//        var assay_to_id = {};
//        var assay_ids = {};

        // Show radio_buttons if there is data
        if (Object.keys(json).length > 0) {
            radio_buttons_display.show();
        }

        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        var previous = null;
        for (var index in sorted_assays) {
            // var assay_unit = sorted_assays[index];

            // var current_chart_id = assay_unit.replace(/\W/g,'_');

//            if (!assay_ids[assay_id]) {
//                assay_ids[assay_id] = true;
//                assay_to_id[assay] = assay_id;
//            }
//            else {
//                var assay_number = 2;
//
//                while (assay_ids[assay_id + '_' + assay_number]) {
//                    assay_number += 1;
//                }
//
//                assay_id = assay_id + '_' + assay_number;
//
//                assay_ids[assay_id] = true;
//                assay_to_id[assay] = assay_id;
//            }

            if (!previous) {
                previous = $('<div>')
                    //.addClass('padded-row')
                    .css('min-height', 400);
                charts_id.append(previous
                    .append($('<div>')
                        .attr('id', charts + '_' + index)
                        .addClass('col-sm-12 col-md-6 chart-container')
                    )
                );
            }
            else {
                previous.append($('<div>')
                    .attr('id', charts + '_' + index)
                    .addClass('col-sm-12 col-md-6 chart-container')
                );
                previous = null;
            }
        }

        for (index in sorted_assays) {
            var assay_unit = sorted_assays[index];
            var assay = assay_unit.split('\n')[0];
            var unit = assay_unit.split('\n')[1];
            var current_chart_id = assay_unit.replace(/\W/g, '_');
            // var add_to_bar_charts = true;

            // var data = google.visualization.arrayToDataTable([
            //     ['Year', 'Sales', 'Expenses'],
            //     ['2004', 1000, 400],
            //     ['2005', 1170, 460],
            //     ['2006', 660, 1120],
            //     ['2007', 1030, 540]
            // ]);

            var data = google.visualization.arrayToDataTable(assays[index]);

            var options = {
                title: assay,
                titleTextStyle: {
                    fontSize: 18,
                    bold: true,
                    underline: true
                },
                // curveType: 'function',
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
                    textStyle: {bold: true},
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    }
                    // baselineColor: 'none',
                    // ticks: []
                },
                vAxis: {
                    title: unit,
                    format: 'short',
                    textStyle: {bold: true},
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    }
                    // baselineColor: 'none',
                    // ticks: []
                },
                pointSize: 5,
                'chartArea': {
                    'width': '80%',
                    'height': '65%'
                },
                'height':400,
                focusTarget: 'category',
                intervals: { style: 'bars' }
            };

            // Find out whether to shrink text
            $.each(assays[index][0], function(index, column_header) {
                if (column_header.length > 12) {
                    options.legend.textStyle.fontSize = 8;
                }
            });

            var chart = null;

            if (assays[index].length > 4) {
                chart = new google.visualization.LineChart(document.getElementById(charts + '_' + index));
            }
            else if (assays[index].length > 1) {
                // Convert to categories
                data.insertColumn(0, 'string', data.getColumnLabel(0));
                // copy values from column 1 (old column 0) to column 0, converted to numbers
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    var val = data.getValue(i, 1);
                    if (val != null) {
                        data.setValue(i, 0, val + ''.valueOf());
                    }
                }
                // remove column 1 (the old column 0)
                data.removeColumn(1);

                chart = new google.visualization.ColumnChart(document.getElementById(charts + '_' + index));
            }

            if (chart) {
                var dataView = new google.visualization.DataView(data);

                // Change interval columns to intervals
                var interval_setter = [0];

                i = 1;
                while (i < data.getNumberOfColumns()) {
                    interval_setter.push(i);
                    if (i+2 < data.getNumberOfColumns() && assays[index][0][i+1].indexOf('_i1') > -1) {
                        interval_setter.push({sourceColumn: i + 1, role: 'interval'});
                        interval_setter.push({sourceColumn: i + 2, role: 'interval'});
                        i += 2;
                    }
                    i += 1;
                }
                dataView.setColumns(interval_setter);

                chart.draw(dataView, options);
            }
        }

        // Recalculate responsive and fixed headers
        $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    }

    function get_readouts() {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readouts',
                study: study_id,
                key: current_key,
                // Tells whether to convert to percent Control
                percent_control: percent_control,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                make_charts(json, 'charts');
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Initially by device
    // get_readouts();

    // Check when radio buttons changed
    $('input[type=radio][name=chart_type_radio]').change(function() {
        current_key = this.value;
        get_readouts();
    });

    // Check if convert_to_percent_control is clicked
    $('#convert_to_percent_control').click(function() {
        percent_control = this.checked;
        get_readouts();
    });
});
