// Contains functions for grouping and filtering data

// Global variable for grouping
window.GROUPING = {
    // Starts null
    refresh_function: null
};

// Naive encapsulation
$(document).ready(function () {
    // Probably doesn't need to be global
    window.GROUPING.group_criteria = {};
    var grouping_checkbox_selector = $('.grouping-checkbox');

    // Semi-arbitrary at the moment
    window.GROUPING.get_grouping_filtering = function() {
        // THIS IS A CRUDE WAY TO TEST THE GROUPING
        // Reset the criteria
        window.GROUPING.group_criteria = {};
        grouping_checkbox_selector.each(function() {
            if (this.checked) {
                if (!window.GROUPING.group_criteria[$(this).attr('data-group-relation')]) {
                    window.GROUPING.group_criteria[$(this).attr('data-group-relation')] = [];
                }
                window.GROUPING.group_criteria[$(this).attr('data-group-relation')].push(
                    $(this).attr('data-group')
                );
            }
        });

        return window.GROUPING.group_criteria;
    };

    // CONTRIVED DIALOG
    // Interestingly, this dialog should be separate and apart from chart_options
    // Really, I might as well make it from JS here
    // TODO PLEASE MAKE THIS NOT CONTRIVED SOON
    var dialog_example = $('#filter_popup');
    if (dialog_example) {
        dialog_example.dialog({
            closeOnEscape: true,
            autoOpen: false,
            close: function () {
                $('body').removeClass('stop-scrolling');
            },
            open: function () {
                $('body').addClass('stop-scrolling');
            }
        });
        dialog_example.removeProp('hidden');
    }

    // Triggers for spawning filters
    // TODO REVISE THIS TERRIBLE SELECTOR
    $('.glyphicon-filter').click(function() {
        dialog_example.dialog('open');
    });

    $('#refresh_plots').click(function() {
        if (!window.GROUPING.refresh_function) {
            console.log('Error refreshing');
        }
        else {
            window.GROUPING.refresh_function();
        }
    });
});
