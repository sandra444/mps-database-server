$(document).ready(function () {
    //console.log("working")
    $('.id_p_time').addClass('form-control');

    //platelabels($("#id_device").val());

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
       console.log("show_item");
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
        var matrixItemText = $(this).text()
        console.log("what input matrix item text ", matrixItemText);
    });
    $("#id_p_matrix_items_in_study").change(function() {
        var matrixItemValue = $(this).val()
        console.log("what input matrix item val", matrixItemValue);
    });
    $("#id_p_sample_location").change(function() {
        var locationValue = $(this).val()
        console.log("what location ", locationValue);
    });
    $("#id_p_time").focusout(function() {
        var timeValue = $(this).val()
        console.log("on exit time", timeValue);
    });
    $("#id_p_well_use").change(function() {
        var welluseValue = $(this).val()
        console.log("what well use ", welluseValue);
    });
    $("#id_p_sample_replicate").change(function() {
        var replicateValue = $(this).val()
        console.log("what replicate ", replicateValue);
    });
    $("#id_p_time_unit").change(function() {
        var timeUnitValue = $(this).val()
        console.log("on change time unit ", timeUnitValue);
    });


    //platelabels($("#id_device").val());

    $("#id_device").change(function() {
      var plateSizeValue = $(this).val()
      console.log("what input plate size change ", plateSizeValue);
      //platelabels(plateSizeValue)
    });

    function platelabels(size)
    {
        var workup_only = false;
        //$("input[name=selectedplatesize]:text").val(inputValue);
        //$("input[name=enteredplatename]:text").val(inputValue);
        var row_labels = [];
        var col_labels = [];
        var row_contents = [];
        //note that this arrangement will be first is 0 for both row and column
        var row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
        var col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'];
        console.log("start of plate size ", size);

        if (size == '24') {
            console.log("24 ", size);
            row_labels = row_labels_all.slice(0,4) //['A','B','C','D'];
            col_labels = col_labels_all.slice(0,6) //['1','2','3','4','5','6'];
            if (workup_only == false)
            {
                row_contents = [
{0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6"},
{0: "A", 1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6"},
{0: "B", 1: "B1", 2: "B2", 3: "B3", 4: "B4", 5: "B5", 6: "B6"},
{0: "C", 1: "C1", 2: "C2", 3: "C3", 4: "C4", 5: "C5", 6: "C6"},
{0: "D", 1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5", 6: "D6"}
                ]
            }
        } else if (size == '96') {
            console.log("96 ", size);
            row_labels = row_labels_all.slice(0,8) //['A','B','C','D','E','F','G','H'];
            col_labels = col_labels_all.slice(0,12) //['1','2','3','4','5','6','7','8','9','10','11','12'];
            if (workup_only == false)
            {
                row_contents =
                    [
{0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12"},
{0: "A", 1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6", 7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12"},
{0: "B", 1: "B1", 2: "B2", 3: "B3", 4: "B4", 5: "B5", 6: "B6", 7: "B7", 8: "B8", 9: "B9", 10: "B10", 11: "B11", 12: "B12"},
{0: "C", 1: "C1", 2: "C2", 3: "C3", 4: "C4", 5: "C5", 6: "C6", 7: "C7", 8: "C8", 9: "C9", 10: "C10", 11: "C11", 12: "C12"},
{0: "D", 1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5", 6: "D6", 7: "D7", 8: "D8", 9: "D9", 10: "D10", 11: "D11", 12: "D12"},
{0: "E", 1: "E1", 2: "E2", 3: "E3", 4: "E4", 5: "E5", 6: "E6", 7: "E7", 8: "E8", 9: "E9", 10: "E10", 11: "E11", 12: "E12"},
{0: "F", 1: "F1", 2: "F2", 3: "F3", 4: "F4", 5: "F5", 6: "F6", 7: "F7", 8: "F8", 9: "F9", 10: "F10", 11: "F11", 12: "F12"},
{0: "G", 1: "G1", 2: "G2", 3: "G3", 4: "G4", 5: "G5", 6: "G6", 7: "G7", 8: "G8", 9: "G9", 10: "G10", 11: "G11", 12: "G12"},
{0: "H", 1: "H1", 2: "H2", 3: "H3", 4: "H4", 5: "H5", 6: "H6", 7: "H7", 8: "H8", 9: "H9", 10: "H10", 11: "H11", 12: "H12"}
                    ]
            }
        } else {
            // '384'
            console.log("384 ", size);
            row_labels = row_labels_all;
            col_labels = col_labels_all;
            if (workup_only == false)
                {
                row_contents =
                    [
{0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "11", 12: "12", 13: "13", 14: "14", 15: "15", 16: "16", 17: "17", 18: "18", 19: "19", 20: "20", 21: "21", 22: "22", 23: "23", 24: "24"},
{0: "A", 1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6", 7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "A12", 13: "A13", 14: "A14", 15: "A15", 16: "A16", 17: "A17", 18: "A18", 19: "A19", 20: "A20", 21: "A21", 22: "A22", 23: "A23", 24: "A24"},
{0: "B", 1: "B1", 2: "B2", 3: "B3", 4: "B4", 5: "B5", 6: "B6", 7: "B7", 8: "B8", 9: "B9", 10: "B10", 11: "B11", 12: "B12", 13: "B13", 14: "B14", 15: "B15", 16: "B16", 17: "B17", 18: "B18", 19: "B19", 20: "B20", 21: "B21", 22: "B22", 23: "B23", 24: "B24"},
{0: "C", 1: "C1", 2: "C2", 3: "C3", 4: "C4", 5: "C5", 6: "C6", 7: "C7", 8: "C8", 9: "C9", 10: "C10", 11: "C11", 12: "C12", 13: "C13", 14: "C14", 15: "C15", 16: "C16", 17: "C17", 18: "C18", 19: "C19", 20: "C20", 21: "C21", 22: "C22", 23: "C23", 24: "C24"},
{0: "D", 1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5", 6: "D6", 7: "D7", 8: "D8", 9: "D9", 10: "D10", 11: "D11", 12: "D12", 13: "D13", 14: "D14", 15: "D15", 16: "D16", 17: "D17", 18: "D18", 19: "D19", 20: "D20", 21: "D21", 22: "D22", 23: "D23", 24: "D24"},
{0: "E", 1: "E1", 2: "E2", 3: "E3", 4: "E4", 5: "E5", 6: "E6", 7: "E7", 8: "E8", 9: "E9", 10: "E10", 11: "E11", 12: "E12", 13: "E13", 14: "E14", 15: "E15", 16: "E16", 17: "E17", 18: "E18", 19: "E19", 20: "E20", 21: "E21", 22: "E22", 23: "E23", 24: "E24"},
{0: "F", 1: "F1", 2: "F2", 3: "F3", 4: "F4", 5: "F5", 6: "F6", 7: "F7", 8: "F8", 9: "F9", 10: "F10", 11: "F11", 12: "F12", 13: "F13", 14: "F14", 15: "F15", 16: "F16", 17: "F17", 18: "F18", 19: "F19", 20: "F20", 21: "F21", 22: "F22", 23: "F23", 24: "F24"},
{0: "G", 1: "G1", 2: "G2", 3: "G3", 4: "G4", 5: "G5", 6: "G6", 7: "G7", 8: "G8", 9: "G9", 10: "G10", 11: "G11", 12: "G12", 13: "G13", 14: "G14", 15: "G15", 16: "G16", 17: "G17", 18: "G18", 19: "G19", 20: "G20", 21: "G21", 22: "G22", 23: "G23", 24: "G24"},
{0: "H", 1: "H1", 2: "H2", 3: "H3", 4: "H4", 5: "H5", 6: "H6", 7: "H7", 8: "H8", 9: "H9", 10: "H10", 11: "H11", 12: "H12", 13: "H13", 14: "H14", 15: "H15", 16: "H16", 17: "H17", 18: "H18", 19: "H19", 20: "H20", 21: "H21", 22: "H22", 23: "H23", 24: "H24"},
{0: "I", 1: "I1", 2: "I2", 3: "I3", 4: "I4", 5: "I5", 6: "I6", 7: "I7", 8: "I8", 9: "I9", 10: "I10", 11: "I11", 12: "I12", 13: "I13", 14: "I14", 15: "I15", 16: "I16", 17: "I17", 18: "I18", 19: "I19", 20: "I20", 21: "I21", 22: "I22", 23: "I23", 24: "I24"},
{0: "J", 1: "J1", 2: "J2", 3: "J3", 4: "J4", 5: "J5", 6: "J6", 7: "J7", 8: "J8", 9: "J9", 10: "J10", 11: "J11", 12: "J12", 13: "J13", 14: "J14", 15: "J15", 16: "J16", 17: "J17", 18: "J18", 19: "J19", 20: "J20", 21: "J21", 22: "J22", 23: "J23", 24: "J24"},
{0: "K", 1: "K1", 2: "K2", 3: "K3", 4: "K4", 5: "K5", 6: "K6", 7: "K7", 8: "K8", 9: "K9", 10: "K10", 11: "K11", 12: "K12", 13: "K13", 14: "K14", 15: "K15", 16: "K16", 17: "K17", 18: "K18", 19: "K19", 20: "K20", 21: "K21", 22: "K22", 23: "K23", 24: "K24"},
{0: "L", 1: "L1", 2: "L2", 3: "L3", 4: "L4", 5: "L5", 6: "L6", 7: "L7", 8: "L8", 9: "L9", 10: "L10", 11: "L11", 12: "L12", 13: "L13", 14: "L14", 15: "L15", 16: "L16", 17: "L17", 18: "L18", 19: "L19", 20: "L20", 21: "L21", 22: "L22", 23: "L23", 24: "L24"},
{0: "M", 1: "M1", 2: "M2", 3: "M3", 4: "M4", 5: "M5", 6: "M6", 7: "M7", 8: "M8", 9: "M9", 10: "M10", 11: "M11", 12: "M12", 13: "M13", 14: "M14", 15: "M15", 16: "M16", 17: "M17", 18: "M18", 19: "M19", 20: "M20", 21: "M21", 22: "M22", 23: "M23", 24: "M24"},
{0: "N", 1: "N1", 2: "N2", 3: "N3", 4: "N4", 5: "N5", 6: "N6", 7: "N7", 8: "N8", 9: "N9", 10: "N10", 11: "N11", 12: "N12", 13: "N13", 14: "N14", 15: "N15", 16: "N16", 17: "N17", 18: "N18", 19: "N19", 20: "N20", 21: "N21", 22: "N22", 23: "N23", 24: "N24"},
{0: "O", 1: "O1", 2: "O2", 3: "O3", 4: "O4", 5: "O5", 6: "O6", 7: "O7", 8: "O8", 9: "O9", 10: "O10", 11: "O11", 12: "O12", 13: "O13", 14: "O14", 15: "O15", 16: "O16", 17: "O17", 18: "O18", 19: "O19", 20: "O20", 21: "O21", 22: "O22", 23: "O23", 24: "O24"},
{0: "P", 1: "P1", 2: "P2", 3: "P3", 4: "P4", 5: "P5", 6: "P6", 7: "P7", 8: "P8", 9: "P9", 10: "P10", 11: "P11", 12: "P12", 13: "P13", 14: "P14", 15: "P15", 16: "P16", 17: "P17", 18: "P18", 19: "P19", 20: "P20", 21: "P21", 22: "P22", 23: "P23", 24: "P24"}
                    ]
                }
        }
        // just to create the stuff hardcoded above (to save run time)
        if (workup_only)
        {
            // from 'A' to ?
            row_labels.forEach(function (rl) {
                var row_dict = {}
                // add for the row label
                //row_dict['0'] = rl
                //console.log(rl)
                // from '1' to ?
                col_labels.forEach(function (cl) {
                    console.log("col ", cl)
                    // this is working 20190917
                    row_dict[cl] = rl + cl
                    console.log("row dict ", row_dict[cl])
                })
                console.log("row dict should be all ", row_dict)
                //push into a list of dictionaries
                row_contents.push(row_dict);
            });
            //console.log(cell_labels)
            console.log('row_contents')
            console.log(row_contents)
            //need a formset for these....this should be name
            // 0: {1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6"}
            // 1: {1: "B1", 2: "B2", 3: "B3", 4: "B4", 5: "B5", 6: "B6"}
            // 2: {1: "C1", 2: "C2", 3: "C3", 4: "C4", 5: "C5", 6: "C6"}
            // 3: {1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5", 6: "D6"}
            // length: 4
            // add a label to the front of column labels to hold the row labels
            //data_packed = [['Plate'].concat(col_labels), row_contents, row_labels]
            //var data_packed = [];
            //data_packed = [col_labels, row_contents, row_labels]
            //buildTableChips(data_packed)
        }
    };


    function buildTableChips(data) {
        // col_labels, row_labels, row_contents
        //.plate-item {background-color: #fffccc}
        //.plate-location {background-color: #c1e3e6}
        //.plate-time {background-color: #d1e8d4}
        //.plate-use {background-color: #baa861}
        //.plate-replicate {background-color: #cc3f54}
        //.plate-label {background-color: #c4c2be}
        console.log("data", data)

        $('#tablecellsselection').empty();
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        var headRow = document.createElement("tr");
        console.log("what's here")
        console.log("data0", data[0])
        console.log("data1", data[1])
        console.log("data2", data[2])
        // column headers
        data[0].forEach(function(el) {
            var th=document.createElement("th");
            th.appendChild(document.createTextNode(el));
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        tablecellsselection.appendChild(thead);
        // add the content, and add a place for sample location and sample time, with class for show/hide
        var idx = 0
        data[1].forEach(function(el) {
            var trc = document.createElement("tr");
            var trl = document.createElement("tr");
            var trt = document.createElement("tr");
            // build content row
            for (var o in el) {
                if (o == 0) {
                    //content
                    var tdc = document.createElement("th");
                    $(tdc).attr('data-col', o);
                    $(tdc).attr('data-row', el[0]);
                    $(tdc).addClass('plate-content');
                    tdc.appendChild(document.createTextNode(el[o]));
                    trc.appendChild(tdc);
                    // location
                    var tdl = document.createElement("th");
                    $(tdl).attr('data-col', o);
                    $(tdl).attr('data-row', el[0]);
                    $(tdl).addClass('plate-location hidden');
                    tdl.appendChild(document.createTextNode(el[o]+" (location)"));
                    trl.appendChild(tdl);
                    // time
                    var tdt = document.createElement("th");
                    $(tdt).attr('data-col', o);
                    $(tdt).attr('data-row', el[0]);
                    $(tdt).addClass('plate-time hidden');
                    tdt.appendChild(document.createTextNode(el[o]+" (time)"));
                    trt.appendChild(tdt);
                } else {
                    //content
                    var tdc = document.createElement("td");
                    $(tdc).attr('data-col', o);
                    $(tdc).attr('data-row', el[0]);
                    $(tdc).addClass('plate-content');
                    tdc.appendChild(document.createTextNode(""));
                    trc.appendChild(tdc);
                    // location
                    var tdl = document.createElement("td");
                    $(tdl).attr('data-col', o);
                    $(tdl).attr('data-row', el[0]);
                    $(tdl).addClass('plate-location hidden');
                    tdl.appendChild(document.createTextNode(""));
                    trl.appendChild(tdl);
                    // time
                    var tdt = document.createElement("td");
                    $(tdt).attr('data-col', o);
                    $(tdt).attr('data-row', el[0]);
                    $(tdt).addClass('plate-time hidden');
                    tdt.appendChild(document.createTextNode(""));
                    trt.appendChild(tdt);
                }
            }
            tbody.appendChild(trc);
            tbody.appendChild(trl);
            tbody.appendChild(trt);
        });
        tablecellsselection.appendChild(tbody);
        return tablecellsselection;
    }


    //this will work, need to keep try of which in the formset, and change the form set of the selected table cell
    //https://www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    //https://stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function changeSelected() {
        $('.ui-selected').each(function() {
            var myid1 = "#id_assayplatereadermapitem_set-"+"0"+ "-time";
            console.log("MYID1 = " + myid1);
            console.log("whati: ",$(myid1).val());
            $(myid1).val(10);
            console.log("whato: ",$(myid1).val());

// #<select name="assayplatereadermapitem_set-0-sample_location" class="form-control selectized"
//             id="id_assayplatereadermapitem_set-0-sample_location"
//             tabindex="-1" style="display: none;">Effluent-Brain</select>
// <option value="16" selected="selected">Basolateral</option>

//var v = $("#yourid").val();
//$("#yourid option[value="+v+"]").text()
//$('.id_100 option[value=val2]').attr('selected','selected');


 //$("input[name=enteredplatename]:text").val(inputValue);

            //<input type="select-one" autocomplete="off" tabindex="" id="id_assayplatereadermapitem_set-0-sample_location-selectized" placeholder="---------" style="width: 46px; opacity: 1; position: relative; left: 0px;">
            //"id_assayplatereadermapitem_set-0-sample_location-selectized"
            var iii = $("#id_assayplatereadermapitem_set-0-sample_replicate").val()
            console.log("iii: ", iii)
            $("#id_assayplatereadermapitem_set-0-sample_replicate").val(5)
            var ii2 = $("#id_assayplatereadermapitem_set-0-sample_replicate").val()
            console.log("ii2: ", ii2)
            $("#id_assayplatereadermapitem_set-0-well_use").val('blank')
            var ii3 = $("#id_assayplatereadermapitem_set-0-well_use").val()
            console.log("ii3: ", $("#id_assayplatereadermapitem_set-0-well_use").val())
            var loc = $("#id_p_sample_location").val()
            console.log("loc: ", loc)
            var mai = $("#id_p_matrix_items_in_study").val()
            console.log("mai: ", mai);
            var mait = $("#id_p_matrix_items_in_study").text()
            console.log("mait: ", mait);
            var wus = $("#id_p_well_use").val()
            console.log("wus: ", wus)
            var tim = $("#id_p_time").val()
            console.log("tim: ", tim);
            var tiu = $("#id_p_time_unit").val()
            console.log("tiu: ", tiu);
            $('#assayplatereadermapitem_set-0-well_use').val('standard');
            $('#assayplatereadermapitem_set-0-well_use').text('Standard');
            var whatme = $(".assayplatereadermapitem_set-0-well_use option:selected").val();
            console.log(whatme)
            var whatme = $('#aitem.well_use').val();
            console.log(whatme)
            var whatme = $('#aitem.well_use').text();
            console.log(whatme)
            $("#item option[value=standard]").text()
            //var arNames = $('#Crd').val()
            //$("#<%=dropDownId.ClientID%>").children("option:selected").val();
            //$(this).text = $("#id_matrix_item_list").text();
            //$("input[name=enteredplatename]:text").val(inputValue)
            //$(this).text("new content");
            //#$(this).text($("#id_p_well_use").text());

                                    //<td id="c1r1" dcol="1" drow="1" class="plate-well-use">{{ aitem.well_use }}</td>
                                   // <td id="c2r2" dcol="2" drow="3" class="plate-location">{{ aitem.sample_location }}</td>
                                    //<td id="c3r3" dcol="3" drow="3" class="plate-time">{{ aitem.time }}</td>
                                    //<td id="c4r4" dcol="4" drow="4" class="plate-label">{{ aitem.name }}</td>

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
            // if ($(this).hasClass("plate-content")) {
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
