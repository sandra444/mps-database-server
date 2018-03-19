$(document).ready(function () {
    //$.fn.bootstrapBtn = $.fn.button.noConflict();

    console.log(tableData);

    // Be sure to check this on upload to stage/etc. Path not URL, so should work?
    var study_pk = window.location.pathname.split("/")[2];

    var image_container = $('#image_mosaic');
    var filter_table = $('#filter_table');
    var image_table = $('#image_table')

    // tableCols[3] = "Test";
    // tableRows[3] = "Tester";

    // Perform on image expansion
    var popupDialogData = {};
    var dialogConfirm = $("#image_popup");
    var dialogOptions = {
        height:750,
        width:1300,
        modal: true,
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
            text: 'Cancel',
            click: function() {
               $(this).dialog("close");
            }
        }],
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            $('body').addClass('stop-scrolling');
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
            $("#myDialogText").html('<div style="vertical-align: top; display: inline-block;"><img src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+popupDialogData["file_name"].split(".")[0]+'_600_600"/><div style="vertical-align: middle; margin-left: 25px; display:inline-block;"><table style="width: 600px;" class="table-hover table-striped table-bordered"><tr><th style="width: 250px;">Chip ID</th><td>'+iChip+'</td></tr><tr><th>Assay Plate ID</th><td>'+iPlate+'</td></tr><tr><th>Assay Well ID</th><td>'+iWell+'</td></tr><tr><th>Time</th><td>'+iTime+'</td></tr><tr><th>Method/Kit</th><td>'+iMethodKit+'</td></tr><tr><th>Target/Analyte</th><td>'+iTargetAnalyte+'</td></tr><tr><th>Subtarget</th><td>'+iSubtarget+'</td></tr><tr><th>Sample Location</th><td>'+iSampleLocation+'</td></tr><tr><th>Replicate</th><td>'+iReplicate+'</td></tr><tr><th>Notes</th><td>'+iNotes+'</td></tr><tr><th>Image File Name</th><td>'+iFileName+'</td></tr><tr><th>Image Field</th><td>'+iField+'</td></tr><tr><th>Image Field Description</th><td>'+iFieldDescription+'</td></tr><tr><th>Image Magnification</th><td>'+iMagnification+'</td></tr><tr><th>Image Resolution</th><td>'+iResolution+'</td></tr><tr><th>Image Resolution Unit</th><td>'+iResolutionUnit+'</td></tr><tr><th>Image Sample Label</th><td>'+iSampleLabel+'</td></tr><tr><th>Image Sample Label Description</th><td>'+iSampleLabelDescription+'</td></tr><tr><th>Image Wavelength (nm)</th><td>'+iWavelength+'</td></tr><tr><th>Image Setting Note</th><td>'+iSettingNote+'</td></tr></table></div></div>');
        }
    };
    var theDialog = dialogConfirm.dialog(dialogOptions);

    var filter_elements = "";
    for (i=0; i<tableCols.length; i++){
        var col = tableCols[i].split(" ").join("").split(",").join("");
        filter_elements += "<tr><th>"+tableCols[i]+"</th><td><input data-filled='0' id='"+col+"' type=checkbox></td></tr>";
    }
    // for (i=0; i<tableRows.length; i++){
    //     filter_elements += "<tr><th>"+tableRows[i]+"</th><td><input id='"+tableRows[i].split(" ").join("").split(",").join("")+"' type=checkbox></td></tr>";
    // }
    filter_table.html(filter_elements);

    var table_elements = "<tr><td style='width: .1%; white-space: no-wrap;'></td>";
    for (i=0; i<tableCols.length; i++){
        var col = tableCols[i].split(" ").join("").split(",").join("");
        table_elements += "<th style='width: .1%; white-space: no-wrap;' class='"+col+" hidden text-center'>"+tableCols[i]+"</th>";
    }
    table_elements += "</tr>"
    for (i=0; i<tableRows.length; i++) {
        var row = tableRows[i].split(" ").join("").split(",").join("");
        table_elements += "<tr style='width: .1%; white-space: no-wrap;' class='"+row+"'><th>"+tableRows[i]+"</th>";
        for (j=0; j<tableCols.length; j++) {
            var col = tableCols[j].split(" ").join("").split(",").join("");
            table_elements += "<td style='width: .1%; white-space: no-wrap;' class='"+col+row+" "+col+" hidden'></td>";
        }
        table_elements += "</tr>";
    }
    image_table.html(table_elements)

    $('#image_table').on('click', '#image_thumbnail', function () {
        popupDialogData = metadata_list[this.getAttribute("data-pic")];
        dialogConfirm.dialog( "open" );
    });

    //Checkbox click event
    $(document).on("click",":checkbox", function(){
        var checkbox = $(this)
        var checkbox_id = $(this).attr('id');
        var cls = checkbox_id.split(' ').pop();
        //console.log(cls);
        //console.log(Object.keys(metadata_list)[0])
        //console.log(metadata_list[Object.keys(metadata_list)[0]]);
        for (i=0; i<Object.keys(tableData).length; i++) {
            if (tableData[Object.keys(tableData)[i]][1] == cls && $(this).data("filled") == '0') {
                $('.'+cls+tableData[Object.keys(tableData)[i]][0]).append('<span data-pic="'+Object.keys(tableData)[i]+'" style="display: inline-block; margin:5px;" id="image_thumbnail"><figure><img src="/media/assay_thumbs/'+study_pk+'/thumbnail_'+metadata_list[Object.keys(tableData)[i]]["file_name"].split(".")[0]+'_120_120"/><figcaption style="width: 120px; word-wrap: break-word;" class="text-center">'+metadata_list[Object.keys(tableData)[i]]["file_name"]+'</figcaption></figure></span>');
            }
        }
        $(this).data("filled", '1')
        if (checkbox.is(':checked')){
            $('#image_table').find('.'+cls).removeClass('hidden');
        } else {
            $('#image_table').find('.'+cls).addClass('hidden');
        }

        // Activates Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip({container:"body"});
    });

});
