$(document).ready(function() {
    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    var radio_buttons_display = $('#radio_buttons');

    function make_charts(assays) {
        // Clear existing charts
        charts.empty();

        // Show radio_buttons if there is data
        if (Object.keys(assays).length > 0) {
            radio_buttons_display.show();
        }

        var previous = null;
        for (var assay in assays) {
            var assay_id = assay.split('  ')[0];
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
            var assay_id = assay.split('  ')[0];

            var current_chart = c3.generate({
                bindto: '#chart_' + assay_id,

                data: {
                    columns: []
                },

                size: {
                  height: 320
                },

                axis: {
                    x: {
                        label: {
                            text: 'Time',
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
                }
            });

            var num = 1;
            var xs = {};
            for (var current_key in assays[assay]) {
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
            url: "/assays_ajax",
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
