$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(refresh_power_analysis);

    window.GROUPING.refresh_function = refresh_power_analysis;

    // FILE-SCOPE VARIABLES
    var study_id = Math.floor(window.location.href.split('/')[5]);

    var columns = [
        {
            title: "Show Details",
            "render": function (data, type, row, meta) {
                if (type === 'display') {
                    return '<input type="checkbox" class="big-checkbox repro-checkbox" data-table-index="' + meta.row + '" data-repro-set="' + row[0] + '">';
                }
                return '';
            },
            "className": "dt-body-center",
            "createdCell": function (td, cellData, rowData, row, col) {
                if (cellData) {
                    $(td).css('vertical-align', 'middle')
                }
            },
            "sortable": false,
            width: '5%'
        },
        {
            title: "Set",
            type: "brute-numeric",
            "render": function (data, type, row) {
                    return '<span class="badge badge-primary repro-set-info">' + row[0] + '</span>';
            }
        },
        {
            title: "Target/Analyte",
            // "render": function (data, type, row) {
            //     return data_groups[row[0]][0];
            // },
            width: '20%'
        },
        {
            title: "Unit",
            // "render": function (data, type, row) {
            //     return data_groups[row[0]][value_unit_index];
            // }
        },
        {
            title: "MPS Models",
            // "render": function (data, type, row) {
            //     return data_group_to_organ_models[row[0]].join('<br>');
            // }
        },
        {
            title: "Sample Locations",
            // "render": function (data, type, row) {
            //     return data_group_to_sample_locations[row[0]].join('<br>');
            // }
        },
        {title: "# of Chips", data: '9'},
        {title: "# of Time Points", data: '10'},
    ];

    gas_table = $('#gas-table').DataTable({
        ajax: {
            url: '/assays_ajax/',
            data: {
                call: 'fetch_power_analysis',
                criteria: JSON.stringify(window.GROUPING.group_criteria),
                post_filter: JSON.stringify(window.GROUPING.current_post_filter),
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
                study: study_id
            },
            type: 'POST',
            dataSrc: function(json) {
                console.log(json);
                $("#clone-container").empty();

                gas_list = json.gas_list;
                header_keys = json.header_keys;
                data_groups = json.data_groups;
                treatment_groups = json.treatment_groups;

                data_group_to_sample_locations = json.data_group_to_sample_locations;
                data_group_to_organ_models = json.data_group_to_organ_models;
                value_unit_index = header_keys.indexOf('Value Unit');
                method_index = header_keys.indexOf('Method');
                setting_index = header_keys.indexOf('Settings');
                cells_index = header_keys.indexOf('Cells');
                target_index = header_keys.indexOf('Target');

                // post_filter setup
                window.GROUPING.set_grouping_filtering(json.post_filter);
                // Stop spinner
                window.spinner.stop();

                return gas_list;
            },
            // Error callback
            error: function (xhr, errmsg, err) {
                $("#clone-container").empty();

                // Stop spinner
                window.spinner.stop();

                alert('An error has occurred, please try different selections.');
                console.log(xhr.status + ": " + xhr.responseText);
            }
        },
        columns: columns,
        columnDefs: [
            { "responsivePriority": 1, "targets": [0,1,2,3] },
            { "responsivePriority": 2, "targets": 5 },
        ],
        "order": [1, 'desc'],
        "responsive": true,
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        deferRender: true,
        drawCallback: function() {
            // Make sure tooltips displayed properly
            $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
        }
    });

    function refresh_power_analysis() {

    }

    function make_escaped_tooltip(title_text) {
        var new_span = $('<div>').append($('<span>')
            .attr('data-toggle', "tooltip")
            .attr('data-title', escapeHtml(title_text))
            .addClass("glyphicon glyphicon-question-sign")
            .attr('aria-hidden', "true")
            .attr('data-placement', "bottom"));
        return new_span.html();
    }
});
