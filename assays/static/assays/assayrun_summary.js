$(document).ready(function() {
    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

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

    function make_charts(assays) {
        // Clear existing charts
        charts.empty();

        var assay_to_id = {};
        var assay_ids = {};

        // Show radio_buttons if there is data
        if (Object.keys(assays).length > 0) {
            radio_buttons_display.show();
        }

        var previous = null;
        for (var assay in assays) {
            var assay_id = assay.split('  ')[0];

            if (!assay_ids[assay_id]) {
                assay_ids[assay_id] = true;
                assay_to_id[assay] = assay_id;
            }
            else {
                var assay_number = 2;

                while (assay_ids[assay_id + '_' + assay_number]) {
                    assay_number += 1;
                }

                assay_id = assay_id + '_' + assay_number;

                assay_ids[assay_id] = true;
                assay_to_id[assay] = assay_id;
            }

            if (!previous) {
                previous = $('<div>')
                    .addClass('padded-row')
                    .css('min-height', 320);
                charts.append(previous
                    .append($('<div>')
                        .attr('id', 'chart_' + assay_id)
                        .addClass('col-sm-6 no-padding')
                    )
                );
            }
            else {
                previous.append($('<div>')
                    .attr('id', 'chart_' + assay_id)
                    .addClass('col-sm-6 no-padding')
                );
                previous = null;
            }
        }
        for (assay in assays) {
            var current_assay_id = assay_to_id[assay];

            var current_chart = c3.generate({
                bindto: '#chart_' + current_assay_id,

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
                            text: assay,
                            //text: name + ' (' + valueUnits + ')',
                            position: 'outer-middle'
                        }
                    }
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

            var sorted_keys = _.sortBy(_.keys(assays[assay]));

            for (var i=0; i<sorted_keys.length; i++) {
                var current_key = sorted_keys[i];
                var current_data = assays[assay][current_key];

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
            $(window).trigger('resize');
        }
    }

    function get_readouts(current_key) {
        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readouts',
                study: study_id,
                // TODO SET UP A WAY TO SWITCH BETWEEN CHIP AND COMPOUND
                key: current_key,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                //console.log(json);
                make_charts(json.assays);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Initially by device
    get_readouts('chip');

    // Check when radio buttons changed
    $('input[type=radio][name=chart_type_radio]').change(function() {
        get_readouts(this.value);
    });
});
