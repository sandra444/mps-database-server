$(function() {
    // Get the CSRF token
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var subtype = $('#id_cell_subtype');
    var type = $('#id_cell_type');

    // Setup date pickers
    var date = $("#id_receipt_date");
    var curr_date = date.val();
    //Add datepicker to receipt date
    date.datepicker();
    date.datepicker("option", "dateFormat", "yy-mm-dd");
    date.datepicker("setDate", curr_date);

    var isolation = $("#id_isolation_datetime");
    var curr_isolation = isolation.val();
    //Add datepicker to isolation
    isolation.datepicker();
    isolation.datepicker("option", "dateFormat", "yy-mm-dd");
    isolation.datepicker("setDate", curr_isolation);

    function whittle_subtype(cell_type) {
        $.ajax({
            url: "/cellsamples_ajax",
            type: "POST",
            dataType: "json",
            data: {
                call: 'get_cell_subtypes',
                cell_type: cell_type,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                var options = json.context;
                var current_value = subtype.val();
                subtype.html(options);
                if ($('#id_cell_subtype option[value='+current_value+']')[0]) {
                    subtype.val(current_value);
                }
                else {
                    subtype.val('');
                }
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Setup whittling
    type.change(function() {
        whittle_subtype(type.val());
    });

    // Initial whittle
    whittle_subtype(type.val());
});
