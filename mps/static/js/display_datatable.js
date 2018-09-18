// This script moves the filter and length widgets for a datatable and make the table visible after it loads
// DEPRECATED: DO NOT USE
$(document).ready(function() {

    // Get URL parameters for auto search
    function urlParam(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results == null){
           return null;
        }
        else{
           return decodeURI(results[1]) || 0;
        }
    }

    // Swap positions of filter and length selection; clarify filter
    $('.dataTables_filter').css('float', 'left').prop('title', 'Separate terms with a space to search multiple fields');
    $('.dataTables_length').css('float', 'right');
    // Reposition download/print/copy
    $('.DTTT_container').css('float', 'none');

    // Clarify usage of sort
    // REMOVED FOR NOW
    // $('.sorting').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
    // $('.sorting_asc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');
    // $('.sorting_desc').prop('title', 'Click a column to change its sorting\n Hold shift and click columns to sort multiple');

    // TODO Not currently used, but this could be helpful
    // Perform auto search (from GET)
    // $('.dataTables_filter input').val(urlParam('search')).trigger($.Event("keyup", { keyCode: 13 }));

    // Reveal the table, as loading is complete
    $('table').prop('hidden', false);

    // Recalculate responsive and fixed headers
    $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
    $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
});
