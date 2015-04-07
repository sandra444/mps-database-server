// This script moves the filter and length widgets for a datatable and make the table visible after it loads
$(document).ready(function() {
    // Swap positions of filter and length selection
    $('.dataTables_filter').css('float', 'left');
    $('.dataTables_length').css('float', 'right');

    // Reveal the table, as loading is complete
    $('table').prop('hidden', false)
});
