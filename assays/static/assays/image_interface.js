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
            $(this).dialog('option', 'height', $(window).height()*0.85);

            $('.ui-dialog :button').blur();
            var iChip = popupDialogData["chip_id"];
            var iPlate = popupDialogData["plate_id"];
            var iWell = popupDialogData["well_id"];
            var iTime = popupDialogData["time"];
            var iMethodKit = popupDialogData["method_kit"];
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
            var iSettingNote = popupDialogData["setting_notes"];
            $("#myDialogText").html('<div class="row no-padding"><div class="thumbnail col-md-12 col-lg-4"><img style="filter: contrast('+contrast+'%)  brightness('+brightness+'%);" src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+popupDialogData["file_name"].split(".")[0]+'_600_600.jpg"/></div><div class="col-md-12 col-lg-7"><table class="table table-hover table-striped table-bordered table-condensed small"><tr><th style="width: 250px;">Chip ID</th><td>'+iChip+'</td></tr><tr><th>Assay Plate ID</th><td>'+iPlate+'</td></tr><tr><th>Assay Well ID</th><td>'+iWell+'</td></tr><tr><th>Time</th><td>'+iTime+'</td></tr><tr><th>Method/Kit</th><td>'+iMethodKit+'</td></tr><tr><th>Target/Analyte</th><td>'+iTargetAnalyte+'</td></tr><tr><th>Subtarget</th><td>'+iSubtarget+'</td></tr><tr><th>Sample Location</th><td>'+iSampleLocation+'</td></tr><tr><th>Replicate</th><td>'+iReplicate+'</td></tr><tr><th>Notes</th><td>'+iNotes+'</td></tr><tr><th>Image File Name</th><td>'+iFileName+'</td></tr><tr><th>Image Field</th><td>'+iField+'</td></tr><tr><th>Image Field Description</th><td>'+iFieldDescription+'</td></tr><tr><th>Image Magnification</th><td>'+iMagnification+'</td></tr><tr><th>Image Resolution</th><td>'+iResolution+'</td></tr><tr><th>Image Resolution Unit</th><td>'+iResolutionUnit+'</td></tr><tr><th>Image Sample Label</th><td>'+iSampleLabel+'</td></tr><tr><th>Image Sample Label Description</th><td>'+iSampleLabelDescription+'</td></tr><tr><th>Image Wavelength (nm)</th><td>'+iWavelength+'</td></tr><tr><th>Image Setting Note</th><td>'+iSettingNote+'</td></tr></table></div></div>');
        }
    };
    var theDialog = dialogConfirm.dialog(dialogOptions);

    var filter_elements = "";
    for (var i=0; i<tableCols.length; i++) {
        // Remove spaces and commas
        // var col = tableCols[i].split(" ").join("").split(",").join("");
        var col = tableCols[i].replace(/\s/g, '').replace(/[,]/g, '');
        // filter_elements += "<tr><th>"+tableCols[i]+"</th><td><input data-filled='0' id='"+col+"' type=checkbox></td></tr>";
        // Unsemantic (but somewhat amusing) use of thumbnail class
        filter_elements += "<button aria-pressed='true' style='min-height:90px; white-space: normal; margin-bottom: 1em;' class='col-lg-2 col-md-4 col-sm-6 col-xs-12 btn btn-default btn-checkbox active'><label class='hand-cursor'>"+tableCols[i]+"</label><input checked id='"+col+"' type=checkbox></button>";
    }
    // for (i=0; i<tableRows.length; i++){
    //     filter_elements += "<tr><th>"+tableRows[i]+"</th><td><input id='"+tableRows[i].split(" ").join("").split(",").join("")+"' type=checkbox></td></tr>";
    // }
    filter_table.html(filter_elements);

    var table_elements = "<tr><td style='width: .1%; white-space: nowrap;'></td>";
    for (i=0; i<tableCols.length; i++) {
        var col = tableCols[i].split(" ").join("").split(",").join("");
        table_elements += "<th style='max-width: 100%; white-space: nowrap;' class='"+col+" text-center'>"+tableCols[i]+"</th>";
    }
    table_elements += "</tr>";
    for (i=0; i<tableRows.length; i++) {
        var row = tableRows[i].split(" ").join("").split(",").join("");
        table_elements += "<tr class='"+row+"'><th class='row-header' style='width: .1%; white-space: nowrap;'>"+tableRows[i]+"</th>";
        for (var j=0; j<tableCols.length; j++) {
            var col = tableCols[j].split(" ").join("").split(",").join("");
            table_elements += "<td class='text-center "+col+row+" "+col+"'></td>";
        }
        table_elements += "</tr>";
    }
    image_table.html(table_elements);

    image_table.on('click', '#image_thumbnail', function () {
        popupDialogData = metadata_list[this.getAttribute("data-pic")];
        dialogConfirm.dialog( "open" );
    });

    //Checkbox click event
    // *All* checkboxes is maybe a little broad
    $(document).on("click",":checkbox", function() {
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
                var caption = metadata_list[Object.keys(tableData)[i]]["target_analyte"] + " (" + metadata_list[Object.keys(tableData)[i]]["sample_location"] + ") "+metadata_list[Object.keys(tableData)[i]]["magnification"]+"x at " + metadata_list[Object.keys(tableData)[i]]["time"]
                $('.'+cls+tableData[Object.keys(tableData)[i]][0]).append('<span data-pic="'+Object.keys(tableData)[i]+'" style="display: inline-block; margin:5px;" id="image_thumbnail"><figure><img style="filter: contrast('+contrast+'%) brightness('+brightness+'%);" src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+metadata_list[Object.keys(tableData)[i]]["file_name"].split(".")[0]+'_120_120.jpg"/><figcaption style="width: 120px; word-wrap: break-word;" class="text-center">'+ caption +'</figcaption></figure></span>');
            }
        }
    }

    $( function() {
        var handle = $( "#handle-contrast" );
        $( "#slider-contrast" ).slider({
            create: function() {
                handle.text( $( this ).slider( "value" ) );
            },
            slide: function( event, ui ) {
                handle.text( ui.value );
                adjustContrast(ui.value);
            },
            value: 100,
            min: 0,
            max: 500
        });
    } );

    $( function() {
        var handle = $( "#handle-brightness" );
        $( "#slider-brightness" ).slider({
            create: function() {
                handle.text( $( this ).slider( "value" ) );
            },
            slide: function( event, ui ) {
                handle.text( ui.value );
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

    $('#reset-to-default').click(function () {
        adjustBrightness(100);
        adjustContrast(100);
        $('#handle-brightness').text(100);
        $('#handle-contrast').text(100);
        $("#slider-brightness").slider( "value", 100 );
        $("#slider-contrast").slider( "value", 100 );
    });

    $(".btn-checkbox").off().on("click", function () {
        var $checkbox = $(this).find(':checkbox');
        $checkbox.trigger("click");
        if ($checkbox.prop('checked')){
            $(this).addClass("active");
        } else {
            $(this).removeClass("active");
        }
    });

});
