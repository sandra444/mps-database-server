$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    $('#id_assay_device_readout').change(function(evt) {
        console.log($('#id_assay_device_readout').val());

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
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    });
});
