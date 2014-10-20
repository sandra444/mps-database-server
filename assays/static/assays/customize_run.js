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
        else {
            data[0] = '';
            set_data();
        }
    }

    function get_types() {
        var types = [];
        for (var i=1; i<4; i++) {
            var val = $('#id_type' + i).val();
            if (val){
                types.push(val);
            }
        }
        data[1] = types.join('_');
        set_data();
    }

    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var data = [
        [],
        [],
        [],
        []
    ];

    var type1 = $('#id_type1');
    var type2 = $('#id_type2');
    var type3 = $('#id_type3');
    var date = $('#id_start_date_0');
    var center = $('#id_center_id');
    var name = $('#id_name');

    //Need to have condition for adding vs. changing data
    get_center_id();
    get_types();
    data[2] = date.val();
    data[3] = name.val();

    //Needs an AJAX call to get centerID
    center.change(function (evt) {
        get_center_id();
    });

    //Get the types for each drop down
    type1.change(function (evt) {
        get_types();
    });

    type2.change(function (evt) {
        get_types();
    });

    type3.change(function (evt) {
        get_types();
    });

    date.data("value", date.val());

    setInterval(function () {
        var date_data = date.data("value"),
            val = date.val();

        if (date_data !== val) {
            date.data("value", val);
            data[2] = $('#id_start_date_0').val();
            set_data();
        }
    }, 100);

    name.on('input', function () {
        data[3] = $('#id_name').val();
        set_data();
    }).trigger('input');
});
