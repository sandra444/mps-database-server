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

        var previous = null;
        for (var index in sorted_assays) {

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

        for (var index in sorted_assays) {
            $('<div>')
                .attr('id', charts + '_' + index)
                .attr('align', 'right')
                .addClass('chart-container')
                .appendTo(charts_id);
        }
    };

    window.CHARTS.make_charts = function(json, charts, changes_to_options) {
        var sorted_assays = json.sorted_assays;
        var assays = json.assays;

        for (index in sorted_assays) {
            var assay_unit = sorted_assays[index];
            var assay = assay_unit.split('\n')[0];
            var unit = assay_unit.split('\n')[1];

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

            // Merge options with the specified changes
            $.extend(options, changes_to_options);

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
    }
});
