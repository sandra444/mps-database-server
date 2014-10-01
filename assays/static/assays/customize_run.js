$(document).ready(function () {

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var date = $('#id_start_date_0');
    var center = $('#id_center_id');
    var name = $('#id_name');

    //Need to have condition for adding vs. changing data
    var data = [[center.val()],[date.val()],[name.val()]];
    var id = $('#id_assay_run_id');

    //Needs an AJAX call to get centerID
    center.change(function(evt) {
        //data[0] = $('#id_center_id').val();

        $.ajax({
            url: "/assays_ajax",
            type: "POST",
            dataType: "json",
            data: {
                // Function to call within the view is defined by `call:`
                call: 'fetch_center_id',

                // First token is the var name within views.py
                // Second token is the var name in this JS file
                id: center.val(),

                // Always pass the CSRF middleware token with every AJAX call
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                data[0] = (json.center_id);
                id.html(data.join('-'));
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });

        id.html(data.join('-'));
    });

    //Need to find a way to handle people clicking the widgets (today's date, etc)
    //date.on('input', function() {
    //    data[1] = $('#id_start_date_0').val();
    //    id.html(data.join('-'));
    //}).trigger('input');

    date.data("value", date.val());

    setInterval(function() {
        var date_data = date.data("value"),
            val = date.val();

        if (date_data !== val) {
            date.data("value", val);
            data[1] = $('#id_start_date_0').val();
            id.html(data.join('-'));
        }
    }, 100);

    name.on('input', function() {
        data[2] = $('#id_name').val();
        id.html(data.join('-'));
    }).trigger('input');
});
