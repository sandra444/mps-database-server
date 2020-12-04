//GLOBAL-SCOPE
window.OMICS = {
    draw_plots: null,
    omics_data: null
};

$(document).ready(function () {
    //show the validation stuff
    $('#form_errors').show()
    // Load core chart package
    google.charts.load('current', {'packages': ['corechart']});
    google.charts.load('visualization', '1', {'packages': ['imagechart']});

    // $('.has-popover').popover({'trigger':'hover'});

    let page_omic_upload_group_id_change = 0;
    let page_omic_upload_group_pk_change = 0;

    let page_omic_upload_group_id_load_1 = 0;
    let page_omic_upload_group_pk_load_1 = 0;
    let page_omic_upload_group_id_load_2 = 0;
    let page_omic_upload_group_pk_load_2 = 0;
    let page_omic_upload_called_from = 'add';

    let page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];
    let page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];

    let page_make_the_group_change = true;

    //set the required-ness of the groups on load based on data type on load
    changed_something_important("load");

    let page_omic_upload_check_load = $('#check_load').html().trim();

    if (page_omic_upload_check_load === 'review') {
        page_omic_upload_called_from = 'load-review';
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    } else {
        page_omic_upload_group_id_load_1 = 1;
        page_omic_upload_group_pk_load_1 = $('#id_group_1')[0].selectize.items[0];
        page_omic_upload_group_id_load_2 = 2;
        page_omic_upload_group_pk_load_2 = $('#id_group_2')[0].selectize.items[0];

        if (page_omic_upload_check_load === 'add') {
            page_omic_upload_called_from = 'load-add';
            get_group_sample_info('load-add');
        } else {
            page_omic_upload_called_from = 'load-update';
            get_group_sample_info('load-update');
        }
    }

    // tool tip requirements
    let page_omic_upload_omic_file_format_deseq2_log2fc_headers = '"name", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"';
    let page_omic_upload_omic_file_format_deseq2_log2fc_tooltip = 'For DESeq2 Log2Fold change data, the header "log2FoldChange" must be in the first row. Other optional columns headers are: "baseMean", "lfcSE", "stat", "pvalue", "padj", and "gene reference" (or "name" or "gene").';
    $('#omic_file_format_deseq2_log2fc_tooltip').next().html($('#omic_file_format_deseq2_log2fc_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_deseq2_log2fc_tooltip));
    let page_omic_anaylsis_method_tooltip = 'The method (i.e. data processing tool, pipeline, etc.) used to process data.';
    $('#omic_anaylsis_method_tooltip').next().html($('#omic_anaylsis_method_tooltip').next().html() + make_escaped_tooltip(page_omic_anaylsis_method_tooltip));

    // indy-sample stuff
    let page_count_files = 'Counts data files must have one header row labeled "Sample ID" with each column labeled with a sample ID and the sample ID must match, EXACTLY, what is provided in the metadata table.  ';
    let page_omic_upload_omic_file_format_normcounts_tooltip = 'Under Development - ' + page_count_files;
    $('#omic_file_format_normcounts_tooltip').next().html($('#omic_file_format_normcounts_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_normcounts_tooltip));
    let page_omic_upload_omic_file_format_rawcounts_tooltip = 'Under Development - ' + page_count_files;
    $('#omic_file_format_rawcounts_tooltip').next().html($('#omic_file_format_rawcounts_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_rawcounts_tooltip));
    let page_drag_action_tooltip = 'Copy will copy and paste that selected value. Increment will add the indicated amount to the cells (note: for text field, will attempt to find a string+value, if found, will increment the value only, if not found, will treat all entered as a string and will add a value starting from 1).  ';
    $('#drag_action_tooltip').next().html($('#drag_action_tooltip').next().html() + make_escaped_tooltip(page_drag_action_tooltip));
    let page_drag_use_tooltip = 'Select what to do to the highlighted cells.';
    $('#drag_use_tooltip').next().html($('#drag_use_tooltip').next().html() + make_escaped_tooltip(page_drag_use_tooltip));
    let page_sample_name_tooltip = 'The sample name must match, exactly, the header of this sample data in the upload file.';
    $('#sample_name_tooltip').next().html($('#sample_name_tooltip').next().html() + make_escaped_tooltip(page_sample_name_tooltip));
    let page_sample_matrix_item_tooltip = 'The MPS Model name (chip/well ID).';
    $('#sample_matrix_item_tooltip').next().html($('#sample_matrix_item_tooltip').next().html() + make_escaped_tooltip(page_sample_matrix_item_tooltip));
    let page_sample_location_tooltip = 'The location in the MPS Model where the sample was collected.';
    $('#sample_location_tooltip').next().html($('#sample_location_tooltip').next().html() + make_escaped_tooltip(page_sample_location_tooltip));
    let page_assay_well_name_tooltip = 'If the omic assay is plate based, the well id (e.g., A1, A2, A3 etc.) - optional.';
    $('#assay_well_name_tooltip').next().html($('#assay_well_name_tooltip').next().html() + make_escaped_tooltip(page_assay_well_name_tooltip));
    let page_sample_time_day_tooltip = 'The time, from the start of the experiment, when the sample was collected. Can enter as Day and/or Hour and/or Minute.';
    $('#sample_time_day_tooltip').next().html($('#sample_time_day_tooltip').next().html() + make_escaped_tooltip(page_sample_time_day_tooltip));
    let page_sample_time_hour_tooltip = 'The time, from the start of the experiment, when the sample was collected. Can enter as Day and/or Hour and/or Minute.';
    $('#sample_time_hour_tooltip').next().html($('#sample_time_hour_tooltip').next().html() + make_escaped_tooltip(page_sample_time_hour_tooltip));
    let page_sample_time_minute_tooltip = 'The time, from the start of the experiment, when the sample was collected. Can enter as Day and/or Hour and/or Minute.';
    $('#sample_time_minute_tooltip').next().html($('#sample_time_minute_tooltip').next().html() + make_escaped_tooltip(page_sample_time_minute_tooltip));
    let page_empty_tooltip = 'Use this to empty cells in the table.';
    $('#empty_tooltip').next().html($('#empty_tooltip').next().html() + make_escaped_tooltip(page_empty_tooltip));

    /**
     * A function to clear the validation errors on change of any field
     */
    function clear_validation_errors() {
        $('#form_errors').hide();
    }

    /**
     * On click to toggle
    */
    // the file format details
    $('#fileFormatDetailsButton').click(function () {
        $('#omic_file_format_details_section').toggle();
    });
    // the graph sections
    $('#omicPreviewTheGraphsButton').click(function () {
        $('#omic_preview_the_graphs_section').toggle();
        $('#omic_preview_the_graphs_section2').toggle();
    });
    /**
     * On change data file
    */
    $('#id_omic_data_file').on('change', function (e) {
        clear_validation_errors();
        //when first change the file, make the preview button available
        $('#omic_preview_button_section').show();
        $('#omic_preview_the_graphs_section').show();
        $('#omic_preview_the_graphs_section2').show();
        changed_something_important("data_file");
    });
    /**
     * On change data type, change what is required page logic
    */
    $('#id_data_type').change(function () {
        clear_validation_errors();
        changed_something_important("data_type");
    });
    /**
     * On changes that affect the graphs/plots on the preview page
    */
    $('#id_anaylsis_method').on('change', function (e) {
        clear_validation_errors();
        changed_something_important("analysis_method");
    });

    function changed_something_important(called_from) {

        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {

            // stuff for the two group fields
            $('#id_group_1').next().addClass('required');
            $('.one-group').show();
            $('#id_group_2').next().addClass('required');
            $('.two-group').show();
            if (called_from != 'load') {
                //this preview is specific for the log2 fold change data...will need something different for counts data
                get_data_for_this_file_ready_for_preview(called_from)
            }

            // stuff for individual sample data
            $('.indy-sample').hide();

        } else {

            //stuff for the two group fields
            page_make_the_group_change = false;
            $('#id_group_1')[0].selectize.setValue('not-full');
            $('#id_group_2')[0].selectize.setValue('not-full');
            page_make_the_group_change = true;

            $('#id_location_1')[0].selectize.setValue('not-full');
            $('#id_time_1_day').val(0);
            $('#id_time_1_hour').val(0);
            $('#id_time_1_minute').val(0);
            page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];
            $('.one-group').hide();

            $('#id_location_2')[0].selectize.setValue('not-full');
            $('#id_time_2_day').val(0);
            $('#id_time_2_hour').val(0);
            $('#id_time_2_minute').val(0);
            page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];
            $('.two-group').hide();

            // stuff for individual sample data
            $('.indy-sample').show();
            sample_metadata_replace_show_hide();
            if (called_from == 'load' || called_from == 'number_samples' || page_metadata_lod_done == false) {
                buildSampleMetadataTable(called_from);
                afterBuildSampleMetadataTable(called_from);
            }

        }
    }

    // START indy-sample stuff
    var sample_metadata_table_id = 'sample_metadata_table';
    var page_metadata_lod_done = false;

    var page_drag_action = null;
    $('.number-samples').hide();
    var page_change_copy_increment = null;
    $('.increment-section').hide()

    if (document.getElementById('radio_replace').checked) {
        page_drag_action = 'replace';
        sample_metadata_replace_show_hide();
    };
    function sample_metadata_replace_show_hide() {

        if (page_drag_action === 'replace') {
            $('.replace-section').show();
            $('.highlight-section').hide();
        } else if (page_drag_action === 'mark') {
            $('.replace-section').hide();
            $('.highlight-section').show();
        } else {
            $('.replace-section').hide();
            $('.highlight-section').hide();
        }
    }

    number_samples_show_hide();
    function number_samples_show_hide() {
        if ($('#id_indy_number_of_samples').val() > 0) {
            $('.number-samples').hide();
        } else {
            $('.number-samples').show();
        }
    }
    $('#id_indy_number_of_samples').on('change', function (e) {
        number_samples_show_hide();
        changed_something_important("number_samples");
    });

    $("input[type='radio'][name='radio_change_copy_increment']").click(function () {
        page_change_copy_increment = $(this).val();
        if (page_change_copy_increment === 'increment-ttb' || page_change_copy_increment === 'increment-btt') {
            $('.increment-section').show();
        } else {
            $('.increment-section').hide();
        }
    });

    $(document).on('click', '#clear_highlights_indy_table', function() {
        $('.special-selected1').removeClass('special-selected1')
    });

    // a default is not set, user has to pick one
    $("input[type='radio'][name='radio_change_drag_action']").click(function () {
        // check to see if any cells in the table have been highlighted
        if ($('.special-selected1').length > 0) {
            page_drag_action = $(this).val();
            sample_metadata_replace_show_hide();
        } else {
            this.checked = false;
            alert("No cells in the Sample Metadata Table have been highlighted. Drag over cells to select them.\n");
        }
    });

    function sample_metadata_replace_show_hide() {
        //options are replace, empty, copys, pastes
        $('.replace-section').hide();
        $('.empty-section').hide();
        $('.copys-section').hide();
        $('.pastes-section').hide();

        if (page_drag_action === 'replace') {
            $('.replace-section').show();
        } else if (page_drag_action === 'empty') {
            $('.empty-section').show();
        } else if (page_drag_action === 'copys') {
            $('.copys-section').show();
        } else if (page_drag_action === 'pastes') {
            $('.pastes-section').show();
        } else {
            // console.log("no selection");
        }
    }

    var metadata_lod = [];
    // make sure order is parallel to form field indy_list_of_keys
    var metadata_headers = [
        'Options',
        'Sample Name/ID (Column Header)',
        'MPS Model Name',
        'Sample Location Name',
        'Sample Time (Day)',
        'Sample Time (Hour)',
        'Sample Time (Minute)',
        'Assay Plate Label',
        'sample_metadata_pk',
        'matrix_item_pk',
        'sample_location_pk',
        ]
    var indy_keys = JSON.parse($('#id_indy_list_of_keys').val());
    let table_order = [[0, "asc"], [1, "asc"], [2, "asc"], [3, "asc"], [4, "asc"], [5, "asc"] ];
    let table_column_defs = [
        {"targets": [0], "visible": true,},
        {"targets": [1], "visible": true,},
        {"targets": [2], "visible": true,},
        {"targets": [3], "visible": true,},
        {"targets": [4], "visible": true,},

        {"targets": [5], "visible": true,},
        {"targets": [6], "visible": true,},
        // {"targets": [7], "visible": true,},
        // {"targets": [8], "visible": true,},
        // {"targets": [9], "visible": true,},
        // {"targets": [10], "visible": true,},

        {responsivePriority: 1, targets: 0},
        {responsivePriority: 2, targets: 1},
        {responsivePriority: 3, targets: 2},
        {responsivePriority: 4, targets: 3},
    ];

    function buildSampleMetadataTable(called_from) {
        if (!page_metadata_lod_done) {
            // need to load metadata_lod
            metadata_lod = JSON.parse($('#id_indy_list_of_dicts').val());
            page_metadata_lod_done = true;
        }

        var elem = document.getElementById('div_for_'+sample_metadata_table_id);
        //remove the table
        elem.removeChild(elem.childNodes[0]);

        var myTableDiv = document.getElementById("div_for_"+sample_metadata_table_id);
        var myTable = document.createElement('TABLE');
        $(myTable).attr('id', sample_metadata_table_id);
        $(myTable).attr('cellspacing', '0');
        $(myTable).attr('width', '100%');
        $(myTable).addClass('display table table-striped table-hover');

        var tableHead = document.createElement("THEAD");
        var tr = document.createElement('TR');
        $(tr).attr('hrow-index', 0);

        tableHead.appendChild(tr);
        var hcolcounter = 0;

        $.each(metadata_headers, function (h_index, header) {
            if (header.includes('_pk') || header.includes('ption')) {
                // do not put in the table
            } else {
                var th = document.createElement('TH');
                $(th).attr('hcol-index', hcolcounter);
                // this was how did with plate....$(th).html(colnumber + top_label_button);
                th.appendChild(document.createTextNode(header));
                tr.appendChild(th);
                hcolcounter = hcolcounter + 1;
            }
        });
        myTable.appendChild(tableHead);

        var tableBody = document.createElement('TBODY');
        var rowcounter = 0;

        $.each(metadata_lod, function (r_index, row) {

            var tr = document.createElement('TR');
            $(tr).attr('row-index', rowcounter);
            tableBody.appendChild(tr);

            let colcounter = 0;
            let myCellContent = '';

            $.each(indy_keys, function (c_index, ikey) {
                if (ikey.includes('_pk') || ikey.includes('ption')) {
                    // do not put in the table
                } else {
                    var td = document.createElement('TD');
                    $(td).attr('col-index', colcounter);
                    $(td).attr('row-index', rowcounter);
                    $(td).attr('id-index', rowcounter * metadata_headers.length + colcounter);

                    if (ikey.includes('ption') && colcounter === 0) {
                        var side_label_button = ' <a id="indy_row' + rowcounter
                            + '" row-index="' + rowcounter
                            + '" class="btn btn-sm btn-primary">'
                            // + 'Copy'
                            + '<span class="glyphicon glyphicon-duplicate" aria-hidden="true"></span>'
                            + ' </a>'
                        $(td).html(side_label_button);
                        tr.appendChild(td);
                    } else {
                        // if ($("#check_load").html().trim() === 'review') {
                            td.appendChild(document.createTextNode(row[ikey]));
                        // } else {
                        //NOTE: the input fields were not sortable, so, skip this idea for now
                        //     if (ikey.includes('item') || ikey.includes('location') || ikey.includes('day') || ikey.includes('hour') || ikey.includes('minute')) {
                        //         td.appendChild(document.createTextNode(row[ikey]));
                        //     } else {
                        //         var size = 15;
                        //         // if (ikey.includes('day') || ikey.includes('hour') || ikey.includes('minute') || ikey.includes('well')) {
                        //         //     size = 5;
                        //         // } else if (ikey.includes('sample')) {
                        //         //     size = 15;
                        //         // } else {
                        //         //     size = 10;
                        //         // }
                        //         var input_button = ' <input type="text" size="' + size + '" name="r'
                        //             + rowcounter + 'c' + colcounter + ' id="r'
                        //             + rowcounter + 'c' + colcounter + ' value=' + row[ikey] + '>';
                        //         $(td).html(input_button);
                        //     }
                        // }
                        tr.appendChild(td);
                    }
                    colcounter = colcounter + 1;
                }
            });
            rowcounter = rowcounter+1
        });
        //todo here here if row less then number samples add some blanks?
        //make an add or delete button....or a row maybe a copy and delete?

        myTable.appendChild(tableBody);
        myTableDiv.appendChild(myTable);

        // When I did not have the var before the variable name, the table headers acted all kinds of crazy
        // do not want the table to paginate, pick a big for display length
        var sampleDataTable = $('#'+sample_metadata_table_id).DataTable({
            "iDisplayLength": 100,
            "sDom": '<B<"row">lfrtip>',
            //do not do the fixed header here...only want for two of the tables
            //https://datatables.net/forums/discussion/30879/removing-fixedheader-from-a-table
            //https://datatables.net/forums/discussion/33860/destroying-a-fixed-header
            fixedHeader: {headerOffset: 50},
            responsive: true,
            "order": table_order,
            "columnDefs": table_column_defs
        });

        return myTable;

    }

    function afterBuildSampleMetadataTable(called_from) {
        // allows table to be selectable, must be AFTER table is created - keep
        $('#' + sample_metadata_table_id).selectable({
            filter: 'td',
            distance: 15,
            stop: selectableDragOnSampleMetadataTable
        });
    }

    // START - secondary changes to assay plate map (Apply and Drag)
    // these get a plate_index_list of wells to change and sends to do the changes
    // NOTE - next line did not work as expected so used the document on HANDY
    // $(".apply-button").on("click", function(){
    $(document).on('click', '.apply-button', function () {
        let apply_button_that_was_clicked = $(this);
        callChangeSelectedByClickApply(apply_button_that_was_clicked);
    });
    // Select wells in platemap to change by drag - selected cells in table
    // https:// www.geeksforgeeks.org/how-to-change-selected-value-of-a-drop-down-list-using-jquery/
    // https:// stackoverflow.com/questions/8978328/get-the-value-of-a-dropdown-in-jquery
    function selectableDragOnPlateMaster() {
        if (global_check_load === 'review' ||
        document.getElementById("id_form_number_file_block_combos").value > 0) {
        // do not let the drag do anything!
        } else {
            callChangeSelectedByDragOnPlate()
        }
    }
    // END - secondary changes to assay plate map (Apply and Drag)

    function selectableDragOnSampleMetadataTable() {
        $('.ui-selected').addClass('special-selected1')
        console.log("calling a drag on")
    //    todo here here if the sample name is changed, redo the data points.... get the flag
    }

    function callChangeSelectedByDragOnPlate() {
        if (global_plate_well_use == 'pastes' && global_plate_copys_plate_index.length == 0) {
            alert('Copy/Paste will not work without a selected section to copy. Use Copy and drag.');
        } else {
            // load the lists based on what is dragged over
            // the plate_indexes of the selected cells in the assay plate map table
            // children of each cell of the assay plate map table that is selected
            // what cells were selected in the GUI
            let plate_index_list = [];
            let plate_indexes_rows = [];
            let plate_indexes_columns = [];
            $('.ui-selected').children().each(function () {
                if ($(this).hasClass("map-well-use")) {
                    let idx = $(this).attr('data-index');
                    plate_index_list.push(idx);
                    plate_indexes_rows.push($(this).attr('row-index'));
                    plate_indexes_columns.push($(this).attr('column-index'));
                }
            });
            // call for pastes or sample, empty, blank, standard
            callChangeSelectedByDragOnPlate2(plate_index_list, plate_indexes_rows, plate_indexes_columns);
        }
    }

    function callChangeSelectedByDragOnPlate2(plate_index_list, plate_indexes_rows, plate_indexes_columns) {
    // this could include the whole plate - so,
    // IF the incrementer is being used and if one of the - start over at top, left, or right
    // then, need to limit to either one column or one row for EACH call to makeSpecificChangesToPlateUsingPlatemapIndexList

    // this is called when drag and any well use option (including copys and pastes), so, have to handle all logic
    global_plate_add_or_edit_etc = 'drag';

    // note: not building an option for Top to Bottom then Right or Top to Bottom then Left - will have to build if requested
    let true_if_changes_made_and_ready_to_recolor_plate = true;
    if (global_plate_well_use === "copys") {
        // change happens for the paste, not the copy, set to false
        true_if_changes_made_and_ready_to_recolor_plate = false;

        // need to load the setup for the selected wells into memory for pasting, but not pasting/changing yet
        storeCurrentWellInfoForCopysFeature(plate_index_list);
        // memory is loaded as long as user does not change the radio button selection
        // auto change the radio but selection pastes
        $("#radio_pastes").prop("checked", true).trigger("click");
        global_plate_well_use = 'pastes';
    } else if (global_plate_well_use === "pastes") {
        // may need to build some logic to look columns (hang over)
        // right now, if the user places the paste and it wraps past the column, it will just wrap
        // may want to make it crop instead

        // some special changes for pastes to control change behavior
        // set all the check boxes to make changes to true so that all will change
        $("#checkbox_matrix_item").prop("checked", true);
        $("#checkbox_location").prop("checked", true);
        $("#checkbox_default_time").prop("checked", true);
        $("#checkbox_dilution_factor").prop("checked", true);
        $("#checkbox_collection_volume").prop("checked", true);
        $("#checkbox_collection_time").prop("checked", true);

        // the assay plate map index list is the pastes drag index
        // console.log("plate index list before load: ", plate_index_list)
        loadPlatemapIndexAndOtherReplacementInfo(plate_index_list);
        // console.log("plate index list after load: ", plate_index_list)
        makeSpecificChangesToPlateUsingPlatemapIndexList(plate_index_list);

        // assume users are doing this so they can change the default time, and turn off all the rest
        $("#checkbox_matrix_item").prop("checked", false);
        $("#checkbox_location").prop("checked", false);
        $("#checkbox_dilution_factor").prop("checked", false);
        $("#checkbox_collection_volume").prop("checked", false);
        $("#checkbox_collection_time").prop("checked", false);
    } else {
        // this is when well use is blank, empty, standard, or sample
        // here here if change blank logic
        if (
            global_plate_well_use === "blank" ||
            global_plate_well_use === "empty" ||
            global_plate_change_copy_increment === "copy") {
            loadPlatemapIndexAndOtherReplacementInfo(plate_index_list);
            makeSpecificChangesToPlateUsingPlatemapIndexList(plate_index_list);
        } else if (
            global_plate_increment_direction === "right-up" ||
            global_plate_increment_direction === "left-down") {
            // the value does not start over - okay to leave as one list
            loadPlatemapIndexAndOtherReplacementInfo(plate_index_list);
            makeSpecificChangesToPlateUsingPlatemapIndexList(plate_index_list);
        } else {
            // check what is changed and see if spans columns or rows
            // if does, need to split a loop of list for each of the columns or each of the rows
            // make a copy of a subset of the plate_index_list and call for each subset
            if (global_plate_increment_direction === 'top-top' ||
                global_plate_increment_direction === 'bottom-bottom') {
                // we are working with columns with restart
                let column_indexes = [...new Set(plate_indexes_columns)];
                column_indexes.forEach(function (el) {
                    let plate_index_list_sub = [];
                    $('.ui-selected').children().each(function () {
                        // send each selected cell of the table to the function for processing
                        // console.log("this: ",$(this))
                        if ($(this).hasClass("map-well-use") && $(this).attr('column-index') == el) {
                            let idx = $(this).attr('data-index');
                            plate_index_list_sub.push(idx);
                        }
                    });
                    plate_index_list_sub_ordered = loadPlatemapIndexAndOtherReplacementInfo(plate_index_list_sub);
                    // console.log("LIST: ", plate_index_list_sub)
                    makeSpecificChangesToPlateUsingPlatemapIndexList(plate_index_list_sub_ordered);
                });
            } else {
                // we are working with rows with restart
                let row_indexes = [...new Set(plate_indexes_rows)]
                row_indexes.forEach(function (el) {
                    // console.log("ggggt row indexex ", el)
                    let plate_index_list_sub = [];
                    $('.ui-selected').children().each(function () {
                        // send each selected cell of the table to the function for processing
                        // console.log("this: ",$(this))
                        if ($(this).hasClass("map-well-use") && $(this).attr('row-index') == el) {
                            let idx = $(this).attr('data-index');
                            plate_index_list_sub.push(idx);
                        }
                    });
                    plate_index_list_sub_ordered = loadPlatemapIndexAndOtherReplacementInfo(plate_index_list_sub);
                    // console.log("LIST: ", plate_index_list_sub)
                    makeSpecificChangesToPlateUsingPlatemapIndexList(plate_index_list_sub_ordered);
                });
            }
        }
    }

    if (true_if_changes_made_and_ready_to_recolor_plate === true) {
        // now, all changes made and ready to what shows in plate based on well use
        setFancyCheckBoxesLoopOverFancyCheckboxClass(plate_index_list, "change");
        // setWhatHiddenInEachWellOfPlateLoopsOverPlate(plate_index_list, "sfc_" + "drag");
    }

    }



    // END indy-sample

    // START section for preview page
    // To make the preview in the upload page
    // NOTE: the upload page has the following elements
    // that are used in getting the data needed
    // form name="omic_file"
    // id="id_data_type"
    // id="id_anaylsis_method"
    // id="id_omic_data_file"
    // And, these elements were added to the upload page
    // id="plots"
    // id="volcano-plots"
    // id="ma-plots"
    function get_data_for_this_file_ready_for_preview(called_from) {
        let data = {
            call: 'fetch_omics_data_for_upload_preview_prep',
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };
        let form = document.omic_file;
        let serializedData = $('form').serializeArray();
        let formData = new FormData(form);
        $.each(serializedData, function(index, field) {
            formData.append(field.name, field.value);
        });
        let study_id = 1;
        formData.append('study_id', study_id);
        let file_id = 1;
        formData.append('file_id', file_id);

        $.each(data, function(index, contents) {
            formData.append(index, contents);
        });

        let is_data = true;
        if (document.getElementById("id_omic_data_file").files.length > 0) {
            is_data = true;
        } else {
            is_data = false;
        }

        if (is_data) {
            window.spinner.spin(document.getElementById('spinner'));
            $.ajax({
                url: '/assays_ajax/',
                type: 'POST',
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false,
                data: formData,
                success: function (json) {
                    window.spinner.stop();
                    if (json.errors) {
                        alert(json.errors);
                    } else {
                        let exist = true;
                        // console.log("a DATA", json)
                        // omics_data = json['data'];
                        // omics_target_name_to_id = json['target_name_to_id'];
                        // omics_file_id_to_name = json['file_id_to_name'];
                        // omics_table = json['table'];
                        // console.log("b data ", omics_data)
                        // console.log("c target_name_to_id ", omics_target_name_to_id)
                        // console.log("d file_id_to_name ", omics_file_id_to_name)
                        // console.log("e table ", omics_table)
                        window.OMICS.omics_data = JSON.parse(JSON.stringify(json));
                        omics_file_id_to_name_all = window.OMICS.omics_data['file_id_to_name'];
                        omics_file_id_to_name = omics_file_id_to_name_all[1];
                        // maxL2FC_a = window.OMICS.omics_data['max_fold_change'];
                        // maxPval_a = window.OMICS.omics_data['max_pvalue'];
                        // minL2FC_a = window.OMICS.omics_data['min_fold_change'];
                        // minPval_a = window.OMICS.omics_data['min_pvalue'];
                        // console.log("a")
                        // console.log(maxL2FC_a)
                        // console.log(maxPval_a)
                        // console.log(minL2FC_a)
                        // console.log(minPval_a)
                        // maxL2FC = -Math.log10(maxL2FC_a);
                        // maxPval = -Math.log10(maxPval_a);
                        // minL2FC = -Math.log10(minL2FC_a);
                        // minPval = -Math.log10(minPval_a);
                        // console.log("no a")
                        // console.log(maxL2FC)
                        // console.log(maxPval)
                        // console.log(minL2FC)
                        // console.log(minPval)
                        // console.log("window.OMICS.omics_data ")
                        // console.log(window.OMICS.omics_data)
                        window.OMICS.draw_plots(window.OMICS.omics_data, true, 0, 0, 0, 0, 0, 0, 0, 'upload');
                        // function(omics_data, firstTime, minPval, maxPval, minL2FC, maxL2FC, minPval_neg, maxPval_neg, L2FC_abs)

                        // put here to avoid race errors
                        if (called_from == 'data_file') {
                            try {
                                id_omic_data_file = $('#id_omic_data_file').val();
                                check_file_add_update(id_omic_data_file);
                            } catch {
                            }
                        }
                    }
                },
                error: function (xhr, errmsg, err) {
                    window.spinner.stop();
                    alert('Encountered an error when trying to make a preview plot. Check to make sure the Data Type selected matches the file selected.');
                    console.log(xhr.status + ': ' + xhr.responseText);
                }
            });
        }
    };
    // END section for preview page

    /**
     * On change method
    */
    $('#id_study_assay').change(function () {
        clear_validation_errors();
        study_assay_value = $('#id_study_assay')[0].selectize.items[0];
        try {
            study_assay_text = $('#id_study_assay')[0].selectize.options[study_assay_value]['text'];
            if (study_assay_text.toLowerCase().includes('tempo-seq')) {
                new_value = 'temposeq_probe';
            } else {
                new_value = 'entrez_gene';
            }
            $('#id_name_reference')[0].selectize.setValue(new_value);
        } catch {
            $('#id_name_reference')[0].selectize.setValue('entrez_gene');
        }
    });
    /**
     * On change a group, call a function that gets sample info
    */
    $('#id_group_1').change(function () {
        clear_validation_errors();
        //console.log('change 1')
        if (page_make_the_group_change) {
            if ($('#id_group_1')[0].selectize.items[0] == $('#id_group_2')[0].selectize.items[0]) {
                $('#id_group_1')[0].selectize.setValue(page_omic_current_group1);
                send_user_groups_are_different_message();
            } else {
                page_omic_upload_called_from = 'change';
                page_omic_upload_group_id_change = 1;
                page_omic_upload_group_pk_change = $('#id_group_1')[0].selectize.items[0];

                if ($('#id_group_'+page_omic_upload_group_id_change)[0].selectize.items[0] != null) {
                    get_group_sample_info('change');
                } else {
                    $('#id_group_'+page_omic_upload_group_id_change)[0].selectize.items[0];
                    $('#id_time_'+page_omic_upload_group_id_change+'_day').val(null);
                    $('#id_time_'+page_omic_upload_group_id_change+'_hour').val(null);
                    $('#id_time_'+page_omic_upload_group_id_change+'_minute').val(null);

                    let $this_dropdown = $(document.getElementById('id_location_'+page_omic_upload_group_id_change));
                    $this_dropdown.selectize()[0].selectize.clearOptions();
                    $('#id_location_'+page_omic_upload_group_id_change)[0].selectize.setValue();
                }
            }
            page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];
        }
    });
    $('#id_group_2').change(function () {
        clear_validation_errors();
        if (page_make_the_group_change) {
            if ($('#id_group_1')[0].selectize.items[0] == $('#id_group_2')[0].selectize.items[0]) {
                $('#id_group_2')[0].selectize.setValue(page_omic_current_group2);
                send_user_groups_are_different_message();
            } else {
                page_omic_upload_called_from = 'change';
                //console.log('change 2')
                page_omic_upload_group_id_change = 2;
                page_omic_upload_group_pk_change = $('#id_group_2')[0].selectize.items[0];

                if ($('#id_group_'+page_omic_upload_group_id_change)[0].selectize.items[0] != null) {
                    get_group_sample_info('change');
                } else {
                    $('#id_group_'+page_omic_upload_group_id_change)[0].selectize.items[0];
                    $('#id_time_'+page_omic_upload_group_id_change+'_day').val(null);
                    $('#id_time_'+page_omic_upload_group_id_change+'_hour').val(null);
                    $('#id_time_'+page_omic_upload_group_id_change+'_minute').val(null);

                    let $this_dropdown = $(document.getElementById('id_location_'+page_omic_upload_group_id_change));
                    $this_dropdown.selectize()[0].selectize.clearOptions();
                    $('#id_location_'+page_omic_upload_group_id_change)[0].selectize.setValue();
                }
            }
            page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];
        }
    });

    // https://www.bitdegree.org/learn/best-code-editor/javascript-download-example-1
    function download(filename, text) {
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
    /**
     * On click to download
    */
    // Start file download.
    document.getElementById("fileFileFormatTwoGroup").addEventListener("click", function(){
    // Start the download of yournewfile.csv file with the content from the text area
        // could tie this to selections in the GUI later, if requested.
        // change with tool tip
        var text = page_omic_upload_omic_file_format_deseq2_log2fc_headers;
        var filename = "TwoGroupDESeq2Omic.csv";

        download(filename, text);
    }, false);

    function send_user_groups_are_different_message() {
        if (typeof $('#id_group_1')[0].selectize.items[0] !== 'undefined') {
            alert('Group 1 and Group 2 must be different or both must be empty.');
        }
    }

     /**
      * When a group is changed, if that group has already been added to the data upload file
      * get the first occurrence that has sample information.
    */
    function get_group_sample_info(called_from) {
        // console.log('1: '+page_omic_upload_group_pk_change)
        // console.log('2: '+page_omic_upload_group_pk_load_1)
        // console.log('3: '+page_omic_upload_group_pk_load_2)
        // console.log('4: '+page_omic_upload_called_from)

        // HANDY if using js split time
        // time_in_minutes = 121
        // var split_time = window.SPLIT_TIME.get_split_time(time_in_minutes);
        // $.each(split_time, function(time_name, time_value) {
        //     console.log(time_name)
        //     console.log(time_value)
        // });

        // if changing a group, need to get all the updated info
        // if an add page, need to call to clear out the location list
        // if update page, need to get the model location list

        let data = {
            call: 'fetch_omic_sample_info_from_upload_data_table',
            called_from: page_omic_upload_called_from,
            groupIdc: page_omic_upload_group_id_change,
            groupPkc: page_omic_upload_group_pk_change,
            groupId1: page_omic_upload_group_id_load_1,
            groupPk1: page_omic_upload_group_pk_load_1,
            groupId2: page_omic_upload_group_id_load_2,
            groupPk2: page_omic_upload_group_pk_load_2,
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };
        window.spinner.spin(document.getElementById('spinner'));
        $.ajax({
            url: '/assays_ajax/',
            type: 'POST',
            dataType: 'json',
            data: data,
            success: function (json) {
                window.spinner.stop();
                if (json.errors) {
                    // Display errors
                    alert(json.errors);
                }
                else {
                    let exist = true;
                    get_group_sample_info_ajax(json, exist);
                }
            },
            // error callback
            error: function (xhr, errmsg, err) {
                window.spinner.stop();
                alert('An error has occurred (finding group sample information). ');
                console.log(xhr.status + ': ' + xhr.responseText);
            }
        });
    }
    // post processing from ajax call
    /**
     * Put the sample data where it needs to go
    */
    let get_group_sample_info_ajax = function (json, exist) {
        // bringing back the D, H, M, and sample location (if found)

        // console.log('--- '+page_omic_upload_group_id_load_1)
        // console.log(json.timemess1)
        // console.log(json.day1)
        // console.log(json.hour1)
        // console.log(json.minute1)
        // console.log(json.locmess1)
        // console.log(json.sample_location_pk1)
        // console.log(json.location_dict1)
        // console.log(json.timemess2)
        // console.log(json.day2)
        // console.log(json.hour2)
        // console.log(json.minute2)
        // console.log(json.locmess2)
        // console.log(json.sample_location_pk2)
        // console.log(json.location_dict2)

        if (page_omic_upload_called_from == 'load-add') {
            // just do the location lists
        } else if (page_omic_upload_called_from == 'load-update') {
            // just do the location lists to restrict to the model
            let pk_loc_1 = $('#id_location_1')[0].selectize.items[0];
            let pk_loc_2 = $('#id_location_2')[0].selectize.items[0];

            let $this_dropdown1 = $(document.getElementById('id_location_1'));
            $this_dropdown1.selectize()[0].selectize.clearOptions();
            let this_dict1 = $this_dropdown1[0].selectize;
            // fill the dropdown with what brought back from ajax call
            $.each(json.location_dict1[0], function( pk, text ) {
                // console.log("1 "+pk+ "  "+text)
                this_dict1.addOption({value: pk, text: text});
            });

            let $this_dropdown2 = $(document.getElementById('id_location_2'));
            $this_dropdown2.selectize()[0].selectize.clearOptions();
            let this_dict2 = $this_dropdown2[0].selectize;
            // fill the dropdown with what brought back from ajax call
            $.each(json.location_dict2[0], function( pk, text ) {
                // console.log("2 "+pk+ "  "+text)
                this_dict2.addOption({value: pk, text: text});
            });

            $('#id_location_1')[0].selectize.setValue(pk_loc_1);
            $('#id_location_2')[0].selectize.setValue(pk_loc_2);
        } else {
            // called from a change of one of the groups
            $('#id_time_'+page_omic_upload_group_id_change+'_day').val(json.day1);
            $('#id_time_'+page_omic_upload_group_id_change+'_hour').val(json.hour1);
            $('#id_time_'+page_omic_upload_group_id_change+'_minute').val(json.minute1);

            // https://github.com/selectize/selectize.js/blob/master/docs/api.md
            // HANDY to set the options of selectized dropdown
            let $this_dropdown = $(document.getElementById('id_location_'+page_omic_upload_group_id_change));
            $this_dropdown.selectize()[0].selectize.clearOptions();
            let this_dict = $this_dropdown[0].selectize;
            // fill the dropdown with what brought back from ajax call
            //the changed one is always returned as the first
            $.each(json.location_dict1[0], function( pk, text ) {
                // console.log("c "+pk+ "  "+text)
                this_dict.addOption({value: pk, text: text});
            });
            $('#id_location_'+page_omic_upload_group_id_change)[0].selectize.setValue(json.sample_location_pk1);
        }

        //HANDY get the value from selectized
        // $('#id_se_block_standard_borrow_string')[0].selectize.items[0];
        //HANDY set value of selectized
        //$('#id_ns_blah')[0].selectize.setValue(page_omic_upload_blah);
        //HANDY get the text from selectized
        //page_omic_upload_aa = $('#id_aa')[0].selectize.options[page_omic_upload_aa]['text'];

    };

     /**
      * When the file is changed and is not null, check to see if the file
      * is already in this study
    */
    function check_file_add_update(id_omic_data_file) {
        if ($("#check_load").html().trim() === 'add') {
            data_file_pk = 0;
        } else {
            parseInt(document.getElementById("this_file_id").innerText.trim())
        }
        let data = {
            call: 'fetch_this_file_is_this_study',
            omic_data_file: id_omic_data_file,
            study_id: parseInt(document.getElementById("this_study_id").innerText.trim()),
            data_file_pk: data_file_pk,
            csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
        };
        window.spinner.spin(document.getElementById('spinner'));
        $.ajax({
            url: '/assays_ajax/',
            type: 'POST',
            dataType: 'json',
            data: data,
            success: function (json) {
                window.spinner.stop();
                if (json.errors) {
                    // Display errors
                    alert(json.errors);
                }
                else {
                    let exist = true;
                    if (json.true_to_continue.toString().toLowerCase() === 'false') {
                       alert(json.message);
                    }
                }
            },
            // error callback
            error: function (xhr, errmsg, err) {
                window.spinner.stop();
                alert('An error has occurred checking the file name. ');
                console.log(xhr.status + ': ' + xhr.responseText);
            }
        });
    }

    // tool tip functions
    function escapeHtml(html) {
        return $('<div>').text(html).html();
    }

    function make_escaped_tooltip(title_text) {
        let new_span = $('<div>').append($('<span>')
            .attr('data-toggle', 'tooltip')
            .attr('data-title', escapeHtml(title_text))
            .addClass('glyphicon glyphicon-question-sign')
            .attr('aria-hidden', 'true')
            .attr('data-placement', 'bottom'));
        return new_span.html();
    }

    // activates Bootstrap tooltips, must be AFTER tooltips are created - keep
    $('[data-toggle="tooltip"]').tooltip({container:'body', html: true});
    
});
