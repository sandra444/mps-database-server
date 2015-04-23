// This script performs an on the spot query of the OpenFDA API to get a range of data
$(document).ready(function () {

    function ISO_to_date(iso) {
        return iso.substring(0,10).replace(/\-/g,'');
    }

    function get_range() {
        // Clear old (if present)
        $('#ae_table').dataTable().fnDestroy();

        var date1= ISO_to_date($('#start_date').val());
        var date2= ISO_to_date($('#end_date').val());

        var name= $('#compound').html();

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
                "sDom": '<"wrapper"t>',
                "order": [[ 1, "desc" ]],
                // Needed to destroy old table
                "bDestroy": true
            });

            $('#ae_table').prop('hidden', false);
        })
        .fail(function() {
            $('#warning').prop('hidden', false);
        });
    }

    $('#submit').click(function() {
        $('#warning').prop('hidden', true);
        $('#ae_table').prop('hidden', true);
        get_range();
    });
});
