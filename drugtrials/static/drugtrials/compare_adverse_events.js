// Name subject to change
// This file allows the user to compare data of different adverse events for differing compounds
$(document).ready(function () {
    // Stores all currently selected compounds
    var compounds = {};
    // Stores all currently selected adverse events
    var adverse_events = {};
    // Format = adverse_event -> compound -> value
    var full_data = {};

    // The bar graphs
    var bar_graphs = c3.generate({
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
            }
        }
    });

    // Add method to sort by checkbox
    // (I reversed it so that ascending will place checked first)
    $.fn.dataTable.ext.order['dom-checkbox'] = function(settings, col){
        return this.api().column(col, {order:'index'}).nodes().map(function(td, i){
            return $('input', td).prop('checked') ? 0 : 1;
        });
    };

    function load_data(adverse_event) {
        var sorted = [];
        for (var compound in full_data[adverse_event]) {
            sorted.push([compound, full_data[adverse_event][compound]]);
        }

        sorted.sort();

        var keys = _.pluck(sorted, 0);
        keys.unshift('x');

        var values = _.pluck(sorted, 1);
        values.unshift(adverse_event);

        bar_graphs.load({
            x: 'x',
            columns: [
                keys,
                values
            ]
        });
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
                }
            }
        });

        for (var adverse_event in adverse_events) {
            delete full_data[adverse_event][compound];
        }

        for (adverse_event in adverse_events) {
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
            delete compounds[compound];
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
            delete adverse_events[adverse_event];
            delete full_data[adverse_event];
            bar_graphs.unload({
              ids: [adverse_event]
            });
        }
    });

    var adverse_events_table = $('#adverse_events').DataTable({
        dom: '<"clear">lfrtip',
        "iDisplayLength": 10,
        "order": [[ 1, "asc" ]],
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
    });

    var compounds_table = $('#compounds').DataTable({
        dom: '<"clear">lfrtip',
        "iDisplayLength": 10,
        "order": [[ 1, "asc" ]],
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
    });

    //var all_compounds = compounds_table.columns(1).data().eq(0);
});
