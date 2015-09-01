// This script performs an on the spot query of the OpenFDA API to get a range of data
$(document).ready(function () {

    var name= $('#compound').html();
    var chart = '';

    var granularity = 'month';

    var plotted = {'Total':false};

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

    function sum_granular(data, sub) {
        var new_data = {};
        var final_data = [];
        $.each(data, function(index, result) {
            var time = result.time;
            var count = result.count;
            var current_month = time.substring(0,sub);
            if (!new_data[current_month]) {
                new_data[current_month] = count;
            }
            else {
                new_data[current_month] += count;
            }
        });
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
            var date1= '19950101';
            var date2= '20150101';

            var url =  ''

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
            var x_format = '%Y%m%d';
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
                        data.time,
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
                            //values: ['2003-01-01','2004-01-01','2005-01-01','2006-01-01','2007-01-01','2008-01-01','2009-01-01','2010-01-01','2011-01-01','2012-01-01','2013-01-01','2014-01-01','2015-01-01'],
                            format: tick_format
                        }
                    }
                }
            });
        }
        else {
            // Add the event to plotted
            plotted[event] = true;
            $('button[data-adverse-event="'+event+'"]').addClass('btn-primary');
            chart.load({
                columns: [
                    data.time,
                    data.values
                ]
            });
        }
    }

    function reset_new_granularity() {
        for (event in plotted) {
            get_range_plot(event, 'keep');
        }
    }

    get_range_plot('Total');

    $('.date-select').click(function() {
        if (this.id != granularity) {
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
});
