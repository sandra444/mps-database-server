//GLOBAL-SCOPE
window.OMICS = {
    draw_plots: null,
    omics_data: null
};

// todo - phase ????  - make it so that the user can overwrite a previous rather than this (this will be complicated)
// todo - as keep building, make sure model form fields in updates are not getting overwritten by form initialization or here

$(document).ready(function () {
    //show the validation stuff
    $('#form_errors').show()

    // Load core chart package
    google.charts.load('current', {'packages': ['corechart']});
    google.charts.load('visualization', '1', {'packages': ['imagechart']});

    let page_omic_upload_called_from_in_js_file = 'add';
    let page_omic_upload_check_load = $('#check_load').html().trim();

    // two group stuff
    // when called from a group change, need to know if 1 or 2 was changed
    let page_omic_upload_group_id_change = 0;
    // what is the pk, of the treatment group in the database of the changed group
    let page_omic_upload_group_pk_change = 0;

    // let page_omic_upload_group_id_load_1 = 0;
    let page_omic_upload_group_pk_load_1 = 0;
    // let page_omic_upload_group_id_load_2 = 0;
    let page_omic_upload_group_pk_load_2 = 0;   
    
    let page_omic_current_group1 = $('#id_group_1')[0].selectize.items[0];
    let page_omic_current_group2 = $('#id_group_2')[0].selectize.items[0];

    let page_make_the_group_change = true;

    // when visible, they are required, make them yellow
    $('#id_group_1').next().addClass('required');
    $('#id_group_2').next().addClass('required');
    $('#id_location_1').next().addClass('required');
    $('#id_location_2').next().addClass('required');
    //at least one is required, so, randomly chose to make the day yellow
    $('#id_time_1_day').addClass('required');
    $('#id_time_2_day').addClass('required');

    // just working variables, but want in different subs, so just declare here
    var current_pk = 0;
    var current_val = '';

    // START - Tool tips
    // tool tips - two group stuff - all moved to help_text (at least, for now)
    // END - Tool tips

    // todo - check about double or single quotes
    let page_omic_upload_omic_file_format_deseq2_log2fc_headers = '"name", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"';

    // Some more load things Section
    changed_something_important('load');
    change_visibility_of_some_doms();

    if (page_omic_upload_check_load === 'review') {
        page_omic_upload_called_from_in_js_file = 'load-review';
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    } else {
        // page_omic_upload_group_id_load_1 = 1;
        page_omic_upload_group_pk_load_1 = $('#id_group_1')[0].selectize.items[0];
        // page_omic_upload_group_id_load_2 = 2;
        page_omic_upload_group_pk_load_2 = $('#id_group_2')[0].selectize.items[0];

        if (page_omic_upload_check_load === 'add') {
            page_omic_upload_called_from_in_js_file = 'load-add';
            get_group_sample_info('load-add');
        } else {
            page_omic_upload_called_from_in_js_file = 'load-update';
            get_group_sample_info('load-update');
            //do not allow changing of data type after a valid submit and save - user has to delete and then add back
            //todo-decide if want to allow or not...
            // $('#id_data_type')[0].selectize.disable();
        }
    }

    // START - General and two group stuff (written during log2fold change)
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
    $('#omicPreviewTheCompareGraphsButton').click(function () {
        $('#omic_preview_compare_graphs_section').toggle();
        $('#omic_preview_compare_graphs_section2').toggle();
    });
    /**
     * On click to toggle
    */
    // the graph sections
    $('#omicPreviewTheCountGraphsButton').click(function () {
        $('#omic_preview_count_graphs_section').toggle();
        $('#omic_preview_count_graphs_section2').toggle();
    });
    /**
     * On change data file
    */
    $('#id_omic_data_file').on('change', function (e) {
        clear_validation_errors();
        //when first change the file, make the preview button available
        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('#omic_preview_compare_button_section').show();
            $('#omic_preview_compare_graphs_section').show();
            $('#omic_preview_compare_graphs_section2').show();
        } else {
            $('#omic_preview_compare_button_section').hide();
            $('#omic_preview_compare_graphs_section').hide();
            $('#omic_preview_compare_graphs_section2').hide();
        }
        changed_something_important('data_file');
    });
    /**
     * On change data type, change what is required page logic
    */
    $('#id_data_type').change(function () {
        clear_validation_errors();
        change_visibility_of_some_doms();
        changed_something_important('data_type');
    });
    function change_visibility_of_some_doms() {
        $('#log2fc_template_section').hide();
        $('#normcounts_template_section').hide();
        $('#rawcounts_template_section').hide();
        $('#group_extra').hide();
        $('#count_extra').hide();

        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('#log2fc_template_section').show();
            $('#group_extra').show();
        } else {

            if ($('#id_data_type')[0].selectize.items[0] == 'rawcounts') {
               $('#rawcounts_template_section').show();
            } else {
               $('#normcounts_template_section').show();
            }
            $('#count_extra').show();
        }
    }
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
                // $('#id_group_1')[0].selectize.setValue(page_omic_current_group1);
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
                // $('#id_group_2')[0].selectize.setValue(page_omic_current_group2);
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
                        let omics_file_id_to_name_all = window.OMICS.omics_data['file_id_to_name'];
                        let omics_file_id_to_name = omics_file_id_to_name_all[1];
                        let error_message =  window.OMICS.omics_data['error_message'];

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
                            // todo need to coordinate with Quinn for the counts data preview

                        }
                        // put here to avoid race errors
                        if (called_from == 'data_file' || called_from == 'data_type') {
                            try {
                                let id_omic_data_file = $('#id_omic_data_file').val();
                                check_file_add_update_ajax_sub(id_omic_data_file);
                            } catch {
                            }
                            let a_new_message = error_message
                            if (error_message.trim().length > 0) {
                                a_new_message = 'Error Message: ' + error_message.trim().length
                            }
                            $('#error_message_compare').text(a_new_message);
                            $('#error_message_counts').text(a_new_message);

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
    // and to call all the downstream functions needed depending on data type and how/when called
    function changed_something_important(called_from) {
        // could make this so it only checks if the data_type was changed, but it is okay this way, so leave it
        if ($('#id_data_type')[0].selectize.items[0] == 'log2fc') {
            $('.compare-group').show();
            $('.counts-data').hide();
        } else {
            $('.compare-group').hide();
            $('.counts-data').show();

            //stuff for the two group fields - make sure some fields are empty so not saved in upload table
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

     /**
      * When a group is changed, if that group has already been added to the data upload file
      * get the first occurrence of this group's sample information from the upload file table.
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
            call: 'fetch_omic_sample_info_first_found_in_upload_file_table',
            called_from: page_omic_upload_called_from_in_js_file,
            group_pkc: page_omic_upload_group_pk_change,
            group_pk1: page_omic_upload_group_pk_load_1,
            group_pk2: page_omic_upload_group_pk_load_2,
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

            // this is where the sub list of sample locations is brought back and used
            let $this_dropdown1 = $(document.getElementById('id_location_1'));
            $this_dropdown1.selectize()[0].selectize.clearOptions();
            let this_dict1 = $this_dropdown1[0].selectize;
            // fill the dropdown with what brought back from ajax call
            $.each(json.location_dict1[0], function( pk, text ) {
                // console.log('1 '+pk+ '  '+text)
                this_dict1.addOption({value: pk, text: text});
            });

            // this is where the sub list of sample locations is brought back and used
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
    function check_file_add_update_ajax_sub(id_omic_data_file) {
        if ($('#check_load').html().trim() === 'add') {
            data_file_pk = 0;
        } else {
            parseInt(document.getElementById('this_file_id').innerText.trim())
        }
        let data = {
            call: 'fetch_this_file_is_this_study_omic_upload_file',
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
                        $('#error_message_compare').text('Warning: '+ json.message);
                        $('#error_message_counts').text('Warning: '+ json.message);
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

    // END - All Functions section

});
