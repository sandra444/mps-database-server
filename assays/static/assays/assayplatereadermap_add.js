$(document).ready(function () {

    //console.log("in js file 1");
    // # id, . class

    // set global variables
    let global_plate_matrix_item_text = "";
    let global_plate_matrix_item = 0;
    let global_plate_well_use = "empty";
    let global_plate_time = 0;
    let global_plate_sample_value = 0;
    let global_plate_standard_value = 0;
    let global_plate_block_value = 0;
    let global_plate_time_unit = "day";
    let global_plate_location_text = "Unspecified";
    let global_plate_location = 0;
    // gets set below depending on add or edit...
    let global_plate_size = 0;
    let global_plate_increment_operation = 'divide';
    let global_plate_change_method = 'copy';
    let global_plate_increment_direction = 'left';
    let global_plate_increment_value = 1;
    let global_plate_sample_change_matrix_item = true;
    let global_plate_sample_change_location = true;
    let global_plate_sample_change_time = true;
    let global_plate_number_file_block_sets = 0;
    let global_plate_file_block_index = 0;
    let global_plate_file_pk_block_pk_index = 0;
    let global_plate_file_pk = 0;
    let global_plate_block_pk = 0;
    //let global_plate_file_block_dict = 0;
    let global_plate_selected_value_formset = 0;
    let global_plate_index_list_matches = [];

    // set based on add or update and if the plate map has been assigned to a file-block
    try {
        // this should happen if the file-block has been assigned
        global_plate_number_file_block_sets = document.getElementById("id_number_file_block_combos").value;
    }
    catch(err) {
        //do nothing
    }

    if (global_plate_number_file_block_sets > 0) {
        $('.select-value-set').removeClass('hidden');
        findValueSet()
    } else {
        // there is only one set with null file and block
        $('.select-value-set').addClass('hidden');
    }
    function findValueSet() {
        //there is at least one set with a file and block
        global_plate_file_pk_block_pk_index = $('#id_ns_file_pk_block_pk').val();
        let pk_pk = $("#id_ns_file_pk_block_pk option:selected").text();
        let split_pk = pk_pk.split("-");
        global_plate_file_pk = split_pk[0];
        global_plate_block_pk = split_pk[1];

        // loop through and find the indexes of the ones that match the selected file and block
        // make parallel arrays of the information needed for display in the plate
        midx = 0;
        global_plate_index_list_matches = [];
        global_plate_time_matches = [];
        global_plate_value_matches = [];
        //TODO, make parallel lists of the value and the time and just use those in plate below.......
        let my_file_v = "";
        let my_block_v = "";
        let my_file = -1;
        let my_block = -1;
        let my_time_v = "";
        let my_value_v = "";
        let my_time = -1;
        let my_value = -1;
        $('#value_formset').children().each(function(cfs) {
            //console.log("$(this) ")
            //console.log($(this));
            //console.log("cfs  midx ")
            //console.log(cfs, " ", midx)
            //console.log("cfs.assayplatereadermapdatafile ")
            my_file_v = "id_assayplatereadermapitemvalue_set-" + cfs + "-assayplatereadermapdatafile";
            my_block_v = "id_assayplatereadermapitemvalue_set-" + cfs + "-assayplatereadermapdatafileblock";
            my_file = $('#' + my_file_v).val();
            my_block = $('#' + my_block_v).val();
            my_time_v = "id_assayplatereadermapitemvalue_set-" + cfs + "-time";
            my_value_v = "id_assayplatereadermapitemvalue_set-" + cfs + "-value";
            my_time = $('#' + my_time_v).val();
            my_value = $('#' + my_value_v).val();
            if ( global_plate_file_pk == my_file && global_plate_block_pk == my_block ) {
                global_plate_index_list_matches.push(cfs);
                global_plate_time_matches.push(my_time);
                global_plate_value_matches.push(my_value);
            }
            midx = midx + 1;
        });
        //console.log(global_plate_index_list_matches)

        // console.log("$('#value_formset')")
        // console.log($('#value_formset'))
        // console.log("$('#value_formset').find('.inline')")
        // console.log($('#value_formset').find('.inline'))
        // console.log("$('#value_formset').find('.inline').first()")
        // console.log($('#value_formset').find('.inline').first())
        // console.log("$('#value_formset').find('.inline').first()[0]")
        // console.log($('#value_formset').find('.inline').first()[0])
        // console.log("$('#value_formset').find('.inline').first()[0].outerHTML")
        // console.log($('#value_formset').find('.inline').first()[0].outerHTML)
    }

    // set the tooltips
    let global_plate_sample_time_unit_tooltip = "Time unit applies to all sample times on the plate.";
    $('#sample_time_unit_tooltip').next().html($('#sample_time_unit_tooltip').next().html() + make_escaped_tooltip(global_plate_sample_time_unit_tooltip));

    let global_plate_well_use_tooltip = "For blank and empty wells, select the well use and drag on plate. For samples and standards, make requested selections then drag on plate.";
    $('#well_use_tooltip').next().html($('#well_use_tooltip').next().html() + make_escaped_tooltip(global_plate_well_use_tooltip));

    let global_plate_reader_unit_tooltip = "Typically something like RFU, unless internal calibration.";
    $('#plate_reader_unit_tooltip').next().html($('#plate_reader_unit_tooltip').next().html() + make_escaped_tooltip(global_plate_reader_unit_tooltip));

    let global_plate_sample_time_tooltip = "For plates with multiple sample times, sample times must be added before plate reader file upload. For plate maps used in a time series, sample time is added during file upload.";
    $('#sample_time_tooltip').next().html($('#sample_time_tooltip').next().html() + make_escaped_tooltip(global_plate_sample_time_tooltip));

    let global_plate_sample_location_tooltip = "Select the location in the model, if applicable, from which the effluent was collected.";
    $('#sample_location_tooltip').next().html($('#sample_location_tooltip').next().html() + make_escaped_tooltip(global_plate_sample_location_tooltip));

    let global_plate_sample_matrix_item_tooltip = "Select the name of the matrix item (chip or well in a plate) associated to the sample. Use the backspace button to clear selection.";
    $('#sample_matrix_item_tooltip').next().html($('#sample_matrix_item_tooltip').next().html() + make_escaped_tooltip(global_plate_sample_matrix_item_tooltip));

    let global_plate_sample_tooltip = "1) Select the matrix item, location, or time to apply."
    global_plate_sample_tooltip = global_plate_sample_tooltip + "2) Check the box of the ones to apply."
    global_plate_sample_tooltip = global_plate_sample_tooltip + "3) Drag on the plate to apply."
    $('#sample_tooltip').next().html($('#sample_tooltip').next().html() + make_escaped_tooltip(global_plate_sample_tooltip));

    let global_plate_standard_tooltip = "Select the target/method/unit associated to this plate map. Use the backspace button to clear selection. Select value of standard and drag onto plate.";
    $('#standard_tooltip').next().html($('#standard_tooltip').next().html() + make_escaped_tooltip(global_plate_standard_tooltip));

    let global_plate_file_block_tooltip = "Changes made to the plate map (including sample location and standard concentration) will apply to all uses of the plate map. Changes made to the sample time will apply only to the specific file-block to which the plate map was assigned.";
    $('#file_block_tooltip').next().html($('#file_block_tooltip').next().html() + make_escaped_tooltip(global_plate_file_block_tooltip));

    let global_plate_file_block_number_tooltip = "The number of times this plate map has been assigned to a block of data. A plate reader output file can contain one or more blocks of data. A block of data is the same dimensions as a plate map.";
    $('#file_block_number_tooltip').next().html($('#file_block_number_tooltip').next().html() + make_escaped_tooltip(global_plate_file_block_number_tooltip));

    // currently there are two radio button: change_method (increment and copy) and increment_direction (left and right)
    // class show/hide and also wht is checked/unchecked based on radio button
    $("input[type='radio'][name='change_method']").click(function() {
        global_plate_change_method = $(this).val();
        if (global_plate_change_method === 'increment') {
            $('.increment-section').removeClass('hidden');
        } else {
            $('.increment-section').addClass('hidden');
        }
    });
    $("input[type='radio'][name='increment_direction']").click(function() {
        global_plate_increment_direction = $(this).val();
    });
    $("input[type='checkbox'][name='change_matrix_item']").click(function() {
        global_plate_sample_change_matrix_item = $(this).prop('checked');
        //console.log(global_plate_sample_change_matrix_item)
    });
    $("input[type='checkbox'][name='change_location']").click(function() {
        global_plate_sample_change_location = $(this).prop('checked');
        //console.log(global_plate_sample_change_location)
    });
    $("input[type='checkbox'][name='change_time']").click(function() {
        global_plate_sample_change_time = $(this).prop('checked');
        //console.log(global_plate_sample_change_time)
    });

    // get the copy of the empty formsets (the "extra" in the forms.py), then remove the empty
    // The forms.py has an extra of 1 for the add page, it gets copied x times (24, 96, 384)
    // The update page also comes with one extra
    let first_item_form = $('#formset').find('.inline').first()[0].outerHTML;
    if ($('#formset').find('.inline').length === 1 && $("#check_load").html() === 'add') {
        $('#formset').find('.inline').first().remove();
    }
    let first_value_form = $('#value_formset').find('.inline').first()[0].outerHTML;
    if ($('#value_formset').find('.inline').length === 1 && $("#check_load").html() === 'add') {
        $('#value_formset').find('.inline').first().remove();
    }
    // adding these made 2x forms, so moved it back to where had it before
    //$('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(global_plate_size);
    // }).trigger('change');

    // Set the global or other variables for the selections
    $("#id_se_file_block").change(function() {
        global_plate_file_block_index = $(this).val();
        global_plate_file_pk_block_pk_index = global_plate_file_block_index;
        //not sure why IDE objects to this, it seems to work....
        $('#id_ns_file_pk_block_pk').val(global_plate_file_block_index);
        findValueSet();
    });
    $("#id_se_matrix_item").change(function() {
        //global_plate_location = $("#id_se_matrix_item").children("option:selected").text();
        global_plate_matrix_item_text = $(this).children("option:selected").text();
        global_plate_matrix_item = $(this).val();
        // to return the pk
        // $(this).val();
    });
    $("#id_se_location").change(function() {
        //global_plate_location = $("#id_se_location").children("option:selected").text();
        global_plate_location_text = $(this).children("option:selected").text();
        global_plate_location = $(this).val();
        // to return the pk
        // $(this).val();
    });
    $("#id_se_time").mouseout(function() {
        global_plate_time = $(this).val();
    });
    $("#id_se_standard_value").mouseout(function() {
        global_plate_standard_value = $(this).val();
    });
    $("#id_se_increment_value").mouseout(function() {
        global_plate_increment_value = $(this).val();
    });
    $("#id_se_increment_operation").change(function() {
        global_plate_increment_operation = $(this).val();
    });
    $("#id_se_time_unit").change(function() {
        global_plate_time_unit = $(this).val();
        //console.log($(this).children("option:selected").text());

        // this loop worked as expected at the time time tested
        // $('#formset').children().each(function() {
        //     console.log($(this).children("option:selected").text());
        //     if ( $(this).hasClass("item") && ( $(this).attr("data-value",'minute') || $(this).attr("data-value",'hour') || $(this).attr("data-value",'day') ) )
        //     {
        //     }
        // });
        // Moved to the main plate map, not the items, so don't need this anymore
        // for (i = 0; i < global_plate_size; i++) {
        //     $('#id_assayplatereadermapitem_set-' + i + '-time_unit').val(global_plate_time_unit);
        // };
    });

    // Controlling more of what shows and does not
    $("#id_se_well_use").change(function() {
        global_plate_well_use = $(this).val();
        $("input[name=change_method][value=copy]").prop( "checked", true );
        global_plate_change_method = 'copy';
        if (global_plate_change_method === 'increment') {
            $('.increment-section').removeClass('hidden');
        } else {
            $('.increment-section').addClass('hidden');
        }
        // hide all, then unhide what want to show
        $('.sample-section').addClass('hidden');
        $('.standard-section').addClass('hidden');
        $('.option-section').addClass('hidden');
        $('.non-sample-section').addClass('hidden');
        global_plate_sample_change = 'none';
        if (global_plate_well_use === 'sample') {
            $('.sample-section').removeClass('hidden');
            $('.option-section').removeClass('hidden');
        } else if (global_plate_well_use === 'standard') {
            $('.non-sample-section').removeClass('hidden');
            $('.standard-section').removeClass('hidden');
            $('.option-section').removeClass('hidden');

        } else {
            $('.non-sample-section').removeClass('hidden');
        }
    });

    //so can select table cells - keep
    $('#plate_table').selectable({
        // SUBJECT TO CHANGE: WARNING!
        filter: 'td',
        distance: 1,
        stop: changeSelected
    });

    //to format the reference table - keep - although, do not plan to show table, but need for javascript
    $('#matrix_items_table').DataTable({
        "iDisplayLength": 25,
        "sDom": '<B<"row">lfrtip>',
        fixedHeader: {headerOffset: 50},
        responsive: true,
        "order": [[2, "asc"]],
    });

    // when loading, what and how to load the plate
    // if add page, start with empty table (plate), if existing, pull from formsets
    // $('.show-add').addClass('hidden');
    // $('.hide-add').addClass('hidden');
    if ($("#check_load").html() === 'add') {
        // $('.show-add').removeClass('hidden');
        global_plate_size = 24;
        plateLabels("adding");
    } else {
        // $('.hide-add').removeClass('hidden');
        // // set initially displaced in the standard target method unit
        // let elem_standard_text = document.getElementById ("existing_study_assay_text");
        // let elem_standard = document.getElementById ("existing_study_assay");
        // global_plate_study_assay_text = elem_standard_text.innerText.trim();
        // global_plate_study_assay = elem_standard.innerText.trim();
        // if (global_plate_study_assay_text != 'None') {
        //     changeStudyAssay()
        // }
        let elem_size = document.getElementById ("existing_device_size");
        //global_plate_size = $("#existing_device_size").val(); does not work...
        global_plate_size = elem_size.innerText;
        plateLabels("existing");
    }

    // function changeStudyAssay() {
    //     //$('#existing_study_assay').val(global_plate_study_assay);
    //     console.log(global_plate_study_assay_text);
    //     console.log(global_plate_study_assay);
    //
    // }

    // when add page and the user changes the plate size, have to reload empty plate the correct size
    // id_device is for the ADD page ONLY, not edit or view
    $("#id_device").change(function() {
        removeFormsets();
        global_plate_size = $("#id_device").val();
        plateLabels("adding");
    });

    // show hide buttons - changing the class of the plate map to show/hide based on checked or unchecked
    // list of ones to start checked so can be easily changed if people decide they want different defaults
    let check_list1 = ['#show_well_use', '#show_matrix_item', '#show_time', '#show_location',
        '#show_label', '#show_compound', '#show_cell', '#show_setting',
        '#show_standard_value'];
    check_list1 = ['#show_well_use', '#show_matrix_item', '#show_time', '#show_location',
        '#show_standard_value'];
    let check_list2 = ['.plate-cells-well-use', '.plate-cells-matrix-item', '.plate-cells-time', '.plate-cells-location',
        '.plate-cells-label', '.plate-cells-compound', '.plate-cells-cell', '.plate-cells-setting',
        '.plate-cells-standard-value',
        '.plate-cells-block-value'];
    check_list2 = ['.plate-cells-well-use', '.plate-cells-matrix-item', '.plate-cells-time', '.plate-cells-location',
        '.plate-cells-standard-value'
        ];
    // check to show and show them
    checkidx = 0;
    check_list1.forEach(function() {
        $(check_list1[checkidx]).prop('checked', true);
        $(check_list2[checkidx]).removeClass('hidden');
        checkidx = checkidx + 1;
    });

    // show/hide content in plate map based on the fancy check boxes
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
    $('#show_label').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-label').removeClass('hidden');
       } else {
            $('.plate-cells-label').addClass('hidden');
       }
    });
    $('#show_compound').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-compound').removeClass('hidden');
       } else {
            $('.plate-cells-compound').addClass('hidden');
       }
    });
    $('#show_cell').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-cell').removeClass('hidden');
       } else {
            $('.plate-cells-cell').addClass('hidden');
       }
    });
    $('#show_setting').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-setting').removeClass('hidden');
       } else {
            $('.plate-cells-setting').addClass('hidden');
       }
    });
    $('#show_standard_value').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-standard-value').removeClass('hidden');
       } else {
            $('.plate-cells-standard-value').addClass('hidden');
       }
    });
    $('#show_block_value').change(function() {
       if ($(this).is(':checked')) {
            $('.plate-cells-block-value').removeClass('hidden');
       } else {
            $('.plate-cells-block-value').addClass('hidden');
       }
    });

    // make the basis for the plate map based on the plate size and if it is add or update/view
    function plateLabels(aore) {
        let size = global_plate_size;
        let row_labels = [];
        let col_labels = [];
        let row_contents = [];
        //note that this arrangement will be first is 0 for both row and column
        let row_labels_all = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'];
        let col_labels_all = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'];
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
            row_contents = [
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
            row_contents = [
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
        // build the plate map with the dimensions of the row_contents (plus headers)
        // It is VERY IMPORTANT to understand that the visual representation of the plate
        // is pulled from the order of the original creation of the plate items!
        buildPlate(data_packed, aore);
    }

    //TODO make sure filling/changing correct sets...
    function buildPlate(data, aore) {
        let key_value_plate_index_row_index = {};
        let key_value_plate_index_column_index = {};
        let top_label_button = ' ';
        let side_label_button = ' ';
        //this table's table tag and closing tag are in the html file
        $('#plate_table').empty();
        let thead = document.createElement("thead");
        let headRow = document.createElement("tr");
        // column headers: first, then the rest in loop
        let th=document.createElement("th");
        th.appendChild(document.createTextNode("Label"));
        headRow.appendChild(th);
        let header_col_index = 0;
        data[0].forEach(function(col) {
            let th=document.createElement("th");
            // th.appendChild(document.createTextNode(col + top_label_button));
            top_label_button = ' <a id="col'+header_col_index+'" column-or-row="column" column-index="'+header_col_index+'" row-index="'+770+'" class="btn btn-sm btn-primary apply-button">Apply to Column</a>'
            $(th).html(col + top_label_button);
            headRow.appendChild(th);
            header_col_index = header_col_index + 1;
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

            side_label_button = ' <a id="row'+ridx+'" column-or-row="row" column-index="'+772+'" row-index="'+ridx+'" class="btn btn-sm btn-primary apply-button">Apply to Row</a>'
            //tdbodyrow.appendChild(document.createTextNode(data[1][ridx]));
            $(tdbodyrow).html(data[1][ridx] + side_label_button);
            trbodyrow.appendChild(tdbodyrow);
            let cidx = 0;
            // build content row (same row as the row_labels (A=A, B=B, etc.)
            // while in a row, go through each column

            data[2][ridx].forEach(function(el) {
                //make all the parts of the table body (note: 10 possible items for display in plate map)
                let td = document.createElement("td");
                let div_label = document.createElement("div");
                $(div_label).attr('data-index', formsetidx);
                $(div_label).attr('row-index', ridx);
                $(div_label).attr('column-index', cidx);
                $(div_label).attr('id', "label-"+formsetidx);
                $(div_label).addClass('map-label plate-cells-label hidden');
                //for coloring, for hiding, start with hidden

                let div_location = document.createElement("div");
                $(div_location).attr('data-index', formsetidx);
                $(div_location).attr('row-index', ridx);
                $(div_location).attr('column-index', cidx);
                $(div_location).attr('id', "location-"+formsetidx);
                $(div_location).addClass('map-location plate-cells-location hidden');

                let div_matrix_item = document.createElement("div");
                $(div_matrix_item).attr('data-index', formsetidx);
                $(div_matrix_item).attr('row-index', ridx);
                $(div_matrix_item).attr('column-index', cidx);
                $(div_matrix_item).attr('id', "matrix_item-"+formsetidx);
                $(div_matrix_item).addClass('map-matrix-item plate-cells-matrix-item hidden');

                let div_well_use = document.createElement("div");
                $(div_well_use).attr('data-index', formsetidx);
                $(div_well_use).attr('row-index', ridx);
                $(div_well_use).attr('column-index', cidx);
                $(div_well_use).attr('id', "use-"+formsetidx);
                $(div_well_use).addClass('map-well-use plate-cells-well-use hidden');

                let div_compound = document.createElement("div");
                $(div_compound).attr('data-index', formsetidx);
                $(div_compound).attr('row-index', ridx);
                $(div_compound).attr('column-index', cidx);
                $(div_compound).attr('id', "compound-"+formsetidx);
                $(div_compound).addClass('map-compound plate-cells-compound hidden');

                let div_cell = document.createElement("div");
                $(div_cell).attr('data-index', formsetidx);
                $(div_cell).attr('row-index', ridx);
                $(div_cell).attr('column-index', cidx);
                $(div_cell).attr('id', "cell-"+formsetidx);
                $(div_cell).addClass('map-cell plate-cells-cell hidden');

                let div_setting = document.createElement("div");
                $(div_setting).attr('data-index', formsetidx);
                $(div_setting).attr('row-index', ridx);
                $(div_setting).attr('column-index', cidx);
                $(div_setting).attr('id', "setting-"+formsetidx);
                $(div_setting).addClass('map-setting plate-cells-setting hidden');

                let div_standard_value = document.createElement("div");
                $(div_standard_value).attr('data-index', formsetidx);
                $(div_standard_value).attr('row-index', ridx);
                $(div_standard_value).attr('column-index', cidx);
                $(div_standard_value).attr('id', "standard-value-"+formsetidx);
                $(div_standard_value).addClass('map-standard-value plate-cells-standard-value hidden');

                let div_time = document.createElement("div");
                $(div_time).attr('data-index', formsetidx);
                $(div_time).attr('row-index', ridx);
                $(div_time).attr('column-index', cidx);
                $(div_time).attr('id', "time-"+formsetidx);
                $(div_time).addClass('map-time plate-cells-time hidden');

                let div_block_value = document.createElement("div");
                $(div_block_value).attr('data-index', formsetidx);
                $(div_block_value).attr('row-index', ridx);
                $(div_block_value).attr('column-index', cidx);
                $(div_block_value).attr('id', "block-value-"+formsetidx);
                $(div_block_value).addClass('map-block-value plate-cells-block-value hidden');

                //content of the element
                if (aore === "adding") {
                    // if adding, need a formset for each well in the plate (for the item and the item value tables)
                    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
                    $('#formset').append(first_item_form.replace(/-0-/g, '-' + formsetidx + '-'));
                    $('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(formsetidx + 1);
                    $('#value_formset').append(first_value_form.replace(/-0-/g, '-' + formsetidx + '-'));
                    $('#id_assayplatereadermapitemvalue_set-TOTAL_FORMS').val(formsetidx + 1);

                    // since adding, all content is place holder
                    div_compound.appendChild(document.createTextNode("-"));
                    div_cell.appendChild(document.createTextNode("-"));
                    div_setting.appendChild(document.createTextNode("-"));
                    div_label.appendChild(document.createTextNode(el));
                    div_well_use.appendChild(document.createTextNode("empty"));
                    div_matrix_item.appendChild(document.createTextNode("-"));
                    div_location.appendChild(document.createTextNode("-"));
                    div_time.appendChild(document.createTextNode("0"));
                    div_standard_value.appendChild(document.createTextNode("0"));
                    div_block_value.appendChild(document.createTextNode("0"));

                    //this auto fills the fields that are needed to join the items and the items values tables
                    //the platemap id will be the same in both since they are two formsets to the main plate map table
                    //these MUST stay parallel or problems WILL happen
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-row_index').val(ridx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-column_index').val(cidx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-plate_index').val(formsetidx);
                    $('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val(el);
                    $('#id_assayplatereadermapitemvalue_set-' + formsetidx + '-plate_index').val(formsetidx);
                } else {
                    // these are needed to display text in the cell instead of the pk (in the plate map)
                    // if no files have been attached to the plate map, get the template one
                    let saved_matrix_item = $('#id_assayplatereadermapitem_set-' + formsetidx + '-matrix_item').val();
                    $('#id_ns_matrix_item').val(saved_matrix_item);
                    let saved_text_matrix_item = $('#id_ns_matrix_item').children("option:selected").text();
                    let saved_location = $('#id_assayplatereadermapitem_set-' + formsetidx + '-location').val();
                    $('#id_ns_location').val(saved_location);
                    let saved_text_location = $('#id_ns_location').children("option:selected").text();

                    div_compound.appendChild(document.createTextNode($('#'+saved_matrix_item+'-compound-short').text()));
                    div_cell.appendChild(document.createTextNode($('#'+saved_matrix_item+'-cell-short').text()));
                    div_setting.appendChild(document.createTextNode($('#'+saved_matrix_item+'-setting-short').text()));

                    div_matrix_item.appendChild(document.createTextNode(saved_text_matrix_item));
                    div_well_use.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-well_use').val()));
                    div_label.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-name').val()));

                    div_location.appendChild(document.createTextNode(saved_text_location));
                    div_standard_value.appendChild(document.createTextNode($('#id_assayplatereadermapitem_set-' + formsetidx + '-standard-value').val()));

                    if (global_plate_number_file_block_sets == 0) {
                        // get from the correct value formset
                        div_block_value.appendChild(document.createTextNode($('#id_assayplatereadermapitemvalue_set-' + formsetidx + '-block-value').val()));
                        div_time.appendChild(document.createTextNode($('#id_assayplatereadermapitemvalue_set-' + formsetidx + '-time').val()));

                    } else {
                        // get the one the user selected by global_plate_index_list_matches
                        // remember, this loop is going through the plate map, by size, so, get the RIGHT one and skip the WRONG ones
                        // TODO confirm that nulls are handled correctly in the push into the array
                        div_block_value.appendChild(document.createTextNode(global_plate_time_matches[formsetidx]));
                        div_time.appendChild(document.createTextNode(global_plate_value_matches[formsetidx]));
                        $(div_time).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                        $(div_block_value).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                    }
                }

                key_value_plate_index_row_index[formsetidx] = ridx;
                key_value_plate_index_column_index[formsetidx] = cidx;

                formsetidx = formsetidx + 1;

                // put it all together - here is where the order matters
                let tdbodycell = document.createElement("td");
                // the order here will determine the order in the well plate
                tdbodycell.appendChild(div_well_use);
                tdbodycell.appendChild(div_matrix_item);
                tdbodycell.appendChild(div_location);
                tdbodycell.appendChild(div_time);
                tdbodycell.appendChild(div_label);
                tdbodycell.appendChild(div_standard_value);
                tdbodycell.appendChild(div_block_value);
                tdbodycell.appendChild(div_compound);
                tdbodycell.appendChild(div_cell);
                tdbodycell.appendChild(div_setting);

                trbodyrow.appendChild(tdbodycell);
                cidx = cidx + 1;
            });
            tbody.appendChild(trbodyrow);
            ridx = ridx + 1;
        });
        plate_table.appendChild(tbody);
        return plate_table
    }

    // what button was clicked in the plate map
    $(".apply-button").on("click", function(e){
        global_plate_sample_change_time = document.getElementById('id_se_time').value;
        global_plate_standard_value = document.getElementById('id_se_standard_value').value;
        global_plate_increment_value = document.getElementById('id_se_increment_value').value;
        //let button_id = e.target.id;
        let my_this = $(this);
        let button_column_index = my_this.attr('column-index');
        let button_row_index = my_this.attr('row-index');
        let button_column_or_row = my_this.attr('column-or-row');
        let plate_index_list = [];
        // find the plate map index of matching column or row and send to the function for processing
        for ( var idx = 0, l = global_plate_size; idx < l; idx++ ) {
            //console.log(idx)
            if (button_column_or_row === 'column') {
                if ($('#use-' + idx).attr('column-index') == button_column_index) {
                    welluseChange(idx);
                    plate_index_list.push(idx);
                }
            } else {
                // row
                if ($('#use-' + idx).attr('row-index') == button_row_index) {
                    welluseChange(idx);
                    plate_index_list.push(idx);
                }
            }
        }
        specificChanges(plate_index_list, 'one')
    });


    // replace in plate map
    // https://www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    // https://stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function changeSelected() {
        let plate_index_list = [];
        // children of each cell of the plate map table that is selected
        $('.ui-selected').children().each(function () {
            // send each selected cell of the table to the function for processing
            global_plate_sample_change_time = document.getElementById('id_se_time').value;
            global_plate_standard_value = document.getElementById('id_se_standard_value').value;
            global_plate_increment_value = document.getElementById('id_se_increment_value').value;

            if ($(this).hasClass("map-well-use")) {
                let idx = $(this).attr('data-index');
                welluseChange(idx);
                plate_index_list.push(idx);
            }
        });
        specificChanges(plate_index_list, 'drag')
    }

    function welluseChange(idx) {
        $('#use-' + idx).text(global_plate_well_use);
        $('#id_assayplatereadermapitem_set-' + idx + '-well_use').val(global_plate_well_use);
        $('#id_assayplatereadermapitemvalue_set-' + idx + '-well_use').val(global_plate_well_use);

        if (global_plate_well_use === 'blank' || global_plate_well_use === 'empty' || global_plate_well_use === 'standard') {
            // reset other fields for user
            $('#matrix_item-' + idx).text("-");
            $('#id_assayplatereadermapitem_set-' + idx + '-matrix_item').val("-");
            $('#id_assayplatereadermapitemvalue_set-' + idx + '-matrix_item').val(null);

            // change the compound displayed in the table to nothing
            $('#compound-' + idx).text("-");
            $('#cell-' + idx).text("-");
            $('#setting-' + idx).text("-");

            $('#location-' + idx).text("-");
            $('#id_assayplatereadermapitem_set-' + idx + '-location').val(null);

            $('#location-' + idx).text("0");
            $('#id_assayplatereadermapitem_set-' + idx + '-location').val(null);

            $('#time-' + idx).text("0");
            $('#id_assayplatereadermapitemvalue_set-' + idx + '-time').val(null);
        }
        if (global_plate_well_use === 'blank' || global_plate_well_use === 'empty' || global_plate_well_use === 'sample') {
            // reset other fields for user
            $('#standard-value-' + idx).text("0");
            $('#id_assayplatereadermapitem_set-' + idx + '-standard-value').val(null);
        }
    }

    function specificChanges(plate_index_list, one_or_drag) {
        let incrementing_time_value = parseFloat(global_plate_time);
        let incrementing_standard_value = parseFloat(global_plate_standard_value);
        let this_operation = global_plate_increment_operation;
        let this_value = global_plate_increment_value;
        let adjusted_value = global_plate_increment_value;

        // standardize the increment by changing order of how selected
        if (global_plate_change_method === 'increment' && global_plate_increment_direction === 'right') {
            plate_index_list_ordered = plate_index_list.sort(function(a, b){return b-a});
            //console.log("dsc ", plate_index_list_ordered)
        } else {
            //save for reference....plate_index_list_ordered = plate_index_list.map(Number).sort(function(a, b){return a-b});
            plate_index_list_ordered = plate_index_list;
            //console.log("asc ", plate_index_list_ordered)
        }
        //console.log("asc ", plate_index_list_ordered)

        // reduce to * or +
        if (global_plate_change_method === 'increment') {
            if (this_operation === 'divide') {
                this_operation = '*';
                adjusted_value = 1.0/this_value;
            } else if (this_operation === 'multiply') {
                this_operation = '*';
                adjusted_value = 1.0*this_value;
            } else if (this_operation === 'subtract') {
                this_operation = '+';
                adjusted_value = -1.0*this_value;
            } else if (this_operation === 'add') {
                this_operation = '+';
                adjusted_value = 1.0*this_value;
            } else {
            }
        }

        // keep to identify the first one
        let which_change_number = 0;
        plate_index_list_ordered.forEach(function(idx) {
            //do for things that can ONLY copy (not increment)
            if (global_plate_well_use === 'sample') {
                // may want to increment matrix item, but will be tricky since it is the pk, not the item name
                // may do for phase two?
                if (global_plate_sample_change_matrix_item === true) {
                    $('#matrix_item-' + idx).text(global_plate_matrix_item_text);
                    $('#id_assayplatereadermapitem_set-' + idx + '-matrix_item').val(global_plate_matrix_item);
                    //$('#id_assayplatereadermapitemvalue_set-' + idx + '-matrix_item').val(global_plate_matrix_item);

                    // change the compound displayed in the table
                    $('#compound-' + idx).text($('#' + global_plate_matrix_item + '-compound-short').text());
                    $('#cell-' + idx).text($('#' + global_plate_matrix_item + '-cell-short').text());
                    $('#setting-' + idx).text($('#' + global_plate_matrix_item + '-setting-short').text());
                }
                if (global_plate_sample_change_location === true) {
                    $('#location-' + idx).text(global_plate_location_text);
                    $('#id_assayplatereadermapitem_set-' + idx + '-location').val(global_plate_location);
                }
            } else if (global_plate_well_use === 'standard') {
                //
            } else {
                // empty or blank
            }
            //do for things that can copy or increment
            if (global_plate_change_method === 'copy' || (global_plate_change_method === 'increment' && which_change_number == 0 )) {
                //copy
                if (global_plate_well_use === 'sample') {
                    if (global_plate_sample_change_time === true) {
                        $('#time-' + idx).text(global_plate_time);


                         //     global_plate_index_list_matches.push(cfs);
                        //     global_plate_time_matches.push(my_time);
                        //     global_plate_value_matches.push(my_value);

                        //div_block_value.appendChild(document.createTextNode(global_plate_time_matches[formsetidx]));
                        //div_time.appendChild(document.createTextNode(global_plate_value_matches[formsetidx]));
                        //$(div_time).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                        //$(div_block_value).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                        // get the right one TODO

                        $('#id_assayplatereadermapitemvalue_set-' + idx + '-time').val(global_plate_time);
                    }
                } else if (global_plate_well_use === 'standard') {
                        $('#standard-value-' + idx).text(global_plate_standard_value);
                        $('#id_assayplatereadermapitem_set-' + idx + '-standard-value').val(global_plate_standard_value);
                } else {
                    // empty or blank
                }
            } else {
                //increment
                //let this_operation = * or +
                //let this_value = adjusted to match
                // thought need to do something different with dragging, but this should work like the matrix
                if (this_operation === "*") {
                    incrementing_time_value = incrementing_time_value * adjusted_value;
                    incrementing_standard_value = incrementing_standard_value * adjusted_value;
                } else {
                    incrementing_time_value = incrementing_time_value + adjusted_value;
                    incrementing_standard_value = incrementing_standard_value + adjusted_value;
                }
                if (global_plate_well_use === 'sample') {
                    if (global_plate_sample_change_time === true) {
                        $('#time-' + idx).text(incrementing_time_value);



                         //     global_plate_index_list_matches.push(cfs);
                        //     global_plate_time_matches.push(my_time);
                        //     global_plate_value_matches.push(my_value);

                        //div_block_value.appendChild(document.createTextNode(global_plate_time_matches[formsetidx]));
                        //div_time.appendChild(document.createTextNode(global_plate_value_matches[formsetidx]));
                        //$(div_time).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                        //$(div_block_value).attr('value-formset-index', global_plate_index_list_matches[formsetidx]);
                        // get the right one TODO






                        $('#id_assayplatereadermapitemvalue_set-' + idx + '-time').val(incrementing_time_value);
                    }
                } else if (global_plate_well_use === 'standard') {
                    $('#standard-value-' + idx).text(incrementing_standard_value);
                    $('#id_assayplatereadermapitem_set-' + idx + '-standard-value').val(incrementing_standard_value);
                } else {
                    // empty or blank
                }
            }
            which_change_number = which_change_number + 1;
        });
    }

    // functions for the tooltips
    function escapeHtml(html) {
        return $('<div>').text(html).html();
    }
    function make_escaped_tooltip(title_text) {
        let new_span = $('<div>').append($('<span>')
            .attr('data-toggle', "tooltip")
            .attr('data-title', escapeHtml(title_text))
            .addClass("glyphicon glyphicon-question-sign pull-left")
            .attr('aria-hidden', "true")
            .attr('data-placement', "bottom"));
        return new_span.html();
    }
    // function to purge previous formsets when adding a page and changing plate size
    function removeFormsets() {
        // get rid of previous formsets before try to add more or the indexes get all messed up
        while ($('#formset').find('.inline').length > 0 ) {
            $('#formset').find('.inline').first().remove();
        }
        $('#id_assayplatereadermapitem_set-TOTAL_FORMS').val(0);
    }
    //keep for reference for now - adding a formset the original way from here:
    //https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/

    // keep this for reference for now - the selected attribute had to be cleared BEFORE another could be assigned!
    //   for each option                      clear selected              find one to select                       select it
    // $("#id_ns_method_target_unit option").removeAttr('selected').filter('[value='+global_plate_study_assay+']').attr('selected', true);
    // other suggested methods, might work if deselect first
    // $("#id_ns_method_target_unit").find('option[value=global_plate_study_assay]').attr('selected','selected');
    // $("#id_ns_method_target_unit > [value=global_plate_study_assay]").attr("selected", "true");
    // OR could loop through (this did not work to apply, but could work for remove than apply)
        // for(let i = 0; i < select_study_assay.options.length; i++){
        //     if(select_study_assay.options[i].value == global_plate_study_assay ){
        //         select_study_assay.options[i].selected = true;
        //         document.getElementById().selectedIndex = i;
        //     }
        // }
    // another method to try, do not recall if worked or not, need to retest
    // var $saveme = $('#standard_target_selected').selectize();
    // var myselection = $saveme[0].selectize;;
    // console.log(myselection)
    // example of finding regexp
    //     var needle = ':'
    //     var re = new RegExp(needle,'gi');
    //     var haystack = global_plate_file_block_dict;
    //     var results = new Array();
    //     while (re.exec(haystack)){
    //       results.push(re.lastIndex-1);
    //     }
});
