$(document).ready(function () {
    // Load core chart package
    google.charts.load('current', {'packages':['corechart']});
    // Set the callback
    google.charts.setOnLoadCallback(reproPie1);

    // FILE-SCOPE VARIABLES
    var study_id = Math.floor(window.location.href.split('/')[5]);

    var gas_list = null;
    var mad_list = null;
    var comp_list = null;
    var lists = {
        chip_list: null,
        cv_list: null
    };
    var pie = null;

    // CRUDE NOT DRY
    var cv_tooltip = "The CV is calculated for each time point and the value reported is the max CV across time points, or the CV if a single time point is present.  The reproducibility status is excellent if Max CV/CV < 5% (Excellent (CV)), acceptable if Max CV/CV < 15% (Acceptable (CV)), and poor if CV > 15% for a single time point (Poor (CV))";
    var icc_tooltip = "The ICC Absolute Agreement of the measurements across multiple time points is a correlation coefficient that ranges from -1 to 1 with values closer to 1 being more correlated.  When the Max CV > 15%, the reproducibility status is reported to be excellent if > 0.8 (Excellent (ICC), acceptable if > 0.2 (Acceptable (ICC)), and poor if < 0.2 (Poor (ICC))";
    var repro_tooltip = "Our classification of this grouping\'s reproducibility (Excellent > Acceptable > Poor/NA). If Max CV < 15% then the status is based on the  Max CV criteria, otherwise the status is based on the ICC criteria when the number of overlapping time points is more than one. For single time point data, if CV <15% then the status is based on the CV criteria, otherwise the status is based on the ANOVA P-Value";
    var missing_tooltip = "Quantity of data values whose values were missing from the data provided and were interpolated by the average of the data values at the same time point";
    var mad_tooltip = "Median Absolute Deviation (MAD) scores of all chip measurement population at every time point. A score > 3.5 or < -3.5 indicates that the chip is an outlier relative to the median of chip measurement population at a that time point";
    var comp_tooltip = "The ICC is calculated for each chip relative to the median of all of the chips.";

    function escapeHtml(html) {
        return $('<div>').text(html).html();
    }

    function make_escaped_tooltip(title_text) {
        var new_span = $('<div>').append($('<span>')
            .attr('data-toggle', "tooltip")
            .attr('data-title', escapeHtml(title_text))
            .addClass("glyphicon glyphicon-question-sign")
            .attr('aria-hidden', "true")
            .attr('data-placement', "bottom"));
        return new_span.html();
    }

    var studyID = $( "#selection-parameters" ).find(".studyId").text();

    var gasTable = $('#gas-table').DataTable({
        ajax: {
            url: '/assays_ajax/',
            data: {
                // TODO TODO TODO THIS DEPENDS ON THE INTERFACE
                call: 'fetch_assay_study_reproducibility',
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
                study: study_id
            },
            type: 'POST',
            dataSrc: function(json) {
                gas_list = json.gas_list;
                mad_list = json.mad_list;
                comp_list = json.comp_list;
                lists.cv_list = json.cv_list;
                lists.chip_list = json.chip_list;
                pie = json.pie;
                reproPie2();

                return gas_list;
            }
        },
        columns: [
            { title: "Show Details",
             "render": function(data, type, row) {
                if (type === 'display') {
                    var groupNum = row[11];
                    return '<input type="checkbox" class="big-checkbox gas-checkbox-'+groupNum+'">';
                }
                return data;
            },
            "className": "dt-body-center",
            "createdCell": function (td, cellData, rowData, row, col) {
                if ( cellData ) {
                    $(td).css('vertical-align', 'middle')
                }
            },
            "sortable": false
            },
            { title: "Set", data: '11', type: "num" },
            { title: "Organ Model", data: '0' },
            { title: "<span style='white-space: nowrap;'>Full Compound<br>Treatment(s)</span>", data: '2', className: 'none',
                render:function (data, type, row, meta) {
                    return '<br>' + data.replace(/\n/g, '<br>');
                }
            },
            { title: "<span style='white-space: nowrap;'>Compound<br>Treatment(s)</span>", data: '2',
                // CRUDE, WORTH REFACTOR
                render:function (data, type, row, meta) {
                    var split_data = data.split('\n');
                    var new_data = [];
                    $.each(split_data, function(index, value) {
                        if (index % 2 === 0) {
                            new_data.push(value);
                        }
                    });
                    new_data = new_data.join('<br>');
                    return new_data;
                }
            },
            { title: "Target/Analyte", data: '3', width: '8%' },
            { title: "Method/Kit", data: '4', width: '8%' },
            { title: "Sample Location", data: '5', width: '8%' },
            { title: "Value Unit", data: '6' },
            { title: "<span style='white-space: nowrap;'>Max CV<br>or CV "+make_escaped_tooltip(cv_tooltip)+"</span>", data: '8' },
            { title: "<span style='white-space: nowrap;'>ICC "+make_escaped_tooltip(icc_tooltip)+"</span>", data: '9' },
            { title: "Reproducibility<br>Status "+make_escaped_tooltip(repro_tooltip), data: '10', render: function(data, type, row, meta) {
                if (data[0] === 'E') {
                    return '<td><span class="hidden">3</span>' + data + '</td>';
                } else if (data[0] === 'A') {
                    return '<td><span class="hidden">2</span>' + data + '</td>';
                } else if (data[0] === 'P') {
                    return '<td><span class="hidden">1</span>' + data + '</td>';
                } else {
                    return '<td><span class="hidden">0</span>'+data+'<span data-toggle="tooltip" title="'+row[14]+'" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></td>';
                }
            }},
            { title: "# of Chips/Wells", data: '12' },
            { title: "# of Time Points", data: '13' },
            { title: "Cells", data: '1', 'className': 'none'},
            { title: "Settings", data: '7', 'className': 'none'},
            { title: "NA Explanation", data: '14', visible: false, 'name': 'naText' }
        ],
        columnDefs: [
            { responsivePriority: 1, targets: 11 },
            { responsivePriority: 2, targets: [0,1,5,8] },
            { responsivePriority: 3, targets: 4 },
            { responsivePriority: 4, targets: 10 },
            { responsivePriority: 5, targets: 9 },
            { responsivePriority: 6, targets: 2 },
            { responsivePriority: 7, targets: 6 },
            { responsivePriority: 8, targets: 7 },
            { responsivePriority: 9, targets: 15 },
            { responsivePriority: 10, targets: 12 },
            { responsivePriority: 11, targets: 14 },
            { responsivePriority: 12, targets: 13 },
            { responsivePriority: 13, targets: 3 },
            { responsivePriority: 14, targets: 16 },
            { "aTargets": [11], "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                if (sData[0] === "E") {
                    $(nTd).css('background-color', '#74ff5b').css('font-weight', 'bold');
                } else if (sData[0] === "A") {
                    $(nTd).css('background-color', '#fcfa8d').css('font-weight', 'bold');
                } else if (sData[0] === "P") {
                    $(nTd).css('background-color', '#ff7863').css('font-weight', 'bold');
                } else {
                    $(nTd).css('background-color', 'Grey').css('font-weight', 'bold');
                }
            }}
        ],
        "order": [[11, 'desc'], [ 1, "asc" ]],
        // Column visibility toggle would displace, hence new means of coloring.
        // "createdRow": function( row, data, dataIndex ) {
        //     if ( data[10][0] === "E" ) {
        //         $( row ).find('td:eq(11)').css( "background-color", "#74ff5b" ).css( "font-weight", "bold"  );
        //     }
        //     else if ( data[10][0] === "A" ) {
        //         $( row ).find('td:eq(11)').css( "background-color", "#fcfa8d" ).css( "font-weight", "bold"  );
        //     }
        //     else if ( data[10][0] === "P" ) {
        //         $( row ).find('td:eq(11)').css( "background-color", "#ff7863" ).css( "font-weight", "bold" );
        //     }
        //     else {
        //         $( row ).find('td:eq(11)').css( "background-color", "Grey" ).css( "font-weight", "bold" );
        //     }
        // },
        "responsive": true,
        dom: 'B<"row">lfrtip',
        fixedHeader: {headerOffset: 50},
        deferRender: true,
        initComplete: function () {
            // Attempt to draw the tables
            drawTables();
        },
        drawCallback: function() {
            // Make sure tooltips displayed properly
            $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
        }
    });

    function drawTables(){
        //Clone reproducibility section per row
        var counter = 1;
        gasTable.rows().every( function ( rowIdx, tableLoop, rowLoop ) {
            var data = this.data();
            var organModel = data[0];
            var targetAnalyte = data[3];
            var methodKit = data[4];
            var sampleLocation = data[5];
            var compoundTreatments = data[2].replace(/\n/g, '<br>');
            var valueUnit = data[6];
            var group = data[11];
            var icc_status = data[10];
            var $elem = $( "#repro-data" );
            var $clone = $elem.first().clone( true ).addClass('repro-'+group).appendTo("#clone-container");
            mad_list[group]['columns'].unshift("Time");
            $clone.find('#repro-title').text('Set ' + group);
            $clone.find('#selection-parameters').html(buildSelectionParameters(studyID, organModel, targetAnalyte, methodKit, sampleLocation, compoundTreatments, valueUnit));
            $clone.find('#selection-parameters').find('td, th').css('padding','8px 10px');
            $clone.find('#chip-rep-rep-ind').html(buildCV_ICC(data[8],data[9]));
            $clone.find('#chip-rep-rep-ind').find('td, th').css('padding','8px 10px');
            $clone.find('#chart1').attr('id', 'chart1-'+group);
            $clone.find('#chart2').attr('id', 'chart2-'+group);
            $clone.find('#mad-score-label').html($clone.find('#mad-score-label').html() + make_escaped_tooltip(mad_tooltip));
            $clone.find('#med-comp-label').html($clone.find('#med-comp-label').html() + make_escaped_tooltip(comp_tooltip));
            if (icc_status[0] === 'E'){
                $clone.find('#repro-status').html('<em>'+icc_status+'</em>').css("background-color", "#74ff5b");
            } else if (icc_status[0] === 'A'){
                $clone.find('#repro-status').html('<em>'+icc_status+'</em>').css("background-color", "#fcfa8d");
            } else if (icc_status[0] === 'P'){
                $clone.find('#repro-status').html('<em>'+icc_status+'</em>').css("background-color", "#ff7863");
            } else {
                $clone.find('#repro-status').html('<em>'+icc_status+'</em><small style="color: black;"><span data-toggle="tooltip" title="'+data[14]+'" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></small>').css("background-color", "Grey");
            }
            $clone.find('#mad-score-matrix').DataTable( {
                columns: mad_columns(group),
                data: mad_list[group]['data'],
                searching: false,
                paging: false,
                info: false
                // fixedColumns: {leftColumns: 1},
                // scrollX: true
            });

            $clone.find('#chip-comp-med').DataTable( {
                columns: [
                    { title: "Chip ID", data: '0' },
                    { title: "ICC Absolute Agreement", data: '1' },
                    { title: "Missing Data Points "+make_escaped_tooltip(missing_tooltip), data: '2' }
                ],
                data: comp_list[group],
                searching: false,
                paging: false,
                info: false
            });
            counter++;
        });
    }

    // Activates Bootstrap tooltips
    $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});

    function drawChart(list, number, title, chartNum, valueUnit, percentage){
        list = lists[list];
        var values = list[number];
        if (values == null){
            return false;
        }
        var allNull = true;
        for (var i = 1; i < values.length; i++) {
            for (var j = 1; j < values[i].length; j++) {
                if (values[i][j] === ""){
                    values[i][j] = null;
                } else {
                    allNull = false;
                }
            }
        }
        if (allNull) {
            return false;
        }
        var data = google.visualization.arrayToDataTable(values);
        var options = {
            // title: title,
            interpolateNulls: true,
            // titleTextStyle: {
            //     fontSize: 18,
            //     bold: true,
            //     underline: true
            // },
            legend: {
                position: 'top',
                maxLines: 5,
                textStyle: {
                    // fontSize: 8,
                    bold: true
                }
            },
            hAxis: {
                title: 'Time (Days)',
                textStyle: {
                    bold: true
                },
                titleTextStyle: {
                    fontSize: 14,
                    bold: true,
                    italic: false
                }
            },
            vAxis: {
                // TODO YOU'LL NEED TO SNAG THE UNITS
                title: valueUnit,
                format: 'scientific',
                textStyle: {
                    bold: true
                },
                titleTextStyle: {
                    fontSize: 14,
                    bold: true,
                    italic: false
                },
                minValue: 0,
                viewWindowMode: 'explicit'
            },
            pointSize: 5,
            'chartArea': {
                'width': '70%',
                'height': '75%'
            },
            'height':250,
            'width':450,
            // Individual point tooltips, not aggregate
            focusTarget: 'datum',
            intervals: {
                // style: 'bars'
                'lineWidth': 0.75
            }
        };
        if (title === 'Chip Values/Time') {
            options['series'] = {0: { lineDashStyle: [4, 4], pointShape: { type: 'diamond', sides: 4 } }};
        }
        if (percentage) {
            options['vAxis'] = {
            title: valueUnit,
            format: 'short',
            textStyle: { bold: true },
            titleTextStyle: {
                    fontSize: 14,
                    bold: true,
                    italic: false
                },
                minValue: 0,
                maxValue: 100,
                viewWindowMode: 'explicit'
            }
        }
        var chart = null;
        if (values.length === 2) {
            chart = new google.visualization.ColumnChart(document.getElementById(chartNum+number));
            options['bar'] = {groupWidth: '25%'};
            options['hAxis']['ticks'] = [{v:values[1][0], f:values[1][0].toString()}]
        } else {
            chart = new google.visualization.LineChart(document.getElementById(chartNum+number));
        }
        chart.draw(data, options);
    }

    function mad_columns(counter){
        var columns = [];
        $.each(mad_list[counter]['columns'], function (i, value) {
            var obj = { 'title' : value };
            columns.push(obj);
        });
        return columns
    }

    function buildSelectionParameters(studyId, organModel, targetAnalyte, methodKit, sampleLocation, compoundTreatments, valueUnit){
        content =
        '<tr><th><h4><strong>Target/Analyte</strong></h4></th><td id="target-analyte-value"><h4><strong>'+targetAnalyte+'</strong></h4></td></tr>'+
        '<tr><th>Study ID</th><td>'+studyId+'</td></tr>'+
        '<tr><th>Organ Model</th><td>'+organModel+'</td></tr>'+
        '<tr><th>Method/Kit</th><td>'+methodKit+'</td></tr>'+
        '<tr><th>Sample Location</th><td>'+sampleLocation+'</td></tr>'+
        '<tr><th>Compound Treatment(s)</th><td>'+compoundTreatments+'</td></tr>'+
        '<tr><th>Value Unit</th><td id="value-unit">'+valueUnit+'</td></tr>'
        return content;
    }

    function buildCV_ICC(cv, icc){
        content = '<tr><th>CV(%)</th><th>ICC-Absolute Agreement</th></tr><tr><td>'+cv+'</td><td>'+icc+'</td></tr>'
        return content;
    }

    //Checkbox click event
    $(document).on("click", ".big-checkbox", function() {
        var checkbox = $(this);
        var checkbox_id = $(this).attr('class');
        var cls = checkbox_id.split(' ').pop();
        var number = cls.substr(cls.lastIndexOf("-") + 1);
        //var number = checkbox_id;
        var reproTable = $('.repro-'+number);
        if (checkbox.is(':checked')) {
            reproTable.removeClass('hidden');
            var axisLabel = reproTable.find('#target-analyte-value').text();
            var valueUnit = reproTable.find('#value-unit').text();
            $(document).find(".repro-goto-"+number).removeClass('hidden');
            if (reproTable.find('#mad-score-matrix').width() > 500) {
                reproTable.find('#mad-score-matrix').parent().parent().removeClass('col-md-6');
                reproTable.find('#mad-score-matrix').parent().parent().addClass('col-xs-12');
                reproTable.find('#chip-comp-med').parent().parent().detach().appendTo(reproTable.find('#overflow'));
            }
            drawChart('chip_list', number, 'Chip Values/Time', 'chart1-', axisLabel + "\n" + valueUnit, false);
            drawChart('cv_list', number, 'CV(%)/Time', 'chart2-', 'CV(%)', true);
        } else {
            reproTable.addClass('hidden')
        }
        // Recalculate responsive and fixed headers
        // $('.spawned-datatable').DataTable().fixedHeader.adjust();
        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body", html: true});
    });

    // On reorder
    gasTable.on( 'order.dt', function () {
        var setOrder = [];
        gasTable.column(1, { search:'applied' } ).data().each(function(value, index) {
            setOrder.push(value);
        });
        orderInfo(setOrder);
    } );

    function orderInfo(orderList){
        for (var i=0; i < orderList.length; i++){
            $('#clone-container .repro-'+orderList[i]).appendTo('#clone-container');
        }
    }

    function reproPie1() {
        var data = google.visualization.arrayToDataTable([
            ['Status', 'Count'],
            ['Loading...', 1]
        ]);
        var options = {
            legend: 'none',
            pieSliceText: 'label',
            'chartArea': {'width': '90%', 'height': '90%'},
            tooltip: {trigger : 'none'},
            pieSliceTextStyle: {
                color: 'white',
                bold: true,
                fontSize: 12
            },
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
        chart.draw(data, options);
    }

    function reproPie2() {
        var data = google.visualization.arrayToDataTable([
            ['Status', 'Count'],
            ['Excellent', pie[0]],
            ['Acceptable', pie[1]],
            ['Poor', pie[2]]
        ]);
        var options = {
            // title: 'Reproducibility Breakdown\n(Click Slices for Details)',
            // titleFontSize:16,
            legend: 'none',
            slices: {
                0: { color: '#74ff5b' },
                1: { color: '#fcfa8d' },
                2: { color: '#ff7863' }
            },
            pieSliceText: 'label',
            pieSliceTextStyle: {
                color: 'black',
                bold: true,
                fontSize: 12
            },
            'chartArea': {'width': '90%', 'height': '90%'},
            pieSliceBorderColor: "black",
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
        chart.draw(data, options);
    }
});
