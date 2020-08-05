$(document).ready(function () {
    //
    // $('.has-popover').popover({'trigger':'hover'});

    let global_check_load = $("#check_load").html().trim();
    if (global_check_load === 'review') {
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    }

    //    tool tip requirements
    let global_omic_file_format_tooltip = "The following headers are required to be located in the first row of the file or worksheet: baseMean, log2FoldChange, lfcSE, stat, pvalue, padj, and gene or name.";
    $('#omic_file_format_tooltip').next().html($('#omic_file_format_tooltip').next().html() + make_escaped_tooltip(global_omic_file_format_tooltip));

    // activates Bootstrap tooltips, must be AFTER tooltips are created - keep
    $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});

    // tool tip functions
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

