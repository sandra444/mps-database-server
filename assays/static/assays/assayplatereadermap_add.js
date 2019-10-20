$(document).ready(function () {
    //console.log("in js file 1");
    // # id, . class

    // these should be the same as the model defaults
    let global_plate_matrix_item_text = "";
    let global_plate_matrix_item = 0;
    let global_plate_well_use = "empty";
    let global_plate_time = 1;
    let global_plate_time_unit = "day";
    let global_plate_replicate = 1;
    let global_plate_location_text = "Unspecified";
    let global_plate_location = 0;
    let global_plate_size = 24;

    // get the copy of the empty formset (the "extra" in the forms.py)
    // The forms.py has an extra of 1
    // for the add page, it gets copied x times (24, 96, 384)
    // the update page also comes with one extra
    // Just takes the html and purges it (avoid duplicate formset instances etc)
    var first_form = $('#form_set').find('.inline').first()[0].outerHTML;
    if ($('#form_set').find('.inline').length === 1 && $("#check_load").html() === 'add') {
        $('#form_set').find('.inline').first().remove();
    }

    // Set the global or other variables for the six selections
    // five for dragging onto plate and time unit
    $("#id_p_matrix_item").change(function() {
        //global_plate_location = $("#id_p_matrix_item").children("option:selected").text();
        global_plate_matrix_item_text = $(this).children("option:selected").text();
        global_plate_matrix_item = $(this).val();
        // to return the pk
        // $(this).val();
    });
    $("#id_p_location").change(function() {
        //global_plate_location = $("#id_p_location").children("option:selected").text();
        global_plate_location_text = $(this).children("option:selected").text();
        global_plate_location = $(this).val();
        // to return the pk
        // $(this).val();
    });
    $("#id_p_time").focusout(function() {
        global_plate_time = $(this).val();
        //console.log("focus")
    });
    $("#id_p_time").change(function() {
        global_plate_time = $(this).val();
        //console.log("change")
    });
    $("#id_p_time").mouseleave(function() {
        global_plate_time = $(this).val();
        //console.log("mouseleave")
    });
    $("#id_p_well_use").change(function() {
        global_plate_well_use = $(this).val();
    });
    $("#id_p_replicate").change(function() {
        global_plate_replicate = $(this).val();
    });
    $("#id_p_time_unit").change(function() {
        global_plate_time_unit = $(this).val();
        //console.log($(this).children("option:selected").text());

        // this loop worked as expected, replacement did not work at the time time tested
        // $('#form_set').children().each(function() {
        //     console.log($(this).children("option:selected").text());
        //     if ( $(this).hasClass("item") && ( $(this).attr("data-value",'minute') || $(this).attr("data-value",'hour') || $(this).attr("data-value",'day') ) )
        //     {
        //         $(this).attr("data-value", global_plate_time_unit);
        //         $(this).val(global_plate_time_unit);
        //     }
        // });

        for (i = 0; i < global_plate_size; i++) {
            $('#id_assayplatereadermapitem_set-' + i + '-time_unit').val(global_plate_time_unit);
        };

    });

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

    //show hide buttons - changing the class of the plate map to show/hide based on checked or unchecked
    $('#show_matrix_item').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-matrix-item').removeClass('hidden');
       } else {
            $('.plate-cells-matrix-item').addClass('hidden');
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
    $('#show_well_use').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-well-use').removeClass('hidden');
       } else {
            $('.plate-cells-well-use').addClass('hidden');
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

    // when loading, what and how to load the plate
    // if add page, start with empty table (plate), if existing, pull from formsets
    if ($("#check_load").html() === 'add') {
        global_plate_size = 24;
        platelabels(global_plate_size, "adding");
    } else {
        global_plate_size = $("#id_device").val();
        platelabels(global_plate_size, "existing");
    }
    // when add page and the user changes the plate size, have to reload empty plate the correct size
    $("#id_device").change(function() {
        removeFormsets();
        global_plate_size = $("#id_device").val();
        platelabels(global_plate_size, "adding");
    });
    // adding these made 2x forms, so moved it back to where had it before
    //$('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(global_plate_size);
    // }).trigger('change');

    function platelabels(size, aore)
    {
        let row_labels = [];
        let col_labels = [];
        let row_contents = [];

        //note that this arrangement will be first is 0 for both row and column
        let row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
        let col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'];
        //console.log("start of plate size ", size);
        if (size == 24) {
            row_labels = row_labels_all.slice(0,4); //['A','B','C','D'];
            col_labels = col_labels_all.slice(0,6); //['1','2','3','4','5','6'];
            row_contents = [
["A1", "A2", "A3", "A4", "A5", "A6"],
["B1", "B2", "B3", "B4", "B5", "B6"],
["C1", "C2", "C3", "C4", "C5", "C6"],
["D1", "D2", "D3", "D4", "D5", "D6"]
                ];
        } else if (size == 96) {
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
        let data_packed = [col_labels, row_labels, row_contents];
        //console.log(col_labels)
        //console.log(row_labels)
        //console.log(row_contents)
        buildPlate(data_packed, aore);
    }

    function buildPlate(data, aore) {
        //this table's table tag and closing tag are in the html file
        $('#plate_table').empty();
        let thead = document.createElement("thead");
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

            data[2][ridx].forEach(function(el) {
                let td = document.createElement("td");
                let div_label = document.createElement("div");
                $(div_label).attr('data-index', formsetidx);
                $(div_label).attr('id', "label-"+formsetidx);
                //for coloring
                $(div_label).addClass('map-label');
                //for hiding
                $(div_label).addClass('plate-cells-label');

                let div_location = document.createElement("div");
                $(div_location).attr('data-index', formsetidx);
                $(div_location).attr('id', "location-"+formsetidx);
                $(div_location).addClass('map-location');
                $(div_location).addClass('plate-cells-location');

                let div_time = document.createElement("div");
                $(div_time).attr('data-index', formsetidx);
                $(div_time).attr('id', "time-"+formsetidx);
                $(div_time).addClass('map-time');
                $(div_time).addClass('plate-cells-time');

                let div_matrix_item = document.createElement("div");
                $(div_matrix_item).attr('data-index', formsetidx);
                $(div_matrix_item).attr('id', "matrix_item-"+formsetidx);
                $(div_matrix_item).addClass('map-matrix-item');
                $(div_matrix_item).addClass('plate-cells-matrix-item');

                let div_well_use = document.createElement("div");
                $(div_well_use).attr('data-index', formsetidx);
                $(div_well_use).attr('id', "use-"+formsetidx);
                $(div_well_use).addClass('map-well-use');
                $(div_well_use).addClass('plate-cells-well-use');

                let div_replicate = document.createElement("div");
                $(div_replicate).attr('data-index', formsetidx);
                $(div_replicate).attr('id', "replicate-"+formsetidx);
                $(div_replicate).addClass('map-replicate');
                $(div_replicate).addClass('plate-cells-replicate');

                //console.log(formsetidx)
                //console.log(ridx)
                //console.log(cidx)

                //content of the element
                if (aore === "adding") {
                    // if adding, need a form for each well in the plate, make a form for each well based on size of plate
                    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
                    $('#form_set').append(first_form.replace(/-0-/g, '-' + formsetidx + '-'));
                    $('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(formsetidx + 1);
                    div_well_use.appendChild(document.createTextNode("empty"));
                    div_matrix_item.appendChild(document.createTextNode("-"));
                    div_time.appendChild(document.createTextNode("0"));
                    div_location.appendChild(document.createTextNode("-"));
                    div_replicate.appendChild(document.createTextNode("1"));
                    div_label.appendChild(document.createTextNode(el));

                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-location').val(0);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-row_index').val(ridx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-column_index').val(cidx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-plate_index').val(formsetidx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val(el);

                } else {
                    let saved_matrix_item = $('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item').val();
                    $('#id_b_matrix_item').val(saved_matrix_item);
                    let saved_text_matrix_item = $('#id_b_matrix_item').children("option:selected").text();
                    let saved_location = $('#id_assayplatereadermapitem_set-' + formsetidx + '-location').val();
                    $('#id_b_location').val(saved_location);
                    let saved_text_location = $('#id_b_location').children("option:selected").text();

                    div_matrix_item.appendChild(document.createTextNode(saved_text_matrix_item));
                    div_location.appendChild(document.createTextNode(saved_text_location));
                    div_well_use.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-well_use').val()));
                    div_time.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-time').val()));
                    div_replicate.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-replicate').val()));
                    div_label.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val()));
                }
                formsetidx = formsetidx + 1;

                // put it all together
                let tdbodycell = document.createElement("td");
                // the order here will determine the order in the well plate
                tdbodycell.appendChild(div_well_use);
                tdbodycell.appendChild(div_matrix_item);
                tdbodycell.appendChild(div_location);
                tdbodycell.appendChild(div_time);
                tdbodycell.appendChild(div_replicate);
                tdbodycell.appendChild(div_label);

                trbodyrow.appendChild(tdbodycell);

                cidx = cidx + 1;
            });

            tbody.appendChild(trbodyrow);
            ridx = ridx + 1;
        });

        plate_table.appendChild(tbody);
        return plate_table
    }

    // replace in plate map
    // https://www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    // https://stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function changeSelected() {
        // children of each cell of the table that is selected
        $('.ui-selected').children().each(function () {
            let change_well_use = 'y';
            // each of the divs in the cell of the table
            let idx = $(this).attr('data-index');
            //console.log("this: ", $(this));
            //console.log("idx: ", idx);
            if ($(this).hasClass("map-location") && (!$(this).hasClass("hidden"))) {
                // change the location in the map (gets the text of the selected pk)
                $('#location-' + idx).text(global_plate_location_text);
                // change in the formset
                $('#id_assayplatereadermapitem_set-' + idx + '-location').val(global_plate_location);
            } else if ($(this).hasClass("map-matrix-item") && (!$(this).hasClass("hidden"))) {
                // change the location in the map (gets the text of the selected pk)
                $('#matrix_item-' + idx).text(global_plate_matrix_item_text);
                // change in the formset
                $('#id_assayplatereadermapitem_set-' + idx + '-matrix_item').val(global_plate_matrix_item);

                // deal with the well use when changing
                if (global_plate_matrix_item_text == null || global_plate_matrix_item_text.length === 0) {
                    $('#use-' + idx).text('empty');
                    $('#id_assayplatereadermapitem_set-' + idx + '-well_use').val('empty');
                } else {
                    $('#use-' + idx).text('sample');
                    $('#id_assayplatereadermapitem_set-' + idx + '-well_use').val('sample');
                };
                change_well_use = "n";

            } else if ($(this).hasClass("map-time") && (!$(this).hasClass("hidden"))) {
                $('#time-' + idx).text(global_plate_time);
                $('#id_assayplatereadermapitem_set-' + idx + '-time').val(global_plate_time);
            } else if ($(this).hasClass("map-replicate") && (!$(this).hasClass("hidden"))) {
                $('#replicate-' + idx).text(global_plate_replicate);
                $('#id_assayplatereadermapitem_set-' + idx + '-replicate').val(global_plate_replicate);
            } else if ($(this).hasClass("map-well-use") && (!$(this).hasClass("hidden"))) {
                if (change_well_use === "y") {
                    // this should happen if the user has put a matrix item in the matrix item selection and it is not hidden
                    $('#use-' + idx).text(global_plate_well_use);
                    $('#id_assayplatereadermapitem_set-' + idx + '-well_use').val(global_plate_well_use);
                }
                if ($('#matrix_item-' + idx).hasClass("hidden") && global_plate_well_use == 'empty' ) {
                    $('#matrix_item-' + idx).removeClass("hidden")
                    $('#matrix_item-' + idx).text("-");
                    $('#matrix_item-' + idx).addClass("hidden")
                    // change in the formset
                    $('#id_assayplatereadermapitem_set-' + idx + '-matrix_item').val(null);
                }
            } else {
                //console.log("this.text else", $(this).text())
            }

        });
    }

    function removeFormsets() {
        // get rid of previous formsets before try to add more or the indexes get all messed up
        while ($('#form_set').find('.inline').length > 0 ) {
            $('#form_set').find('.inline').first().remove();
        }
        $('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(0);
    }

    //keep for reference for now - adding a formset the original way from here:
    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
});




