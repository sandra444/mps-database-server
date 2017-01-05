$(document).ready(function() {
    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    var current_key = 'chip';
    var percent_control = false;

    var radio_buttons_display = $('#radio_buttons');

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
    function make_charts(assays, charts) {
        // Clear existing charts
        var charts_id = $('#' + charts);
        charts_id.empty();

//        var assay_to_id = {};
//        var assay_ids = {};

        // Show radio_buttons if there is data
        if (Object.keys(assays).length > 0) {
            radio_buttons_display.show();
        }

        var sorted_assays = _.sortBy(_.keys(assays));

        var previous = null;
        for (var index in sorted_assays) {
            var assay_unit = sorted_assays[index];

            var current_chart_id = assay_unit.replace(/\W/g,'_');

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
                    .addClass('padded-row')
                    .css('min-height', 320);
                charts_id.append(previous
                    .append($('<div>')
                        .attr('id', charts + '_' + current_chart_id)
                        .addClass('col-sm-12 col-md-6 chart-container')
                    )
                );
            }
            else {
                previous.append($('<div>')
                    .attr('id', charts + '_' + current_chart_id)
                    .addClass('col-sm-12 col-md-6 chart-container')
                );
                previous = null;
            }
        }

        var bar_chart_list = [];

        for (index in sorted_assays) {
        	var assay_unit = sorted_assays[index];
            var assay = assay_unit.split('\n')[0];
            var unit = assay_unit.split('\n')[1];
            var current_chart_id = assay_unit.replace(/\W/g,'_');
            var add_to_bar_charts = true;

            var current_chart = c3.generate({
                bindto: '#' + charts + '_' + current_chart_id,

                data: {
                    columns: []
                },
                size: {
                  height: 320
                },
                axis: {
                    x: {
                        label: {
                            text: 'Time (days)',
                            // TODO ADD UNITS
                            //text: 'Time (' + timeUnits + ')',
                            position: 'outer-center'
                        }
                    },
                    // TODO Y AXIS LABEL
                    y: {
                        label: {
                            text: unit,
                            position: 'outer-middle'
                        }
                    }
                },
                title: {
                	text: assay
                },
                tooltip: {
                    format: {
                        value: function (value, ratio, id) {
                            var format = value % 1 === 0 ? d3.format(',d') : d3.format(',.2f');
                            return format(value);
                        }
                    }
                },
                padding: {
                  right: 10
                },
                // TODO this is not optimal
                // manually reposition axis label
                onrendered: function() {
                    $('.c3-axis-x-label').attr('dy', '35px');
                },
                color: {
                    // May need more colors later (these colors might also be too similar?)
                    pattern: pattern
                }
            });

            var num = 1;
            var xs = {};

            var sorted_keys = _.sortBy(_.keys(assays[assay_unit]));

            for (var i=0; i<sorted_keys.length; i++) {
                var current_key = sorted_keys[i];
                var current_data = assays[assay_unit][current_key];

                // Add to bar charts if no time scale exceeds 3 points
                if (add_to_bar_charts && current_data.time.length > 3) {
                    add_to_bar_charts = false;
                }

                xs[current_key] = 'x' + num;

                current_data.time.unshift('x' + num);
                current_data.values.unshift(current_key);

                current_chart.load({
                    xs: xs,

                    columns: [
                        current_data.time,
                        current_data.values
                    ]
                });

                num += 1;
            }
            // Callously triggering resizes can solve problems... but cause others
            // $(window).trigger('resize');

            // Add to bar charts if no time scale exceeds 3 points
            if (add_to_bar_charts) {
                bar_chart_list.push(current_chart);
            }
        }

        // Make bar charts
        for (var chart_index in bar_chart_list) {
            bar_chart_list[chart_index].transform('bar');
        }
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
                // console.log(json);
                make_charts(json.assays, 'charts');
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Initially by device
    get_readouts();

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
