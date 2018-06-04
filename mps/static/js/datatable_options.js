// Add method to sort by checkbox
// (I reversed it so that ascending will place checked first)
$(document).ready(function () {
    $.fn.dataTable.ext.order['dom-checkbox'] = function (settings, col) {
        return this.api().column(col, {order: 'index'}).nodes().map(function (td, i) {
            return $('input', td).prop('checked') ? 0 : 1;
        });
    };

    $.fn.dataTable.ext.order['time-in-minutes'] = function (settings, col) {
        return this.api().column(col, {order: 'index'}).nodes().map(function (td, i) {
            return parseFloat($('.time_in_minutes', td).val());
        });
    };

    // Define numeric comma sorting
    $.extend($.fn.dataTableExt.oSort, {
        "numeric-comma-pre": function (a) {
            var x = a.replace(/,/g, '');
            return parseFloat(x);
        },

        "numeric-comma-asc": function (a, b) {
            return ((a < b) ? -1 : ((a > b) ? 1 : 0));
        },

        "numeric-comma-desc": function (a, b) {
            return ((a < b) ? 1 : ((a > b) ? -1 : 0));
        }
    });

    // Define brute numeric sort
    $.extend($.fn.dataTableExt.oSort, {
        "brute-numeric-pre": function (a) {
            var x = a.replace(/\D/g, '');
            return parseFloat(x);
        },

        "brute-numeric-asc": function (a, b) {
            return ((a < b) ? -1 : ((a > b) ? 1 : 0));
        },

        "brute-numeric-desc": function (a, b) {
            return ((a < b) ? 1 : ((a > b) ? -1 : 0));
        }
    });

// Defines the options for the print, copy, and save as buttons
    $.extend(true, $.fn.dataTable.defaults, {
        buttons: [
            'copy', 'csv', 'print'
        ]
        // swfPath: '/static/swf/flashExport.swf'
    });
});
// $.fn.dataTable.TableTools.defaults.aButtons = [
//     {
//         "sExtends": "copy",
//         "sButtonText": "Copy to Clipboard",
//         "mColumns": "sortable",
//         "bFooter": false
//     },
//     {
//         "sExtends": "csv",
//         "sButtonText": "Save as CSV",
//         "mColumns": "sortable",
//         "bFooter": false
//     },
//     {
//         "sExtends": "print",
//         "sButtonText": "Print"
//         // Unfortunately it seems columns can not be removed from print in this way
//         //"mColumns": "sortable"
//     }
// ];
// $.fn.dataTable.TableTools.defaults.sSwfPath = '/static/swf/copy_csv_xls.swf';
