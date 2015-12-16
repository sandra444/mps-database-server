$(document).ready(function() {
    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    function make_charts(assays) {
        for (var assay in assays) {
            var assay_id = assay.split('  ')[0];
            charts.append($('<div>')
                    .attr('id', 'chart_' + assay_id)
            );
        }
        for (assay in assays) {
            var assay_id = assay.split('  ')[0];

            var current_chart = c3.generate({
                bindto: '#chart_' + assay_id,

                data: {
                    columns: []
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

    function get_readouts() {
        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_readouts',
                study: study_id,
                key: 'chip',
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                console.log(json);
                make_charts(json.assays);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    get_readouts();
});
