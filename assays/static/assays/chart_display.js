// Contains functions for making charts for data

// Global variable for charts
window.CHARTS = {};

// Load the Visualization API and the corechart package.
// google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
// THE CALLBACK FUNCTION IS NOT DEFINED HERE BUT IN THE RESPECTIVE MAIN FILE
// SUBJECT TO CHANGE
// google.charts.setOnLoadCallback(window.CHARTS.callback);

$(document).ready(function () {
    window.CHARTS.prepare_chart_options = function(charts) {
        var options = {};

        $.each($('#' + charts + 'chart_options').find('input'), function() {
            if (this.checked) {
                options[this.name.replace(charts, '')] = this.value;
            }
        });

        return options;
    };

    window.CHARTS.prepare_side_by_side_charts = function(json, charts) {
        // Clear existing charts
        var charts_id = $('#' + charts);
        charts_id.empty();

        // If errors, report them and then terminate
        if (json.errors) {
            alert(json.errors);
            return;
        }

        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        var previous = null;
        for (var index in sorted_assays) {
            if (assays[index].length > 1) {
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
        }
    };

    window.CHARTS.prepare_charts_by_table = function(json, charts) {
        // Clear existing charts
        var charts_id = $('#' + charts);
        charts_id.empty();

        // If errors, report them and then terminate
        if (json.errors) {
            alert(json.errors);
            return;
        }

        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        for (var index in sorted_assays) {
            if (assays[index].length > 1) {
                $('<div>')
                    .attr('id', charts + '_' + index)
                    .attr('align', 'right')
                    .addClass('chart-container')
                    .appendTo(charts_id);
            }
        }
    };

    window.CHARTS.display_treament_groups = function(treatment_groups) {
        // TODO KIND OF UGLY
        var header_keys = [
            // 'device',
            'organ_model',
            'cells',
            'compounds',
            'setups_with_same_group'
        ];
        var headers = {
            // 'device': 'Device',
            'organ_model': 'Organ Model',
            'cells': 'Cells',
            'compounds': 'Compounds',
            'setups_with_same_group': 'Chips/Wells'
        };

        // Semi-arbitrary at the moment
        var treatment_group_table = $('#treatment_group_table');
        var treatment_group_display = $('#treatment_group_display');
        var treatment_group_head = $('#treatment_group_head');

        treatment_group_head.empty();

        var new_row =  $('<tr>').append(
            $('<th>').html('Group')
        );

        $.each(header_keys, function(index, item) {
            var new_td = $('<th>').html(headers[item]);
            new_row.append(new_td);
        });

        treatment_group_head.append(new_row);

        treatment_group_display.empty();
        treatment_group_table.DataTable().clear();
        treatment_group_table.DataTable().destroy();

        $.each(treatment_groups, function(index, treatment) {
            var group_name = 'Group ' + (index + 1);
            var group_id = group_name.replace(' ', '_');

            var new_row = $('<tr>')
                .attr('id', group_id)
                .append(
                $('<td>').html(group_name)
            );

            $.each(header_keys, function(header_index, current_header) {
                // Replace newlines with breaks
                var new_td = $('<td>').html(treatment[current_header].split("\n").join("<br />"));
                new_row.append(new_td);
            });

            treatment_group_display.append(new_row);
        });

        treatment_group_table.DataTable({
            // Cuts out extra unneeded pieces in the table
            dom: 'B<"row">rt',
            fixedHeader: {headerOffset: 50},
            responsive: true,
            paging: false,
            order: [[ 0, "asc" ]],
            // Needed to destroy old table
            bDestroy: true,
            // Try to get a more reasonable size for cells
            columnDefs: [
                // Treat the group column as if it were just the number
                { "type": "num", "targets": 0 },
                { "width": "20%", "targets": 2 },
                { "width": "30%", "targets": 3 },
                { "width": "30%", "targets": 4 }
            ]
        });

        // TODO NOT DRY
        // Reposition download/print/copy
        $('.DTTT_container').css('float', 'none');

        // Clarify usage of sort
        $('.sorting').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
        $('.sorting_asc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
        $('.sorting_desc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');

        // Recalculate responsive and fixed headers
        $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    };

    window.CHARTS.make_charts = function(json, charts, changes_to_options) {
        // Show the chart options
        // NOTE: the chart options are currently shown by default, subject to change

        // If nothing to show
        if (!json.assays) {
            $('#' + charts).html('No data to display');
        }

        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        for (index in sorted_assays) {
            var assay_unit = sorted_assays[index];
            var assay = assay_unit.split('\n')[0];
            var unit = assay_unit.split('\n')[1];

            var data = google.visualization.arrayToDataTable(assays[index]);

            var options = {
                title: assay,
                interpolateNulls: true,
                // tooltip: {
                //     isHtml: true
                //     trigger: 'selection'
                // },
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
                    textStyle: {
                        bold: true
                    },
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
                    textStyle: {
                        bold: true
                    },
                    titleTextStyle: {
                        fontSize: 14,
                        bold: true,
                        italic: false
                    },
                    // This doesn't seem to interfere with displaying negative values
                    minValue: 0,
                    viewWindowMode: 'explicit'
                    // baselineColor: 'none',
                    // ticks: []
                },
                pointSize: 5,
                'chartArea': {
                    'width': '80%',
                    'height': '65%'
                },
                'height':400,
                // Individual point tooltips, not aggregate
                focusTarget: 'datum',
                intervals: {
                    style: 'bars'
                }
            };

            // Merge options with the specified changes
            $.extend(options, changes_to_options);

            // Find out whether to shrink text
            $.each(assays[index][0], function(index, column_header) {
                if (column_header.length > 12) {
                    options.legend.textStyle.fontSize = 10;
                }
            });

            var chart = null;

            if (assays[index].length > 4) {
                chart = new google.visualization.LineChart(document.getElementById(charts + '_' + index));

                // If the scale is not already small
                if (assays[index][assays[index].length-1][0] - assays[index][1][0] > 1) {
                    // If line chart and small difference between last two numbers, make the max horizontal value one day higher than necessary
                    if (assays[index][assays[index].length-1][0] - assays[index][assays[index].length-2][0] < 0.5) {
                        options.hAxis.maxValue = assays[index][assays[index].length - 1][0] + 1;
                    }
                    // Do the same for minimum
                    if (assays[index][2][0] - assays[index][1][0] < 0.5 ) {
                        options.hAxis.minValue = assays[index][1][0] - 1;
                    }
                }
            }
            else if (assays[index].length > 1) {
                // Convert to categories
                data.insertColumn(0, 'string', data.getColumnLabel(0));
                // copy values from column 1 (old column 0) to column 0, converted to numbers
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    var val = data.getValue(i, 1);
                    if (val != null) {
                        // PLEASE NOTE: Floats are truncated to 3 decimals
                        data.setValue(i, 0, parseFloat(val.toFixed(3)) + ''.valueOf());
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

        window.CHARTS.display_treament_groups(json.treatment_groups);

        // Triggers for legends (TERRIBLE SELECTOR)
        $('g:has("g > text")').mouseover(function() {
            var text_section = $(this).find('text');
            if (text_section.length === 1) {
                var content_split = $(this).find('text').text().split(/(\d+)/);
                var current_pos = $(this).position();
                // Make it appear slightly below the legend
                var current_top = current_pos.top + 50;
                // Get the furthest left it should go
                var current_left = $('#breadcrumbs').position.left;
                // var current_left = 200;
                var row_id_to_use = '#' + content_split[0].replace(' ', '_') + content_split[1];
                var row_clone = $(row_id_to_use).clone().addClass('bg-warning');

                $('#group_display_body').empty().append(row_clone);

                var second_row = $('<tr>').addClass('bg-warning');
                var hidden_rows = false;

                $(row_id_to_use).find('td:hidden').each(function(index) {
                    hidden_rows = true;
                    second_row.append($(this).clone().show());
                });

                if (hidden_rows) {
                    $('#group_display_body').append(second_row);
                }

                $('#group_display').show()
                    .css({top: current_top, left: current_left, position:'absolute'});
            }
        }).mouseout(function() {
            $('#group_display').hide();
        });
    };
});
