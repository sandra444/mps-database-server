$(document).ready(function() {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(reproPie);

    function reproPie() {
        var number_of_rows = $('tbody tr').length;
        for (x=0;x<number_of_rows;x++){
            if ($( "#piechart"+x )[0]) {
                var pie = $("#piechart"+x).data('nums').split("|");
                var pieData = google.visualization.arrayToDataTable([
                    ['Status', 'Count'],
                    ['E', parseInt(pie[0])],
                    ['A', parseInt(pie[1])],
                    ['P', parseInt(pie[2])]
                ]);
                var pieOptions = {
                    // title: 'Reproducibility Breakdown\n(Click Slices for Details)',
                    // titleFontSize:16,
                    legend: 'none',
                    slices: {
                        0: { color: '#74ff5b' },
                        1: { color: '#fcfa8d' },
                        2: { color: '#ff7863' }
                    },
                    pieSliceText: 'none',
                    pieSliceTextStyle: {
                        color: 'black',
                        bold: true,
                        fontSize: 12
                    },
                    'chartArea': {'width': '90%', 'height': '90%'},
                    backgroundColor: { fill:'transparent' },
                    is3D: true,
                    pieSliceBorderColor:"transparent",
                    enableInteractivity: false
                };
                var pieChart = new google.visualization.PieChart(document.getElementById('piechart'+x));
                pieChart.draw(pieData, pieOptions);
            }
        }
        var data_table = $('#studies').DataTable( {
            dom: 'B<"row">lfrtip',
            fixedHeader: {headerOffset: 50},
            responsive: true,
            "iDisplayLength": 50,
            // Initially sort on start date (descending), not ID
            "order": [ 2, "desc" ],
            "aoColumnDefs": [
                {
                    "bSortable": false,
                    "aTargets": [0]
                },
                {
                    "width": "10%",
                    "targets": [0]
                },
                {
                    "type": "numeric-comma",
                    "targets": [5, 6]
                },
                {
                    'className': 'none',
                    'targets': [7, 10]
                },
                {
                    'sortable': false,
                    'targets': [8]
                }
            ]
        });
    }
});
