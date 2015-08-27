// This script performs an on the spot query of the OpenFDA API to get a range of data
$(document).ready(function () {

    var name= $('#compound').html();

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

    function get_range_plot(event) {
        // TODO Contrived for now, should these be user selected?
        var date1= '20040101';
        var date2= '20150101';

        var url =  ''

        if (event != 'total') {
            url = "https://api.fda.gov/drug/event.json?search=receivedate:["+date1+"+TO+"+date2+"]%20AND%20patient.reaction.reactionmeddrapt:"+event+"%20AND%20patient.drug.openfda.generic_name:"+name+"&count=receivedate";
        }
        else {
            url = "https://api.fda.gov/drug/event.json?search=receivedate:["+date1+"+TO+"+date2+"]%20AND%20patient.drug.openfda.generic_name:"+name+"&count=receivedate";
        }

        console.log(url);

        $.getJSON(url, function(data) {
            var results = data.results;

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
            alert('An error has occured')
        });
    }

    function plot(event, data) {
        if (event == 'total') {
            var chart = c3.generate({
                bindto: '#plot',
                data: {
                    x: 'time',
                    xFormat: '%Y%m%d', // default '%Y-%m-%d',
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
                            format: '%Y-%m-%d'
                        }
                    }
                }
            });
        }
        else {
            chart.load({
                columns: [
                    data.time,
                    data.values
                ]
            });
        }
    }

    get_range_plot('total');

    $('#submit').click(function() {
        $('#warning').prop('hidden', true);
        $('#ae_table').prop('hidden', true);
        get_range_table();
    });
});
