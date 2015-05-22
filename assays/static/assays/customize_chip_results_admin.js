// TODO REVISE
$(document).ready(function () {
    function getIDs() {
        var i = 0;
        var IDs = [];
        while ($('#id_assayresult_set-'+i+'-assay_name')[0]){
            IDs.push(i);
            i += 1;
        }
        return IDs;
    }

    function changeNew() {
        var i = Math.max.apply(null,getIDs());
        $('#id_assayresult_set-'+i+'-assay_name').html(inlineOptions);
    }

    function changeAll(reset) {
        var IDs = getIDs();
        var vals = [];

        if (!reset) {
            for (var i in IDs) {
                vals.push($('#id_assayresult_set-'+i+'-assay_name').val());
            }
        }

        for (var j in IDs) {
            $('#id_assayresult_set-'+j+'-assay_name').html(inlineOptions);
            if (!reset) {
                $('#id_assayresult_set-'+j+'-assay_name').val(vals[j]);
            }
        }
    }

    var study = $('#id_assay_device_readout');
    var setup = $('#id_chip_setup');
    var setupVal = setup.val();
    var newRow = $('.add-row').children().children();
    var inlineOptions = "";
    var setupOptions = "";

    // Initial setup whittle
    $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','','')).then(function(data) {
        setupOptions = data;
        setup.html(setupOptions);
        setup.val(setupVal);
    });

    // Initial inline whittle
    $.when(whittle('chip_setup',setup.val(),'AssayChipReadout','AssayChipReadoutAssay','readout_id')).then(function(data) {
        inlineOptions = data;
        changeAll(false);
    });

    // Whittle setup when study changes
    study.change(function() {
        $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','','')).then(function(data) {
            setupOptions = data;
            setup.html(setupOptions);
            setup.trigger('change');
        });
    });

    // Whittle inline when setup changes
    setup.change(function() {
        $.when(whittle('chip_setup',setup.val(),'AssayChipReadout','AssayChipReadoutAssay','readout_id')).then(function(data) {
            inlineOptions = data;
            changeAll(true);
            setupVal = setup.val();
        });
    });

    newRow.click(function() {
        changeNew();
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
