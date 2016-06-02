// Name subject to change
// This file allows the user to compare data of different adverse events for differing compounds
// TODO THIS SCRIPT NEEDS TO BE REVISED TO LIMIT API HITS
$(document).ready(function () {
    // Prevent CSS conflict with Bootstrap
    $.fn.button.noConflict();

    // Stores all currently selected compounds
    var compounds = {};
    // Stores all currently selected adverse events
    var adverse_events = {};
    // Format = adverse_event -> compound -> value
    var full_data = {};

    // The bar graphs
    var bar_graphs = null;

    var raw_hidden = true;

    var selections = $('#selections');
    var MAX_SAVED_SELECTIONS = 5;

    var initial_pattern = [
        '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
        '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
        '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
        '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5',
        '#18F285', '#A8EDCB',
        '#E6F02E', '#E5E8A5',
        '#AAF514', '#CDF283',
        '#52400B', '#635B42',
        '#CCCCCC', '#E3E3E3'
    ];

    var pattern = [];
    // First darker, second lighter
    $.each(initial_pattern, function(index, col) {
        if (index % 2 == 0) {
            pattern.push(d3.hsl(col).darker(0.75));
        }
        else {
            pattern.push(d3.hsl(col).brighter(0.20));
        }
    });

    var table_options =
    {
        dom: '<"clear">lfrtip',
        "iDisplayLength": 10,
        "order": [[ 2, "desc" ]],
        "aoColumnDefs": [
            {
                "width": "10%",
                "targets": [0]
            },
            {
                "sSortDataType": "dom-checkbox",
                "targets": 0
            }
        ]
    };

    // Open and then close dialog so it doesn't get placed in window itself
    var dialog = $('#selection_dialog');
    dialog.dialog({
        width: 825,
        height: 500,
        closeOnEscape: true,
        autoOpen: false,
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            $('body').addClass('stop-scrolling');
        }
    });
    dialog.removeProp('hidden');

    // Add method to sort by checkbox
    // (I reversed it so that ascending will place checked first)
    $.fn.dataTable.ext.order['dom-checkbox'] = function(settings, col) {
        return this.api().column(col, {order:'index'}).nodes().map(function(td, i) {
            return $('input', td).prop('checked') ? 0 : 1;
        });
    };

    // Plugin to show/hide extra axis
    c3.chart.fn.axis.show_y2 = function(shown) {
        var $$ = this.internal, config = $$.config;
        config.axis_y2_show = !!shown;
        $$.axes.y2.style("visibility", config.axis_y2_show ? 'visible' : 'hidden');
        $$.redraw();
    };

    // Pass true for reset to reset the table after finished
    function clear_selections(reset) {
        compounds_table.search('');
        adverse_events_table.search('');
        $('input[type=search]').val('');

        adverse_events_checkboxes.prop('checked', false);
        compounds_checkboxes.prop('checked', false);

        adverse_events = {};
        compounds = {};
        full_data = {};

        create_initial_plot();

        if (reset) {
            adverse_events_table.page.len(10).draw();
            compounds_table.page.len(10).draw();
        }
    }

    function save_selections() {
        var current_selections = {
            'adverse_events': _.keys(adverse_events),
            'compounds': _.keys(compounds)
        };

        var all_selections = [];
        var current_storage = localStorage.getItem('compare_ae_selections');

        if (current_storage) {
            all_selections = JSON.parse(current_storage);

            if (all_selections.length >= MAX_SAVED_SELECTIONS) {
                all_selections = all_selections.slice(1);
            }
        }
        all_selections.push(current_selections);
        all_selections = JSON.stringify(all_selections);

        localStorage.setItem('compare_ae_selections', all_selections)
    }

    function display_load_dialog() {
        var current_storage = localStorage.getItem('compare_ae_selections');
        if (current_storage) {
            var all_selections = JSON.parse(current_storage);

            // Clear old selections
            selections.html('');

            $.each(all_selections, function(index, selection) {
                var row = $('<tr>').addClass('table-selection')
                    .attr('data-selection-index', index);

                var ae_column = $('<td>').text(selection.adverse_events.join(', '));
                var compound_column = $('<td>').text(selection.compounds.join(', '));

                row.append(ae_column);
                row.append(compound_column);
                selections.append(row);
            });
        }

        dialog.dialog('open');
        // Remove focus
        $('.ui-dialog :button').blur();
    }

    function check_selection(value, checkboxes) {
        $.each(checkboxes, function(index, checkbox) {
            if (checkbox.value == value) {
                $(checkbox).prop('checked', true);
            }
        });
    }

    function load_selections(selection_index) {
        clear_selections(false);

        var current_storage = localStorage.getItem('compare_ae_selections');
        var all_selections = JSON.parse(current_storage);

        var ae_selections = all_selections[selection_index].adverse_events;
        var compound_selections = all_selections[selection_index].compounds;

        $.each(ae_selections, function(index, adverse_event) {
            adverse_events[adverse_event] = adverse_event;
            check_selection(adverse_event, adverse_events_checkboxes);
        });

        adverse_events_table.order([[0, 'asc']]);
        adverse_events_table.page.len(10).draw();

        $.each(compound_selections, function(index, compound) {
            compounds[compound] = compound;
            check_selection(compound, compounds_checkboxes);
        });

        compounds_table.order([[0, 'asc']]);
        compounds_table.page.len(10).draw();

        dialog.dialog('close');

        collect_all_adverse_events();
    }

    function create_initial_plot() {
        bar_graphs = c3.generate({
            bindto: '#bar_graphs',
            size: {
                height: 500
            },
            data: {
                x: 'x',
                columns: [],
                type: 'bar'
            },
            axis: {
                x: {
                    type: 'category'
//                    label: {
//                        text: 'Compound',
//                        position: 'outer-center'
//                    }
                },
                y: {
                    label: {
                        text: 'Number of Reports  per 10,000 Mentions',
                        position: 'outer-middle'
                    }
                },
                y2: {
                    show: !raw_hidden,
                    label: {
                        text: 'Number of Reports',
                        position: 'outer-middle'
                    }
                }
            },
            color: {
                // May need more colors later (these colors might also be too similar?)
                pattern: pattern
            },
            // Consider way to deal with overbearing tooltips
            tooltip: {
                //position: function (data, width, height, element) {
                //    return {top: 0, left: 0}
                //}
                format: {
                    value: function (value, ratio, id) {
                        var format = value % 1 === 0 ? d3.format(',d') : d3.format(',.2f');
                        return format(value);
                    }
                },
                // REQUIRES POLYFILL IN CHROME
                grouped: false
            },
            bar: {
                width: {
                    ratio: 0.85
                }
            },
            grid: {
                focus: {
                    show: false
                }
            }
        });
    }

    function load_data(adverse_event) {
        var sorted = [];
        for (var compound in full_data[adverse_event]) {
            sorted.push([compound, full_data[adverse_event][compound]]);
        }

        sorted.sort();

        var keys = _.pluck(sorted, 0);
        var values = _.pluck(sorted, 1);

        var normalized_values = [];

        for (var i=0; i<keys.length; i++) {
            if (estimated_usage[keys[i]]) {
                // Number of reports per 10,000 mentions
                normalized_values.push(values[i] / estimated_usage[keys[i]] * 10000);
            }
            else {
                normalized_values.push(0);
            }
        }

        keys.unshift('x');
        values.unshift(adverse_event + ' (COUNT)');
        normalized_values.unshift(adverse_event);

        var axes = {};
        axes[adverse_event] = 'y';
        axes[adverse_event + ' (COUNT)'] = 'y2';

        bar_graphs.load({
            x: 'x',
            columns: [
                keys,
                normalized_values,
                values
            ],
            axes: axes
        });

        if (raw_hidden) {
            bar_graphs.hide(_.map(adverse_events, function(num, key){ return key + ' (COUNT)'; }), {withLegend: true});
        }
    }

    function collect_all_adverse_events() {
        // Yes, I know the truthiness of 0 is false, I just want to be clear here
        if (_.keys(compounds).length > 0 && _.keys(adverse_events).length > 0) {
            for (var adverse_event in adverse_events) {
                for (var compound in compounds) {
                    if (!full_data[adverse_event] || !full_data[adverse_event][compound]) {
                        get_adverse_events_for_compound(adverse_event, compound);
                    }
                }
            }
        }
    }

    // !IMPORTANT! NOTE THAT COMPOUND WILL NOT ALWAYS CORRESPOND WITH OPENFDA ('ROSIGLITAZONE' vs. 'ROSIGLITAZONE MALEATE')
    // This function is to compensate for when a compound isn't in the top 1000 hits
    function get_adverse_events_for_compound(adverse_event, compound) {
        // Note that this will produce a list of unrelated drugs that were being taken at the same time as patients taking the given compound
        var url = 'https://api.fda.gov/drug/event.json?search=patient.reaction.reactionmeddrapt.exact:"'+ adverse_event +'"%20AND%20patient.drug.openfda.generic_name:"' + compound + '"&count=patient.drug.openfda.generic_name.exact';

        if (!full_data[adverse_event]) {
            full_data[adverse_event] = {};
        }

        $.getJSON(url, function(data) {
            var index = 0;

            while (index < data.results.length && data.results[index].term.indexOf(compound) < 0) {
                index += 1;
            }

            full_data[adverse_event][compound] = data.results[index].count;

            if (data.results[index].term.indexOf(compound) < 0) {
                alert('Mismatch detected: ' + data.results[index].term + ' vs. ' + compound);
            }

            load_data(adverse_event);
        })
        .fail(function() {
            console.log('Fail: ' + url);

            full_data[adverse_event][compound] = 0;

            load_data(adverse_event);
        });
    }

    // This function gets as many compounds as it can (1000) for the given AE
    function get_top_adverse_events(adverse_event) {
        var url = 'https://api.fda.gov/drug/event.json?search=patient.reaction.reactionmeddrapt.exact:"'+ adverse_event +'"&count=patient.drug.openfda.generic_name.exact&limit=1000';

        $.getJSON(url, function(data) {
            console.log(data);
        })
        .fail(function() {
            console.log('Failed: ' + url);
        });
    }

    function remove_compound(compound) {
        delete compounds[compound];

        create_initial_plot();

        for (var adverse_event in adverse_events) {
            delete full_data[adverse_event][compound];
        }

        for (adverse_event in adverse_events) {
            load_data(adverse_event);
        }
    }

    function remove_adverse_event(removed_adverse_event) {
        delete adverse_events[removed_adverse_event];
        delete full_data[removed_adverse_event];

        // The benefit, and problem, with unloading is that the colors do not change
        //bar_graphs.unload({
        //    ids: [adverse_event, adverse_event + ' (COUNT)']
        //});

        create_initial_plot();

        for (var adverse_event in adverse_events) {
            load_data(adverse_event);
        }
    }

    // Tracks the clicking of checkboxes to fill compounds
    $('.compound').change(function() {
        var compound = this.value;

        if (this.checked) {
            compounds[compound] = compound;
            collect_all_adverse_events();
        }
        else {
            remove_compound(compound);
        }
    });
    // Tracks the clicking of checkboxes to fill adverse events
    $('.adverse-event').change(function() {
        var adverse_event = this.value;

        if (this.checked) {
            adverse_events[adverse_event] = adverse_event;
            collect_all_adverse_events();
        }
        else {
            remove_adverse_event(adverse_event);
        }
    });

    $('#show_raw').click(function() {
        if (raw_hidden) {
            bar_graphs.show(_.map(adverse_events, function(num, key){ return key + ' (COUNT)'; }), {withLegend: true});
            $(this).addClass('btn-primary')
                .text('Hide Raw Counts');
            raw_hidden = false;
            bar_graphs.axis.show_y2(true);
        }
        else {
            bar_graphs.hide(_.map(adverse_events, function(num, key){ return key + ' (COUNT)'; }), {withLegend: true});
            $(this).removeClass('btn-primary')
                .text('Show Raw Counts');
            raw_hidden = true;
            bar_graphs.axis.show_y2(false);
        }
    });

    $('#save_selections').click(function() {
        save_selections();
    });

    $('#load_selections').click(function() {
        display_load_dialog();
    });

    $('#clear_selections').click(function() {
        clear_selections(true);
    });

    selections.on('click', '.table-selection', function() {
        load_selections(+$(this).attr('data-selection-index'));
    });

    var adverse_events_table = $('#adverse_events').DataTable(table_options);

    var compounds_table = $('#compounds').DataTable(table_options);

    var adverse_events_cells = adverse_events_table.cells().nodes();
    var adverse_events_checkboxes = $(adverse_events_cells).find(':checkbox');

    var compounds_cells = compounds_table.cells().nodes();
    var compounds_checkboxes = $(compounds_cells).find(':checkbox');

    create_initial_plot();

    var full_compounds = compounds_table.columns(1).data().eq(0);

    var all_compounds = [];
    for (var index=0; index < full_compounds.length; index++) {
        all_compounds.push(full_compounds[index].replace(/<\/?[^>]+(>|$)/g, ''));
    }

    var full_estimates = compounds_table.columns(3).data().eq(0);

    var all_estimates = [];
    for (index=0; index < full_estimates.length; index++) {
        all_estimates.push(full_estimates[index].replace(/,/g, ''));
    }

    var estimated_usage = {};
    _.each(all_compounds,function(key, index){estimated_usage[key] = parseInt(all_estimates[index]);});
});
