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
    
    let page_omic_upload_called_from_in_js_file = 'add';
    let page_omic_upload_check_load = $('#check_load').html().trim();

    // $('.has-popover').popover({'trigger':'hover'});

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

    // indy sample stuff
    var sample_metadata_table_id = 'sample_metadata_table';
    //has the info for the indy metadata table been populated - use so only pull from initial form once
    var page_metadata_lod_done = false;
    var page_drag_action = null;
    var page_change_duplicate_increment = null;
    //the current one
    var metadata_lod = [];
    //v number of the current one (should be 1, 2, 3, 4, or 5 after first population)
    var metadata_lod_current_index = 0;
    //for holding versions to allow for undo and redo
    var metadata_lod_cum = [];
    //the table that is highlighted
    var metadata_highlighted_tirow = [];
    var metadata_highlighted_ticol = [];
    var metadata_highlighted_tikey = [];
    var metadata_highlighted_content = [];

    // make sure order is parallel to form field indy_list_of_keys
    var metadata_headers = [
        'Row Options',
        'File Column Header',
        'Chip or Well ID',
        'Sample Location',
        'Assay Well Name (optional)',
        'Sample Time (Day)',
        'Sample Time (Hour)',
        'Sample Time (Minute)',
        'sample_metadata_pk',
        'matrix_item_pk',
        'sample_location_pk',
        ]
    var include_header_in_indy_table = [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        ]
    var indy_keys = JSON.parse($('#id_indy_list_of_keys').val());
    // make a cross reference to the html dom name
    // todo deal with the name/pk issue
    var ikey_to_html_replace = {};
    $.each(indy_keys, function (index, ikey) {
        if (index === 1) {
            ikey_to_html_replace[ikey] ='sample_name';
        } else
        if (index === 2) {
            ikey_to_html_replace[ikey] ='id_indy_matrix_item';
        }
        if (index === 3) {
            ikey_to_html_replace[ikey] ='id_indy_sample_location';
        } else
        if (index === 4) {
            ikey_to_html_replace[ikey] ='assay_well_name';
        }
        if (index === 5) {
            ikey_to_html_replace[ikey] ='time_day';
        }
        if (index === 6) {
            ikey_to_html_replace[ikey] ='time_hour';
        } else
        if (index === 7) {
            ikey_to_html_replace[ikey] ='time_minute';
        }
    });

    let table_order = [[0, "asc"], [1, "asc"], [2, "asc"], [3, "asc"], [4, "asc"], [5, "asc"] ];
    let table_column_defs = [
        // { "width": "20%" },
        // { width: 200, targets: 0 }
        // {"targets": [0], "visible": true,},
        // {"targets": [1], "visible": true,},
        // {"targets": [2], "visible": true,},
        // {"targets": [3], "visible": true,},
        // {"targets": [4], "visible": true,},
        //
        // {"targets": [5], "visible": true,},
        // {"targets": [6], "visible": true,},
        // // {"targets": [7], "visible": true,},
        // // {"targets": [8], "visible": true,},
        // // {"targets": [9], "visible": true,},
        // // {"targets": [10], "visible": true,},
        //
        // {responsivePriority: 1, targets: 0},
        // {responsivePriority: 2, targets: 1},
        // {responsivePriority: 3, targets: 2},
        // {responsivePriority: 4, targets: 3},
    ];

    // START - Tool tips

    // tool tips - two group stuff
    let page_omic_upload_omic_file_format_deseq2_log2fc_headers = '"name", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"';
    let page_omic_upload_omic_file_format_deseq2_log2fc_tooltip = 'For DESeq2 Log2Fold change data, the header "log2FoldChange" must be in the first row. Other optional columns headers are: "baseMean", "lfcSE", "stat", "pvalue", "padj", and "gene reference" (or "name" or "gene").';
    $('#omic_file_format_deseq2_log2fc_tooltip').next().html($('#omic_file_format_deseq2_log2fc_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_deseq2_log2fc_tooltip));
    let page_omic_anaylsis_method_tooltip = 'The method (i.e. data processing tool, pipeline, etc.) used to process data.';
    $('#omic_anaylsis_method_tooltip').next().html($('#omic_anaylsis_method_tooltip').next().html() + make_escaped_tooltip(page_omic_anaylsis_method_tooltip));

    // tool tips - indy-sample stuff
    let page_count_files = 'Counts data files must have one header row labeled "Sample ID" with each column labeled with a sample ID and the sample ID must match, EXACTLY, what is provided in the metadata table.  ';
    let page_omic_upload_omic_file_format_normcounts_tooltip = 'Under Development - ' + page_count_files;
    $('#omic_file_format_normcounts_tooltip').next().html($('#omic_file_format_normcounts_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_normcounts_tooltip));
    let page_omic_upload_omic_file_format_rawcounts_tooltip = 'Under Development - ' + page_count_files;
    $('#omic_file_format_rawcounts_tooltip').next().html($('#omic_file_format_rawcounts_tooltip').next().html() + make_escaped_tooltip(page_omic_upload_omic_file_format_rawcounts_tooltip));
    let page_drag_action_tooltip = 'Copy will copy and paste that selected value. Increment will add the indicated amount to the cells (note: for text field, will attempt to find a string+value, if found, will increment the value only, if not found, will treat all entered as a string and will add a value starting from 1).  ';
    $('#drag_action_tooltip').next().html($('#drag_action_tooltip').next().html() + make_escaped_tooltip(page_drag_action_tooltip));
    let page_drag_use_tooltip = 'Select what to do to the highlighted cells.';
    $('#drag_use_tooltip').next().html($('#drag_use_tooltip').next().html() + make_escaped_tooltip(page_drag_use_tooltip));
    let page_sample_name_tooltip = 'The header of this sample data in the upload file.';
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

    // END - Tool tips

    // Set the required-ness of the groups on load based on data type on load
    changed_something_important("load");
    // some additional load functions that need to be run
    // indy sample functions
    number_samples_show_hide();

    if (page_omic_upload_check_load === 'review') {
        page_omic_upload_called_from_in_js_file = 'load-review';
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    } else {
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
        }
    }

    // START pre indy-sample general and two group stuff
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
    document.getElementById("fileFileFormatTwoGroup").addEventListener("click", function(){
    // Start the download_two_group_example of yournewfile.csv file with the content from the text area
        // could tie this to selections in the GUI later, if requested.
        // change with tool tip
        var text = page_omic_upload_omic_file_format_deseq2_log2fc_headers;
        var filename = "TwoGroupDESeq2Omic.csv";

        download_two_group_example(filename, text);
    }, false);

    // END pre indy-sample general and two group stuff

    // START added during indy-sample development click and change etc

    $('#id_indy_number_of_samples').on('change', function (e) {
        number_samples_show_hide();
        indyCalledToMakeTheAnEmptyTableOfXrows();
    });

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
        $('.special-selected1').removeClass('special-selected1')
        $('.special-selected2').removeClass('special-selected2')
        whatIsCurrentlyHighlightedInTheIndyTable();
    });

    // a default is not set in the html file, so, user has to pick one
    $("input[type='radio'][name='radio_change_drag_action']").click(function () {
        // check to see if any cells in the table have been highlighted
        if ($('.special-selected1').length > 0) {
            page_drag_action = $(this).val();
            sample_metadata_replace_show_hide();
        } else {
            page_drag_action = null;
            sample_metadata_replace_show_hide();
            alert("Drag over cells to highlight before selecting an Action.\n");
        }
    });

    $(document).on('click', '#indy_instructions', function() {
        $('.indy-instructions').toggle();
    });

    $(document).on('click', '#replace_in_indy_table', function() {
        indyCalledToReplace();
    });

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

    // END added during indy-sample development click and change etc


    // START - All Functions section

    // START section for preview page of the log2 fold change visualizations
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
    // END section for preview page of the log2 fold change visualizations

    // Other Functions

    // Called from a variety of places, including load, to set the right visibilities based on the data type
    // and to call all the downstream functions needed depending on data type and how/when called
    function changed_something_important(called_from) {

        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {

            // $('.two-group').show();
            // $('.one-group').show();
            $('.compare-group').show();
            $('.indy-sample').hide();

            // stuff for the two group fields
            $('#id_group_1').next().addClass('required');
            $('#id_group_2').next().addClass('required');

            if (called_from != 'load') {
                //this preview is specific for the log2 fold change data...will need something different for counts data
                get_data_for_this_file_ready_for_preview(called_from)
            }

        } else {

            // $('.one-group').hide();
            // $('.two-group').hide();
            $('.compare-group').hide();
            $('.indy-sample').show();

            // setting some of the inside classes to hidden
            $('.number-samples').hide();
            $('.increment-section').hide();
            $('.indy-instructions').hide();

            //stuff for the two group fields - make sure some fields are empty
            page_make_the_group_change = false;
            $('#id_group_1')[0].selectize.setValue('not-full');
            $('#id_group_2')[0].selectize.setValue('not-full');
            page_make_the_group_change = true;

            $('#id_location_1')[0].selectize.setValue('not-full');
            $('#id_time_1_day').val(0);
            $('#id_time_1_hour').val(0);
            $('#id_time_1_minute').val(0);
            page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];


            $('#id_location_2')[0].selectize.setValue('not-full');
            $('#id_time_2_day').val(0);
            $('#id_time_2_hour').val(0);
            $('#id_time_2_minute').val(0);
            page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];

            sample_metadata_replace_show_hide();
            // do this the first time called 
            // this should be the first time it is called, either by load or change data type
            if (!page_metadata_lod_done) {
                // need to load metadata_lod the first time
                metadata_lod = JSON.parse($('#id_indy_list_of_dicts').val());
                metadata_lod_current_index = 0;
                metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
                page_metadata_lod_done = true;
            }
            indySampleMetadataCallBuildAndPost();
        }
    }

    // https://www.bitdegree.org/learn/best-code-editor/javascript-download-example-1
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

     /**
      * When the number of indy samples is > 0
    */
    function number_samples_show_hide() {
        if ($('#id_indy_number_of_samples').val() > 0) {
            $('.number-samples').hide();
        } else {
            $('.number-samples').show();
        }
    }

    function sample_metadata_replace_show_hide() {
        //options are replace, empty, copys, pastes
        $('.replace-section').hide();
        $('.empty-section').hide();
        $('.copys-section').hide();
        $('.pastes-section').hide();

        if (!page_drag_action) {
            $('#radio_replace').prop('checked', false);
            $('#radio_empty').prop('checked', false);
            $('#radio_copys').prop('checked', false);
            $('#radio_pastes').prop('checked', false);
        } else
        if (page_drag_action === 'replace') {
            $('.special-selected2').removeClass('special-selected2');
            $('.replace-section').show();
        } else if (page_drag_action === 'empty') {
            $('.special-selected2').removeClass('special-selected2');
            $('.empty-section').show();
            indyCalledToEmpty();
        } else if (page_drag_action === 'copys') {
            $('.special-selected2').removeClass('special-selected2');
            $('.copys-section').show();
        } else if (page_drag_action === 'pastes') {
            $('.pastes-section').show();
        } else {
            // console.log("no selection");
        }
    }

    function indyUndoRedoButtonVisibilityCheck() {
        var current_length_list = metadata_lod_cum.length;
        // should a button show after whatever change brought you here
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
        whatIsCurrentlyHighlightedInTheIndyTable();
        //todo make the form field what is curently in the table!!!IMPORTANT!!!
    }

    // START - The functions that change the indy sample metadata table

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
        var thisRow = $(thisButton).attr("row-index");
        var thisRowMinusHeader = thisRow-1;

        //    todo - need to think about and plan for the pk in addition to the name of the chip and of the location!
        var dictrow = metadata_lod[thisRowMinusHeader];
        if (dictrow['sample_name'].length > 0) {
            // check the row to see if it has a field header
            $('#id_indy_sample_metadata_table_was_changed').attr('checked', true);
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked', true);
        } else {
            // check the row to see if the whole row is empty
            $.each(indy_keys, function (index, ikey) {
                if (include_header_in_indy_table[index] === 1) {
                    if (dictrow[ikey].length > 0) {
                        $('#id_indy_sample_metadata_table_was_changed').attr('checked', true);
                    }
                }
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
        $('#id_indy_number_of_samples').val(metadata_lod.length);
        number_samples_show_hide();
    }

    // ~~ Make a bunch of empty rows when sample row number is changed
    function indyCalledToMakeTheAnEmptyTableOfXrows() {
        // in the first make of the empty table, all rows will be empty, so, not data change occurred
        // if rows were deleted until there were none, so that this option was available, the flags should have been flipped aready
        //     $('#id_indy_sample_metadata_table_was_changed').attr('checked',true);
        //     $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',true);
        if (metadata_lod.length === 0) {
            var i;
            for (i = 0; i < $('#id_indy_number_of_samples').val(); i++) {
                var dict = {};
                $.each(indy_keys, function (index, ikey) {
                    if (include_header_in_indy_table[index] === 1) {
                        dict[ikey] = null;
                    }
                });
                metadata_lod.push(dict);
            }
            metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
            metadata_lod_current_index = metadata_lod_cum.length - 1;
            indySampleMetadataCallBuildAndPost();
            $('#id_indy_number_of_samples').val(metadata_lod.length);
            number_samples_show_hide();
        } else {
            alert('Selecting the number of rows is only allowed when the table is empty.')
        }
    }

    // ~~ The radio button change or change plus the go button/drag
    function indyCalledToPastes() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        // todo get the correct metadata_lod
        sameChangesToTableFromEmptyReplaceGoAndPaste();

    }
    
    function indyCalledToReplace() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();

        // change the content of the cell with what is in the selections
        // this is just a start, need to figure out how to get and add the names and pks!
        var index = 0;
        for (index = 0; index < metadata_highlighted_content.length; index++) {
            var tirow = metadata_highlighted_tirow[index];
            var tikey = metadata_highlighted_tikey[index];
            // do not forget to subtract the header row
            // this is the copy
            metadata_lod[tirow-1][tikey] = $('#'+ikey_to_html_replace[tikey]).val();
            // todo build the increment
            // todo
        }
        sameChangesToTableFromEmptyReplaceGoAndPaste();
    }

    function indyCalledToEmpty() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        // just change the content of the cell
        var index = 0;
        for (index = 0; index < metadata_highlighted_content.length; index++) {
            var tirow = metadata_highlighted_tirow[index];
            var tikey = metadata_highlighted_tikey[index];
            // do not forget to subtract the header row
            metadata_lod[tirow-1][tikey] = '';
        }
        sameChangesToTableFromEmptyReplaceGoAndPaste();
    }

    function sameFrontMatterToTableFromEmptyReplaceGoAndPaste() {
        whatIsCurrentlyHighlightedInTheIndyTable();
        $('#id_indy_sample_metadata_table_was_changed').attr('checked',true);

        if (metadata_highlighted_tikey.indexOf('sample_name') >= 0) {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',true);
        } else {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',false);
        }
    }

    function sameChangesToTableFromEmptyReplaceGoAndPaste() {
        metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
        metadata_lod_current_index = metadata_lod_cum.length - 1;
        indySampleMetadataCallBuildAndPost();
        $('#id_indy_number_of_samples').val(metadata_lod.length);
    }

    function whatIsCurrentlyHighlightedInTheIndyTable() {
        metadata_highlighted_tirow = [];
        metadata_highlighted_ticol = [];
        metadata_highlighted_tikey = [];
        metadata_highlighted_content = [];
        $('.special-selected1').each(function() {
            metadata_highlighted_tirow.push($(this).attr("row-index"));
            metadata_highlighted_ticol.push($(this).attr("col-index"));
            metadata_highlighted_tikey.push($(this).attr("ikey"));
            metadata_highlighted_content.push($(this).val());
        });
        // a special check to grey out replace content if field not in the ikey list that has a dom element
        for (var ikey in ikey_to_html_replace) {
            if (metadata_highlighted_tikey.indexOf(ikey) >= 0) {
                $('#'+ikey_to_html_replace[ikey]).addClass('required');
            } else {
                $('#'+ikey_to_html_replace[ikey]).removeClass('required');
            }
        }
    }

    // END - The functions that change the indy table
    
    function selectableDragOnSampleMetadataTable() {
        if (page_drag_action === 'pastes') {
            $('.special-selected2').removeClass('special-selected2');
            // want to highlight from the first location, so, want only the first one
            var icount = 0;
            $('.ui-selected').each(function() {
                if (icount === 0) {
                    $(this).addClass('special-selected2');                    
                }
                $(this).removeClass('ui-selected');
                icount = icount + 1;
            }); 
            indyCalledToPastes();
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

    function buildSampleMetadataTable() {

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
            ikey = indy_keys[h_index];
            if (include_header_in_indy_table[h_index] === 1) {
                if (header.includes('ption')) {
                    if (page_omic_upload_check_load === 'add' || page_omic_upload_check_load === 'update') {
                        var th = document.createElement('TH');
                        $(th).attr('hcol-index', hcolcounter);
                        $(th).attr('ikey', ikey);
                        th.appendChild(document.createTextNode(header));
                        tr.appendChild(th);
                        hcolcounter = hcolcounter + 1;
                    }
                } else {
                    var th = document.createElement('TH');
                    $(th).attr('hcol-index', hcolcounter);
                    $(th).attr('ikey', ikey);
                    // this was how did with plate....$(th).html(colnumber + top_label_button);
                    th.appendChild(document.createTextNode(header));
                    tr.appendChild(th);
                    hcolcounter = hcolcounter + 1;
                }
            }
        });
        myTable.appendChild(tableHead);

        var tableBody = document.createElement('TBODY');
        //the header row is 0, to keep consistent, start with 1, but watch when using the lod's
        var rowcounter = 1;

        $.each(metadata_lod, function (r_index, row) {

            var tr = document.createElement('TR');
            $(tr).attr('row-index', rowcounter);
            tableBody.appendChild(tr);

            let colcounter = 0;
            let myCellContent = '';

            $.each(indy_keys, function (c_index, ikey) {
                if (include_header_in_indy_table[c_index] === 1) {
                    var td = document.createElement('TD');
                    $(td).attr('col-index', colcounter);
                    $(td).attr('row-index', rowcounter);
                    $(td).attr('id-index', rowcounter * metadata_headers.length + colcounter);
                    $(td).attr('ikey', ikey);

                    if (ikey.includes('ption') && colcounter === 0) {
                        if (page_omic_upload_check_load === 'add' || page_omic_upload_check_load === 'update') {
                            var side_label_button =
                                ' <a class="add_indy_row" id="add_indy_row' + rowcounter
                                + '" row-index="' + rowcounter
                                + '" class="btn btn-sm btn-primary">'
                                // + 'duplicate'
                                + '<span class="glyphicon glyphicon-duplicate" aria-hidden="true"></span>'
                                + ' </a>'
                            +
                                ' <a class="delete_indy_row" id="delete_indy_row' + rowcounter
                                + '" row-index="' + rowcounter
                                + '" class="btn btn-sm btn-primary">'
                                // + 'duplicate'
                                + '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>'
                                + ' </a>'
                            $(td).html(side_label_button);
                            tr.appendChild(td);
                        }
                    } else {
                        // if ($("#check_load").html().trim() === 'review') {
                            td.appendChild(document.createTextNode(row[ikey]));
                            $(td).attr('class', 'no-wrap');
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

        myTable.appendChild(tableBody);
        myTableDiv.appendChild(myTable);

        // When I did not have the var before the variable name, the table headers acted all kinds of crazy
        var sampleDataTable = $('#'+sample_metadata_table_id).removeAttr('width').DataTable({
            // "iDisplayLength": 100,
            paging:         false,
            "sDom": '<B<"row">lfrtip>',
            //do not do the fixed header here...only want for two of the tables
            //https://datatables.net/forums/discussion/30879/removing-fixedheader-from-a-table
            //https://datatables.net/forums/discussion/33860/destroying-a-fixed-header
            fixedHeader: {headerOffset: 50},
            // responsive: true,
            "order": table_order,
            "columnDefs": table_column_defs,
            // fixedColumns: true
            "autoWidth": true
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
