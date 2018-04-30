$(document).ready(function () {
    var study_pk = Math.floor(window.location.pathname.split("/")[3]);

    // Crude, for old schema
    if (isNaN(study_pk)) {
        study_pk = Math.floor(window.location.pathname.split("/")[2]);
    }

    // Not currently used
    // var image_container = $('#image_mosaic');
    var filter_table = $('#filter_table');
    var image_table = $('#image_table');

    var contrast = 100;
    var brightness = 100;

    // tableCols[3] = "Test";
    // tableRows[3] = "Tester";

    // Perform on image expansion
    var popupDialogData = {};
    var dialogConfirm = $("#image_popup");
    var dialogOptions = {
        resizable: false,
        draggable: false,
        position: {my:"top", at:"top", of:window},
        modal: false,
        closeOnEscape: true,
        autoOpen: false,
        buttons: [
        {
            text: 'Download Full Size Image',
            click: function() {
                window.open('/media/assay_images/'+study_pk+'/'+popupDialogData["file_name"]);
            }
        },
        {
            text: 'Back',
            click: function() {
               $(this).dialog("close");
            }
        }],
        close: function() {
            // Permit scrolling again
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            // Prevent scrolling
            $('body').addClass('stop-scrolling');

            // Change height if necessary
            // if ($(window).height() < 950) {
            //     $(this).dialog('option', 'height', $(window).height() - 100);
            // }
            // else {
            //     $(this).dialog('option', 'height', 750);
            // }
            //
            // if ($(window).width() < 1300) {
            //     $(this).dialog('option', 'width', $(window).width() - 200);
            // }
            // else {
            //     $(this).dialog('option', 'width', 1800);
            // }

            $(this).dialog('option', 'width', $(window).width());
            $(this).dialog('option', 'height', ($(window).height()-$('#floating-sliders').height()-1));

            $(this).closest('.ui-dialog').find('.ui-dialog-buttonpane button:eq(2)').focus();
            var iChip = popupDialogData["chip_id"];
            var iPlate = popupDialogData["plate_id"];
            var iWell = popupDialogData["well_id"];
            var iTime = popupDialogData["time"];
            var iMethodKit = popupDialogData["method_kit"];
            var iStainPairings = popupDialogData["stain_pairings"];
            var iTargetAnalyte = popupDialogData["target_analyte"];
            var iSubtarget = popupDialogData["subtarget"];
            var iSampleLocation = popupDialogData["sample_location"];
            var iReplicate = popupDialogData["replicate"];
            var iNotes = popupDialogData["notes"];
            var iFileName = popupDialogData["file_name"];
            var iField = popupDialogData["field"];
            var iFieldDescription = popupDialogData["field_description"];
            var iMagnification = popupDialogData["magnification"];
            var iResolution = popupDialogData["resolution"];
            var iResolutionUnit = popupDialogData["resolution_unit"];
            var iSampleLabel = popupDialogData["sample_label"];
            var iSampleLabelDescription = popupDialogData["sample_label_description"];
            var iWavelength = popupDialogData["wavelength"];
            var iColorMapping = popupDialogData['color_mapping'];
            var iSettingNote = popupDialogData["setting_notes"];
            // Construct Dialog Box Title
            var tempTarget = iTargetAnalyte.split(' | ');
            var tempLabel = iSampleLabel.split(' | ');
            var tempColor = iColorMapping.split(' | ');
            var titleText = "";
            if (tempTarget.length == 1 || tempLabel.length == 1 || tempColor.length == 1){
                titleText = iTargetAnalyte + " ("+iSampleLabel+" | "+iColorMapping.toUpperCase()+")";
            } else {
                try {
                    for (i = 0; i < tempTarget.length; i++) {
                        titleText += tempTarget[i] + " ("+tempLabel[i]+" | "+tempColor[i].toUpperCase()+")";
                        if (i < tempTarget.length-1) {
                            titleText += ", ";
                        }
                    }
                } catch(err) {
                    titleText = iTargetAnalyte + " ("+iSampleLabel+", "+iColorMapping.toUpperCase()+")";
                }
            }


            // $("#myDialogText").html('<div class="row no-padding"><div class="thumbnail col-md-12 col-lg-4"><img style="filter: contrast('+contrast+'%)  brightness('+brightness+'%);" src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+popupDialogData["file_name"].split(".")[0]+'_600_600.jpg"/></div><div class="col-md-12 col-lg-7"><table class="table table-hover table-striped table-bordered table-condensed small"><tr><th style="width: 250px;">Chip ID</th><td>'+iChip+'</td></tr><tr><th>Assay Plate ID</th><td>'+iPlate+'</td></tr><tr><th>Assay Well ID</th><td>'+iWell+'</td></tr><tr><th>Time</th><td>'+iTime+'</td></tr><tr><th>Method/Kit</th><td>'+iMethodKit+'</td></tr><tr><th>Target/Analyte</th><td>'+iTargetAnalyte+'</td></tr><tr><th>Subtarget</th><td>'+iSubtarget+'</td></tr><tr><th>Sample Location</th><td>'+iSampleLocation+'</td></tr><tr><th>Replicate</th><td>'+iReplicate+'</td></tr><tr><th>Notes</th><td>'+iNotes+'</td></tr><tr><th>Image File Name</th><td>'+iFileName+'</td></tr><tr><th>Image Field</th><td>'+iField+'</td></tr><tr><th>Image Field Description</th><td>'+iFieldDescription+'</td></tr><tr><th>Image Magnification</th><td>'+iMagnification+'</td></tr><tr><th>Image Resolution</th><td>'+iResolution+'</td></tr><tr><th>Image Resolution Unit</th><td>'+iResolutionUnit+'</td></tr><tr><th>Image Sample Label</th><td>'+iSampleLabel+'</td></tr><tr><th>Image Sample Label Description</th><td>'+iSampleLabelDescription+'</td></tr><tr><th>Image Wavelength (ex/em nm)</th><td>'+iWavelength+'</td></tr><tr><th>Image Color Mapping</th><td>'+iColorMapping+'</td></tr><tr><th>Image Setting Note</th><td>'+iSettingNote+'</td></tr></table></div></div>');
            $("#myDialogText").html('<div class="row no-padding"><div class="thumbnail col-md-12 col-lg-4"><img style="filter: contrast('+contrast+'%)  brightness('+brightness+'%);" src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+popupDialogData["file_name"].split(".")[0]+'_600_600.jpg"/></div><div class="col-md-12 col-lg-7"><table class="table table-hover table-striped table-bordered table-condensed small"><tr><th style="width: 250px;">Chip ID</th><td>'+
                iChip+'</td></tr><tr><th>Assay Plate ID</th><td>'+
                iPlate+'</td></tr><tr><th>Assay Well ID</th><td>'+
                iWell+'</td></tr><tr><th>Time</th><td>'+
                iTime+'</td></tr><tr><th>Method/Kit</th><td>'+
                iMethodKit+'</td></tr><tr><th>Target-Stain Pairings</th><td><b>'+
                iStainPairings+'</td></tr></b><tr><th>Target/Analyte</th><td>'+
                iTargetAnalyte+'</td></tr><tr><th>Sample Location</th><td>'+
                iSampleLocation+'</td></tr><tr><th>Notes</th><td>'+
                iNotes+'</td></tr><tr><th>Image File Name</th><td>'+
                iFileName+'</td></tr><tr><th>Image Field</th><td>'+
                iField.split(".")[0]+' <span data-toggle="tooltip" title="'+
                iFieldDescription+'" class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></td></tr><tr><th>Image Magnification</th><td>'+
                iMagnification.split(".")[0]+'x</td></tr><tr><th>Image Resolution</th><td>'+
                iResolution+" "+iResolutionUnit+'</td></tr><tr><th>Image Sample Label</th><td>'+
                iSampleLabel+' <span data-toggle="tooltip" title="'+
                iSampleLabelDescription+'" class="glyphicon glyphicon-info-sign" aria-hidden="true"></span></td></tr><tr><th>Image Wavelength (ex/em nm)</th><td>'+
                iWavelength+'</td></tr><tr><th>Image Color Mapping</th><td>'+
                iColorMapping+'</td></tr><tr><th>Image Setting Note</th><td>'+
                iSettingNote+'</td></tr></table></div></div>');
            $("#ui-id-1")[0].innerHTML = titleText;
        }
    };
    var theDialog = dialogConfirm.dialog(dialogOptions);

    var filter_elements = "";
    for (var i=0; i<tableCols.length; i++) {
        var col = tableCols[i].replace(/\s/g, '').replace(/[,]/g, '');
        filter_elements += "<button aria-pressed='true' style='max-width: 160px; min-height: 80px; white-space: normal; margin-bottom: 1em;' class='col-lg-2 col-md-4 col-sm-6 col-xs-12 btn btn-3d btn-default btn-checkbox active'><label class='hand-cursor'>"+tableCols[i].toUpperCase()+"</label><input checked id='"+col+"' type=checkbox></button>";
    }
    // for (i=0; i<tableRows.length; i++){
    //     filter_elements += "<tr><th>"+tableRows[i]+"</th><td><input id='"+tableRows[i].split(" ").join("").split(",").join("")+"' type=checkbox></td></tr>";
    // }
    filter_table.html(filter_elements);

    // Sloppy solution keeping this a td
    var table_elements = "<thead><tr><td style='font-weight: bold; width: .1%; white-space: nowrap;'>Chip/Well</td>";
    for (i=0; i<tableCols.length; i++) {
        var col = tableCols[i].replace(/\s/g, '').replace(/[,]/g, '');
        table_elements += "<th style='white-space: nowrap;' class='"+col+" text-center'>"+tableCols[i].toUpperCase()+"</th>";
    }
    table_elements += "</tr></thead><tbody>";
    for (i=0; i<tableRows.length; i++) {
        var row = tableRows[i].replace(/\s/g, '').replace(/[,]/g, '');
        table_elements += "<tr class='"+row+"'><th class='row-header' style='width: .1%; white-space: nowrap;'><a href='/assays/assaymatrixitem/"+metadata_list[tableRows[i]]+"/'>"+tableRows[i]+"</a></th>";
        for (var j=0; j<tableCols.length; j++) {
            var col = tableCols[j].replace(/\s/g, '').replace(/[,]/g, '');
            table_elements += "<td class='text-center "+col+row+" "+col+"'></td>";
        }
        table_elements += "</tr>";
    }
    table_elements += "</tbody>";
    image_table.html(table_elements);

    image_table.on('click', '#image_thumbnail', function () {
        popupDialogData = metadata_list[this.getAttribute("data-pic")];
        dialogConfirm.dialog("open");
        $(".ui-dialog").find("button").blur();
    });

    //Checkbox click event
    $("#filter_table").on("click",":checkbox", function() {
        var checkbox = $(this);
        var checkbox_id = $(this).attr('id');
        var cls = checkbox_id.split(' ').pop();
        if (checkbox.is(':checked')) {
            image_table.find('.'+cls).removeClass('hidden');
        } else {
            image_table.find('.'+cls).addClass('hidden');
        }
        $('.row-header').css('width', '.1%').css('white-space', 'nowrap');

        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body"});
    });

    for (j=0; j<tableCols.length; j++){
        cls = tableCols[j].split(" ").join("").split(",").join("");
        for (var i=0; i<Object.keys(tableData).length; i++) {
            if (tableData[Object.keys(tableData)[i]][1] == cls) {
                var caption = metadata_list[Object.keys(tableData)[i]]["target_analyte"] + " (" + metadata_list[Object.keys(tableData)[i]]["sample_location"] + "), "+metadata_list[Object.keys(tableData)[i]]["sample_label"]+", "+metadata_list[Object.keys(tableData)[i]]["magnification"].split(".")[0]+"x at " + metadata_list[Object.keys(tableData)[i]]["time"];
                $('.'+cls+tableData[Object.keys(tableData)[i]][0]).append('<span data-pic="'+Object.keys(tableData)[i]+'" style="vertical-align: top; display: inline-block; margin:2px;" id="image_thumbnail"><figure><img style="height: 120px; width: 120px; filter: contrast('+contrast+'%) brightness('+brightness+'%);" src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+metadata_list[Object.keys(tableData)[i]]["file_name"].split(".")[0]+'_120_120.jpg"/><figcaption style="width: 120px; word-wrap: break-word;" class="text-center">'+ caption +'</figcaption></figure></span>');
            }
        }
    }

    $( function() {
        var handle = $( "#handle-contrast" );
        $( "#slider-contrast" ).slider({
            create: function() {
                handle.text( $( this ).slider( "value" ) + "%" );
            },
            slide: function( event, ui ) {
                handle.text( ui.value + "%");
                adjustContrast(ui.value);
            },
            value: 100,
            min: 0,
            max: 200
        });
    } );

    $( function() {
        var handle = $( "#handle-brightness" );
        $( "#slider-brightness" ).slider({
            create: function() {
                handle.text( $( this ).slider( "value" ) + "%" );
            },
            slide: function( event, ui ) {
                handle.text( ui.value + "%");
                adjustBrightness(ui.value);
            },
            value: 100,
            min: 0,
            max: 500
        });
    } );

    function adjustContrast(newContrast){
        contrast = newContrast;
        $( "img" ).not('img[src$="/static/img/brand.png"]').each(function() {
            $( this ).css( "filter", "contrast("+contrast+"%) brightness("+brightness+"%)");
        });
    }

    function adjustBrightness(newBrightness){
        brightness = newBrightness;
        $( "img" ).not('img[src$="/static/img/brand.png"]').each(function() {
            $( this ).css( "filter", "contrast("+contrast+"%) brightness("+brightness+"%)");
        });
    }

    // Return brightness and contrast to 100%.
    $('#reset-to-default').click(function () {
        adjustBrightness(100);
        adjustContrast(100);
        $('#handle-brightness').text("100%");
        $('#handle-contrast').text("100%");
        $("#slider-brightness").slider( "value", 100 );
        $("#slider-contrast").slider( "value", 100 );
    });

    // Toggle buttons.
    $(".btn-checkbox").on("mouseup", function () {
        var $checkbox = $(this).find(':checkbox');
        $checkbox.trigger("click");
        if ($checkbox.prop('checked')){
            $(this).addClass("active");
        } else {
            $(this).removeClass("active");
        }
        $(this).blur();
        doSearch(true);
    });

    image_table.dataTable({
        // columns: generateColumns(),
        "ordering": false,
        "filter": false,
        "searching": false,
        dom: 'frt',
        fixedHeader: {headerOffset: 50},
        deferRender: true
    });

    // On keystroke, run search function.
    $('#search-box').keyup(function (e) {
        if(e.keyCode === 8) {
            doSearch(true);
        } else {
            doSearch(false);
        }
    });

    // Filter table based on contents of search textbox.
    // TODO A caption may contain a query, but if a future caption does not, the row will be hidden.
    function doSearch(backspace) {
        var query = $('#search-box').val().toUpperCase();
        var isChip = false;
        if (backspace) {
            makeAllVisible();
        }
        image_table.find('figcaption').each(function(index, value) {
            buttonActive = $('#'+$(value).parent().parent().parent().attr("class").split(" ")[2]).prop('checked');
            if ($(value).text().toUpperCase().includes(query)) {
                if (buttonActive) {
                    $(value).parent().parent().removeClass('hidden');
                } else {
                    $(value).parent().parent().addClass('hidden');
                }
            } else {
                for (var i=0; i<tableRows.length; i++) {
                    if (tableRows[i].toUpperCase().includes(query)) {
                        isChip = true;
                        break;
                    }
                }
                if (isChip) {
                    image_table.find('th').each(function(index, value) {
                        if (index > tableCols.length-1){
                            if ($(value).text().toUpperCase().includes(query)) {
                                $(value).parent().removeClass('hidden');
                            } else {
                                $(value).parent().addClass('hidden');
                            }
                        }
                    });
                } else {
                    $(value).parent().parent().addClass('hidden');
                }
            }
        });
        hideEmpty();
    }

    // Reveal every row and image.
    function makeAllVisible(){
        image_table.find('figcaption').each(function(index, value) {
            $(value).parent().parent().removeClass('hidden');
        });
        image_table.find('th').each(function(index, value) {
            if (index > tableCols.length-1){
                $(value).parent().removeClass('hidden');
            }
        });
    }

    // Hide rows that contain no images.
    function hideEmpty() {
        for (i=0; i<tableRows.length; i++) {
            if ($('.'+tableRows[i]).height() < 100) {
                $('.'+tableRows[i]).addClass('hidden');
            }
        }

        // Adjust fixedHeader
        $($.fn.dataTable.tables(true)).DataTable().fixedHeader.adjust();
    }

    // Increase the height of the footer to ensure it is not obscured
    $('#footer').height("+=150");

    // Center JQuery Dialog Window Title
    $("#ui-id-1").css('text-align', 'center').css('width','100%').css('font-size', '16px');

    // Make JQuery Dialog title bar not blend in with browser UI so strongly
    $(".ui-dialog").find(".ui-widget-header").css('background', 'linear-gradient(#111111, #333333)').css('color', 'white');

    // "Close" and "Download" buttons as Bootstrap buttons.
    // TODO Figure out what classes contribute to strange hovering when you are less tired.
    $(".ui-dialog").find(".ui-button-text-only").addClass('btn btn-primary').removeClass('ui-state-default');

    // Escape Key closes dialog windows
    $(document).keydown(function(e) {
        // ESCAPE key pressed
        if (e.which == 27) {
            $(theDialog).dialog('close');
        }
    });
});
