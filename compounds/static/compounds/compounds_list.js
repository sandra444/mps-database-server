$(document).ready(function() {
    var show_mps = $('#show_mps');
    var show_epa = $('#show_epa');
    var show_unassigned = $('#show_unassigned');

    var filters = {
        'MPS': true,
        'EPA': true,
        'Unassigned': true
    };

    // This function filters the dataTable rows
    $.fn.dataTableExt.afnFiltering.push(function(oSettings, aData, iDataIndex) {
        for (var filter in filters) {
            if (filters[filter] && aData[9].indexOf(filter) > -1) {
                return true;
            }
        }
    });

    // Shrinks the name column when on small screen (illegible otherwise)
    function resize() {
        if($(document).width() < 335) {
            $('.text-wrapped').css('font-size', '11px');
            $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
        }
        else {
            $('.text-wrapped').css('font-size', '14px');
            $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
        }
    }

    var table = $('#compounds').DataTable({
        dom: 'B<"row">lfrtip',
        fixedHeader: true,
        responsive: true,
        "order": [[ 2, "asc" ]],
        "aoColumnDefs": [
            {
                "bSortable": false,
                "aTargets": [0, 1, 10]
            },
            {
                "targets": [4, 9],
                "visible": false,
                "searchable": true
            },
            {
                "width": "5%",
                "targets": [0, 1]
            },
            {
                responsivePriority: 1,
                targets: [0, 2]
            },
            {
                responsivePriority: 2,
                targets: [1]
            }
        ],
        "iDisplayLength": 25
    });

    // Initial resize
    resize();

    $('.table-filter').click(function() {
        filters['MPS'] = show_mps.prop('checked');
        filters['EPA'] = show_epa.prop('checked');
        filters['Unassigned'] = show_unassigned.prop('checked');

        // Redraw the table
        table.draw();
    });

    // Run resize function on resize
    $(window).resize(function() {
      resize();
    });

    // Crude way to deal with resizing from images
    setTimeout(function() {
         $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    }, 500);
});
