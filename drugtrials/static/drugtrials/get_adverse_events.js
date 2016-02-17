// This script performs an on the spot query of the OpenFDA API to get a range of data
$(document).ready(function () {

    var name= $('#compound').html();
    var chart = '';

    // The total will give the x_axis every other plot must adhere to
    var x_axis = null;
    var x_format = '%Y%m';

    var granularity = 'month';

    var plotted = {};

    function ISO_to_date(iso) {
        return iso.substring(0,10).replace(/\-/g,'');
    }

    function get_range_table() {
        // Clear old (if present)
        $('#ae_table').dataTable().fnDestroy();

        var date1= ISO_to_date($('#start_date').val());
        var date2= ISO_to_date($('#end_date').val());

        var limit= $('#limit').val();

        if (!limit) {
            limit = 5;
        }

        if (limit > 100) {
            limit = 100;
        }

        var url = "https://api.fda.gov/drug/event.json?search=receivedate:["+date1+"+TO+"+date2+"]%20AND%20patient.drug.openfda.generic_name:"+name+"&count=patient.reaction.reactionmeddrapt.exact";

        $.getJSON(url, function(data) {
            var html = "";

            var results = data.results;

            if (!results) {
                $('#warning').prop('hidden', false);
            }

            if (limit > results.length) {
                limit = results.length;
            }

            for (var i=0; i<limit; i++) {
                html += "<tr>";
                html += '<td><a href="https://en.wikipedia.org/wiki/' + results[i].term.toLowerCase() + '">' + results[i].term + '</a></td>';
                html += '<td>' + results[i].count + '</td>';
                html += '</tr>';
            }

            $('#ae_body').html(html);

            $('#ae_table').DataTable( {
                "iDisplayLength": 200,
                "sDom": '<T<"clear">t>',
                "order": [[ 1, "desc" ]],
                // Needed to destroy old table
                "bDestroy": true
            });

            // Reposition download/print/copy
            $('.DTTT_container').css('float', 'none');

            $('#ae_table').prop('hidden', false);
        })
        .fail(function() {
            $('#warning').prop('hidden', false);
        });
    }

    function stringify_month(month) {
        if (month < 10) {
            return '0' + month;
        }
        else {
            return '' + month;
        }
    }

    function sum_granular(data, sub) {
        var new_data = {};
        var final_data = [];
        $.each(data, function(index, result) {
            var time = result.time;
            var count = result.count;
            var current_section = time.substring(0,sub);
            if (!new_data[current_section]) {
                new_data[current_section] = count;
            }
            else {
                new_data[current_section] += count;
            }
        });

        // Add zeros for missing data
        if (x_axis) {
            $.each(x_axis.slice(1), function(index, time) {
                if (!new_data[time]) {
                    new_data[time] = 0;
                }
            });
        }
        else {
            var min_year = parseInt(data[0].time.substring(0,4));
            var max_year = parseInt(data[data.length-1].time.substring(0,4));

            if (granularity === 'month') {
                var min_month = parseInt(data[0].time.substring(4,6));
                var max_month = parseInt(data[data.length-1].time.substring(4,6));
                var current_month = '';

                // First year
                for (var month = min_month; month <= 12; month++) {
                    current_month = stringify_month(month);

                    if (!new_data[''+min_year+current_month]) {
                        new_data[''+min_year+current_month] = 0;
                    }
                }

                // Other years
                for (var current_year = min_year+1; current_year < max_year; current_year++) {
                    for (month = 1; month <= 12; month++) {
                        current_month = stringify_month(month);

                        if (!new_data[''+current_year+current_month]) {
                            new_data[''+current_year+current_month] = 0;
                        }
                    }
                }

                // Last year
                for (month = 1; month <= max_month; month++) {
                    current_month = stringify_month(month);

                    if (!new_data[''+max_year+current_month]) {
                        new_data[''+max_year+current_month] = 0;
                    }
                }
            }
            else if (granularity === 'year') {
                for (var year = min_year; year <= max_year; year++) {
                    if (!new_data[''+year]) {
                        new_data[''+year] = 0;
                    }
                }
            }
        }

        $.each(new_data, function(time, count) {
            final_data.push({'time': time, 'count': count});
        });
        return final_data;
    }

    function process_data(data) {
        // Default granularity from OpenFDA
        if (granularity === 'day') {
            return data;
        }
        else if (granularity === 'month') {
            return sum_granular(data, 6);
        }
        else if (granularity === 'year') {
            return sum_granular(data, 4);
        }
    }

    function get_range_plot(event, keep) {
        var url_event = event.replace(/ /g, '+');
        // If the event is already in the chart, then remove it
        if (plotted[event] && !keep) {
            chart.unload({
                ids: [event]
            });
            delete plotted[event];
            $('button[data-adverse-event="'+event+'"]').removeClass('btn-primary');
        }

        else {
            // TODO Contrived for now, should these be user selected?
            var date1 = '19950101';

            // Get today's date
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth()+1; //January is 0!
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }
            if (mm < 10) {
                mm = '0' + mm;
            }

            // Cast as a string by concatenating the empty string
            var date2 = ''+yyyy+''+mm+''+dd;

            var url =  '';

            if (event != 'Total') {
                url = 'https://api.fda.gov/drug/event.json?search=receivedate:['+date1+'+TO+'+date2+']%20AND%20patient.reaction.reactionmeddrapt.exact:"'+url_event+'"%20AND%20patient.drug.openfda.generic_name:'+name+'&count=receivedate';
            }
            else {
                url = 'https://api.fda.gov/drug/event.json?search=receivedate:['+date1+'+TO+'+date2+']%20AND%20patient.drug.openfda.generic_name:'+name+'&count=receivedate';
            }

            $.getJSON(url, function(data) {
                var results = process_data(data.results);

                if (!results) {
                    alert('No results were found');
                }

                var time = _.pluck(results, 'time');
                time.unshift('time');
                var values = _.pluck(results, 'count');
                values.unshift(event);

                plot(event, {'time':time, 'values':values});
            })
            .fail(function() {
                alert('An error has occured: ' + url);
            });
        }
    }

    function plot(event, data) {
        if (event == 'Total') {
            x_axis = data.time;

            x_format = '%Y%m%d';
            var tick_format = '%Y-%m-%d';

            if (granularity === 'month') {
                x_format = '%Y%m';
                tick_format = '%Y-%m';
            }
            else if (granularity === 'year') {
                x_format = '%Y';
                tick_format = '%Y';
            }

            chart = c3.generate({
                bindto: '#plot',
                data: {
                    x: 'time',
                    xFormat: x_format, // default '%Y-%m-%d',
                    columns: [
                        x_axis,
                        data.values
                    ]
                },
                point: {
                    show: false
                },
                axis : {
                    x: {
                        type: 'timeseries',
                        tick: {
                            format: tick_format
                        }
                    }
                },
                subchart: {
                    show: true
                }
            });

            // Plot others for when the plot is reset
            for (event in plotted) {
                get_range_plot(event, 'keep');
            }
        }
        else {
            // Add the event to plotted
            plotted[event] = true;
            $('button[data-adverse-event="'+event+'"]').addClass('btn-primary');
            chart.load({
                xFormat: x_format,
                columns: [
                    data.time,
                    data.values
                ]
            });
        }
    }

    function reset_new_granularity() {
        x_axis = null;
        get_range_plot('Total');
    }

    get_range_plot('Total');

    $('.date-select').click(function() {
        if (this.id != granularity) {
            $('.date-select').removeClass('btn-primary');
            $(this).addClass('btn-primary');
            granularity = this.id;
            $('#plot').empty();
            reset_new_granularity();
        }
    });

    $('.plot_ae').click(function() {
        get_range_plot(this.getAttribute('data-adverse-event'));
    });

    $('#submit').click(function() {
        $('#warning').prop('hidden', true);
        $('#ae_table').prop('hidden', true);
        get_range_table();
    });

    // Initialize and adjust data table
    $('#reported_events').DataTable({
        "iDisplayLength": 200,
        "sDom": '<T<"clear">ft>',
        "order": [[ 2, "desc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0]
            }
        ]
    });

    $('#reported_events').prop('hidden', false);
    // Reposition download/print/copy
    $('.DTTT_container').css('float', 'none');
});
