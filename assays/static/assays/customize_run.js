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
        if (group.val()) {
            $.ajax({
                url: "/assays_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    // Function to call within the view is defined by `call:`
                    call: 'fetch_center_id',

                    // First token is the var name within views.py
                    // Second token is the var name in this JS file
                    id: group.val(),

                    // Always pass the CSRF middleware token with every AJAX call
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    data[0] = json.center_id;
                    $('#center_name').html(json.center_name);
                    set_data();
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            data[0] = '';
            $('#center_name').html('');
            set_data();
        }
    }

    function get_types() {
        for (var i in type_selectors) {
            if(!type_selectors[i].is(":checked")) {
                types[i] = '';
            }
            else {
                types[i] = fills[i];
            }
        }

        var selected = [];
        for (var i=0; i<types.length; i++) {
            var val = types[i];
            if (val){
                selected.push(val);
            }
        }
        data[1] = selected.join('_');
        set_data();
    }

    // Middleware token for AJAX call
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var data = [
        [],
        [],
        [],
        []
    ];

    // Keep types same length as number of study types
    var types = ['','','',''];

    // Individual selectors for booleans
    var tox = $('#id_toxicity');
    var eff = $('#id_efficacy');
    var dm = $('#id_disease');
    var cc = $('#id_cell_characterization');
    // Array of selectors
    var type_selectors = [tox,eff,dm,cc];
    // Array of abbreviations
    var fills = ['TOX','EFF','DM','CC'];

    var date = $('#id_start_date');
    var group = $('#id_group');
    var name = $('#id_name');

    //Need to have condition for adding vs. changing data
    get_center_id();
    get_types();
    data[2] = date.val();
    data[3] = name.val();

    //Needs an AJAX call to get centerID
    group.change(function (evt) {
        get_center_id();
    });

    //Get the types for each checkbox

    //Get the types for each checkbox
    $.each(type_selectors, function(index, value) {
        value.change(function (evt) {
            get_types();
        });
    });

//    tox.change(function (evt) {
//        get_types();
//    });
//
//    eff.change(function (evt) {
//        get_types();
//    });
//
//    dm.change(function (evt) {
//        get_types();
//    });
//
//    cc.change(function (evt) {
//        get_types();
//    });

    date.data("value", date.val());


    // Set interval to regularly check for new date
    setInterval(function () {
        var date_data = date.data("value"),
            val = date.val();

        if (date_data !== val) {
            date.data("value", val);
            data[2] = $('#id_start_date').val();
            set_data();
        }
    }, 100);

    name.on('input', function () {
        data[3] = $('#id_name').val();
        set_data();
    }).trigger('input');
});
