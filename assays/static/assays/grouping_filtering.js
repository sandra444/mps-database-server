// Contains functions for grouping and filtering data

// Global variable for grouping
window.GROUPING = {
    // Starts null
    refresh_function: null,
    // Starts null
    full_post_filter: null,
    // Starts empty
    current_post_filter: {}
};

// Naive encapsulation
$(document).ready(function () {
    // Current base model
    var current_parent_model = null;
    // Current filter
    var current_filter = null;
    var full_post_filter_data = [];
    var current_post_filter_data = [];

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

    // TODO PLEASE MAKE THIS NOT CONTRIVED SOON
    var filter_popup = $('#filter_popup');
    var filter_table = filter_popup.find('table');
    var filter_data_table = null;
    var filter_body = filter_table.find('tbody');
    // var filter_popup_header = filter_popup.find('h5');

    if (filter_popup) {
        filter_popup.dialog({
            width: 825,
            closeOnEscape: true,
            autoOpen: false,
            close: function () {
                $('body').removeClass('stop-scrolling');
            },
            open: function () {
                $('body').addClass('stop-scrolling');
            }
        });
        filter_popup.removeProp('hidden');
    }

    var filter_popup_title = filter_popup.parent().find("span.ui-dialog-title");

    // Triggers for spawning filters
    // TODO REVISE THIS TERRIBLE SELECTOR
    $('.post-filter-spawn').click(function() {
        // Parent row
        var current_title = $(this).parent().parent().find('td').eq(2).html();

        // Current parent model
        current_parent_model = $(this).attr('data-parent-model');
        // Current filter
        current_filter = $(this).attr('data-filter-relation');

        // Set title and header
        filter_popup_title.html(current_title);
        // filter_popup_header.html(current_filter);

        if (window.GROUPING.full_post_filter && window.GROUPING.full_post_filter[current_parent_model]) {
            full_post_filter_data = window.GROUPING.full_post_filter[current_parent_model][current_filter];
            current_post_filter_data = window.GROUPING.current_post_filter[current_parent_model][current_filter];

            // Clear current contents
            if (filter_data_table) {
                filter_table.DataTable().clear();
                filter_table.DataTable().destroy();
            }

            filter_body.empty();

            var html_to_append = [];

            if (full_post_filter_data) {
                // Spawn checkboxes
                $.each(full_post_filter_data, function (obj_val, obj_name) {
                    var row = '<tr>';

                    if (current_post_filter_data[obj_val]) {
                        row += '<td width="10%" class="text-center"><input data-obj-name="' + obj_name + '" class="big-checkbox post-filter-checkbox" type="checkbox" value="' + obj_val + '" checked></td>';
                    }
                    else {
                        row += '<td width="10%" class="text-center"><input data-obj-name="' + obj_name + '" class="big-checkbox post-filter-checkbox" type="checkbox" value="' + obj_val + '"></td>';
                    }

                    row += '<td>' + obj_name + '</td>';

                    row += '</tr>';

                    html_to_append.push(row);
                });
            }
            else {
                html_to_append.push('<tr><td></td><td>No data to display.</td></tr>');
            }

            filter_body.html(html_to_append.join(''));

            filter_data_table = filter_table.DataTable({
                autoWidth: false,
                destroy: true,
                dom: '<"wrapper"lfrtip>',
                deferRender: true,
                iDisplayLength: 10,
                order: [1, 'asc']
            });

            // Swap positions of filter and length selection; clarify filter
            $('.dataTables_filter').css('float', 'left').prop('title', 'Separate terms with a space to search multiple fields');
            $('.dataTables_length').css('float', 'right');

            filter_popup.dialog('open');
        }
    });

    // TODO CHECKBOX TRIGGER
    $(document).on('click', '.post-filter-checkbox', function() {
        if (current_parent_model && current_filter) {
            if ($(this).prop('checked')) {
                current_post_filter_data[$(this).val()] = $(this).attr('data-obj-name');
            }
            else {
                delete current_post_filter_data[$(this).val()];
            }
        }
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
