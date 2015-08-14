// The compound report must be able to:
// 1.) Employ some method to filter desired compounds (will resemble list display with checkboxes)
// 2.) Display all of the requested compound data in the desired table
// 3.) Display D3 "Sparklines" for every assay for the given compound (TODO LOOK AT D3 TECHNIQUE)

$(document).ready(function () {
    // Middleware token for CSRF validation
    var middleware_token = getCookie('csrftoken');

    // Object of all selected compounds
    var compounds = {};

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
        $('#results_table').prop('hidden',false);

        // Clear old (if present)
        $('#results_table').dataTable().fnDestroy();
        $('#results_body').html('');

        for (var compound in data) {
            var values = data[compound].table;
            var row = "<tr>";
            row += "<td><a href='/compounds/"+values['id']+"'>" + compound + "</a></td>";

            row += "<td>" + values['Dose (xCmax)'] + "</td>";
            row += "<td>" + values['cLogP']  + "</td>";
            row += "<td>" + values['Pre-clinical Findings'] + "</td>";
            row += "<td>" + values['Clinical Findings'] + "</td>";
            row += "<td>" + values['id'] + "</td>";
            row += "<td>" + values['id'] + "</td>";

            row += "</tr>";
            $('#results_body').append(row);
        }

        $('#results_table').DataTable({
            dom: 'T<"clear">frtip',
            "iDisplayLength": 100,
            // Needed to destroy old table
            "bDestroy": true
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
