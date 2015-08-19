// The compound report must be able to:
// 1.) Employ some method to filter desired compounds (will resemble list display with checkboxes)
// 2.) Display all of the requested compound data in the desired table
// 3.) Display D3 "Sparklines" for every assay for the given compound (TODO LOOK AT D3 TECHNIQUE)

$(document).ready(function () {
    // Middleware token for CSRF validation
    var middleware_token = getCookie('csrftoken');

    // Object of all selected compounds
    var compounds = {};

    var width = 100;
    var height = 25;
    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);
    var line = d3.svg.line()
             .interpolate("basis")
             .x(function(d) { return x(d.time); })
             .y(function(d) { return y(d.value); });

    function sparkline(elem_id, plot, x_domain, y_domain) {
        //console.log(x_domain);
        //console.log(y_domain);
        data = [];
        for (var time in plot) {
            var value = +plot[time];
            var x_time = +time;
            data.push({'time':x_time, 'value':value});
        }

        // Sort by time
        data = _.sortBy(data, function(obj){ return +obj.time });

        // TODO THE X AND Y DOMAINS NEED TO SCALE TOGETHER ACROSS ASSAYS
        // FOR THE X AXIS: 0-Max(X) IF I AM NOT MISTAKEN
        // FOR THE Y AXIS: 0-100 UNLESS Y FOR THE ASSAY EXCEEDS 100
        x.domain([0, x_domain]);
        y.domain([0, y_domain]);

        d3.select(elem_id)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('path')
            .datum(data)
            .attr('class', 'sparkline')
            .attr('d', line);
    }

    // AJAX call for getting data
    function get_data() {
        $.ajax({
            url: "/compounds_ajax",
            type: "POST",
            dataType: "json",
            data: {
                call: 'fetch_compound_report',
                compounds: JSON.stringify(compounds),
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                // Stop spinner
                window.spinner.stop();
                // Build table
                build_table(json);
            },
            error: function (xhr, errmsg, err) {
                // Stop spinner
                window.spinner.stop();
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    function build_table(data) {
        // Show graphic
        $('#graphic').prop('hidden',false);

        // Clear old (if present)
        $('#results_table').dataTable().fnDestroy();
        $('#results_body').html('');

        // Acquire domains for the plots (based on assay)
        var x_max = {};
        var y_max = {};
        for (var compound in data) {
            var all_plots = data[compound].plot;
            for (var assay in all_plots) {
                if (!x_max[assay]) {
                    x_max[assay] = 0;
                    y_max[assay] = 100;
                }
                var assay_plots = all_plots[assay];
                for (var concentration in assay_plots) {
                    for (var time in assay_plots[concentration]) {
                        var value = +assay_plots[concentration][time];
                        time = +time;
                        x_max[assay] = time > x_max[assay] ? time: x_max[assay];
                        y_max[assay] = value > y_max[assay] ? value: y_max[assay];
                    }
                }
            }
        }

        for (var compound in data) {
            var values = data[compound].table;
            var plot = data[compound].plot;

            var row = "<tr>";

            row += "<td><a href='/compounds/"+values['id']+"'>" + compound + "</a></td>";
            row += "<td>" + values['Dose (xCmax)'] + "</td>";
            row += "<td>" + values['cLogP']  + "</td>";
            row += "<td>" + values['Pre-clinical Findings'] + "</td>";
            row += "<td>" + values['Clinical Findings'] + "</td>";

            // Recently added
            row += "<td>" + values['PK/Metabolism'] + "</td>";

            row += "<td>";

            // Make the table
            row += "<table id='"+compound+"_table' class='table table-striped table-bordered'>";

            // Add a row for the header
            row += "<tr id='"+compound+"_header'><td></td></tr>";

            row += "</table>";
            row += "</td>";

            row += "</tr>";
            $('#results_body').append(row);

            for (var assay in plot) {
                // Tack this assay on to the header
                $('#'+compound+'_header').append($('<td>')
                    // The use of days here is contrived, actual units to be decided on later
                    .text(assay + ' (' + values.max_time[assay] + ' days)')
                    .addClass('small'));
                for (var concentration in plot[assay]) {
                    var row_id = compound + '_' + concentration.replace('.','_');
                    // If the concentration does not have a row, add it to the table
                    if (!$('#'+row_id)[0]) {
                        // Add the row
                        $('#'+compound+'_table').append($('<tr>')
                            .attr('id', row_id)
                            .append($('<td>')
                                .text(concentration.replace('_',' '))));
                    }
                    for (var every_assay in x_max) {
                        // Add a cell for the assay given concentration
                        if (!$('#'+compound + '_' + every_assay + '_' + concentration.replace('.','_'))[0]) {
                            $('#' + row_id).append($('<td>')
                                .attr('id', compound + '_' + every_assay + '_' + concentration.replace('.', '_')));
                        }
                    }
                }
            }

            for (var assay in plot) {
                for (var concentration in plot[assay]) {
                    sparkline(
                        '#' + compound + '_' + assay + '_' + concentration.replace('.','_'),
                        plot[assay][concentration],
                        x_max[assay],
                        y_max[assay]
                    );
                }
            }
        }

        $('#results_table').DataTable({
            dom: 'T<"clear">rt',
            "iDisplayLength": 100,
            // Needed to destroy old table
            "bDestroy": true,
            "order": [[ 0, "asc" ]],
            "aoColumnDefs": [
                {
                    "bSortable": false,
                    "aTargets": [6]
                }
            ]
        });

        // Swap positions of filter and length selection
        $('.dataTables_filter').css('float','left');
        // Reposition download/print/copy
        $('.DTTT_container').css('float', 'none');
    }

    // Submission
    function submit() {
        // Hide Selection html
        $('#selection').prop('hidden',true);
        // Show spinner
        window.spinner.spin(
            document.getElementById("spinner")
        );
        get_data();
    }

    // Checks whether the submission button was clicked
    $('#submit').click(function() {
        submit();
    });

    // Tracks the clicking of checkboxes to fill compounds
    $('.checkbox').change( function() {
        var compound = this.value;
        if (this.checked) {
            compounds[compound] = compound;
        }
        else {
            delete compounds[compound]
        }
    });

    window.onhashchange = function() {
        if (location.hash != '#show') {
            $('#graphic').prop('hidden', true);
            $('#selection').prop('hidden', false);
        }
        else {
            $('#graphic').prop('hidden', false);
            $('#selection').prop('hidden', true);
        }
    };
});
