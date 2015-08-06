$.fn.dataTable.TableTools.defaults.aButtons = [
    {
        "sExtends": "copy",
        "sButtonText": "Copy to Clipboard",
        "mColumns": "sortable",
        "bFooter": false
    },
    {
        "sExtends": "csv",
        "sButtonText": "Save as CSV",
        "mColumns": "sortable",
        "bFooter": false
    },
    {
        "sExtends": "print",
        "sButtonText": "Print"
        // Unfortunately it seems columns can not be removed from print in this way
        //"mColumns": "sortable"
    }
];
$.fn.dataTable.TableTools.defaults.sSwfPath = '/static/swf/copy_csv_xls.swf';

