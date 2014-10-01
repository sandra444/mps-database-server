$(document).ready(function () {

    var id = $('#id_assay_run_id');
    id.prop('readonly', true);

    //Will not submit disabled field; use readonly instead
    function set_data() {
        id.prop('readonly', false);
        id.html(data.join('-'));
        id.prop('readonly', true);
    }

    function get_center_id() {
        if (center.val()) {
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
                    data[0] = json.center_id;
                    set_data();
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else{
            data[0] = '';
            set_data();
        }
    }

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var data = [[],[],[]];

    var date = $('#id_start_date_0');
    var center = $('#id_center_id');
    var name = $('#id_name');

    //Need to have condition for adding vs. changing data
    get_center_id();
    data[1] = date.val();
    data[2] = name.val();

    //Needs an AJAX call to get centerID
    center.change(function (evt) {
        get_center_id();
    });

    date.data("value", date.val());

    setInterval(function () {
        var date_data = date.data("value"),
            val = date.val();

        if (date_data !== val) {
            date.data("value", val);
            data[1] = $('#id_start_date_0').val();
            set_data();
        }
    }, 100);

    name.on('input', function () {
        data[2] = $('#id_name').val();
        set_data();
    }).trigger('input');
});
