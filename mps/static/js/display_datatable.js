// This script moves the filter and length widgets for a datatable and make the table visible after it loads
$(document).ready(function() {
    // Swap positions of filter and length selection
    $('.dataTables_filter').css('float', 'left');
    $('.dataTables_length').css('float', 'right');

    // Clarify usage of search
    $('.dataTables_filter').prop('title', 'Separate terms with a space to search multiple fields');

    // Clarify usage of sort
    $('.sorting').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
    $('.sorting_asc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
    $('.sorting_desc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');


    // Reveal the table, as loading is complete
    $('table').prop('hidden', false)
});
