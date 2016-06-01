// TODO REVISE
$(document).ready(function () {
    function getIDs() {
        var i = 0;
        var IDs = [];
        while ($('#id_assaychipresult_set-'+i+'-assay_name')[0]){
            IDs.push(i);
            i += 1;
        }
        return IDs;
    }

    function changeNew() {
        var i = Math.max.apply(null,getIDs());
        $('#id_assaychipresult_set-'+i+'-assay_name').html(inlineOptions);
    }

    function changeAll(reset) {
        var IDs = getIDs();
        var vals = [];

        if (!reset) {
            for (var i in IDs) {
                vals.push($('#id_assaychipresult_set-'+i+'-assay_name').val());
            }
        }

        for (var j in IDs) {
            $('#id_assaychipresult_set-'+j+'-assay_name').html(inlineOptions);
            if (!reset) {
                $('#id_assaychipresult_set-'+j+'-assay_name').val(vals[j]);
            }
        }
    }

    var readout = $('#id_chip_readout');
    var newRow = $('.add-row').children().children();
    var inlineOptions = "";

    // Initial readout whittle
    $.when(whittle('readout_id',readout.val(),'AssayChipReadoutAssay','','')).then(function(data) {
        inlineOptions = data;
        // Only reset (pass true) when you want to overwrite existing
        changeAll(false);
    });

    // Whittle when readout changes
    readout.change(function() {
        $.when(whittle('readout_id',readout.val(),'AssayChipReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(true);
        });
    });

    newRow.click(function() {
        changeNew();
    });

    // This is to deal with new inline entries when on the frontend
    $("#add_button-assaychipresult_set").click(function() {
        changeNew();
    });

    // Resolve deletion error frontend
    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on("click", "input[name*='DELETE']", function(event) {
        $.when(whittle('readout_id',readout.val(),'AssayChipReadoutAssay','','')).then(function(data) {
            inlineOptions = data;
            changeAll(false);
        });
    });

    // This is to deal with new inline entries when on the frontend
//    if ($("#add_button")[0]) {
//        $("#add_button").click(function() {
//        changeNew();
//        });
//    }
//
//    // Resolve deletion error frontent
//    // This selector will check all items with DELETE in the name, including newly created ones
//    $( "body" ).on( "click", "input[name*='DELETE']", function(event) {
//        $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','AssayChipReadout','chip_setup')).then(function(data) {
//            options = data;
//            changeAll(false);
//        });
//    });
});
