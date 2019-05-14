$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(refresh_power_analysis);

    window.GROUPING.refresh_function = refresh_power_analysis;
    window.GROUPING.process_get_params();

    // FILE-SCOPE VARIABLES
    var study_id = Math.floor(window.location.href.split('/')[5]);

    var group_table = null;
    var compounds_table = null;
    // var selection_parameters_table = $('#selection-parameters');
    // var selection_parameters_table_container = $('#selection-parameters-table-container');
    var compounds_table_container = $('#compounds-table-container');

    var active_compounds_checkboxes = 0;

    function refresh_power_analysis() {
        window.spinner.spin(
            document.getElementById("spinner")
        );

        if (group_table) {
            group_table.clear();
            group_table.destroy();

            // KILL ALL LINGERING HEADERS
            $('.fixedHeader-locked').remove();
        }

        $('#gas-table').find('body').empty();

        var group_table_columns = [
            {
                title: "Show Details",
                "render": function (data, type, row, meta) {
                    if (type === 'display') {
                        return '<input type="checkbox" class="big-checkbox power-analysis-group-checkbox" data-table-index="' + meta.row + '" data-power-analysis-group="' + row[0] + '" data-compounds-table-info="' + data_groups[row[0]][0] + '$$$$$' + data_groups[row[0]][value_unit_index] + '$$$$$' + data_group_to_organ_models[row[0]].join('<br>') + '$$$$$' + data_group_to_sample_locations[row[0]].join('<br>') + '">';
                    }
                    return '';
                },
                "className": "dt-body-center",
                "createdCell": function (td, cellData, rowData, row, col) {
                    if (cellData) {
                        $(td).css('vertical-align', 'middle');
                    }
                },
                "sortable": false,
                width: '5%'
            },
            {
                title: "Set",
                type: "brute-numeric",
                "render": function (data, type, row) {
                    return '<span class="badge badge-primary data-power-analysis-group-info">' + row[0] + '</span>';
                },
                width: '5%'
            },
            {
                title: "Target/Analyte",
                "render": function (data, type, row) {
                    return data_groups[row[0]][0];
                },
                width: '20%'
            },
            {
                title: "Unit",
                "render": function (data, type, row) {
                    return data_groups[row[0]][value_unit_index];
                }
            },
            {
                title: "MPS Models",
                "render": function (data, type, row) {
                    return data_group_to_organ_models[row[0]].join('<br>');
                }
            },
            {
                title: "Sample Locations",
                "render": function (data, type, row) {
                    return data_group_to_sample_locations[row[0]].join('<br>');
                }
            },
            {title: "# of Chips", data: '4', width: '5%'},
            {title: "# of Time Points", data: '5', width: '10%'},
        ];

        // console.log(JSON.stringify(window.GROUPING.group_criteria));

        group_table = $('#group-table').DataTable({
            ajax: {
                url: '/assays_ajax/',
                data: {
                    call: 'fetch_power_analysis_group_table',
                    criteria: JSON.stringify(window.GROUPING.group_criteria),
                    post_filter: JSON.stringify(window.GROUPING.current_post_filter),
                    csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
                    study: study_id
                },
                type: 'POST',
                dataSrc: function(json) {
                    console.log(json);
                    $("#clone-container").empty();

                    data_groups = json.data_groups;
                    header_keys = json.header_keys;
                    data_groups = json.data_groups;
                    treatment_groups = json.treatment_groups;
                    power_analysis_group_table = json.power_analysis_group_table;
                    compounds_table_data = json.compound_table_data;
                    console.log(compounds_table_data);

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
                    return power_analysis_group_table;
                },
                // Error callback
                error: function (xhr, errmsg, err) {
                    console.log("ERR");
                    $("#clone-container").empty();

                    // Stop spinner
                    window.spinner.stop();

                    alert('An error has occurred, please try different selections.');
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            },
            columns: group_table_columns,
            columnDefs: [
                { "responsivePriority": 1, "targets": [0,1,2,3] },
                { "responsivePriority": 2, "targets": 5 },
            ],
            "order": [1, 'asc'],
            "responsive": true,
            dom: 'B<"row">lfrtip',
            paging: false,
            fixedHeader: {headerOffset: 50},
            deferRender: true,
            drawCallback: function() {
                // Make sure tooltips displayed properly
                $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
            }
        });
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

    // Group Table Checkbox click event
    $(document).on("click", ".power-analysis-group-checkbox", function() {
        var checkbox = $(this);
        var number = checkbox.attr('data-power-analysis-group');
        // var row_info = $(this).data('compounds-table-info').split('$$$$$');
        // console.log(row_info);
        if (checkbox.is(':checked')) {
            $('.power-analysis-group-checkbox').each(function(){
                if (!this.checked) {
                    $(this).parent().parent().hide();
                }
            });
            make_compounds_datatable(number);
        } else {
            $('.power-analysis-group-checkbox').each(function(){
                if (!this.checked) {
                    $(this).parent().parent().show();
                }
            });
            unmake_compounds_datatable();
        }
        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
        // Recalc Fixed Headers
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    });

    // Compounds Table Checkbox click event
    $(document).on("click", ".power-analysis-compounds-checkbox", function() {
        var checkbox = $(this);
        var number = checkbox.attr('data-power-analysis-compound');
        if (active_compounds_checkboxes < 3) {
            if (checkbox.is(':checked')) {
                active_compounds_checkboxes += 1;
                if (active_compounds_checkboxes === 2) {
                    $('.power-analysis-compounds-checkbox').each(function(){
                        if (!this.checked) {
                            $(this).parent().parent().hide();
                        }
                    });
                }
            } else {
                active_compounds_checkboxes -= 1;
                if (active_compounds_checkboxes === 1) {
                    $('.power-analysis-compounds-checkbox').each(function(){
                        if (!this.checked) {
                            $(this).parent().parent().show();
                        }
                    });
                }
            }
        }

        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
        // Recalc Fixed Headers
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    });

    function make_compounds_datatable(group_num){

        // selection_parameters_table.html(
        //     '<tr><th>Target/Analyte</th><td>'+ selection_parameters[0] + '</td></tr>' +
        //     '<tr><th>Unit</th><td>'+ selection_parameters[1] + '</td></tr>' +
        //     '<tr><th>MPS Model</th><td>'+ selection_parameters[2] + '</td></tr>' +
        //     '<tr><th>Sample Location</th><td>'+ selection_parameters[3] + '</td></tr>'
        // );

        var compounds_table_columns = [
            {
                title: "Show Details",
                "render": function (data, type, row, meta) {
                    if (type === 'display') {
                        return '<input type="checkbox" class="big-checkbox power-analysis-compounds-checkbox" data-table-index="' + meta.row + '" data-power-analysis-compound="' + row[0] + '">';
                    }
                    return '';
                },
                "className": "dt-body-center",
                "createdCell": function (td, cellData, rowData, row, col) {
                    if (cellData) {
                        $(td).css('vertical-align', 'middle');
                    }
                },
                "sortable": false,
                width: '5%'
            },
            {
                title: "Compounds",
                "render": function (data, type, row) {
                    return row[0];
                }
            },
            {
                title: "# of Chips",
                "render": function (data, type, row) {
                    return row[1];
                }
            },
            {
                title: "# of Time Points",
                "render": function (data, type, row) {
                    return row[2];
                }
            },

        ];

        compounds_table = $('#compounds-table').DataTable({
            data: compounds_table_data[group_num],
            columns: compounds_table_columns,
            paging: false,
            "order": [1, 'asc'],
            "responsive": true,
        });

        // selection_parameters_table_container.removeAttr('hidden');
        compounds_table_container.removeAttr('hidden');
    }

    function unmake_compounds_datatable() {
        compounds_table.destroy()
        compounds_table_container.attr('hidden', true);
    }
});
