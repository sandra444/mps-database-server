$(document).ready(function () {
    
    // START do on load

    //show the validation stuff
    $('#form_errors').show();

    // there will only be upload and review, not add (add is a special case of update handled by the forms.py!)
    let page_omic_metadata_check_load = $('#check_load').html().trim();

    // indy sample stuff
    var sample_metadata_table_id = 'sample_metadata_table';

    // make sure to update this as needed (to match what comes from utils.py)
    var indy_row_label = 'Sample Label'

    var code_of_the_sample_pattern = '';

    var indy_list_of_dicts_of_table_rows = JSON.parse($('#id_indy_list_of_dicts_of_table_rows').val());
    var indy_list_of_column_labels = JSON.parse($('#id_indy_list_of_column_labels').val());
    var indy_list_of_column_labels_show_hide = JSON.parse($('#id_indy_list_of_column_labels_show_hide').val());
    var indy_matrix_item_list = JSON.parse($('#id_indy_matrix_item_list').val());
    var indy_list_columns_hide = [];
    var indy_list_time_units_to_include_initially = JSON.parse($('#id_indy_list_time_units_to_include_initially').val());
    var indy_dict_time_units_to_table_column = JSON.parse($('#id_indy_dict_time_units_to_table_column').val());

    findTheTimeUnitsThatShouldBeInTheTableAndAsDefault();
    var page_radio_time_value = $("input[type='radio'][name='radio_time_unit']:checked").val();

    // Prepare and build the table on load
    // the current one
    var metadata_lod = indy_list_of_dicts_of_table_rows;
    // version number aka current index - is the current one (should be 1, 2, 3, 4, or 5 after first population)
    var metadata_lod_current_index = 0;
    //for holding versions to allow for undo and redo
    var metadata_lod_cum = [];
    metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
    //the table info that is highlighted
    var metadata_highlighted = [];
    var list_of_fields_for_replacing_that_are_highlighted = [];
    var icol_last_highlighted_seen = {};

    // just working variables, but want in different subs, so just declare here
    var current_pk = 0;
    var current_val = '';
    var page_paste_cell_irow = null;
    var page_paste_cell_icol = null;

    var indy_table_order = [];
    var indy_table_column_defs = [{bSortable: false, targets: [5 ,]},
        {'targets': indy_list_columns_hide, 'visible': false,},
    ];
    // indy_table_column_defs = [{bSortable: false, targets: [1,]}];
        // { 'width': '20%' },
        // { width: 200, targets: 0 }
        // {'targets': [0], 'visible': true,},
        // {'targets': [1], 'visible': true,},
        // {responsivePriority: 1, targets: 0},
        // {responsivePriority: 2, targets: 1},

    // make a cross reference to the html dom name of the content box
    // make a cross reference to the html of the content box
    // note: the column header is an attribute of the cells in the indy table
    // and the key of these to dicts is the column header
    // e.g. col-label='Chip or Well Name'
    var icol_to_html_outer = {};
    var icol_to_html_element = {};
    // Note that these keys are hardcoded to columns headers or metadata labels
    // todo check these for new ones...not sure they are correct
    icol_to_html_outer['Chip/Well Name'] = 'h_indy_matrix_item';
    icol_to_html_element['Chip/Well Name'] = 'matrix_item_name';
    icol_to_html_outer['Sample Location'] = 'h_indy_sample_location';
    icol_to_html_element['Sample Location'] = 'sample_location_name';
    icol_to_html_outer['Sample Time (Day)'] = 'h_indy_time_day';
    icol_to_html_element['Sample Time (Day)'] = 'time_day';
    icol_to_html_outer['Sample Time (Hour)'] = 'h_indy_time_hour';
    icol_to_html_element['Sample Time (Hour)'] = 'time_hour';
    icol_to_html_outer['Sample Time (Minute)'] = 'h_indy_time_minute';
    icol_to_html_element['Sample Time (Minute)'] = 'time_minute';

    if (page_omic_metadata_check_load === 'review') {
        // HANDY - to make everything on a page read only (for review page)
        $('.selectized').each(function() { this.selectize.disable() });
        $(':input').attr('disabled', 'disabled');
    }

    // has a default in html page
    var page_radio_duplicate_value = $("input[type='radio'][name='radio_change_duplicate_increment']:checked").val();
    var page_drag_action = $("input[type='radio'][name='radio_change_drag_action']:checked").val();

    //set the visibility based on default form selections (as set in the html)
    radioDuplicateVisibility();
    radioActionVisibility();
    radioTimeVisibility();
    goBuildSampleMetadataTable();
    postBuildSampleMetadataTable();
    
    // END do on load

    // START clicks and changes section
    $(document).on('click', '#undoIndyButton', function() {
        indyClickedToUndoRedoChangeToTable('undo');
    });
    $(document).on('click', '#redoIndyButton', function() {
        indyClickedToUndoRedoChangeToTable('redo');
    });
    
    $(document).on('click', '#clearHighlightingButton', function() {
        $('.special-selected1').removeClass('special-selected1');
        whatIsCurrentlyHighlightedInTheIndyTable();
    });

    $(document).on('click', '#highlightAllSampleLabelsButton', function() {
        $('.special-label-td').addClass('special-selected1');
        whatIsCurrentlyHighlightedInTheIndyTable();
    });

    $("input[type='radio'][name='radio_change_duplicate_increment']").click(function () {
        page_radio_duplicate_value = $(this).val();
        radioDuplicateVisibility();
    });

    $("input[type='radio'][name='radio_change_drag_action']").click(function () {
        page_drag_action = $(this).val();
        radioActionVisibility();
    });

    $("input[type='radio'][name='radio_time_unit']").click(function () {
        page_radio_time_value = $(this).val();
        radioTimeVisibility();
        changeListThatGovernsOmitsForTheTimesInTable();
        goBuildSampleMetadataTable();
        postBuildSampleMetadataTable();
    });

    $(document).on('click', '#replaceInTableButton', function() {
        indyCalledToReplace();
    });
    $(document).on('click', '#clearInTableButton', function() {
        indyCalledToClear();
    });
    $(document).on('click', '#deleteInTableButton', function() {
        indyCalledToDelete();
    });
    $(document).on('click', '#pastesInTableButton', function() {
        indyCalledToPastes();
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

    // just need the pattern so know how to populate when highlighted and clicked
    $(document).on('change', '#id_indy_sample_label', function() {
        code_of_the_sample_pattern = $('#id_indy_sample_label').children('option:selected').val();
    });

    // when the user changes a sample label using the input instead of a pattern
    // they would need to do this for replicates to change them
    $(document).on('focusout', '.special-label', function (e) {
        let what_cell_changed = $(this);
        // console.log(what_cell_changed)
        let this_row_index = what_cell_changed.attr("row-index");
        let this_col_index = what_cell_changed.attr("col-index");
        //this assumes all the columns are included in the table - BE CAREFUL with that
        metadata_lod[this_row_index-1][indy_row_label] = what_cell_changed.val();
        pushToMetadataLodCum();
        checkUndoRedoButtonVisibility();
        // note that, we do NOT need to redraw the table for this
        // do need to write back to the form field
        $('#id_indy_list_of_dicts_of_table_rows').val(JSON.stringify(metadata_lod));
    });

    // END clicks and changes section


    // START - All Functions section

    function radioDuplicateVisibility() {
        $('.increment-section').hide();
        if (page_radio_duplicate_value === 'increment') {
            $('.increment-section').show();
        }
    }

    function radioActionVisibility() {
        $('.empty-section').hide();
        $('.pastes-section').hide();
        $('.delete-section').hide();
        $('.replace-section').hide();

        if (page_drag_action === 'pastes') {
            $('.pastes-section').show();
        } else if (page_drag_action === 'empty') {
            $('.empty-section').show();
        } else if (page_drag_action === 'delete') {
            $('.delete-section').show();
        } else if (page_drag_action === 'replace') {
            $('.replace-section').show();
        }
    }

    function radioTimeVisibility() {
        $('#h_indy_time_day').hide();
        $('#h_indy_time_hour').hide();
        $('#h_indy_time_minute').hide();

        if (page_radio_time_value === 'day') {
            $('#h_indy_time_day').show();
            $('#sample_time_label').text('Sample Time (Day)');
        } else if (page_radio_time_value === 'hour') {
            $('#h_indy_time_hour').show();
            $('#sample_time_label').text('Sample Time (Hour)');
        } else if (page_radio_time_value === 'minute') {
            $('#h_indy_time_minute').show();
            $('#sample_time_label').text('Sample Time (Minute)');
        } else {
            $('#sample_time_label').text('?');
        }
    }

    function checkUndoRedoButtonVisibility() {
        var current_length_list = metadata_lod_cum.length;
        // should a button (undo or redo) show after whatever change brought you here
        if (metadata_lod_current_index > 0) {
            // yes, can undo another time
            $('#undoIndyButton').show();
        } else {
            $('#undoIndyButton').hide();
        }

        if (metadata_lod_current_index < current_length_list-1) {
            // yes, can undo another time
            $('#redoIndyButton').show();
        } else {
            $('#redoIndyButton').hide();
        }
    }

    /**
     * When this page opens, there is a list sent back that has
     * units that should be displayed in the table
     * and a dictionary with the unit and the column number in the table
     * this pushing both to the utils.py 
    */
    function findTheTimeUnitsThatShouldBeInTheTableAndAsDefault() {
        // set default unit based on what IS in the units initially from utils.py
        $('#radio_minute').prop('checked', true);
        if (indy_list_time_units_to_include_initially.indexOf('day') > -1) {
            $('#radio_day').prop('checked', true);
        } else if (indy_list_time_units_to_include_initially.indexOf('hour') > -1) {
            $('#radio_hour').prop('checked', true);
        }
        page_radio_time_value = $("input[type='radio'][name='radio_time_unit']:checked").val();

        let obj = indy_dict_time_units_to_table_column;
        Object.keys(obj).forEach(function(key) {
           // console.log(key + " " + obj[key]);
           if (indy_list_time_units_to_include_initially.indexOf(key) < 0) {
                indy_list_columns_hide.push(obj[key])
           }
        });
    }
    
    function changeListThatGovernsOmitsForTheTimesInTable () {
        // this will ONLY make a column visible, it will NOT hide a column
        // This happens when the user changes the selection of the time unit in the replace content section
        // get the column number from the unit
        let obj = indy_dict_time_units_to_table_column;
        let num_in_list = obj[page_radio_time_value];
        // if it is in the list to hide in the table, remove it
        const index = indy_list_columns_hide.indexOf(num_in_list);
        if (index > -1) {
          indy_list_columns_hide.splice(index, 1);
        }
    }





    function indyCallMultiFunctionUndoBuildPostUpdate() {
        checkUndoRedoButtonVisibility();
        goBuildSampleMetadataTable();
        postBuildSampleMetadataTable();
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
        //
        metadata_lod = JSON.parse(JSON.stringify(metadata_lod_cum[metadata_lod_current_index]));

        indyCallMultiFunctionUndoBuildPostUpdate();
    }

    //
    // function indyClickedAddOrDeleteRow(thisButton, add_or_delete) {
    //     var thisRow = $(thisButton).attr('row-index');
    //     var thisRowMinusHeader = thisRow-1;
    //
    //     var dictrow = metadata_lod[thisRowMinusHeader];
    //     if (dictrow['file_column_header'].length > 0) {
    //         // check the row to see if it has a field header

    //     } else {
    //         // check the row to see if the whole row is empty
    //         $.each(indy_list_of_column_labels, function (index, icol) {
    //             // do to all in the metadata_lod, not just the ones shown in the table, so, comment this out for now
    //             // if (include_header_in_indy_table[index] === 1) {
    //                 if (dictrow[icol].length > 0) {
    //
    //                 }
    //             // }
    //         });
    //     }
    //     if (add_or_delete === 'add') {
    //         metadata_lod.push(dictrow);
    //     } else {
    //         metadata_lod.splice(thisRowMinusHeader, 1);
    //     }
    //
    //     metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
    //     metadata_lod_current_index = metadata_lod_cum.length - 1;
    //     indyCallMultiFunctionUndoBuildPostUpdate();
    // }

    // ~~ The radio button change or change plus the go button/drag
    function indyCalledToPastes() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        indyCalledGutsPastes();
        pushToMetadataLodCum();
        indyCallMultiFunctionUndoBuildPostUpdate();
    }

    function indyCalledToClear() {
         // not going to allow this
        // function indyCalledToEmpty() {
        //     sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        //     // just change the content of the cell
        //     var index = 0;
        //     for (index = 0; index < metadata_highlighted.length; index++) {
        //         var tirow = metadata_highlighted[index]['metadata_highlighted_tirow'];
        //         var ticol = metadata_highlighted[index]['metadata_highlighted_ticol'];
        //         // do not forget to subtract the header row
        //         metadata_lod[tirow-1][ticol] = '';
        //         if (ticol === 'matrix_item_name') {
        //             metadata_lod[tirow-1]['matrix_item_pk'] = '';
        //         } else if (ticol === 'sample_location_name') {
        //             metadata_lod[tirow-1]['sample_location_pk'] = '';
        //         }
        //     }
        //     pushToMetadataLodCum();
        // indyCallMultiFunctionUndoBuildPostUpdate();
        // }
    }

    function indyCalledToDelete() {
    }

    function indyCalledToReplace() {
        sameFrontMatterToTableFromEmptyReplaceGoAndPaste();
        indyCalledGutsReplace();
        pushToMetadataLodCum();
        indyCallMultiFunctionUndoBuildPostUpdate();

        //todo need to reset the option boxes highlighting (what you are picking to use for the replace)
        //it is not resetting correctly
    }
    
    function indyCalledGutsPastes() {
        // pastes - column will stay the same, rows will change, but, remember that, rows might not be in order
            if (page_drag_action === 'pastes') {
                $("#radio_duplicate").prop("checked", true).trigger("click");
                tirow_in_metadata_lod = tirow - 1; //still working on this todo!!
            }  
    }  

    function indyCalledGutsReplace() {

        //code_of_the_sample_pattern = $('#id_indy_sample_label').children('option:selected').val();
        // sample_option_choices = (
        //     ('clt', 'Chip/Well - Location - Time'),
        //     ('sn1', 'Sample-1 to Sample-99999 etc'),
        //     ('sn2', 'Sample-01 to Sample-99'),
        //     ('sn3', 'Sample-001 to Sample-999'),
        // )


        // replace - has the increment option, but always replacing the same cell
        
        // because the pks are not in the table, they will not ever be highlighted
        // BUT, we want to keep them matching the names selected in the metadata_lod
        // so that, they are correct in the form field that is sent back
        // plan to check in the back end to make sure they went together
        // could remove the pks altogether, but, what if users decide want to see them.....       

        // find content of the replacement fields
        let current_matrix_item_name = $('#matrix_item_name').text();
        let current_matrix_item_pk = $('#matrix_item_pk').text();        
        let current_sample_location_name = $('#sample_location_name').text();
        let current_sample_location_pk = $('#sample_location_pk').text();
        let current_display_time = $('#time_display').val();

        // console.log("1 ",current_matrix_item_name)
        // console.log("1 ",current_matrix_item_pk)
        // console.log("1 ",current_sample_location_name)
        // console.log("1 ",current_sample_location_pk)
        // console.log("1 ",current_display_time)
        //
        // console.log("Before Duplicate  metadata_lod ")
        // console.log(metadata_lod)

        for (var index = 0; index < metadata_highlighted.length; index++) {
            // this index is the index of the array of highlighted cells

            // what is the row and column number of the attribute of the highlighted cell
            var tirow = metadata_highlighted[index]['metadata_highlighted_tirow'];
            var ticol = metadata_highlighted[index]['metadata_highlighted_ticol'];
            var tmeta = metadata_highlighted[index]['metadata_highlighted_meta_label'];
            var tlcol = metadata_highlighted[index]['metadata_highlighted_tlcol'];

            // what row of the metadata_lod is being changed?             

            // because we add a header row and, sometimes, an apply button row
            // depending on how add_apply_row_col_to_indy_table is set above
            // the index in the metadata_lod (list of dictionaries of each row of the table)
            // may be one or two less then the attribute of the highlighted cell
            // e.g. row-index of cell is 2, index in metadata_lod is 0
            // see utils.py find_the_labels_needed_for_the_indy_omic_table
            // note that, extra stuff in columns IS IN the metadata_lod
            // at lease for now, so no subtraction needed
            var ticol_in_metadata_lod = ticol;
            var tirow_in_metadata_lod = tirow - 1;
            if (add_apply_row_col_to_indy_table) {
                tirow_in_metadata_lod = tirow - 2;
            }

            // sample location can ONLY be duplicate!
            if (tmeta === 'Sample Location' || tlcol === 'Sample Location') {
                if (current_sample_location_name.length > 0) {
                    if ($('#id_header_type')[0].selectize.items[0] === 'well') {
                        metadata_lod[tirow_in_metadata_lod][tlcol] = current_sample_location_name;
                        metadata_lod[tirow_in_metadata_lod+3][tlcol] = current_sample_location_pk;
                    } else {
                        metadata_lod[tirow_in_metadata_lod]['Sample Location'] = current_sample_location_name;
                        metadata_lod[tirow_in_metadata_lod]['sample_location_pk'] = current_sample_location_pk;
                    }
                }
            } else {
                if (page_radio_duplicate_value === 'duplicate') {

                    if (tmeta === 'Sample Time' || tlcol === 'Sample Time') {
                        if (current_display_time.length > 0) {
                            if ($('#id_header_type')[0].selectize.items[0] === 'well') {
                                metadata_lod[tirow_in_metadata_lod][tlcol] = current_display_time;
                            } else {
                                metadata_lod[tirow_in_metadata_lod]['Sample Time'] = current_display_time;
                            }
                        }
                    } else if (tmeta === 'Chip/Well Name'  || tlcol === 'Chip/Well Name') {
                        if (current_matrix_item_name.length > 0) {
                            if ($('#id_header_type')[0].selectize.items[0] === 'well') {
                                metadata_lod[tirow_in_metadata_lod][tlcol] = current_matrix_item_name;
                                metadata_lod[tirow_in_metadata_lod+3][tlcol] = current_matrix_item_pk;
                            } else {
                                metadata_lod[tirow_in_metadata_lod]['Chip/Well Name'] = current_matrix_item_name;
                                metadata_lod[tirow_in_metadata_lod]['matrix_item_pk'] = current_matrix_item_pk;
                            }
                        }
                    }

                } else {
                    // an increment
                    // var current_index = icol_last_highlighted_seen[ticol_in_metadata_lod+'_index'];
                    //
                    // if (current_index === -99) {
                    //     // on the first one, it is a duplicate and change info for next
                    //     metadata_lod[tirow_in_metadata_lod][ticol_in_metadata_lod] = current_val;
                    //     if (ticol_in_metadata_lod === 'matrix_item_name') {
                    //         metadata_lod[tirow_in_metadata_lod]['matrix_item_pk'] = current_pk;
                    //     }
                    //     // update the last found object for next go
                    //     icol_last_highlighted_seen[ticol_in_metadata_lod] = current_val;
                    //     icol_last_highlighted_seen[ticol_in_metadata_lod + '_index'] = 0;
                    // } else {
                        // // not the first occurrence of this ticol_in_metadata_lod
                        // current_val = icol_last_highlighted_seen[ticol_in_metadata_lod];
                        //
                        // var i_current_val = 0;
                        // if (ticol_in_metadata_lod === 'time_display' || ticol_in_metadata_lod === 'time_hour' || ticol_in_metadata_lod === 'time_minute') {
                        //     if (page_radio_duplicate_value === 'increment-ttbltr' ||
                        //         page_radio_duplicate_value === 'increment-ttbrtl' ||
                        //         page_radio_duplicate_value === 'increment-ttbo'
                        //         ) {
                        //         // it is + for both because the holding dict was sorting descending
                        //         i_current_val = parseFloat(current_val) + parseFloat($('#increment_value').val());
                        //     } else {
                        //         alert('Make sure to select to duplicate or increment');
                        //     }
                        // } else if (ticol_in_metadata_lod === 'matrix_item_name') {
                        //     // find the index of the last one, increase the index, if not out of range, replace
                        //     var index_in_indy_matrix_item_list = indy_matrix_item_list.indexOf(current_val);
                        //     var new_index = index_in_indy_matrix_item_list + parseInt($('#increment_value').val());
                        //     if (index_in_indy_matrix_item_list >=0 && new_index < indy_matrix_item_list.length) {
                        //         i_current_val = indy_matrix_item_list[new_index];
                        //     } else {
                        //         i_current_val = current_val;
                        //     }
                        // } else if (ticol_in_metadata_lod === 'file_column_header') {
                        //     // find the index of the last one, increase the index, if not out of range, replace
                        //     // var index_in_indy_row_labels = indy_row_labels.indexOf(current_val);
                        //     // var new_index = index_in_indy_row_labels + parseInt($('#increment_value').val());
                        //     // if (index_in_indy_row_labels >=0 && new_index < indy_row_labels.length) {
                        //     //     i_current_val = indy_row_labels[new_index];
                        //     // } else {
                        //     //     i_current_val = current_val;
                        //     // }
                        // } else {
                        //     // todo well name still need an increment
                        //     // could i look from the right until finds first non number and split? - maybe a list? not sure yet..
                        //     // maybe string split the whole thing and index backards to first non number, then icrement the number
                        //     // could go back as string, but probably easier to work with list...think about
                        //         alert('Increment for this field is in development: '+ticol_in_metadata_lod);
                        //
                        // }
                        // var i_current_index = parseInt(icol_last_highlighted_seen[ticol_in_metadata_lod + '_index']) + 1;
                        // // update the last found object for next go
                        // icol_last_highlighted_seen[ticol_in_metadata_lod] = i_current_val;
                        // icol_last_highlighted_seen[ticol_in_metadata_lod + '_index'] = i_current_index;
                        // // update the correct location in the table metadata
                        // metadata_lod[tirow_in_metadata_lod][ticol_in_metadata_lod] = i_current_val;

                    // }
                }
            }
        }
    }

    function sameFrontMatterToTableFromEmptyReplaceGoAndPaste() {
        whatIsCurrentlyHighlightedInTheIndyTable();

        //todo not sure need this...check later
        if (list_of_fields_for_replacing_that_are_highlighted.indexOf('file_column_header') >= 0) {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',true);
        } else {
            $('#id_indy_sample_metadata_field_header_was_changed').attr('checked',false);
        }

        // for replace, increment is only available in the replace, but allow the resorting here
        //todo check this later
        var metadata_highlighted_temp = [];
        metadata_highlighted_temp = JSON.parse(JSON.stringify(metadata_highlighted));
        if (page_drag_action === 'replace') {
            if (page_radio_duplicate_value === 'increment-ttbltr' ||
            page_radio_duplicate_value === 'increment-ttbo') {
                // think should be in the order of the table, so, leave it as is
            } else if (page_radio_duplicate_value === 'increment-ttbrtl') {
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

    function pushToMetadataLodCum() {
        metadata_lod_cum.push(JSON.parse(JSON.stringify(metadata_lod)));
        metadata_lod_current_index = metadata_lod_cum.length - 1;
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

    // this is called when drag across the metadata table
    function selectableDragOnSampleMetadataTable() {
                //todo fix this...only allow time in unit showw in replace contetnt to be highlighted!!
        $('.ui-selected').each(function() {
            if ($(this).hasClass('special-selected1')) {
                $(this).removeClass('special-selected1');
            } else {
                $(this).addClass('special-selected1');
            }
            $(this).removeClass('ui-selected');
        });
        // if keep this updated, can turn the fields in the replace content section yellow with every change
        whatIsCurrentlyHighlightedInTheIndyTable();
    }

    function whatIsCurrentlyHighlightedInTheIndyTable() {
        // Made a test to see what is considered highlighted vrs visible
        // Found that, only what is highlighted and visible is changed
        // $(sample_metadata_table_id).DataTable().rows( { filter: 'applied' } ).every( function () {
        //     var row = this.data();
        //     console.log("###row ", row)
        // });

        metadata_highlighted = [];
        list_of_fields_for_replacing_that_are_highlighted = [];
        let index = 0;
        $('.special-selected1').each(function() {
            var dict_highlighted_indy_metadata = {};
            var imetadata_highlighted_tirow = $(this).attr('row-index');
            var imetadata_highlighted_ticol = $(this).attr('col-index');
            var imetadata_highlighted_tlcol = $(this).attr('col-label');
            var imetadata_highlighted_content = null;

            // since this goes through all the columns, they could be different types
            // try different ways of pulling the content, and
            // keep in mind that the content could actually be null
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

            //at this point, should have
            // console.log("###index ",index)
            // console.log("row i ",imetadata_highlighted_tirow)
            // console.log("col i ",imetadata_highlighted_ticol)
            // console.log("col l ",imetadata_highlighted_tlcol)
            // console.log("content ",imetadata_highlighted_content)

            //store in a dictionary
            dict_highlighted_indy_metadata['metadata_highlighted_tirow'] = imetadata_highlighted_tirow;
            dict_highlighted_indy_metadata['metadata_highlighted_ticol'] = imetadata_highlighted_ticol;
            dict_highlighted_indy_metadata['metadata_highlighted_tlcol'] = imetadata_highlighted_tlcol;
            dict_highlighted_indy_metadata['metadata_highlighted_content'] = imetadata_highlighted_content;
            //put in a list of dictionaries of what is highlighted
            metadata_highlighted.push(dict_highlighted_indy_metadata);
            list_of_fields_for_replacing_that_are_highlighted.push(imetadata_highlighted_tlcol);
            index = index + 1;
        });
        // a special check to turn replace content boxes yellow if one or more is highlighted in the table
        // e.g. if the user has highlighted one or more chips, turn chip/well name in the replace content yellow
        $('#h_indy_sample_location').removeClass('required');
        $('#h_indy_matrix_item').removeClass('required');
        $('#h_indy_sample_time').removeClass('required');
        $('#h_indy_time_day').removeClass('required');
        $('#h_indy_time_hour').removeClass('required');
        $('#h_indy_time_minute').removeClass('required');
        $('#h_indy_sample_name_options').removeClass('required');

        $.each(list_of_fields_for_replacing_that_are_highlighted, function (index, e) {
            if (e.indexOf('ocation') >= 0) {
                $('#h_indy_sample_location').addClass('required');
            } else if (e.indexOf('hip') >= 0) {
                $('#h_indy_matrix_item').addClass('required');
            } else if (e.indexOf('ime (D') >= 0) {
                $('#h_indy_sample_time').addClass('required');
            } else if (e.indexOf('ime (H') >= 0) {
                $('#h_indy_sample_time').addClass('required');
            } else if (e.indexOf('ime (M') >= 0) {
                $('#h_indy_sample_time').addClass('required');
            } else if (e.indexOf('abel') >= 0) {
                $('#h_indy_sample_name_options').addClass('required');
            }
        });

        // need for replace and pastes to keep track of last seen during the replace/pastes
        // costs a little extra to put here, but will always be ready
        icol_last_highlighted_seen = {};
        $.each(indy_list_of_column_labels, function (index, icol) {
            icol_last_highlighted_seen[icol] = '99';
            icol_last_highlighted_seen[icol+'_index'] = -99;
        });
    }

    function goBuildSampleMetadataTable() {
        // if there were errors and the user did something to change the table, hide the errors
        $('#form_errors').hide();

        var table = $('#' + sample_metadata_table_id).DataTable();
        var searchTerm = table.search();

        // build a table
        // set to the table div
        var elem = document.getElementById('div_for_' + sample_metadata_table_id);
        //remove an existing table
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

        $.each(indy_list_of_column_labels, function (i_index, colLabel) {
            // include in table or not: 1 is for include
            if (indy_list_of_column_labels_show_hide[i_index] === 1) {
                var th = document.createElement('TH');
                $(th).attr('col-index', colcounter);
                $(th).attr('row-index', rowcounter);
                $(th).attr('col-label', colLabel);
                th.appendChild(document.createTextNode(colLabel));
                tr.appendChild(th);
                colcounter = colcounter + 1;
            }
            // else, do not put in the table and do not increment the header counter
        });
        rowcounter = rowcounter + 1;

        tableHead.appendChild(tr);

        myTable.appendChild(tableHead);
        var tableBody = document.createElement('TBODY');

        colcounter = 0;
        let myCellContent = '';
        $.each(metadata_lod, function (i_index, row) {
            var tr = document.createElement('TR');
            $(tr).attr('row-index', rowcounter);
            tableBody.appendChild(tr);

            colcounter = 0;
            let myCellContent = '';

            $.each(indy_list_of_column_labels, function (i_index, colLabel) {
                myCellContent = row[colLabel];

                // include in table or not - 1 is for include
                if (indy_list_of_column_labels_show_hide[i_index] === 1) {
                    var td = document.createElement('TD');
                    $(td).attr('col-index', colcounter);
                    $(td).attr('row-index', rowcounter);
                    $(td).attr('col-label', colLabel);

                    if (colLabel === indy_row_label) {
                        let this_me = '<input type="text" class="special-label" id="sample_row_' + rowcounter
                            + '" name="' + colLabel + '" value="' + myCellContent
                            + '" col-index="' + colcounter + '" row-index="' + rowcounter + '">';
                        $(td).html(this_me);
                        $(td).attr('class', 'special-label-td');
                    } else {
                        td.appendChild(document.createTextNode(myCellContent));
                    }
                    tr.appendChild(td);
                    colcounter = colcounter + 1;
                }
            });
            rowcounter = rowcounter + 1;

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
            'order': indy_table_order,
            'columnDefs': indy_table_column_defs,
            // fixedColumns: true
            'autoWidth': true
        });

        // HANDY each row of datatable
        // Do not need but keep for reference
        // https://stackoverflow.com/questions/29077902/how-to-loop-through-all-rows-in-datatables-jquery
        // sampleDataTable.rows().every(function () {
        //     this.data()
        //     // is a list, with the first one being the tags and such
        //     console.log("this row ",this.data());
        //     console.log("this row ",this.data()[0]);
        //     // the tags and such look like a long string, so, to find an attribute, must be creative
        //     // below is HANDY for looping through, and getting a value.by name, but we do not need that here
        //     var data = this.data();
        //     data.forEach(function (value, index) {
        //         // if (value.isActive)
        //         // {
        //          console.log('value ',value);
        //
        //          // console.log(value.UserName);
        //         // }
        //     })
        // });

        //reference $('#glossary_table_filter :input').val(searchTerm).trigger('input');
        //reference $('#glossary_table_filter :input').val(null).trigger('input');
        $('#' + sample_metadata_table_id + '_filter :input').val(searchTerm).trigger('input');
        return myTable;
    }

    function postBuildSampleMetadataTable() {
        // allows table to be selectable, must be AFTER table is created - keep
        $('#' + sample_metadata_table_id).selectable({
            filter: 'td',
            distance: 15,
            stop: selectableDragOnSampleMetadataTable
        });
    }

    // END - All Functions section

});
