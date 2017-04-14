$(document).ready(function() {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(get_readouts);

    var charts = $('#charts');
    var middleware_token = getCookie('csrftoken');
    var study_id = Math.floor(window.location.href.split('/')[4]);

    var current_key = 'chip';
    var mean_type = 'arithmetic';
    var interval_type = 'ste';
    var percent_control = false;

    var radio_buttons_display = $('#radio_buttons');

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
                mean_type: mean_type,
                interval_type: interval_type,
                include_all: '',
                // Tells whether to convert to percent Control
                percent_control: percent_control,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                // Show radio_buttons if there is data
                if (Object.keys(json).length > 0) {
                    radio_buttons_display.show();
                }

                window.CHARTS.prepare_side_by_side_charts(json, 'charts');
                window.CHARTS.make_charts(json, 'charts');

                // Recalculate responsive and fixed headers
                $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
                $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Initially by device
    // get_readouts();

    // Check when chart type changes
    $('input[type=radio][name=chart_type_radio]').change(function() {
        current_key = this.value;
        get_readouts();
    });

    // Check when mean type changes
    $('input[type=radio][name=mean_type_radio]').change(function() {
        mean_type = this.value;
        get_readouts();
    });

    // Check when interval type changes
    $('input[type=radio][name=interval_type_radio]').change(function() {
        interval_type = this.value;
        get_readouts();
    });

    // Check if convert_to_percent_control is clicked
    $('#convert_to_percent_control').click(function() {
        percent_control = this.checked;
        get_readouts();
    });
});
