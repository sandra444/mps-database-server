$(document).ready(function () {

    platelabels($("#id_device").val());
    //console.log("working")
    $('.id_p_time').addClass('form-control');

    //so can select table cells - keep
    $('#plate_table').selectable({
        // SUBJECT TO CHANGE: WARNING!
        filter: 'td',
        distance: 1,
        stop: changeSelected
    });

   //to format the reference table - keep
    $('#matrix_items_table').DataTable({
        "iDisplayLength": 25,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[2, "asc"]],
    });

    //show hide buttons - changing the class hide status based on checked or unchecked
   $('#show_item').change(function() {
       //console.log("show_item");
       if ($(this).is(':checked')) {
            $('.plate-cells-item').removeClass('hidden');
            console.log("show_item remove hidden");
       } else {
            $('.plate-cells-item').addClass('hidden');
            console.log("show_item add hidden");
       }
   });
   $('#show_time').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-time').removeClass('hidden');
       } else {
            $('.plate-cells-time').addClass('hidden');
       }
   });
   $('#show_location').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-location').removeClass('hidden');
       } else {
            $('.plate-cells-location').addClass('hidden');
       }
   });
   $('#show_use').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-use').removeClass('hidden');
       } else {
            $('.plate-cells-use').addClass('hidden');
       }
   });
   $('#show_replicate').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-replicate').removeClass('hidden');
       } else {
            $('.plate-cells-replicate').addClass('hidden');
       }
   });
   $('#show_label').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-label').removeClass('hidden');
       } else {
            $('.plate-cells-label').addClass('hidden');
       }
   });

    // The six selections
    // five for dragging onto plate and time unit
    // This is for viewing only
    $("#id_p_matrix_items_in_study").change(function() {
        var matrixItemText = $(this).text();
        console.log("what input matrix item text ", matrixItemText);
    });
    $("#id_p_matrix_items_in_study").change(function() {
        var matrixItemValue = $(this).val();
        console.log("what input matrix item val", matrixItemValue);
    });
    $("#id_p_sample_location").change(function() {
        var locationValue = $(this).val();
        console.log("what location ", locationValue);
    });
    $("#id_p_time").focusout(function() {
        var timeValue = $(this).val();
        console.log("on exit time", timeValue);
    });
    $("#id_p_well_use").change(function() {
        var welluseValue = $(this).val();
        console.log("what well use ", welluseValue);
    });
    $("#id_p_sample_replicate").change(function() {
        var replicateValue = $(this).val();
        console.log("what replicate ", replicateValue);
    });
    $("#id_p_time_unit").change(function() {
        var timeUnitValue = $(this).val();
        console.log("on change time unit ", timeUnitValue);
    });

    $("#id_device").change(function() {
      var plateSizeValue = $(this).val();
      console.log("what input plate size change ", plateSizeValue);
      platelabels(plateSizeValue);
    });

    function platelabels(size)
    {
        //console.log("in the function");
        //$("input[name=selectedplatesize]:text").val(inputValue);
        //$("input[name=enteredplatename]:text").val(inputValue);
        var row_labels = [];
        var col_labels = [];
        var row_contents = [];

        //note that this arrangement will be first is 0 for both row and column
        var row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
        var col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'];
        //console.log("start of plate size ", size);
        if (size == '24') {
            //console.log("24 ", size);
            row_labels = row_labels_all.slice(0,4); //['A','B','C','D'];
            col_labels = col_labels_all.slice(0,6); //['1','2','3','4','5','6'];
            row_contents = [
["A1", "A2", "A3", "A4", "A5", "A6"],
["B1", "B2", "B3", "B4", "B5", "B6"],
["C1", "C2", "C3", "C4", "C5", "C6"],
["D1", "D2", "D3", "D4", "D5", "D6"]
                ];
        } else if (size == '96') {
            //console.log("96 ", size);
            row_labels = row_labels_all.slice(0,8); //['A','B','C','D','E','F','G','H'];
            col_labels = col_labels_all.slice(0,12); //['1','2','3','4','5','6','7','8','9','10','11','12'];
            row_contents =
                    [
["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"],
["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12"],
["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12"],
["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12"],
["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12"],
["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12"],
["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12"]
                    ];

        } else {
            // '384'
            //console.log("384 ", size);
            row_labels = row_labels_all;
            col_labels = col_labels_all;
            row_contents =
                    [
["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19", "A20", "A21", "A22", "A23", "A24"],
["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24"],
["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24"],
["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24"],
["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24"],
["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24"],
["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G19", "G20", "G21", "G22", "G23", "G24"],
["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "G13", "H14", "H15", "H16", "H17", "H18", "H19", "H20", "H21", "H22", "H23", "H24"],
["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10", "I11", "I12", "I13", "I14", "I15", "I16", "I17", "I18", "I19", "I20", "I21", "I22", "I23", "I24"],
["J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9", "J10", "J11", "J12", "J13", "J14", "J15", "J16", "J17", "J18", "J19", "J20", "J21", "J22", "J23", "J24"],
["K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8", "K9", "K10", "K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18", "K19", "K20", "K21", "K22", "K23", "C24"],
["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14", "L15", "L16", "L17", "L18", "L19", "L20", "L21", "L22", "L23", "L24"],
["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23", "M24"],
["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22", "N23", "N24"],
["O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "O9", "O10", "O11", "O12", "O13", "O14", "O15", "O16", "O17", "O18", "O19", "O20", "O21", "O22", "O23", "O24"],
["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "G13", "P14", "P15", "P16", "P17", "P18", "P19", "P20", "P21", "P22", "P23", "P24"]
                    ];
        };

        // add a label to the front of column labels to hold the row labels
        //data_packed = [['Plate'].concat(col_labels), row_contents, row_labels]
        //var data_packed = [];
        data_packed = [col_labels, row_labels, row_contents];
        buildPlate(data_packed);
    };

    function buildPlate(data) {
        //console.log("data", data);
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        var tr = document.createElement("tr");
        var td = document.createElement("td");
        var headRow = document.createElement("tr");

        $('#plate_table').empty();

        // column headers
        // first column header
        var th=document.createElement("th");
        th.appendChild(document.createTextNode("Label"));
        headRow.appendChild(th);
        // rest of column headers
        data[0].forEach(function(col) {
            var th=document.createElement("th");
            th.appendChild(document.createTextNode(col));
            headRow.appendChild(th);
        })

        thead.appendChild(headRow);
        plate_table.appendChild(thead);

        // for each row
        // get the first column
        var ridx = 0
        //console.log("data[1]: ",data[1])
        data[1].forEach(function(row) {
            //console.log("ridx: ", ridx)
            //console.log("data[1][ridx]: ", data[1][ridx])
            var trlabel = document.createElement("tr");
            var trloc = document.createElement("tr");
            var trtime = document.createElement("tr");
            var tritem = document.createElement("tr");
            var truse = document.createElement("tr");
            var trrep = document.createElement("tr");

            var tdlabel = document.createElement("th");
            $(tdlabel).addClass('plate-label');
            tdlabel.appendChild(document.createTextNode(data[1][ridx]));
            trlabel.appendChild(tdlabel);

            var tdloc = document.createElement("th");
            $(tdloc).addClass('plate-location');
            tdloc.appendChild(document.createTextNode(data[1][ridx]));
            trloc.appendChild(tdloc);

            var tdtime = document.createElement("th");
            $(tdtime).addClass('plate-time');
            tdtime.appendChild(document.createTextNode(data[1][ridx]));
            trtime.appendChild(tdtime);

            var tditem = document.createElement("th");
            $(tditem).addClass('plate-item');
            tditem.appendChild(document.createTextNode(data[1][ridx]));
            tritem.appendChild(tditem);

            var tduse = document.createElement("th");
            $(tduse).addClass('plate-use');
            tduse.appendChild(document.createTextNode(data[1][ridx]));
            truse.appendChild(tduse);

            var tdrep = document.createElement("th");
            $(tdrep).addClass('plate-replicate');
            tdrep.appendChild(document.createTextNode(data[1][ridx]));
            trrep.appendChild(tdrep);


            var cidx = 0;

            //.plate-item {background-color: #fffccc}
            //.plate-location {background-color: #c1e3e6}
            //.plate-time {background-color: #d1e8d4}
            //.plate-use {background-color: #baa861}
            //.plate-replicate {background-color: #cc3f54}
            //.plate-label {background-color: #c4c2be}

            // build content row (same row as the row_labels (A=A, B=B, etc.)
            data[2][ridx].forEach(function(el) {

                var tdlabel = document.createElement("td");
                $(tdlabel).attr('data-col', cidx);
                $(tdlabel).attr('data-row', ridx);
                $(tdlabel).attr('id', "label|"+ridx+","+cidx);
                $(tdlabel).addClass('plate-label');
                tdlabel.appendChild(document.createTextNode(el));
                trlabel.appendChild(tdlabel);

                var tdloc = document.createElement("td");
                $(tdloc).attr('data-col', cidx);
                $(tdloc).attr('data-row', ridx);
                $(tdloc).attr('id', "location|"+ridx+","+cidx);
                $(tdloc).addClass('plate-location');
                tdloc.appendChild(document.createTextNode(el));
                trloc.appendChild(tdloc);

                var tdtime = document.createElement("td");
                $(tdtime).attr('data-col', cidx);
                $(tdtime).attr('data-row', ridx);
                $(tdtime).attr('id', "time|"+ridx+","+cidx);
                $(tdtime).addClass('plate-time');
                tdtime.appendChild(document.createTextNode(el));
                trtime.appendChild(tdtime);

                var tditem = document.createElement("td");
                $(tditem).attr('data-col', cidx);
                $(tditem).attr('data-row', ridx);
                $(tditem).attr('id', "item|"+ridx+","+cidx);
                $(tditem).addClass('plate-item');
                tditem.appendChild(document.createTextNode(el));
                tritem.appendChild(tditem);

                var tduse = document.createElement("td");
                $(tduse).attr('data-col', cidx);
                $(tduse).attr('data-row', ridx);
                $(tduse).attr('id', "use|"+ridx+","+cidx);
                $(tduse).addClass('plate-use');
                tduse.appendChild(document.createTextNode(el));
                truse.appendChild(tduse);

                var tdrep = document.createElement("td");
                $(tdrep).attr('data-col', cidx);
                $(tdrep).attr('data-row', ridx);
                $(tdrep).attr('id', "replicate|"+ridx+","+cidx);
                $(tdrep).addClass('plate-replicate');
                tdrep.appendChild(document.createTextNode(el));
                trrep.appendChild(tdrep);

                cidx = cidx + 0;
            })
            tbody.appendChild(trlabel);
            tbody.appendChild(truse);
            tbody.appendChild(tritem);
            tbody.appendChild(trloc);
            tbody.appendChild(trtime);
            tbody.appendChild(trrep);
            ridx = ridx + 1
        })
        plate_table.appendChild(tbody);
        return plate_table
    }


    //this will work, need to keep try of which in the formset, and change the form set of the selected table cell
    //https://www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    //https://stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function changeSelected() {
        $('.ui-selected').each(function() {

            //.plate-item {background-color: #fffccc}
            //.plate-location {background-color: #c1e3e6}
            //.plate-time {background-color: #d1e8d4}
            //.plate-use {background-color: #baa861}
            //.plate-replicate {background-color: #cc3f54}
            //.plate-label {background-color: #c4c2be}

            //$(tdlabel).attr('id', "label|"+ridx+","+cidx);
            var myid1 = "#id_assayplatereadermapitem_set-"+"0"+ "-time";
            console.log("MYID1 = " + myid1);
            console.log("whati: ",$(myid1).val());
            $(myid1).val(10);
            console.log("whato: ",$(myid1).val());

            //$("#id_assayplatereadermapitem_set-0-sample_location option[value="+loc+"]").text();
            //$("#id_assayplatereadermapitem_set-0-sample_location").val(loc);
            //$('#id_assayplatereadermapitem_set-0-sample_location-selectized option:selected').val(loc);
//<div class="selectize-input items has-options full has-items"><div class="item" data-value="2">Effluent-Brain</div><input type="select-one" autocomplete="off" tabindex="" id="id_assayplatereadermapitem_set-0-sample_location-selectized" style="width: 4px; opacity: 0; position: absolute; left: -10000px;"></div>

            //$('.c2r2 option[value=loc]').attr('selected','selected');

            ///    if (field_name == 'name' || current_form.find('input[name$="name"]').val()) {
            //        form_field_to_add_to.val(current_value);
            //if (current_method_id) {
            //    current_method[0].selectize.setValue(current_method_id);
            //}

            //var myid2 = "#id_assayplatereadermapitem_set-"+"0"+ "-sample_location"
            //console.log("whati: ",$("#id_assayplatereadermapitem_set-0-sample_location").text());
            ///console.log("to: ",$("#id_p_sample_location").option())
            //$("#id_assayplatereadermapitem_set-0-sample_location option[value=35]")attr('selcted',})"($("#id_p_sample_location").text());
            //onsole.log("whato: ",$("#id_assayplatereadermapitem_set-0-sample_location-selectized").text);

            // var myid3 = "#id_assayplatereadermapitem_set-"+"0"+ "-well_use-selectized"
            // console.log("whati: ",$(myid3).text());
            // console.log("to: ",$("#id_p_well_use").text())
            // $(myid3).text($("#id_p_well_use").text());
            // console.log("whato: ",$(myid3).text());
            //
            // var myid4 = "#id_assayplatereadermapitem_set-"+"0"+ "-name-selectized"
            // console.log("whati: ",$(myid4).text());
            // console.log("to: ",$("#id_p_matrix_items_in_study").text())
            // $(myid4).text($("#id_p_matrix_items_in_study").text());
            // console.log("whato: ",$(myid4).text());


            // console.log($(this));
            // console.log($(this).class);
            // console.log($(this).text());
            // console.log($(this).attr('dcol'));
            // console.log($(this).attr('drow'));
            // //<td data-col="3" data-row="B" class="plate-location">B 3 (location)</td>
            // if ($(this).hasClass("plate-label")) {
            //     #console.log("content ",$("#id_p_well_use").text());
            //     //$(this).text = $("#id_matrix_item_list").text();
            //     //$("input[name=enteredplatename]:text").val(inputValue)
            //     //$(this).text("new content");
            //     #$(this).text($("#id_p_well_use").text());
            // } else if ($(this).hasClass("plate-location")) {
            //     console.log("location ",$("#id_p_sample_location").text());
            //     #$(this).text($("#id_p_sample_location").text());
            // } else {
            //     console.log("time ",$("#id_p_time").val());
            //     #$(this).text($("#id_p_time").val());
            // }
        });
    }



    //<input type="number" name="assayplatereadermapitem_set-0-time" value="1.0" step="any" class="form-control" id="id_assayplatereadermapitem_set-0-time">







/*
$('#add_more').click(function() {
	var form_idx = $('#id_form-TOTAL_FORMS').val();
	$('#form_set').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
	$('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
});
*/





});
