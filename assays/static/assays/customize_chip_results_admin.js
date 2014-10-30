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
        $('#id_assayresult_set-'+i+'-assay_name').html(options);
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
            $('#id_assayresult_set-'+j+'-assay_name').html(options);
            if (!reset) {
                $('#id_assayresult_set-'+j+'-assay_name').val(vals[j]);
            }
        }
    }

    var study = $('#id_assay_device_readout');
    var newRow = $('.add-row').children().children();
    var options = "";

    $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','AssayChipReadout','chip_setup')).then(function(data) {
        options = data;
        changeAll(false);
    });

    study.change(function() {
        $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','AssayChipReadout','chip_setup')).then(function(data) {
            options = data;
            changeAll(true);
        });
    });

    newRow.click(function() {
        changeNew();
    });
});
