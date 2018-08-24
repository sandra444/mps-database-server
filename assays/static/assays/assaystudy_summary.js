$(document).ready(function() {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(get_readouts);
    google.charts.setOnLoadCallback(reproPie);

    window.GROUPING.refresh_function = get_readouts;

    var charts = $('#charts');
    var study_id = Math.floor(window.location.href.split('/')[5]);

    // Name for the charts for binding events etc
    var charts_name = 'charts';

    function get_readouts() {
        var data = {
            // TODO TODO TODO CHANGE CALL
            call: 'fetch_data_points',
            study: study_id,
            criteria: JSON.stringify(window.GROUPING.get_grouping_filtering()),
            post_filter: JSON.stringify(window.GROUPING.current_post_filter),
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };

        var options = window.CHARTS.prepare_chart_options(charts_name);

        data = $.extend(data, options);

        // Show spinner
        window.spinner.spin(
            document.getElementById("spinner")
        );

        $.ajax({
            url: "/assays_ajax/",
            type: "POST",
            dataType: "json",
            data: data,
            success: function (json) {
                // Stop spinner
                window.spinner.stop();

                window.CHARTS.prepare_side_by_side_charts(json, charts_name);
                window.CHARTS.make_charts(json, charts_name);

                // Recalculate responsive and fixed headers
                $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
                $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
            },
            error: function (xhr, errmsg, err) {
                // Stop spinner
                window.spinner.stop();

                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Setup triggers
    $('#' + charts_name + 'chart_options').find('input').change(function() {
        get_readouts();
    });

    $('#exportinclude_all').change(function() {
        var export_button = $('#export_button');
        if ($(this).prop('checked')) {
            export_button.attr('href', export_button.attr('href') + '?include_all=true');
        }
        else {
            export_button.attr('href', export_button.attr('href').split('?')[0]);
        }
    }).trigger('change');

    function reproPie() {
        if ($( "#piechart-title" )[0]) {
            var pie = $("#piechart-title").data('nums').split("|");
            var pieData = google.visualization.arrayToDataTable([
                ['Status', 'Count'],
                ['Excellent', parseInt(pie[0])],
                ['Acceptable', parseInt(pie[1])],
                ['Poor', parseInt(pie[2])]
            ]);
            var pieOptions = {
                // title: 'Reproducibility Breakdown\n(Click Slices for Details)',
                // titleFontSize:16,
                legend: 'none',
                slices: {
                    0: { color: '#74ff5b' },
                    1: { color: '#fcfa8d' },
                    2: { color: '#ff7863' }
                },
                pieSliceText: 'label',
                pieSliceTextStyle: {
                    color: 'black',
                    bold: true,
                    fontSize: 12
                },
                'chartArea': {'width': '90%', 'height': '90%'},
                // pieSliceBorderColor:"transparent",
            };
            var pieChart = new google.visualization.PieChart(document.getElementById('piechart'));
            pieChart.draw(pieData, pieOptions);
        }
    }
});
