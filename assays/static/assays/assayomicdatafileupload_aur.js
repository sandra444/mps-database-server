//GLOBAL-SCOPE
window.OMICS = {
    draw_plots: null,
    omics_data: null
};

// todo - maybe - make it so that the user can overwrite a previous rather than this (this will be complicated)
// todo - remove an error for the log2 fold change where group1 can not equal group 2 - this could happen if the times are different - think about....
// todo at some point, check to make sure to limit the sample locations to what is listed in models in the study, if listed (location_1, 2 and sample location - three places currently)
// todo add a highlight all to columns required
// todo make sure form saved are not getting overwritten when come into update or review form

//todo what if change the tie unit???? time_unit_instance

$(document).ready(function () {
    //show the validation stuff
    $('#form_errors').show()

    // Load core chart package
    google.charts.load('current', {'packages': ['corechart']});
    google.charts.load('visualization', '1', {'packages': ['imagechart']});
    
    let page_omic_upload_called_from_in_js_file = 'add';
    let page_omic_upload_check_load = $('#check_load').html().trim();

    // two group stuff
    let page_omic_upload_group_id_change = 0;
    let page_omic_upload_group_pk_change = 0;

    let page_omic_upload_group_id_load_1 = 0;
    let page_omic_upload_group_pk_load_1 = 0;
    let page_omic_upload_group_id_load_2 = 0;
    let page_omic_upload_group_pk_load_2 = 0;   
    
    let page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];
    let page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];

    let page_make_the_group_change = true;

    // when visible, they are required, make them yellow
    $('#id_group_1').next().addClass('required');
    $('#id_group_2').next().addClass('required');
    $('#id_location_1').next().addClass('required');
    $('#id_location_2').next().addClass('required');

    // indy sample stuff
    var sample_metadata_table_id = 'sample_metadata_table';
    //has the info for the indy metadata table been populated - use so only pull from initial form once
    var page_metadata_lod_done = false;
    // had no default in html page
    var page_drag_action = null;
    // has a default in html page
    var page_change_duplicate_increment = 'duplicate';
    //the current one
    var metadata_lod = [];
    //v number of the current one (should be 1, 2, 3, 4, or 5 after first population)
    var metadata_lod_current_index = 0;
    //for holding versions to allow for undo and redo
    var metadata_lod_cum = [];
    //the table that is highlighted
    var metadata_highlighted = [];
    var list_of_icols_for_replace_highlighting = [];
    var icol_last_highlighted_seen = {};
    var indy_sample_metadata_table_current_row_order = [];

    // just working variables, but want in different subs, so just declare here
    var current_pk = 0;
    var current_val = '';

    // make sure to update this as needed (to match what comes from utils.py)
    var indy_well_meta_label = 'Metadata'
    var indy_row_label = 'Label'
    var indy_button_label = 'Button'
    
    var indy_list_of_dicts_of_table_rows = JSON.parse($('#id_indy_list_of_dicts_of_table_rows').val());
    console.log('indy_list_of_dicts_of_table_rows')
    console.log(indy_list_of_dicts_of_table_rows)
    var indy_list_of_column_labels = JSON.parse($('#id_indy_list_of_column_labels').val());
    var indy_list_of_column_labels_show_hide = JSON.parse($('#id_indy_list_of_column_labels_show_hide').val());

    // a queryset, using the form field - var indy_sample_location = JSON.parse($('#id_indy_sample_location').val());
    // a queryset, using the form field - var indy_matrix_item = JSON.parse($('#id_indy_matrix_item').val());

    var indy_matrix_item_list = JSON.parse($('#id_indy_matrix_item_list').val());
    var include_column_in_indy_table = indy_list_of_column_labels_show_hide;
    var chip_list = indy_matrix_item_list;
    var indy_column_labels = indy_list_of_column_labels;
    //var indy_row_labels = indy_list_of_row_labels;

    // boolean, using the form field - var indy_sample_metadata_table_was_changed = JSON.parse($('#id_indy_sample_metadata_table_was_changed').val());
        
    // todo need to update for the table as a plate
    // still need to decide how will nest the table (if well nest the table)
    // this will control what gets put in the table, but metadata_lod will have all the indy_column_labels in it
    // todo need to get the two extra sample times out and assay well name, but for now, turned them off
    

    // make a cross reference to the html dom name
    // todo - fix for new assumption that all headers are going in and are not editable
    // also - todo fix to add buttons for highlight change whole column and whole row
    var icol_to_html_outer = {};
    var icol_to_html_element = {};
    $.each(indy_column_labels, function (index, ikey) {
        if (index === 1) {
            icol_to_html_outer[ikey] ='h_indy_file_column_header_list';
            icol_to_html_element[ikey] ='file_column_header';
        } else
        if (index === 2) {
            icol_to_html_outer[ikey] ='h_indy_matrix_item';
            icol_to_html_element[ikey] ='matrix_item_name';
        } else
        if (index === 3) {
            icol_to_html_outer[ikey] ='h_indy_sample_location';
            icol_to_html_element[ikey] ='sample_location_name';
        } else
        // if (index === 4) {
        //     icol_to_html_outer[ikey] ='h_indy_assay_well_name';
        //     icol_to_html_element[ikey] ='assay_well_name';
        // } else
        if (index === 5) {
            icol_to_html_outer[ikey] ='h_indy_time_in_unit';
            icol_to_html_element[ikey] ='time_day';
        } else
        // if (index === 6) {
        //     icol_to_html_outer[ikey] ='h_indy_time_hour';
        //     icol_to_html_element[ikey] ='time_hour';
        // } else
        // if (index === 7) {
        //     icol_to_html_outer[ikey] = 'h_indy_time_minute';
        //     icol_to_html_element[ikey] = 'time_minute';
        // } else
        if (index === 8) {
            // icol_to_html_outer[ikey] ='h_indy_matrix_item';
            icol_to_html_element[ikey] ='matrix_item_pk';
        } else
        if (index === 9) {
            // icol_to_html_outer[ikey] ='h_indy_sample_location';
            icol_to_html_element[ikey] ='sample_location_pk';
        } else {

        }
    });

    // let table_order = [[0, 'asc'], [1, 'asc'], [2, 'asc'], [3, 'asc'], [4, 'asc'], [5, 'asc'] ];
    // todo - get the order column fixed
    let table_order = [ ];
    let table_column_defs = [
        // { 'width': '20%' },
        // { width: 200, targets: 0 }
        // {'targets': [0], 'visible': true,},
        // {'targets': [1], 'visible': true,},
        // {responsivePriority: 1, targets: 0},
        // {responsivePriority: 2, targets: 1},
    ];

    // START - Tool tips

    //todo update all the tool tips (add/remove as needed)

    // tool tips - two group stuff - all moved to help_text (at least, for now)

    // tool tips - indy-sample stuff
    //todo see if still need these....
    let page_drag_action_tooltip = 'Copy will copy and paste that selected value. Increment will add the indicated amount to the cells (note: for text field, will attempt to find a string+value, if found, will increment the value only, if not found, will treat all entered as a string and will add a value starting from 1).  ';
    $('#drag_action_tooltip').next().html($('#drag_action_tooltip').next().html() + make_escaped_tooltip(page_drag_action_tooltip));
    let page_drag_use_tooltip = 'Select what to do to the highlighted cells.';
    $('#drag_use_tooltip').next().html($('#drag_use_tooltip').next().html() + make_escaped_tooltip(page_drag_use_tooltip));
    let page_file_column_header_tooltip = 'The header of this sample data in the upload file.';
    $('#file_column_header_tooltip').next().html($('#file_column_header_tooltip').next().html() + make_escaped_tooltip(page_file_column_header_tooltip));
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

    // END - Tool tips

    // Some more load things Section
    changed_something_important('load');
    change_visibility_of_some_doms();

    if (page_omic_upload_check_load === 'review') {
        page_omic_upload_called_from_in_js_file = 'load-review';
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    } else {
        // todo add class to the sample time and sample location to make the box yellow - check to make sure we are not going to time unit and one time before mess with this
        // todo whenever it shows, PI asked for it to be required
        // todo build a required check into the form processess
        page_omic_upload_group_id_load_1 = 1;
        page_omic_upload_group_pk_load_1 = $('#id_group_1')[0].selectize.items[0];
        page_omic_upload_group_id_load_2 = 2;
        page_omic_upload_group_pk_load_2 = $('#id_group_2')[0].selectize.items[0];

        if (page_omic_upload_check_load === 'add') {
            page_omic_upload_called_from_in_js_file = 'load-add';
            get_group_sample_info('load-add');
        } else {
            page_omic_upload_called_from_in_js_file = 'load-update';
            get_group_sample_info('load-update');
            //do not allow changing of data type after a valid submit and save - user has to delete and then add back
            $('#id_data_type').selectize.disable();
        }
    }

    // START - General and two group stuff (written during log2fold change - that is pre indy
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
    /**
     * On click to toggle
    */
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
        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('#omic_preview_button_section').show();
            $('#omic_preview_the_graphs_section').show();
            $('#omic_preview_the_graphs_section2').show();
        } else {
            $('#omic_preview_button_section').hide();
            $('#omic_preview_the_graphs_section').hide();
            $('#omic_preview_the_graphs_section2').hide();
        }
        changed_something_important('data_file');
    });
    /**
     * On change data type, change what is required page logic
    */
    $('#id_data_type').change(function () {
        clear_validation_errors();

        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('#id_header_type')[0].selectize.setValue('target');
        } else {
            if ($('#id_header_type')[0].selectize.items[0] == 'target') {
                $('#id_header_type')[0].selectize.setValue('well');
            }
        }

        change_visibility_of_some_doms();

        changed_something_important('data_type');
    });
    function change_visibility_of_some_doms() {
        console.log("$('#id_data_type')[0].selectize.items[0] ",$('#id_data_type')[0].selectize.items[0])
        $('#omic_preview_button_section').hide();
        $('#omic_preview_the_graphs_section').hide();
        $('#omic_preview_the_graphs_section2').hide();

        $('#log2fc_template_section').hide();
        $('#normcounts_template_section').hide();
        $('#rawcounts_template_section').hide();

        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('#omic_preview_button_section').show();
            $('#omic_preview_the_graphs_section').show();
            $('#omic_preview_the_graphs_section2').show();
            console.log("should show the log2fc")
            $('#log2fc_template_section').show();

        } else {

            if ($('#id_data_type')[0].selectize.items[0] == 'rawcounts') {
               $('#rawcounts_template_section').show();
            } else {
               $('#normcounts_template_section').show();

            }
        }
    }
    /**
     * On change header type, change what is required page logic
    */
    $('#id_header_type').change(function () {
        clear_validation_errors();
        changed_something_important('header_type');
    });
    /**
     * On changes that affect the graphs/plots on the preview page
    */
    $('#id_anaylsis_method').on('change', function (e) {
        clear_validation_errors();
        changed_something_important('analysis_method');
    });
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
     * On change a group 1, call a function that gets sample info
    */
    $('#id_group_1').change(function () {
        clear_validation_errors();
        //console.log('change 1')
        if (page_make_the_group_change) {
            if ($('#id_group_1')[0].selectize.items[0] == $('#id_group_2')[0].selectize.items[0]) {
                $('#id_group_1')[0].selectize.setValue(page_omic_current_group1);
                send_user_groups_are_different_message();
            } else {
                page_omic_upload_called_from_in_js_file = 'change';
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
    /**
     * On change a group 2, call a function that gets sample info
    */
    $('#id_group_2').change(function () {
        clear_validation_errors();
        if (page_make_the_group_change) {
            if ($('#id_group_1')[0].selectize.items[0] == $('#id_group_2')[0].selectize.items[0]) {
                $('#id_group_2')[0].selectize.setValue(page_omic_current_group2);
                send_user_groups_are_different_message();
            } else {
                page_omic_upload_called_from_in_js_file = 'change';
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
    /**
     * On click to download_two_group_example
    */
    // Start file download_two_group_example.
    document.getElementById('fileFileFormatTwoGroup').addEventListener('click', function(){
    // Start the download_two_group_example of yournewfile.csv file with the content from the text area
        // could tie this to selections in the GUI later, if requested.
        // change with tool tip
        //todo - check the use of double quotes in some fields and not the first field....
        var text = page_omic_upload_omic_file_format_deseq2_log2fc_headers;
        var filename = 'TwoGroupDESeq2Omic.csv';

        download_two_group_example(filename, text);
    }, false);

    // END - General and two group stuff (written during log2fold change - that is pre indy

    // START added during indy-sample development click and change etc

    $("input[type='radio'][name='radio_change_duplicate_increment']").click(function () {
        page_change_duplicate_increment = $(this).val();
        if (page_change_duplicate_increment === 'increment-ttb' || page_change_duplicate_increment === 'increment-btt') {
            $('.increment-section').show();
        } else {
            $('.increment-section').hide();
        }
    });

    $(document).on('click', '#undoIndyButton', function() {
        indyClickedToUndoRedoChangeToTable('undo');
    });
    $(document).on('click', '#redoIndyButton', function() {
        indyClickedToUndoRedoChangeToTable('redo');
    });
    
    $(document).on('click', '#add_row_to_indy_table', function() {
        // may want to keep track in the number of samples - thing about how to keep track and redraw the table or add a row to the table...
    });

    $(document).on('click', '#clear_highlights_indy_table', function() {
        $('.special-selected1').removeClass('special-selected1');
        $('.special-selected2').removeClass('special-selected2');
        page_paste_cell_icol = null;
        page_paste_cell_irow = null;
        if (page_drag_action === 'pastes') {
            page_drag_action = null;
            sample_metadata_replace_show_hide();
        }
        whatIsCurrentlyHighlightedInTheIndyTable();
    });

    // a default is NOT set in the html file, so, user has to pick one
    $("input[type='radio'][name='radio_change_drag_action']").click(function () {
        // check to see if any cells in the table have been highlighted - such a pain....remove for now, but may need to had back a copys radio button
        // if ($('.special-selected1').length > 0) {
        //     page_drag_action = $(this).val();
        //     sample_metadata_replace_show_hide();
        // } else {
        //     if ($(this).val() === 'copys') {
        //         page_drag_action = $(this).val();
        //         sample_metadata_replace_show_hide();
        //     } else {
        //         page_drag_action = null;
        //         sample_metadata_replace_show_hide();
        //         alert('Drag over cells to highlight before selecting an Action.\n');
        //     }
        // }
        if ($(this).val() === 'pastes' || $(this).val() === 'empty') {
            if ($('.special-selected1').length > 0) {
                page_drag_action = $(this).val();
                sample_metadata_replace_show_hide();
            } else {
                page_drag_action = null;
                sample_metadata_replace_show_hide();
                alert('Drag over cells to highlight before selecting this Action.\n');
            }
        } else {
            page_drag_action = $(this).val();
            sample_metadata_replace_show_hide();
        }
    });
    //
    // $(document).on('click', '#indy_instructions', function() {
    //     $('.indy-instructions').toggle();
    // });

    $(document).on('click', '#replace_in_indy_table', function() {
        indyCalledToReplace();
    });

    //todo - going to get rid of these, but need to add others (highlight row/column)
    // clicked on an add row button in the indy table
    $(document).on('click', '.add_indy_row', function () {
        let add_button_clicked = $(this);
        indyClickedToAddRow(add_button_clicked);
    });
    // clicked on an add row button in the indy table
    $(document).on('click', '.delete_indy_row', function () {
        let delete_button_clicked = $(this);
        indyClickedToDeleteRow(delete_button_clicked);
    });

    // need on change events for chip id and for sample location so can populate the corresponding dom element
    // could have just used a memory variable, but having the text and pk in a dom element made picking a general process for all!
    // note in html file, search ~pk_tracking_note~
    $(document).on('change', '#id_indy_matrix_item', function() {
        var thisText = $('#id_indy_matrix_item').children('option:selected').text();
        var thisValue = $('#id_indy_matrix_item').children('option:selected').val();
        document.getElementById('matrix_item_name').innerHTML = thisText;
        document.getElementById('matrix_item_pk').innerHTML = thisValue;
    });
    $(document).on('change', '#id_indy_sample_location', function() {
        var thisText = $('#id_indy_sample_location').children('option:selected').text();
        var thisValue = $('#id_indy_sample_location').children('option:selected').val();
        document.getElementById('sample_location_name').innerHTML = thisText;
        document.getElementById('sample_location_pk').innerHTML = thisValue;
    });
    // not going to offer this to users - when sure about this, todo, delete this commented out stuff
    // $(document).on('change', '#id_indy_file_column_header_list', function() {
    //     var thisText = $('#id_indy_file_column_header_list').children('option:selected').text();
    //     var thisValue = $('#id_indy_file_column_header_list').children('option:selected').val();
    //     document.getElementById('file_column_header').innerHTML = thisText;
    //     document.getElementById('sample_pk').innerHTML = thisValue;
    // });

    // END added during indy-sample development click and change etc


    // START - All Functions section

    // ##START section for preview page(s)
    // FIRST, designed for log2 fold change by DESeq2 - phase I omic development fall 2020
    // To make the preview on this upload page:
    // NOTE: the upload page has the following elements that are used in getting the data needed
    // form name='omic_file'
    // id='id_data_type'
    // id='id_anaylsis_method'
    // id='id_omic_data_file'
    // And, these elements were added to the upload page
    // id='plots'
    // id='volcano-plots'
    // id='ma-plots''
    // THEN, in early 2021, extended for phase II omic development
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
        if (document.getElementById('id_omic_data_file').files.length > 0) {
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

                        window.OMICS.omics_data = JSON.parse(JSON.stringify(json));
                        omics_file_id_to_name_all = window.OMICS.omics_data['file_id_to_name'];
                        omics_file_id_to_name = omics_file_id_to_name_all[1];

                        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
                            // console.log('a DATA', json)
                            // omics_data = json['data'];
                            // omics_target_name_to_id = json['target_name_to_id'];
                            // omics_file_id_to_name = json['file_id_to_name'];
                            // omics_table = json['table'];
                            // console.log('b data ', omics_data)
                            // console.log('c target_name_to_id ', omics_target_name_to_id)
                            // console.log('d file_id_to_name ', omics_file_id_to_name)
                            // console.log('e table ', omics_table)
                            // maxL2FC_a = window.OMICS.omics_data['max_fold_change'];
                            // maxPval_a = window.OMICS.omics_data['max_pvalue'];
                            // minL2FC_a = window.OMICS.omics_data['min_fold_change'];
                            // minPval_a = window.OMICS.omics_data['min_pvalue'];
                            // console.log('a')
                            // console.log(maxL2FC_a)
                            // console.log(maxPval_a)
                            // console.log(minL2FC_a)
                            // console.log(minPval_a)
                            // maxL2FC = -Math.log10(maxL2FC_a);
                            // maxPval = -Math.log10(maxPval_a);
                            // minL2FC = -Math.log10(minL2FC_a);
                            // minPval = -Math.log10(minPval_a);
                            // console.log('no a')
                            // console.log(maxL2FC)
                            // console.log(maxPval)
                            // console.log(minL2FC)
                            // console.log(minPval)
                            // console.log('window.OMICS.omics_data ')
                            // console.log(window.OMICS.omics_data)
                            window.OMICS.draw_plots(window.OMICS.omics_data, true, 0, 0, 0, 0, 0, 0, 0, 'upload');
                            // function(omics_data, firstTime, minPval, maxPval, minL2FC, maxL2FC, minPval_neg, maxPval_neg, L2FC_abs)
                        }  else {
                            // todo need to coordinate with Quinn for the counts data


                        }
                        // put here to avoid race errors
                        if (called_from == 'data_file' || called_from == 'data_type') {
                            try {
                                id_omic_data_file = $('#id_omic_data_file').val();
                                check_file_add_update(id_omic_data_file);
                            } catch {
                            }
                            if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
                            } else {
                                // to do need to fill the sample names list to use for replace in the list and in the pick box
                                // todo - changing this so that it won't put in a replace option list, but will
                                // either write them to a table or a plate - lots of work todo here
                                indy_file_headers = window.OMICS.omics_data['indy_file_column_header_list'];
                                if (indy_file_headers.length === 0) {
                                    alert('There was no information pulled back from the file selected. This is commonly caused by a named header for the gene reference being missing. Use: gene, gene reference, or name as a column header for the gene field.')
                                }
                                // console.log('indy_file_headers ',indy_file_headers)

                                // todo these could be samples or well names...still working on this
                                // indy_row_labels = [];


                                // todo, load the prefix and number, think about how will use to make a plate looking table

                                // todo - do not think we will be using this drop down anymore, but keep since might need some of this code for getting what need for plate list(s)
                                let $this_dropdown = $(document.getElementById('id_indy_file_column_header_list'));

                                //HANDY-selectize selection clear and refill all
                                // clear the current selection or it can remain in the list :o
                                $('#id_indy_file_column_header_list').selectize()[0].selectize.clear()

                                // clear all options and refill
                                $this_dropdown.selectize()[0].selectize.clearOptions();
                                let this_dict = $this_dropdown[0].selectize;
                                // fill the dropdown with what brought back from ajax call
                                $.each(indy_file_headers, function( pk, text ) {
                                    console.log('c '+pk+ '  '+text)
                                    var in_me = text.indexOf('nnamed');
                                    if (in_me < 0) {
                                        lctext = text.toLowerCase();
                                        if (lctext === 'gene reference' || lctext === 'name' || lctext === 'gene'  || lctext === 'gene id') {
                                            //    skip it
                                        } else {
                                            this_dict.addOption({value: pk, text: text});
                                            // indy_row_labels.push(text);
                                        }
                                    }
                                });
                            }
                        }
                    }
                },
                error: function (xhr, errmsg, err) {
                    window.spinner.stop();
                    alert('Encountered an error when trying read the upload file. Check to make sure the Data Type selected matches the file selected.');
                    console.log(xhr.status + ': ' + xhr.responseText);
                }
            });
        }
    };
    // ##END section for preview page(s)

    // Other Functions

    // Called from a variety of places, including load, to set the right visibilities based on the data type
    // and also based on header_type....
    // and to call all the downstream functions needed depending on data type and how/when called
    function changed_something_important(called_from) {
        // console.log("called_from ",called_from)

        // could make this so it only checks if the data_type was changed, but it is okay this way, so leave it
        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {

            $('.compare-group').show();
            $('.indy-sample').hide();

            //stuff for the indy fields - all model form fields are used for log2fc

        } else {

            $('.compare-group').hide();
            $('.indy-sample').show();

            // setting some of the inside classes to hidden
            $('.increment-section').hide();

            //stuff for the two group fields - make sure some fields are empty for the indy upload files
            //this is so that stuff that is not related to the file is not saved in the upload file table
            page_make_the_group_change = false;
            $('#id_group_1')[0].selectize.setValue('not-full');
            $('#id_group_2')[0].selectize.setValue('not-full');
            page_make_the_group_change = true;

            $('#id_location_1')[0].selectize.setValue('not-full');
            $('#id_time_1_display').val(0);
            page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];

            $('#id_location_2')[0].selectize.setValue('not-full');
            $('#id_time_2_display').val(0);
            page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];

            sample_metadata_replace_show_hide();

            // do this ONLY for the first time need the metadata_lod, it may be on load, but may not
            if (!page_metadata_lod_done) {
                // need to load metadata_lod the first time
                metadata_lod = indy_list_of_dicts_of_table_rows;
                console.log('metadata_lod')
                console.log(metadata_lod)
                metadata_lod_current_index = 0;
                metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
                page_metadata_lod_done = true;
            }
            indySampleMetadataCallBuildAndPost();
        }

        // if returning from existing, will be loaded in form, so, only need when CHANGE the data file
        if (called_from != 'load') {
            get_data_for_this_file_ready_for_preview(called_from)
        }
    }

    // https://www.bitdegree.org/learn/best-code-editor/javascript-download-example-1
    //todo-change on double quote issue - want or not - all or none??
    function download_two_group_example(filename, text) {
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }

    function send_user_groups_are_different_message() {
        if (typeof $('#id_group_1')[0].selectize.items[0] !== 'undefined') {
            alert('Group 1 and Group 2 must be different or both must be empty.');
        }
        //todo, want to change sample time, this may need to be turned off, could have same groups with different sample time or location
        //todo, need to check in the form qc too
    }

     /**
      * When a group is changed, if that group has already been added to the data upload file
      * get the first occurrence that has sample information.
    */
    function get_group_sample_info(called_from) {
        // console.log('1: '+page_omic_upload_group_pk_change)
        // console.log('2: '+page_omic_upload_group_pk_load_1)
        // console.log('3: '+page_omic_upload_group_pk_load_2)
        // console.log('4: '+page_omic_upload_called_from_in_js_file)

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
            called_from: page_omic_upload_called_from_in_js_file,
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

        if (page_omic_upload_called_from_in_js_file == 'load-add') {
            // just do the location lists
        } else if (page_omic_upload_called_from_in_js_file == 'load-update') {
            // just do the location lists to restrict to the model
            let pk_loc_1 = $('#id_location_1')[0].selectize.items[0];
            let pk_loc_2 = $('#id_location_2')[0].selectize.items[0];

            let $this_dropdown1 = $(document.getElementById('id_location_1'));
            $this_dropdown1.selectize()[0].selectize.clearOptions();
            let this_dict1 = $this_dropdown1[0].selectize;
            // fill the dropdown with what brought back from ajax call
            $.each(json.location_dict1[0], function( pk, text ) {
                // console.log('1 '+pk+ '  '+text)
                this_dict1.addOption({value: pk, text: text});
            });

            let $this_dropdown2 = $(document.getElementById('id_location_2'));
            $this_dropdown2.selectize()[0].selectize.clearOptions();
            let this_dict2 = $this_dropdown2[0].selectize;
            // fill the dropdown with what brought back from ajax call
            $.each(json.location_dict2[0], function( pk, text ) {
                // console.log('2 '+pk+ '  '+text)
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
                // console.log('c '+pk+ '  '+text)
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
        if ($('#check_load').html().trim() === 'add') {
            data_file_pk = 0;
        } else {
            parseInt(document.getElementById('this_file_id').innerText.trim())
        }
        let data = {
            call: 'fetch_this_file_is_this_study',
            omic_data_file: id_omic_data_file,
            study_id: parseInt(document.getElementById('this_study_id').innerText.trim()),
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

    function sample_metadata_replace_show_hide() {
        //options are replace, empty, copys, pastes
        // for now, not using copys, but, keep in case PI wants to go back to something more like plate map app
        $('.replace-section').hide();
        $('.empty-section').hide();
        // $('.copys-section').hide();
        $('.pastes-section').hide();

        if (!page_drag_action) {
            $('#radio_replace').prop('checked', false);
            $('#radio_empty').prop('checked', false);
            // $('#radio_copys').prop('checked', false);
            $('#radio_pastes').prop('checked', false);
        } else if (page_drag_action === 'replace') {
            $('.special-selected2').removeClass('special-selected2');
            $('.replace-section').show();
        } else if (page_drag_action === 'empty') {
            $('.special-selected2').removeClass('special-selected2');
            $('.empty-section').show();
            indyCalledToEmpty();
        // } else if (page_drag_action === 'copys') {
        //     $('.special-selected2').removeClass('special-selected2');
        //     $('.copys-section').show();
        } else if (page_drag_action === 'pastes') {
            $('.pastes-section').show();
        } else {
            // console.log('no selection');
        }
    }

    function indyUndoRedoButtonVisibilityCheck() {
        var current_length_list = metadata_lod_cum.length;
        // should a button (undo or redo) show after whatever change brought you here
        if (metadata_lod_current_index > 0) {
            // yes, can undo another time
            $('#undo_button_div').show();
        } else {
            $('#undo_button_div').hide();
        }

        if (metadata_lod_current_index < current_length_list-1) {
            // yes, can undo another time
            $('#redo_button_div').show();
        } else {
            $('#redo_button_div').hide();
        }
    }

    function indySampleMetadataCallBuildAndPost() {
        indyUndoRedoButtonVisibilityCheck();
        buildSampleMetadataTable();
        afterBuildSampleMetadataTable();
        // do not want strip the highlighting after build table - instead, reapply the highlighting that was there
        // todo fix the reapply highlighting
        //reapplyTheHighlightingToTheIndyTable();
        // whatIsCurrentlyHighlightedInTheIndyTable();
        $('#id_indy_list_of_dicts_of_table_rows').val(JSON.stringify(metadata_lod));
    }

    // START - The functions that drive change to the indy sample metadata table

    // ~~ The undo or redo button functions
    //todo - maybe add some cleaning of the master list if it gets too big
    function indyClickedToUndoRedoChangeToTable(which_do) {
        var current_length_list = metadata_lod_cum.length;
        // undo goes toward the 0 index, redo towards the length of the index
        // the buttons should only be visible if the undo/redo is possible, but check before add/subtract
        if (which_do === 'undo') {            
            if (metadata_lod_current_index > 0) {
                metadata_lod_current_index = metadata_lod_current_index - 1;
            } else {
                alert('No undo storage at the current time')
            }
        } else {
            // which_do === 'redo'
            if (metadata_lod_current_index < current_length_list-1) {
                metadata_lod_current_index = metadata_lod_current_index + 1;
            } else {
                alert('No redo storage at the current time')
            }
        }

        metadata_lod = JSON.parse(JSON.stringify(metadata_lod_cum[metadata_lod_current_index]));
        // assume that change flags happened when made the, ignore undo - no reversal of flags for undo for now
        //     $('#id_indy_sample_metadata_table_was_changed').attr('checked',true);
        //     $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',true);
        indySampleMetadataCallBuildAndPost();
    }

    // ~~ The row-wise buttons
    function indyClickedToAddRow(thisButton) {
        indyClickedAddOrDeleteRow(thisButton, 'add');
    }

    function indyClickedToDeleteRow(thisButton) {
        indyClickedAddOrDeleteRow(thisButton, 'delete');
    }

    function indyClickedAddOrDeleteRow(thisButton, add_or_delete) {
        var thisRow = $(thisButton).attr('row-index');
        var thisRowMinusHeader = thisRow-1;

        var dictrow = metadata_lod[thisRowMinusHeader];
        if (dictrow['file_column_header'].length > 0) {
            // check the row to see if it has a field header
            $('#id_indy_sample_metadata_table_was_changed').attr('checked', true);
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked', true);
        } else {
            // check the row to see if the whole row is empty
            $.each(indy_column_labels, function (index, icol) {
                // do to all in the metadata_lod, not just the ones shown in the table, so, comment this out for now
                // if (include_header_in_indy_table[index] === 1) {
                    if (dictrow[icol].length > 0) {
                        $('#id_indy_sample_metadata_table_was_changed').attr('checked', true);
                    }
                // }
            });
        }
        if (add_or_delete === 'add') {
            metadata_lod.push(dictrow);
        } else {
            metadata_lod.splice(thisRowMinusHeader, 1);
        }

        metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
        metadata_lod_current_index = metadata_lod_cum.length - 1;
        indySampleMetadataCallBuildAndPost();
    }

    // ~~ The radio button change or change plus the go button/drag
    function indyCalledToPastes() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        indyCalledGutsPastesAndReplace('pastes');
        sameChangesToTableFromEmptyReplaceGoAndPaste();
    }
    
    function indyCalledToReplace() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        // resort for increment is in the front matter (above)
        indyCalledGutsPastesAndReplace('replace');
        sameChangesToTableFromEmptyReplaceGoAndPaste();

        //todo need to reset the option boxes highlighting (what you are picking to use for the replace)
        //it is not resetting correctly
    }

    function indyCalledGutsPastesAndReplace(called_from) {
        // replace - has the increment option, but always replacing the same cell
        // pastes - column will stay the same, rows will change, but, remember that, rows might not be in order
        // so use the actual order of the table, which is stored in indy_sample_metadata_table_current_row_order

        if (page_drag_action === 'pastes') {
            alert("paste is still in development")
        }

        var tirow_changing = null;
        for (var index = 0; index < metadata_highlighted.length; index++) {
            // console.log('metadata_highlighted[index]['metadata_highlighted_tirow'] '+metadata_highlighted[index]['metadata_highlighted_tirow'])
            // console.log('metadata_highlighted[index]['metadata_highlighted_ticol'] '+metadata_highlighted[index]['metadata_highlighted_ticol'])
            // console.log('metadata_highlighted[index]['metadata_highlighted_content'] '+metadata_highlighted[index]['metadata_highlighted_content'])

            var tirow = metadata_highlighted[index]['metadata_highlighted_tirow'];
            var ticol = metadata_highlighted[index]['metadata_highlighted_ticol'];

            if (page_drag_action === 'pastes') {
                $("#radio_duplicate").prop("checked", true).trigger("click");
                tirow_changing = tirow - 1; //still working on this todo!!
            } else {
                tirow_changing = tirow - 1;
            }

            // get using the .val for input fields
            current_val = $('#' + icol_to_html_element[ticol]).val();

            // because the pks are not in the table, they will not ever be highlighted
            // BUT, we want to keep them matching the names selected in the metadata_lod
            // so that, they are correct in the form field that is sent back
            // plan to check in the back end to make sure they went together
            // could remove the pks altogether, but, what if users decide want to see them.....
            current_pk = 0;
            if (ticol === 'matrix_item_name') {
                current_pk = $('#matrix_item_pk').text();
                current_val = $('#' + icol_to_html_element[ticol]).text();
            } else if (ticol === 'sample_location_name') {
                current_pk = $('#sample_location_pk').text();
                current_val = $('#' + icol_to_html_element[ticol]).text();
            } else if (ticol === 'file_column_header') {
                current_pk = $('#file_column_header_pk').text();
                current_val = $('#' + icol_to_html_element[ticol]).text();
            }

            // do not forget to subtract the header row when getting metadata_lod index!
            if (ticol === 'sample_location_name') {
                // can only duplicate, not increment the sample location
                metadata_lod[tirow_changing][ticol] = current_val;
                metadata_lod[tirow_changing]['sample_location_pk'] = current_pk;
            } else {
                if (page_change_duplicate_increment === 'duplicate') {
                    metadata_lod[tirow_changing][ticol] = current_val;
                    if (ticol === 'matrix_item_name') {
                        metadata_lod[tirow_changing]['matrix_item_pk'] = current_pk;
                    }
                } else {
                    // an increment
                    var current_index = icol_last_highlighted_seen[ticol+'_index'];

                    if (current_index === -99) {
                        // on the first one, it is a duplicate and change info for next
                        metadata_lod[tirow_changing][ticol] = current_val;
                        if (ticol === 'matrix_item_name') {
                            metadata_lod[tirow_changing]['matrix_item_pk'] = current_pk;
                        }
                        // update the last found object for next go
                        icol_last_highlighted_seen[ticol] = current_val;
                        icol_last_highlighted_seen[ticol + '_index'] = 0;
                    } else {
                        // not the first occurrence of this ticol
                        current_val = icol_last_highlighted_seen[ticol];

                        var i_current_val = 0;
                        if (ticol === 'time_day' || ticol === 'time_hour' || ticol === 'time_minute') {
                            if (page_change_duplicate_increment === 'increment-ttb'
                                || page_change_duplicate_increment === 'increment-btt') {
                                // it is + for both because the holding dict was sorting descending
                                i_current_val = parseFloat(current_val) + parseFloat($('#increment_value').val());
                            } else {
                                alert('Make sure to select to duplicate or increment');
                            }
                        } else if (ticol === 'matrix_item_name') {
                            // find the index of the last one, increase the index, if not out of range, replace
                            var index_in_chip_list = chip_list.indexOf(current_val);
                            var new_index = index_in_chip_list + parseInt($('#increment_value').val());
                            if (index_in_chip_list >=0 && new_index < chip_list.length) {
                                i_current_val = chip_list[new_index];
                            } else {
                                i_current_val = current_val;
                            }
                        } else if (ticol === 'file_column_header') {
                            // find the index of the last one, increase the index, if not out of range, replace
                            // var index_in_indy_row_labels = indy_row_labels.indexOf(current_val);
                            // var new_index = index_in_indy_row_labels + parseInt($('#increment_value').val());
                            // if (index_in_indy_row_labels >=0 && new_index < indy_row_labels.length) {
                            //     i_current_val = indy_row_labels[new_index];
                            // } else {
                            //     i_current_val = current_val;
                            // }
                        } else {
                            // todo well name still need an increment
                            // could i look from the right until finds first non number and split? - maybe a list? not sure yet..
                            // maybe string split the whole thing and index backards to first non number, then icrement the number
                            // could go back as string, but probably easier to work with list...think about
                                alert('Increment for this field is in development: '+ticol);

                        }
                        var i_current_index = parseInt(icol_last_highlighted_seen[ticol + '_index']) + 1;
                        // update the last found object for next go
                        icol_last_highlighted_seen[ticol] = i_current_val;
                        icol_last_highlighted_seen[ticol + '_index'] = i_current_index;
                        // update the correct location in the table metadata
                        metadata_lod[tirow_changing][ticol] = i_current_val;

                    }
                }
            }
        }
    };

    function indyCalledToEmpty() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        // just change the content of the cell
        var index = 0;
        for (index = 0; index < metadata_highlighted.length; index++) {
            var tirow = metadata_highlighted[index]['metadata_highlighted_tirow'];
            var ticol = metadata_highlighted[index]['metadata_highlighted_ticol'];
            // do not forget to subtract the header row
            metadata_lod[tirow-1][ticol] = '';
            if (ticol === 'matrix_item_name') {
                metadata_lod[tirow-1]['matrix_item_pk'] = '';
            } else if (ticol === 'sample_location_name') {
                metadata_lod[tirow-1]['sample_location_pk'] = '';
            }
        }
        sameChangesToTableFromEmptyReplaceGoAndPaste();
    }

    function sameFrontMatterToTableFromEmptyReplaceGoAndPaste() {
        whatIsCurrentlyHighlightedInTheIndyTable();
        $('#id_indy_sample_metadata_table_was_changed').attr('checked',true);

        if (list_of_icols_for_replace_highlighting.indexOf('file_column_header') >= 0) {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',true);
        } else {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',false);
        }

        // for replace, increment is only available in the replace, but allow the resorting here
        var metadata_highlighted_temp = [];
        metadata_highlighted_temp = JSON.parse(JSON.stringify(metadata_highlighted));
        if (page_drag_action === 'replace') {
            if (page_change_duplicate_increment === 'increment-ttb') {
                // think should be in the order of the table, so, leave it as is
            } else if (page_change_duplicate_increment === 'increment-btt') {
                // index should be from top to bottom
                metadata_highlighted = [];
                for (var index = metadata_highlighted_temp.length - 1; index >= 0; index--) {
                    metadata_highlighted.push(metadata_highlighted_temp[index]);
                }
            } else {
                // duplicate - index should not matter
            }
        }

    }

    function sameChangesToTableFromEmptyReplaceGoAndPaste() {
        metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
        metadata_lod_current_index = metadata_lod_cum.length - 1;
        indySampleMetadataCallBuildAndPost();
    }

    //todo, changed the ikey to col-index - will need to check this later
    function reapplyTheHighlightingToTheIndyTable() {
        var tirow = null;
        var ticol = null;
        var thisElementList = null;
        for (index = 0; index < metadata_highlighted.length; index++) {
            tirow = metadata_highlighted[index]['metadata_highlighted_tirow'];
            ticol = metadata_highlighted[index]['metadata_highlighted_ticol'];
            thisElementList = $('td[col-index*="' + ticol + '"][row-index*="' + tirow + '"]');
            // $("td[col-index*='file_column_header'][row-index*='1']").addClass('special-selected1')
            // console.log("thisElementList ",thisElementList)
            if ( (thisElementList.hasClass('no-edit') || thisElementList.hasClass('no-edit-data'))
                && $('#id_header_type')[0].selectize.items[0] === 'well') {
            //    skip todo fix this so can not hightling the empty wells!
            } else {
                thisElementList.addClass('special-selected1');
            }
        }
        if (page_paste_cell_irow) {
            tirow = page_paste_cell_irow;
            ticol = page_paste_cell_icol;
            thisElementList = $('td[col-index*="' + ticol + '"][row-index*="' + tirow + '"]');
            thisElementList.addClass('special-selected2');
        }
    }

    //todo check all the attibute labels - adding new ones
    function whatIsCurrentlyHighlightedInTheIndyTable() {
        metadata_highlighted = [];
        list_of_icols_for_replace_highlighting = [];
        $('.special-selected1').each(function() {
            var dict = {};
            var imetadata_highlighted_tirow = $(this).attr('row-index');
            var imetadata_highlighted_ticol = $(this).attr('col-index');
            var imetadata_highlighted_tlrow = $(this).attr('row-label');
            var imetadata_highlighted_tlcol = $(this).attr('col-label');
            var imetadata_highlighted_label = $(this).attr('meta-label');

            // since this goes through all the keys, and they could be different types, try different ways of pulling
            // keep in mind that the content could actually be null, if it is, make it a space
            var imetadata_highlighted_content = null;
            try {
                imetadata_highlighted_content = $(this).val();
            } catch {
                 imetadata_highlighted_content = '';
            }
            if (!imetadata_highlighted_content) {
                try {
                    imetadata_highlighted_content = $(this).text();
                } catch {
                    imetadata_highlighted_content = '';
                }
            }
            if (!imetadata_highlighted_content) {
                try {
                    imetadata_highlighted_content = $(this).innerHTML.trim();
                } catch {
                    imetadata_highlighted_content = '';
                }
            }
            if (imetadata_highlighted_content.length === 0) {
                imetadata_highlighted_content = $(this).text();
            }
            if (imetadata_highlighted_content.length === 0) {
                try {
                    imetadata_highlighted_content = $(this).innerHTML.trim();
                } catch {
                    imetadata_highlighted_content = '';
                }
            }
            dict['metadata_highlighted_tirow'] = imetadata_highlighted_tirow;
            dict['metadata_highlighted_ticol'] = imetadata_highlighted_ticol;
            dict['metadata_highlighted_ticol'] = imetadata_highlighted_ticol;
            dict['metadata_highlighted_content'] = imetadata_highlighted_content;
            list_of_icols_for_replace_highlighting.push(imetadata_highlighted_ticol);
            metadata_highlighted.push(dict);
        });
        // a special check to grey out replace content if field not in the icol list that has a dom element
        for (var icol in icol_to_html_outer) {
            if (list_of_icols_for_replace_highlighting.indexOf(icol) >= 0) {
                $('#'+icol_to_html_outer[icol]).addClass('required');
            } else {
                $('#'+icol_to_html_outer[icol]).removeClass('required');
            }
        }
        // console.log('metadata_highlighted ',metadata_highlighted)
        
        // need for replace and pastes to keep track of last seen during the replace/pastes
        // costs a little extra to put here, but will always be ready
        icol_last_highlighted_seen = {};
        $.each(indy_column_labels, function (index, icol) {
            icol_last_highlighted_seen[icol] = '99';
            icol_last_highlighted_seen[icol+'_index'] = -99;
        });
    }

    // END - The functions that change the indy table
    
    var page_paste_cell_irow = null;
    var page_paste_cell_icol = null;
    function selectableDragOnSampleMetadataTable() {
        // console.log("dragging")
        if (page_drag_action === 'pastes') {
            if (document.getElementsByClassName('special-selected1').length === 0) {
                page_drag_action = null;
                sample_metadata_replace_show_hide();
                alert('Select some text to copy before drag to paste');
            } else {
                $('.special-selected2').removeClass('special-selected2');
                // want to highlight from the first location, so, want only the first one
                var icount = 0;
                $('.ui-selected').each(function () {
                    if (icount == 0) {
                        $(this).addClass('special-selected2');
                        page_paste_cell_irow = $(this).attr('row-index');
                        page_paste_cell_icol = $(this).attr('col-index');
                        //todo add others????
                    }
                    // $(this).removeClass('ui-selected');
                    icount = icount + 1;
                });
                indyCalledToPastes();
            }
        } else {
            $('.special-selected2').removeClass('special-selected2');
            $('.ui-selected').each(function() {
                if ($(this).hasClass('special-selected1')) {
                    $(this).removeClass('special-selected1');
                } else {
                    $(this).addClass('special-selected1');
                }
                $(this).removeClass('ui-selected');
            });
        }
        // if keep this updated, can use to grey out replace fields that are not needed
        whatIsCurrentlyHighlightedInTheIndyTable();
    }



    //may want to move these later todo make these work without the sort...
    $(document).on('click', '.apply-column-button', function (e) {
        e.stopPropagation();
        let apply_button_that_was_clicked = $(this);
        console.log(apply_button_that_was_clicked);

        let this_col_index = this.getAttribute("col-index");
        //what is the column-index, for each with this column-index
        $('.indy-data').each(function() {
            if ($(this).attr('col-index') === this_col_index) {
                if ($(this).hasClass('special-selected1')) {
                    $(this).removeClass('special-selected1');
                } else {
                    $(this).addClass('special-selected1');
                }
            }
        });
    });
    $(document).on('click', '.apply-row-button', function (e) {
        e.stopPropagation();
        let apply_button_that_was_clicked = $(this);
        console.log(apply_button_that_was_clicked);

        let this_row_index = this.getAttribute("row-index");
        //what is the column-index, for each with this column-index
        $('.indy-data').each(function() {
            if ($(this).attr('row-index') === this_row_index) {
                if ($(this).hasClass('special-selected1')) {
                    $(this).removeClass('special-selected1');
                } else {
                    $(this).addClass('special-selected1');
                }
            }
        });
    });

    function buildSampleMetadataTable() {

        // build a table
        var elem = document.getElementById('div_for_' + sample_metadata_table_id);
        //remove the table
        if (elem.childNodes[0]) {
            elem.removeChild(elem.childNodes[0]);
        }

        var myTableDiv = document.getElementById('div_for_' + sample_metadata_table_id);
        var myTable = document.createElement('TABLE');
        $(myTable).attr('id', sample_metadata_table_id);
        $(myTable).attr('cellspacing', '0');
        $(myTable).attr('width', '100%');
        $(myTable).addClass('display table table-striped table-hover');

        var tableHead = document.createElement('THEAD');

        var tr = document.createElement('TR');
        var rowcounter = 0;
        $(tr).attr('row-index', rowcounter);
        var colcounter = 0;

        $.each(indy_column_labels, function (i_index, colLabel) {
            // include in table or not - 1 is for include
            if (include_column_in_indy_table[i_index] === 1) {
                var th = document.createElement('TH');
                $(th).attr('col-index', colcounter);
                $(th).attr('row-index', rowcounter);
                $(th).attr('col-label', colLabel);
                $(th).attr('row-label', indy_column_labels);
                $(th).attr('meta-label', indy_column_labels);

                if (colLabel.includes(indy_button_label)) {
                    th.appendChild(document.createTextNode(''));
                } else {
                    th.appendChild(document.createTextNode(colLabel));
                }


                // when put in the header like this, the column sorted
                // if (colLabel.includes(indy_row_label) || colLabel.includes(indy_well_meta_label) || page_omic_upload_check_load === 'review') {
                //    th.appendChild(document.createTextNode(colLabel));
                // } else {
                //     let top_label_button = ' <a col-index="' + colcounter
                //     + '" class="btn btn-sm btn-primary apply-column-button">'
                //     + '<span class="glyphicon glyphicon-option-vertical" aria-hidden="true"></span></a>'
                //     $(th).html(colLabel + top_label_button);
                // }

                tr.appendChild(th);
                colcounter = colcounter + 1;
            }
            // else, do not put in the table and do not increment the header counter
        });

        tableHead.appendChild(tr);

        myTable.appendChild(tableHead);
        var tableBody = document.createElement('TBODY');

        // start add arrow down row in body
        if (5==5 && page_omic_upload_check_load != 'review') {
            var tr = document.createElement('TR');
            rowcounter = rowcounter + 1;
            $(tr).attr('row-index', rowcounter);

            colcounter = 0;
            $.each(indy_column_labels, function (i_index, colLabel) {
                if (include_column_in_indy_table[i_index] === 1) {
                    var td = document.createElement('TD');
                    if (colLabel.includes(indy_row_label) ||
                        colLabel.includes(indy_well_meta_label) ||
                        colLabel.includes(indy_button_label)) {
                        td.appendChild(document.createTextNode(''));
                    } else {
                        $(td).attr('class', 'apply-column-button');
                        let top_label_button = ' <a col-index="' + colcounter
                            + '" class="btn btn-sm btn-primary apply-column-button">'
                            + '<span class="glyphicon glyphicon-resize-vertical" aria-hidden="true"></span></a>'
                        $(td).html(top_label_button);
                    }
                    $(td).attr('class', 'no-edit');
                    tr.appendChild(td);
                    colcounter = colcounter + 1;
                }
            });
            rowcounter = rowcounter + 1;
        }
        tableBody.appendChild(tr);
        // end add arrow down row in body

        colcounter = 0;
        let myCellContent = '';
        $.each(metadata_lod, function (i_index, row) {
            let rowLabel = row[indy_row_label];
            let metaLabel = row[indy_row_label];
            if ($('#id_header_type')[0].selectize.items[0] === 'well') {
                metaLabel = row[indy_well_meta_label];
            }
            // if doing as a well, there are some rows we do not want in the table, but want in our metadata_lod
            if (
                $('#id_header_type')[0].selectize.items[0] === 'well'
                &&
                (metaLabel === 'matrix_item_pk' ||
                    metaLabel === 'sample_location_pk' ||
                    metaLabel === 'sample_metadata_pk')
                ) {
                // skip over the rows of metadata_lod that we just do not want (pk rows)
            } else {
                var tr = document.createElement('TR');
                $(tr).attr('row-index', rowcounter);
                tableBody.appendChild(tr);

                colcounter = 0;
                let myCellContent = '';

                $.each(indy_column_labels, function (i_index, colLabel) {
                    myCellContent = row[colLabel];

                    // include in table or not - 1 is for include
                    if (include_column_in_indy_table[i_index] === 1) {

                        if (colLabel.includes(indy_row_label) ||
                            colLabel.includes(indy_well_meta_label) ||
                            colLabel.includes(indy_button_label)) {

                            var th = document.createElement('TH');
                            $(th).attr('col-index', colcounter);
                            $(th).attr('row-index', rowcounter);
                            $(th).attr('col-label', colLabel);
                            $(th).attr('row-label', 'header');
                            $(th).attr('meta-label', 'header');

                            if (page_omic_upload_check_load != 'review' && colLabel.includes(indy_button_label)) {
                                $(th).attr('class', 'apply-row-button');
                                let row_label_button = ' <a row-index="' + rowcounter
                                + '" class="btn btn-sm btn-primary apply-row-button">'
                                + '<span class="glyphicon glyphicon-resize-horizontal" aria-hidden="true"></span></a>'
                                //$(th).html(myCellContent + row_label_button);
                                $(th).html(row_label_button);
                                $(th).attr('class', 'no-edit');
                            } else {
                                th.appendChild(document.createTextNode(myCellContent));
                            }
                            tr.appendChild(th);
                        } else {
                            var td = document.createElement('TD');
                            $(td).attr('col-index', colcounter);
                            $(td).attr('row-index', rowcounter);
                            $(td).attr('col-label', colLabel);
                            $(td).attr('row-label', rowLabel);
                            $(td).attr('meta-label', metaLabel);
                            td.appendChild(document.createTextNode(myCellContent));
                            let contentLength = myCellContent.trim().length;
                            //todo think about how to do this - do want empty or some place holder?
                            console.log("myCellContent ",myCellContent, " ", contentLength)
                            if (contentLength == 0 && $('#id_header_type')[0].selectize.items[0] === 'well') {
                                $(td).attr('class', 'no-edit-data');
                            } else {
                                $(td).attr('class', 'indy-data');
                            }
                            tr.appendChild(td);
                        }
                        colcounter = colcounter + 1;
                    }
                });
                rowcounter = rowcounter + 1;
            }
        });

        myTable.appendChild(tableBody);
        myTableDiv.appendChild(myTable);

        // When I did not have the var before the variable name, the table headers acted all kinds of crazy
        var sampleDataTable = $('#' + sample_metadata_table_id).removeAttr('width').DataTable({
            // 'iDisplayLength': 100,
            paging: false,
            'sDom': '<B<"row">lfrtip>',
            //do not do the fixed header here...only want for two of the tables
            //https://datatables.net/forums/discussion/30879/removing-fixedheader-from-a-table
            //https://datatables.net/forums/discussion/33860/destroying-a-fixed-header
            fixedHeader: {headerOffset: 50},
            // responsive: true,
            'order': table_order,
            'columnDefs': table_column_defs,
            // fixedColumns: true
            'autoWidth': true
        });

        sampleDataTable.rows().every(function () {
            // this.data() is a list, with the first one being the tags and such
            // console.log("this row ",this.data());
            // console.log("this row ",this.data()[0]);
            // the tags and such look like a long string, so, to find an attribute, must be creative
            // below is HANDY for looping through, and getting a value.by name, but we do not need that here
            // var data = this.data();
            // data.forEach(function (value, index) {
            //     // if (value.isActive)
            //     // {
            //      console.log('value ',value);
            //https://stackoverflow.com/questions/29077902/how-to-loop-through-all-rows-in-datatables-jquery
            //      // console.log(value.UserName);
            //     // }
            // })
            var tags_and_such = this.data()[0].replace('=', '"').replace(' ', '"');
            var tags_and_such_list = tags_and_such.split('"');
            var index_of_row_index_label = -1;
            var row_index = -1;
            tags_and_such_list.forEach(function (value, index) {
                if (value.indexOf('row-index') >= 0) {
                    index_of_row_index_label = index;
                }
                ;
            });
            if (index_of_row_index_label >= 0) {
                row_index = tags_and_such_list[index_of_row_index_label + 1];
                indy_sample_metadata_table_current_row_order.push(row_index);
            } else {
                console.log('The row index should always be found...');
            }
        });
        return myTable;
    }

    function afterBuildSampleMetadataTable() {
        // allows table to be selectable, must be AFTER table is created - keep
        $('#' + sample_metadata_table_id).selectable({
            filter: 'td',
            distance: 15,
            stop: selectableDragOnSampleMetadataTable
        });
    }    

    // END - All Functions section

    // START - general tool tip functions
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

    // END - general tool tip functions

});
