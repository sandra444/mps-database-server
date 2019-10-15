$(document).ready(function () {
    console.log("in js file 1");

    // these should be the same as the model defaults
    let global_plate_matrix_item_show = "";
    let global_plate_matrix_item_value = 0;
    let global_plate_well_use = "empty";
    let global_plate_time = 1;
    let global_plate_time_unit = "day";
    let global_plate_replicate = 1;
    let global_plate_location_show = "";
    let global_plate_location_value = 0;
    let global_plate_size = 24;

    // did now seem to work so put in forms.py $('.id_p_time').addClass('form-control');

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

    console.log("in js file 2");

    //show hide buttons - changing the class of the plate map to show/hide based on checked or unchecked
    $('#show_item').change(function() {
       //console.log("show_item");
       if ($(this).is(':checked')) {
            $('.plate-cells-item').removeClass('hidden');
       } else {
            $('.plate-cells-item').addClass('hidden');
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

    console.log("in js file 3");

    // when loading, what and how to load the plate
    if ($("#page_called").val() === 'add') {
        $("#device").val(global_plate_size);
        platelabels($(global_plate_size), "y");
    } else {
        platelabels($("#device").val(), "n");
    }

    // when add page and the user changes the plate size, have to reload empty plate the correct size
    $("#device").change(function() {
      global_plate_size = $(this).val();
      platelabels(global_plate_size, "y");
    });

    function platelabels(size, adding)
    {
        //console.log("in the function");
        console.log("in platelabels function");
        //$("input[name=selectedplatesize]:text").val(inputValue);
        //$("input[name=enteredplatename]:text").val(inputValue);
        let row_labels = [];
        let col_labels = [];
        let row_contents = [];

        //note that this arrangement will be first is 0 for both row and column
        let row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
        let col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'];
        //console.log("start of plate size ", size);
        if (size === 24) {
            row_labels = row_labels_all.slice(0,4); //['A','B','C','D'];
            col_labels = col_labels_all.slice(0,6); //['1','2','3','4','5','6'];
            row_contents = [
["A1", "A2", "A3", "A4", "A5", "A6"],
["B1", "B2", "B3", "B4", "B5", "B6"],
["C1", "C2", "C3", "C4", "C5", "C6"],
["D1", "D2", "D3", "D4", "D5", "D6"]
                ];
        } else if (size === 96) {
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
        }

        // add a label to the front of column labels to hold the row labels
        //data_packed = [['Plate'].concat(col_labels), row_contents, row_labels]
        //let data_packed = [];
        let data_packed = [col_labels, row_labels, row_contents];
        buildPlate(data_packed, adding);
    }

    function buildPlate(data, adding) {
        let list_formset_fields = ['sample_location','matrix_item','time','time_unit','well_use','sample_replicate']
        console.log("in build plate function");
        //console.log("data", data);
        //this table's table tag and closing tag are in the html file
        $('#plate_table').empty();
        let thead = document.createElement("thead");
        //let td = document.createElement("td");
        let headRow = document.createElement("tr");
        // column headers: first, then the rest in loop
        let th=document.createElement("th");
        th.appendChild(document.createTextNode("Label"));
        headRow.appendChild(th);
        data[0].forEach(function(col) {
            let th=document.createElement("th");
            th.appendChild(document.createTextNode(col));
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        plate_table.appendChild(thead);

        // for each row
        let tbody = document.createElement("tbody");
        //let tr = document.createElement("tr");
        // get the first column (A B C D E...)
        let formsetidx = 0;
        let ridx = 0;
        data[1].forEach(function(row) {
            let trbodyrow = document.createElement("tr");
            let tdbodyrow = document.createElement("th");
            tdbodyrow.appendChild(document.createTextNode(data[1][ridx]));
            trbodyrow.appendChild(tdbodyrow);

            let cidx = 0;

            // build content row (same row as the row_labels (A=A, B=B, etc.)
            // while in a row, go through each column
            // make these six in a nested table

            data[2][ridx].forEach(function(el) {

                let tdlabel = document.createElement("td");
                $(tdlabel).attr('data-index', formsetidx);
                $(tdlabel).attr('id', "label|"+ridx+","+cidx);
                //for coloring
                $(tdlabel).addClass('map-label');
                $(tdlabel).addClass('no-selectize');

                let tdloc = document.createElement("td");
                $(tdloc).attr('data-index', formsetidx);
                $(tdloc).attr('id', "location|"+ridx+","+cidx);
                $(tdloc).addClass('map-location');
                $(tdloc).addClass('no-selectize');

                let tdtime = document.createElement("td");
                $(tdtime).attr('data-index', formsetidx);
                $(tdtime).attr('id', "time|"+ridx+","+cidx);
                $(tdtime).addClass('map-time');
                $(tdtime).addClass('no-selectize');

                let tditem = document.createElement("td");
                $(tditem).attr('data-index', formsetidx);
                $(tditem).attr('id', "item|"+ridx+","+cidx);
                $(tditem).addClass('map-item');
                $(tditem).addClass('no-selectize');

                let tduse = document.createElement("td");
                $(tduse).attr('data-index', formsetidx);
                $(tduse).attr('id', "use|"+ridx+","+cidx);
                $(tduse).addClass('map-use');
                $(tduse).addClass('no-selectize');

                let tdrep = document.createElement("td");
                $(tdrep).attr('data-index', formsetidx);
                $(tdrep).attr('id', "replicate|"+ridx+","+cidx);
                $(tdrep).addClass('map-replicate');
                $(tdrep).addClass('no-selectize');

                let cellTableTD = document.createElement("td");
                $(cellTableTD).attr('id', "#nt_"+ridx+","+cidx);
                let cellTable = document.createElement("table");
                let cellBody = document.createElement("body");

                let celliTR1 = document.createElement("tr");
                let celliTR2 = document.createElement("tr");
                let celliTR3 = document.createElement("tr");
                let celliTR4 = document.createElement("tr");
                let celliTR5 = document.createElement("tr");
                let celliTR6 = document.createElement("tr");

                //for hiding
                $(celliTR1).addClass('plate-cells-label');
                $(celliTR2).addClass('plate-cells-use');
                $(celliTR3).addClass('plate-cells-item');
                $(celliTR4).addClass('plate-cells-time');
                $(celliTR5).addClass('plate-cells-location');
                $(celliTR6).addClass('plate-cells-replicate');
                // example $(celliTR6).addClass('plate-cells-replicate hidden');


                if (adding === "y") {
                    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
                    $('#form_set').append($('#empty_form').html().replace(/__prefix__/g, formsetidx));
                    $('#id_form-TOTAL_FORMS').val(parseInt(formsetidx));
                    //https://medium.com/all-about-django/adding-forms-dynamically-to-a-django-formset-375f1090c2b0
                    //list_formset_fields.forEach(function(ef) {
                        $('#empty_form').html().attr('name').replace('set-undefined-', 'set-' + formsetidx + '-');
                        $('#empty_form').html().attr('id').replace('set-undefined-', 'set-' + formsetidx + '-');
                    //});

                    tduse.appendChild(document.createTextNode("empty"));
                    tditem.appendChild(document.createTextNode("-"));
                    tdtime.appendChild(document.createTextNode("0"));
                    tdloc.appendChild(document.createTextNode("-"));
                    tdrep.appendChild(document.createTextNode("1"));
                    tdlabel.appendChild(document.createTextNode(el));

                    //$("input[name=enteredplatename]:text").val(inputValue);
                    $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-study').val($('#object_study').val());
                    $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-assayplatereadermap').val($('#object_plate_size').val());

                    $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-row_index').val(ridx);
                    $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-column_index').val(cidx);
                    //<br>form device {% include 'generic_field.html' with field=form.device label="Plate Size"  %}
                    //<br>plate size <h4 id="object_plate_size">{{ object.device }}</h4>
                    //<br>plate id <h4 id="object_plate_id">{{ object.id }}</h4>
                    //<br>study <h4 id="object_study">{{ object.study }}</h4>
                    //<br>form name {% include 'generic_field.html' with field=form.name label="Map Name"  %}
                    //{#  This is used to know if building plate from scratch or from existing plate (add, view, update)#}
                    //<br>page called <div id="page_called"><br>{{ page_called }}<br></div>

                } else {
                    // the formset where ridx is row_index and cidx is column_index
                    //    row_index = models.IntegerField(default=1, blank=True )
                    //     column_index = models.IntegerField(default=1, blank=True )
                    // or where el (A1, A2) is name
                    //#TODO fix this later...
                    //id_assayplatereadermapitem_set-0-study-selectized
                    if (formsetidx < 3) {
                        //left them undefined
                        //tditem.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item').data('value')));
                        //tdloc.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-sample_location').data('value')));

                        // this fills them with the pk...close..need to get the associated name
                        tditem.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item').val()));
                        tdloc.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-sample_location').val()));
                        //TODO figure out how to fill with the name instead of the pk
                        let myname_matrixitem = $('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item')
                        let myname_location = $('#id_assayplatereadermapitem_set-' + formsetidx + '-location')


                        tduse.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-well_use').val()));
                        tdtime.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-time').val()));
                        tdrep.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-sample_replicate').val()));
                        tdlabel.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val()));

/*                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-well_use').val());
                        // this prints ALL the matrix items...not what we want, but could be why the loading time .text
                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item').text());
                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-time').val());
                        // this prints ALL the matrix items...not what we want, but could be why the loading time .text
                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-sample_location').text());
                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-sample_replicate').val());
                        console.log($('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val());*/

                    } else {
                        tduse.appendChild(document.createTextNode("empty"));
                        tditem.appendChild(document.createTextNode("-"));
                        tdtime.appendChild(document.createTextNode("0"));
                        tdloc.appendChild(document.createTextNode("-"));
                        tdrep.appendChild(document.createTextNode("1"));
                        tdlabel.appendChild(document.createTextNode(el));
                    }
                }
                formsetidx = formsetidx + 1;

                // put it all together
                celliTR1.appendChild(tdlabel);
                cellBody.appendChild(celliTR1);
                celliTR2.appendChild(tduse);
                cellBody.appendChild(celliTR2);
                celliTR3.appendChild(tditem);
                cellBody.appendChild(celliTR3);
                celliTR4.appendChild(tdtime);
                cellBody.appendChild(celliTR4);
                celliTR5.appendChild(tdloc);
                cellBody.appendChild(celliTR5);
                celliTR6.appendChild(tdrep);
                cellBody.appendChild(celliTR6);
                cellTable.appendChild(cellBody);
                cellTableTD.appendChild(cellTable);
                trbodyrow.appendChild(cellTableTD);

                cidx = cidx + 1;
            });

            tbody.appendChild(trbodyrow);
            ridx = ridx + 1;
        });

        plate_table.appendChild(tbody);
        return plate_table
    }

    console.log("in js file 4");

    // Set the global or other variables for the six selections
    // five for dragging onto plate and time unit
    $("#id_p_matrix_items_in_study").change(function() {
        //http://jsfiddle.net/9aXYc/39/
        global_plate_matrix_item_show = $(this).val();
        global_plate_matrix_item_value = $(this).data('value');
        console.log('data value: ', global_plate_matrix_item_show);
        console.log('value: ', global_plate_matrix_item_value);
    });
    $("#id_p_sample_location").change(function() {
        global_plate_location_show = $(this).val();
        global_plate_location_value = $(this).data('value');
        console.log('data value: ', global_plate_location_show);
        console.log('value: ', global_plate_location_value);
    });
    $("#id_p_time").focusout(function() {
        global_plate_time = $(this).val();
    });
    $("#id_p_well_use").change(function() {
        global_plate_well_use = $(this).val();
    });
    $("#id_p_sample_replicate").change(function() {
        global_plate_replicate = $(this).val();
    });
    $("#id_p_time_unit").change(function() {
        global_plate_time_unit = $(this).val();
        let i;
        for (i = 0; i < global_plate_size; i++) {
          $('#id_assayplatereadermapitem_set-' + i + '-time_unit').val(global_plate_time_unit);
        }
    });

    console.log("in js file 5");

    // replace in plate map
    // https://www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    // https://stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function changeSelected() {
        $('.ui-selected').each(function () {
            if ($(this).hasClass("map-location") && (!$(this).hasClass("hidden"))) {
                //fills with the pk  TODO get filled with name
                $(this).text(global_plate_location_show);

                //did not make a change
                //$('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-sample_location').data(global_plate_location_value);
                $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-sample_location').val(global_plate_location_show);

            } else if ($(this).hasClass("map-item") && (!$(this).hasClass("hidden"))) {
                //fills with the pk  TODO get filled with name
                $(this).text(global_plate_matrix_item_show);

                //$(this).data('value', global_plate_matrix_item_value);

                //did not make a change
                //$('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-matrix_item').data(global_plate_matrix_item_value);
                //this is working correctly
                $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-matrix_item').val(global_plate_matrix_item_show);

            } else if ($(this).hasClass("map-time") && (!$(this).hasClass("hidden"))) {
                $(this).text(global_plate_time);
                $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-time').val(global_plate_time);
            } else if ($(this).hasClass("map-replicate") && (!$(this).hasClass("hidden"))) {
                $(this).text(global_plate_replicate);
                $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-sample_replicate').val(global_plate_replicate);
            } else if ($(this).hasClass("map-use") && (!$(this).hasClass("hidden"))) {
                $(this).text(global_plate_well_use);
                $('#id_assayplatereadermapitem_set-' + $(this).attr('data-index') + '-well_use').val(global_plate_well_use);
            } else {
                //console.log("this.text else", $(this).text())
            }
            //#TODO need to figure out why the model foreign keys are not going in correctly.
        });
    }

    console.log("in js file 6");

    //keep for references for now - can use if formset is not hidden
    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
    $('#add_more').click(function() {
    var form_idx = $('#id_form-TOTAL_FORMS').val();
    $('#form_set').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
    $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
    //error $('#empty_form').html().attr('name').replace('set-undefined-', 'set-' + form_idx + 1 + '-');
    // error$('#empty_form').html().attr('id').replace('set-undefined-', 'set-' + form_idx + 1 + '-');
    //$('#empty_form').html().id = "newid";
    //$('#empty_form').html().name = "newname";
        //TODO figure out how to reference new formsets...maybe Luke knows
    });

});

//        console.log("start of plate size ", inputValue);
//         $("input[name=enteredplatename]:text").val(inputValue);



