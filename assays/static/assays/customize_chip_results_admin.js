$(document).ready(function () {

    var readout = $('#id_assay_device_readout');
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var ajax_call = function () {
        console.log(readout.val());

        if (!readout.val()) {
            $('#compound').html("");
            $('#chip_test_type').html("");
            $('#assay').html("");
            $('#run').html("");
            $('#model').html("");
            return;
        }

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_chip_info',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: readout.val(),

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                $('#compound').html(json.compound + ' ' + json.concentration + ' (' + json.unit + ')');
                $('#chip_test_type').html(json.chip_test_type);
                $('#assay').html(json.assay);
                $('#run').html(json.run);
                $('#model').html(json.model);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    };

    var add = '<div class="form-row">' +
        '<div class="field-box"><label for="run">Run:</label><p id="run"></p></div>' +
        '<div class="field-box"><label for="model">Chip Model:</label><p id="model"></p></div>' +
        '<div class="field-box"><label for="assay">Assay:</label><p id="assay"></p></div>' +
        '<div class="field-box"><label for="compound">Compound:</label><p id="compound"></p></div>' +
        '<div class="field-box"><label for="chip_test_type">Test Type:</label><p id="chip_test_type"></p></div>';

    $('<div id="view_data">').appendTo($('fieldset')[0]).html(add);

    if (readout.val()) {
        ajax_call();
    }

    readout.change(function (evt) {
        ajax_call();
    });
});
