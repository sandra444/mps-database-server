// This script is for displaying the readout and everything before in plate results
// TODO NEEDS REFACTOR
// TODO PREFERRABLY CONSOLIDATE THESE DISPLAY FUNCTION (DO NOT REPEAT YOURSELF)
$(document).ready(function () {
    // The setup
    var readout = $('#id_readout');

    // ADMIN ONLY
//    if ($('fieldset')[0]) {
//        // On setup change, acquire labels and build table
//        readout.change(function() {
//            window.LAYOUT.get_device_layout(readout.val(), 'assay_device_readout', false);
//        });
//
//        // If a setup is initially chosen
//        // (implies readout exists)
//        if (readout.val()) {
//            // Initial table and so on
//            window.LAYOUT.get_device_layout(readout.val(), 'assay_device_readout', false);
//        }
//    }

    // WHITTLE
    function getIDs() {
        var i = 0;
        var IDs = [];
        while ($('#id_assayplateresult_set-'+i+'-assay_name')[0]){
            IDs.push(i);
            i += 1;
        }
        return IDs;
    }

    function changeNew() {
        var i = Math.max.apply(null,getIDs());
        $('#id_assayplateresult_set-'+i+'-assay_name').html(inlineOptions);
    }

    function changeAll(reset) {
        var IDs = getIDs();
        var vals = [];

        if (!reset) {
            for (var i in IDs) {
                vals.push($('#id_assayplateresult_set-'+i+'-assay_name').val());
            }
        }

        for (var j in IDs) {
            $('#id_assayplateresult_set-'+j+'-assay_name').html(inlineOptions);
            if (!reset) {
                $('#id_assayplateresult_set-'+j+'-assay_name').val(vals[j]);
            }
        }
    }

    var newRow = $('.add-row').children().children();
    var inlineOptions = "";

    // Initial readout whittle
    $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
        inlineOptions = data;
        // Only reset (pass true) when you want to overwrite existing
        changeAll(false);
    });

    // Whittle when readout changes
    readout.change(function() {
        $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(true);
        });
    });

    newRow.click(function() {
        changeNew();
    });

    // This is to deal with new inline entries when on the frontend
    $("#add_button-assayplateresult_set").click(function() {
        changeNew();
    });

    // Resolve deletion error frontend
    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on("click", "input[name*='DELETE']", function(event) {
        $.when(whittle('readout_id',readout.val(),'AssayPlateReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(false);
        });
    });
});
