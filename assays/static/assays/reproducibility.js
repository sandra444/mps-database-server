$(document).ready(function () {

    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawTables);

    var cv_tooltip = '<span title="The CV is calculated for each time point and the value reported is the max CV across time points, or the CV if a single point is present." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    var icc_tooltip = '<span title="The ICC is a correlation coefficient that ranges from -1 to 1 with values closer to 1 being more correlated. The reproducibility status is excellent if > 0.8, acceptable if >0.2, and poor if < 0.2." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    var repro_tooltip = '<span title="Our classification of this grouping\'s reproducibility (Excellent > Acceptable > Poor/NA). If Max CV < 15% then the status is based on the  Max CV criteria, otherwise the status is based on the ICC criteria" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    var missing_tooltip = '<span title="Quantity of data points whose values were inferred by taking the average of values in the same series." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    //var comp_tooltip = '<span title="The ICC is calculated for each chip relative to the median of all of the chips." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';
    //var mad_tooltip = '<span title="Median absolute deviation of all chips\' values at all time points." class="glyphicon glyphicon-question-sign" aria-hidden="true"></span>';

    var studyID = $( "#selection-parameters" ).find(".studyId").text();

    var gasTable = $('#gas-table').DataTable( {
        data: gas_list,
        columns: [
            { title: "Show Details",
             "render": function(data, type, row) {
                if (type === 'display') {
                    groupNum = row[10];
                    return '<input type="checkbox" class="gas-checkbox-'+groupNum+'">';
                    //<a class="hidden repro-goto-'+groupNum+'" onclick=$(.repro-'+groupNum+').scrollIntoView();>Go to</a>
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
            { title: "Replica Set", data: '10', type: "num" },
            { title: "Organ Model", data: '0' },
            { title: "Compound<br>Treatment(s)", data: '2' },
            { title: "Target/Analyte", data: '3' },
            { title: "Method/Kit", data: '4' },
            { title: "Sample Location", data: '5' },
            { title: "Value Unit", data: '6' },
            { title: "Max CV/CV "+cv_tooltip, data: '7' },
            { title: "ICC Absolute Agreement "+icc_tooltip, data: '8' },
            { title: "Reproducibility<br>Status "+repro_tooltip, data: '9', render: function(data, type, row, meta){
                if (data == "Excellent (ICC)" || data == "Excellent (CV)"){
                    return '<td><span class="hidden">3</span>'+data+'</td>';
                } else if (data == "Acceptable (ICC)" || data == "Acceptable (CV)") {
                    return '<td><span class="hidden">2</span>'+data+'</td>';
                } else if (data == "Poor (ICC)" || data == "Poor (CV)") {
                    return '<td><span class="hidden">1</span>'+data+'</td>';
                } else {
                    return '<td><span class="hidden">0</span>'+data+'<span title="'+row[13]+'" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></td>';
                }
            } },
            { title: "# of Chips/Wells", data: '11' },
            { title: "# of Time Points", data: '12' },
            { title: "Cells", data: '1', class: 'none' },
            { title: "NA Explanation", data: '13', visible: false, 'name': 'naText' }
        ],
        "order": [[ 1, "asc" ]],
        "createdRow": function( row, data, dataIndex ) {
            if ( data[9][0] == "E" ) {
                $( row ).find('td:eq(10)').css( "background-color", "#74ff5b" ).css( "font-weight", "bold"  );
            }
            else if ( data[9][0] == "A" ) {
                $( row ).find('td:eq(10)').css( "background-color", "#fcfa8d" ).css( "font-weight", "bold"  );
            }
            else if ( data[9][0] == "P" ) {
                $( row ).find('td:eq(10)').css( "background-color", "#ff7863" ).css( "font-weight", "bold" );
            }
            else {
                $( row ).find('td:eq(10)').css( "background-color", "Grey" ).css( "font-weight", "bold" );
            }
        },
        "responsive": true,
        dom: 'B<"row">frtip'
    } );

    function drawTables(){
        //Clone reproducibility section per row
        var counter = 1;
        gasTable.rows().every( function ( rowIdx, tableLoop, rowLoop ) {
            var data = this.data();
            var organModel = data[0];
            var targetAnalyte = data[3];
            var methodKit = data[4];
            var sampleLocation = data[5];
            var compoundTreatments = data[2];
            var valueUnit = data[6];
            var group = data[10];
            var icc_status = data[9];
            var $elem = $( "#repro-data" );
            var $clone = $elem.first().clone( true ).addClass('repro-'+counter).appendTo("#clone-container").val("");
            mad_list[counter]['columns'].unshift("Time");
            $clone.find('#repro-title').text('Replica Set ' + group)
            $clone.find('#selection-parameters').html(buildSelectionParameters(studyID, organModel, targetAnalyte, methodKit, sampleLocation, compoundTreatments, valueUnit));
            $clone.find('#selection-parameters').find('td, th').css('padding','8px 10px');
            $clone.find('#chip-rep-rep-ind').html(buildCV_ICC(data[7],data[8]));
            $clone.find('#chip-rep-rep-ind').find('td, th').css('padding','8px 10px');
            $clone.find('#chart1').attr('id', 'chart1-'+counter);
            $clone.find('#chart2').attr('id', 'chart2-'+counter);
            if (icc_status == 'NA') {
                $clone.find('#repro-status').html('<em>'+icc_status+'</em><small style="color: black;"><span title="'+data[13]+'" class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></small>');
            } else {
                $clone.find('#repro-status').html('<em>'+icc_status+'</em>');
            }
            $clone.find('#mad-score-matrix').DataTable( {
                aoColumns: mad_columns(counter),
                data: mad_list[counter]['data'],
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
                            { title: "Missing Data Points "+missing_tooltip, data: '2' }
                        ],
                data: comp_list[counter],
                searching: false,
                paging: false,
                info: false
            });
            counter++;
        } );
    };

    // Middleware token for AJAX call
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');
});

function drawChart(list, number, title, chartNum, valueUnit){
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
    if (allNull){
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
            format: 'short',
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
        focusTarget: 'datum'
    };
    if (title == 'Chip Values/Time'){
        options['series'] = {0: { lineDashStyle: [4, 4], pointShape: { type: 'diamond', sides: 4 } }};
    }
    chart = new google.visualization.LineChart(document.getElementById(chartNum+number));
    chart.draw(data, options);
}

function mad_columns(counter){
    var columns = [];
    $.each(mad_list[counter]['columns'], function (i, value) {
        var obj = { 'sTitle' : value };
        columns.push(obj);
    });
    return columns
}

function buildSelectionParameters(studyId, organModel, targetAnalyte, methodKit, sampleLocation, compoundTreatments, valueUnit){
    content = '<tr><th>Study ID</th><td>'+studyId+'</td></tr><tr><th>Organ Model</th><td>'+organModel+'</td></tr><tr><th>Target/Analyte</th><td id="target-analyte-value">'+targetAnalyte+'</td></tr><tr><th>Method/Kit</th><td>'+methodKit+'</td></tr><tr><th>Sample Location</th><td>'+sampleLocation+'</td></tr><tr><th>Compound Treatment(s)</th><td>'+compoundTreatments+'</td></tr><tr><th>Value Unit</th><td>'+valueUnit+'</td></tr>'
    return content;
}

function buildCV_ICC(cv, icc){
    content = '<tr><th>CV(%)</th><th>ICC-Absolute Agreement</th></tr><tr><td>'+cv+'</td><td>'+icc+'</td></tr>'
    return content;
}

//Checkbox click event
$(document).on("click",":checkbox", function(){
    var checkbox = $(this)
    var checkbox_id = $(this).attr('class');
    var cls = checkbox_id.split(' ').pop();
    var number = cls.substr(cls.lastIndexOf("-") + 1);
    //var number = checkbox_id;
    var reproTable = $('.repro-'+number);
    if (checkbox.is(':checked')){
        //console.log("Showing Table " + number);
        reproTable.removeClass('hidden');
        var axisLabel = reproTable.find('#target-analyte-value').text();
        $(document).find(".repro-goto-"+number).removeClass('hidden')
        if (reproTable.find('#mad-score-matrix').width() > 500) {
            reproTable.find('#mad-score-matrix').parent().parent().removeClass('col-md-6');
            reproTable.find('#mad-score-matrix').parent().parent().addClass('col-xs-12');
            reproTable.find('#chip-comp-med').parent().parent().detach().appendTo(reproTable.find('#overflow'));
        }
        drawChart(chip_list, number, 'Chip Values/Time', 'chart1-', axisLabel);
        drawChart(cv_list, number, 'CV(%)/Time', 'chart2-', 'CV(%)');
    } else {
        //console.log("Hiding Table " + number);
        reproTable.addClass('hidden')
        //$(document).find(".repro-goto-"+number).addClass('hidden')
    }
    // Recalculate responsive and fixed headers
    $($.fn.dataTable.tables(true)).DataTable().responsive.recalc();
});
