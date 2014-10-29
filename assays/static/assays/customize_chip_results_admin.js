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

    function changeAll() {
        var IDs = getIDs();

        for (var i in IDs) {
            $('#id_assayresult_set-'+i+'-assay_name').html(options);
        }
    }

    var study = $('#id_assay_device_readout');
    var newRow = $('.add-row');
    var options = "";

    study.change(function() {
        $.when(whittle('assay_run_id',study.val(),'AssayChipSetup','AssayChipReadout','chip_setup')).then(function(data) {
            options = data;
            changeAll();
        })
    });

    newRow.click(function() {
        changeNew();
    });
});
