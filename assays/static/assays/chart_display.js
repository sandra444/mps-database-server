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
    var colors = [
        "rgba(0,128,0,0.4)", "rgba(26,140,0,0.4)", "rgba(51,152,0,0.4)",
        "rgba(77,164,0,0.4)", "rgba(102,176,0,0.4)", "rgba(128,188,0,0.4)",
        "rgba(153,200,0,0.4)", "rgba(179,212,0,0.4)", "rgba(204,224,0,0.4)",
        "rgba(230,236,0,0.4)", "rgba(255,255,0,0.4)", "rgba(243,230,0,0.4)",
        "rgba(231,204,0,0.4)", "rgba(219,179,0,0.4)", "rgba(207,153,0,0.4)",
        "rgba(195,128,0,0.4)", "rgba(183,102,0,0.4)", "rgba(171,77,0,0.4)",
        "rgba(159,51,0,0.4)", "rgba(147,26,0,0.4)", "rgba(135,0,0,0.4)"
    ];

    // Avoid magic strings for heatmap elements
    var heatmap_filters_selector = $('#heatmap_filters').find('select');
    var matrix_body_selector = $('#matrix_body');
    var heatmap_wrapper_selector = $('#heatmap_wrapper');
    // TODO TODO TODO TEMPORARILY EXPOSE
    var heatmap_data = {};
    // Charts
    var all_charts = {};
    var all_events = {};

    // Semi-arbitrary at the moment
    var treatment_group_table = $('#treatment_group_table');
    var treatment_group_display = $('#treatment_group_display');
    var treatment_group_head = $('#treatment_group_head');
    var treatment_group_data_table = null;

    // Probably should just have full data!
    var group_to_data = [];
    var device_to_group = {};
    var all_treatment_groups = [];

    // CONTRIVED DIALOG
    // Interestingly, this dialog should be separate and apart from chart_options
    // Really, I might as well make it from JS here
    // TODO PLEASE MAKE THIS NOT CONTRIVED SOON
    var dialog_example = $('#filter_popup');
    if (dialog_example) {
        dialog_example.dialog({
           closeOnEscape: true,
           autoOpen: false,
           close: function() {
               $('body').removeClass('stop-scrolling');
           },
           open: function() {
               $('body').addClass('stop-scrolling');
           }
        });
        dialog_example.removeProp('hidden');
    }

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

    // No longer in use
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

    window.CHARTS.display_treatment_groups = function(treatment_groups, header_keys) {
        device_to_group = {};

        // TODO KIND OF UGLY
        if (!header_keys) {
            header_keys = [
                // 'device',
                'organ_model',
                'cells',
                'compounds',
                'settings',
                'setups_with_same_group'
            ];
        }

        var headers = {
            // 'device': 'Device',
            'organ_model': 'MPS Model',
            'cells': 'Cells',
            'compounds': 'Compounds',
            'settings': 'Settings',
            'setups_with_same_group': 'Chips/Wells'
        };

        if (treatment_group_data_table) {
            treatment_group_table.DataTable().clear();
            treatment_group_table.DataTable().destroy();
        }

        treatment_group_display.empty();

        treatment_group_head.empty();

        var new_row =  $('<tr>').append(
            $('<th>').html('Group')
        );

        $.each(header_keys, function(index, item) {
            var new_td = $('<th>').html(headers[item]);
            new_row.append(new_td);
        });

        treatment_group_head.append(new_row);

        $.each(treatment_groups, function(index, treatment) {
            var group_index = (index + 1);
            var group_name = 'Group ' + group_index;
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

                // Somewhat sloppy conditional
                if (current_header === 'setups_with_same_group') {
                    $.each(new_td.find('a'), function (anchor_index, anchor) {
                        device_to_group[anchor.text] = index;
                    });
                }
            });

            all_treatment_groups.push(new_row.clone());
            // group_to_data[group_index] = new_row.clone();

            treatment_group_display.append(new_row);
        });

        treatment_group_data_table = treatment_group_table.DataTable({
            // Cuts out extra unneeded pieces in the table
            dom: 'B<"row">lfrtip',
            fixedHeader: {headerOffset: 50},
            responsive: true,
            // paging: false,
            order: [[ 0, "asc" ]],
            // Needed to destroy old table
            bDestroy: true,
            // Try to get a more reasonable size for cells
            columnDefs: [
                // Treat the group column as if it were just the number
                { "type": "brute-numeric", "targets": 0, "width": "10%" }
                // Poses a problem due to variable table
                // { "width": "10%", "targets": 1 },
                // { "width": "15%", "targets": 2 },
                // { "width": "20%", "targets": 3 },
                // { "width": "15%", "targets": 4 }
            ]
        });

        // TODO NOT DRY
        // Swap positions of filter and length selection; clarify filter
        $('.dataTables_filter').css('float', 'left').prop('title', 'Separate terms with a space to search multiple fields');
        $('.dataTables_length').css('float', 'right');
        // Reposition download/print/copy
        $('.DTTT_container').css('float', 'none');


        // Recalculate responsive and fixed headers
        $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    };

    window.CHARTS.get_heatmap_dropdowns = function(starting_index) {
        if (heatmap_data.matrices && _.keys(heatmap_data.matrices).length > 0) {
            heatmap_wrapper_selector.show();

            var current_index = 0;
            var data_level = heatmap_data.values;
            var current;

            while (current_index < starting_index) {
                current = heatmap_filters_selector.eq(current_index);
                data_level = data_level[current.val()];
                current_index++;
            }

            while (current_index < heatmap_filters_selector.length) {
                current = heatmap_filters_selector.eq(current_index);
                var former_value = current.val();

                if (former_value === null || starting_index < current_index) {
                    current.empty();
                    $.each(_.sortBy(_.keys(data_level)), function (index, key) {
                        var dropdown_text = key.split('\n')[0];
                        current.append($('<option>').val(key).text(dropdown_text));
                    });

                    if (former_value && current.find('option[value="' + former_value + '"]').length > 0) {
                        current.val(former_value);
                    }
                }

                data_level = data_level[current.val()];
                current_index++;
            }

            // Make the heatmap
            // Get the values for the heatmap
            var means = {};

            $.each(data_level, function (key, values) {
                means[key] = d3.mean(values);
            });

            var median = d3.median(means);
            // Get the min
            var min_value = _.min(means);
            min_value -= min_value * 0.000001;
            // Get the max
            var max_value = _.max(means);
            max_value += max_value * 0.000001;
            // Get the colorscale
            var color_scale = d3.scale.quantile()
                .domain([min_value, median, max_value])
                .range(colors);

            // Actually display the heatmap
            var current_matrix = heatmap_data.matrices[$('#id_heatmap_matrix').val()];

            matrix_body_selector.empty();

            // Check to see if new forms will be generated
            for (var row_index = 0; row_index < current_matrix.length; row_index++) {
                var row_id = 'row_' + row_index;
                var current_row = $('<tr>')
                    .attr('id', row_id);

                for (var column_index = 0; column_index < current_matrix[row_index].length; column_index++) {
                    var new_cell = $('<td>');

                    var current_key = row_index + '_' + column_index;
                    var value = data_level[current_key];
                    var mean_value = means[current_key];

                    if (value) {
                        new_cell.html(value.join(', '));
                        new_cell.css('background-color', color_scale(mean_value));
                    }
                    else {
                        new_cell.css('background-color', '#606060');
                    }

                    // Add
                    current_row.append(new_cell);
                }

                matrix_body_selector.append(current_row);
            }
        }
        else {
            heatmap_wrapper_selector.hide();
        }
    };

    // window.CHARTS.make_heatmap = function() {
    //
    // };

    window.CHARTS.make_charts = function(json, charts, changes_to_options) {
        // Remove triggers
        if (all_events[charts]) {
            $.each(all_events[charts], function(index, event) {
                google.visualization.events.removeListener(event);
            });
        }

        // Clear all charts
        all_charts[charts] = [];
        all_events[charts] = [];
        group_to_data[charts] = [];

        // Show the chart options
        // NOTE: the chart options are currently shown by default, subject to change

        heatmap_data = json.heatmap;

        window.CHARTS.get_heatmap_dropdowns(0);

        // Naive way to learn whether dose vs. time
        var is_dose = $('#' + charts + 'dose_select').prop('checked');

        var x_axis_label = 'Time (Days)';
        if (is_dose) {
            x_axis_label = 'Dose (μM)';
        }

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
                // Changes styling and prevents flickering issue
                // tooltip: {
                //     isHtml: true
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
                    title: x_axis_label,
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

            // NAIVE: I shouldn't perform a whole refresh just to change the scale!
            if (document.getElementById(charts + 'category_select').checked) {
                options.focusTarget = 'category';
            }

            if (document.getElementById(charts + 'log_x').checked) {
                options.hAxis.scaleType = 'log';
            }
            if (document.getElementById(charts + 'log_y').checked) {
                options.vAxis.scaleType = 'log';
            }

            // Merge options with the specified changes
            $.extend(options, changes_to_options);

            // REMOVED FOR NOW
            // Find out whether to shrink text
            // $.each(assays[index][0], function(index, column_header) {
            //     if (column_header.length > 12) {
            //         options.legend.textStyle.fontSize = 10;
            //     }
            // });

            var chart = null;

            // Line chart if more than one time point and less than 101 colors
            if (assays[index].length > 2 && assays[index][0].length < 101) {
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
            // Nothing if more than 100 colors
            else if (assays[index][0].length > 100) {
                document.getElementById(charts + '_' + index).innerHTML = '<div class="alert alert-danger" role="alert">' +
                    '<span class="glyphicon glyphicon-warning-sign" aria-hidden="true"></span>' +
                    '<span class="sr-only">Danger:</span>' +
                    ' <strong>' + assay + ' ' + unit + '</strong>' +
                    '<br>This plot has too many data points, please try filtering.' +
                '</div>'
            }
            // Bar chart if only one time point
            else if (assays[index].length > 1) {
                // Convert to categories
                data.insertColumn(0, 'string', data.getColumnLabel(0));
                // copy values from column 1 (old column 0) to column 0, converted to numbers
                for (var i = 0; i < data.getNumberOfRows(); i++) {
                    var val = data.getValue(i, 1);
                    // I don't mind this type-coercion, null, undefined (and maybe 0?) don't need to be parsed
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
                    if (i + 2 < data.getNumberOfColumns() && assays[index][0][i+1].indexOf('~@i1') > -1) {
                        interval_setter.push({sourceColumn: i + 1, role: 'interval'});
                        interval_setter.push({sourceColumn: i + 2, role: 'interval'});
                        i += 2;
                    }
                    i += 1;
                }
                dataView.setColumns(interval_setter);

                chart.draw(dataView, options);

                chart.chart_index = index;

                all_charts[charts].push(chart);
            }
        }

        window.CHARTS.display_treatment_groups(json.treatment_groups, json.header_keys);

        for (var index=0; index < all_charts[charts].length; index++) {
            group_to_data[charts].push({});

            for (i=0; i < assays[index][0].length; i++) {
                if (assays[index][0][i].indexOf('~@i1') === -1 && assays[index][0][i].indexOf('~@i2') === -1) {
                    // Need to link EACH CHARTS values to the proper group
                    // EMPHASIS ON EACH CHART
                    // Somewhat naive
                    if (document.getElementById(charts + 'group_select').checked) {
                        // NOTE -1
                        group_to_data[charts][index][i] = assays[index][0][i].replace(/\D/g, '') - 1;
                    }
                    else {
                        var device = assays[index][0][i].split(' || ')[0];
                        // console.log(device);
                        // console.log(device_to_group);
                        group_to_data[charts][index][i] = device_to_group[device];
                    }
                }
            }

            // Makes use of a somewhat zany closure
            var current_event = google.visualization.events.addListener(all_charts[charts][index], 'onmouseover', (function (charts, chart_index) {
                return function (entry) {
                    var current_pos = $(all_charts[charts][chart_index].container).position();
                    var current_top = current_pos.top + 75;
                    var current_left = $('#breadcrumbs').position.left;
                    if (entry.row === null && entry.column) {
                        var row_clone = all_treatment_groups[group_to_data[charts][chart_index][entry.column]].clone().addClass('bg-warning');
                        if (row_clone) {
                            $('#group_display_body').empty().append(row_clone);

                            $('#group_display').show()
                                .css({top: current_top, left: current_left, position:'absolute'});
                        }
                    }
                }
            })(charts, index));
            all_events[charts].push(current_event);

            current_event = google.visualization.events.addListener(all_charts[charts][index], 'onmouseout', function () {
                $('#group_display').hide();
            });
            all_events[charts].push(current_event);
        }
    };

    // Triggers for heatmap filters
    heatmap_filters_selector.change(function() {
        window.CHARTS.get_heatmap_dropdowns(Math.floor($(this).data('heatmap-index')));
    });

    // Triggers for spawning filters
    // TODO REVISE THIS TERRIBLE SELECTOR
    $('.glyphicon-filter').click(function() {
        dialog_example.dialog('open');
    });
});
