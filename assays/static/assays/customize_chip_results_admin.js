$(document).ready(function () {

    //$('<div id="view_data">').appendTo($('fieldset')[0]).html('<div class="form-row"><div class="field-box"><label for="compound">Compound:</label><input type="text" readonly id="compound"></div><div class="field-box"><label for="concentration">Concentration:</label><input type="text" readonly id="concentration">></div><div class="field-box"><label for="unit">Unit:</label><input type="text" readonly id="unit"></div><div class="field-box"><label for="chip_test_type">Test Type:</label><input type="text" readonly id="chip_test_type"></div>');

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var ajax_call = function () {
        console.log($('#id_assay_device_readout').val());

        if (!$('#id_assay_device_readout').val()) {
            $('#compound').html("");
            $('#concentration').html("");
            $('#unit').html("");
            $('#chip_test_type').html("");
            $('#assay').html("");
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
                id: $('#id_assay_device_readout').val(),

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                console.log(json);
                $('#compound').html(json.compound);
                $('#concentration').html(json.concentration);
                $('#unit').html(json.unit);
                $('#chip_test_type').html(json.chip_test_type);
                $('#assay').html(json.assay);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    var add = '<div class="form-row"><div class="field-box">' +
        '<label for="compound">Compound:</label><p id="compound"></p></div>' +
        '<div class="field-box"><label for="concentration">Concentration:</label><p id="concentration"></p><p id="unit"></p></div>' +
        '<div class="field-box"><label for="assay">Assay:</label><p id="assay"></p></div>' +
        '<div class="field-box"><label for="chip_test_type">Test Type:</label><p id="chip_test_type"></p></div>';

    $('<div id="view_data">').appendTo($('fieldset')[0]).html(add);

    if ($('#id_assay_device_readout').val()) {
        ajax_call();
    }

    $('#id_assay_device_readout').change(function (evt) {
        ajax_call();
    });
});
