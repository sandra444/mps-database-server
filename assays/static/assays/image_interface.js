$(document).ready(function () {

    $.fn.bootstrapBtn = $.fn.button.noConflict();

    image_container = $.find('#image_mosaic')[0];
    filter_table = $('#filter_table');
    image_table = $('#image_table');
    // for (i=0; i<Object.keys(metadata_list).length; i++){
    //     image_container.append('<button>Test?</button>');
    // }
    var filter_elements = "";
    for (i=0; i<tableCols.length; i++){
        filter_elements += "<tr><th>"+tableCols[i]+"</th><td><input type=checkbox></td></tr>";
    }
    for (i=0; i<tableRows.length; i++){
        filter_elements += "<tr><th>"+tableRows[i]+"</th><td><input type=checkbox></td></tr>";
    }
    filter_table.html(filter_elements);

    var table_elements = "<tr><td></td>";
    for (i=0; i<tableCols.length; i++){
        table_elements += "<th class='"+tableCols[i].replace(/\s+/g, '')+"'>"+tableCols[i]+"</th>";
    }
    table_elements += "</tr>"
    for (i=0; i<tableRows.length; i++) {
        table_elements += "<tr class='"+tableRows[i].replace(/\s+/g, '')+"'><th>"+tableRows[i]+"</th>";
        for (j=0; j<tableCols.length; j++) {
            table_elements += "<td class='"+tableCols[i].replace(/\s+/g, '')+"'>IMAGE</td>";
        }
        table_elements += "</tr>";
    }
    console.log(metadata_list);
    image_table.html(table_elements)

    var dialogConfirm = $("#image_popup");

    $( function() {
        dialogConfirm.dialog({
            height:750,
            width:500,
            modal: true,
            closeOnEscape: true,
            autoOpen: false,
            buttons: [
            {
                text: 'Download Full Size Image',
                click: function() {
                    $("#submit").trigger("click");
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
                console.log("Opened!");
                $('body').addClass('stop-scrolling');
                $('.ui-dialog :button').blur();
                var iChip = "Test";
                var iPlate = "Test";
                var iWell = "Test";
                var iTime = "Test";
                var iMethodKit = "Test";
                var iTargetAnalyte = "Test";
                var iSubtarget = "Test";
                var iSampleLocation = "Test";
                var iReplicate = "Test";
                var iNotes = "Test";
                var iFileName = "Test";
                var iField = "Test";
                var iFieldDescription = "Test";
                var iMagnification = "Test";
                var iResolution = "Test";
                var iResolutionUnit = "Test";
                var iSampleLabel = "Test";
                var iSampleLabelDescription = "Test";
                var iWavelength = "Test";
                var iSettingNote = "Test";
                $("#myDialogText").html('<table class="table-hover table-striped table-bordered"><tr><th>Chip ID</th><td>'+iChip+'</td></tr><tr><th>Assay Plate ID</th><td>'+iPlate+'</td></tr><tr><th>Assay Well ID</th><td>'+iWell+'</td></tr><tr><th>Time</th><td>'+iTime+'</td></tr><tr><th>Method/Kit</th><td>'+iMethodKit+'</td></tr><tr><th>Target/Analyte</th><td>'+iTargetAnalyte+'</td></tr><tr><th>Subtarget</th><td>'+iSubtarget+'</td></tr><tr><th>Sample Location</th><td>'+iSampleLocation+'</td></tr><tr><th>Replicate</th><td>'+iReplicate+'</td></tr><tr><th>Notes</th><td>'+iNotes+'</td></tr><tr><th>Image File Name</th><td>'+iFileName+'</td></tr><tr><th>Image Field</th><td>'+iField+'</td></tr><tr><th>Image Field Description</th><td>'+iFieldDescription+'</td></tr><tr><th>Image Magnification</th><td>'+iMagnification+'</td></tr><tr><th>Image Resolution</th><td>'+iResolution+'</td></tr><tr><th>Image Resolution Unit</th><td>'+iResolutionUnit+'</td></tr><tr><th>Image Sample Label</th><td>'+iSampleLabel+'</td></tr><tr><th>Image Sample Label Description</th><td>'+iSampleLabelDescription+'</td></tr><tr><th>Image Wavelength (nm)</th><td>'+iWavelength+'</td></tr><tr><th>Image Setting Note</th><td>'+iSettingNote+'</td></tr></table>');
                console.log(metadata_list[31]);
            }
        });

        console.log("Loaded?");
        $( "#image_thumbnail" ).on( "click", function() {
            console.log("Clicked!");
            dialogConfirm.dialog( "open" );
        });

    });

    //dialogConfirm.removeProp('hidden');

});
