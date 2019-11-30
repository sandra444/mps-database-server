$(document).ready(function() {

    let global_plate_file_index_tooltip = "Click to upload a plate reader file and add it to the study.";
    $('#plate_file_index_tooltip').next().html($('#plate_file_index_tooltip').next().html() + make_escaped_tooltip(global_plate_file_index_tooltip));

    //to format the table - keep
    $('#assayplatereaderfiles').DataTable({
        "iDisplayLength": 25,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[2, "asc"]],
    });

    function escapeHtml(html) {
        return $('<div>').text(html).html();
    }

    function make_escaped_tooltip(title_text) {
        let new_span = $('<div>').append($('<span>')
            .attr('data-toggle', "tooltip")
            .attr('data-title', escapeHtml(title_text))
            .addClass("glyphicon glyphicon-question-sign")
            .attr('aria-hidden', "true")
            .attr('data-placement', "bottom"));
        return new_span.html();
    }

});
