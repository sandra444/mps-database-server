$(function() {
    // Get the CSRF token
    var middleware_token = $('[name=csrfmiddlewaretoken]').attr('value');

    var cell_image = $('#id_cell_image');
    var image_display = $('#image_display');
    var current_display = $('#current_display');

    var subtype = $('#id_cell_subtype');
    var type = $('#id_cell_type');

    // Setup date pickers
    var date = $("#id_receipt_date");
    var current_date = date.val();
    //Add datepicker to receipt date
    date.datepicker();
    date.datepicker("option", "dateFormat", "yy-mm-dd");
    date.datepicker("setDate", current_date);

    var isolation = $("#id_isolation_datetime");
    var current_isolation = isolation.val();
    //Add datepicker to isolation
    isolation.datepicker();
    isolation.datepicker("option", "dateFormat", "yy-mm-dd");
    isolation.datepicker("setDate", current_isolation);

    function whittle_subtype(cell_type) {
        $.ajax({
            url: "/cellsamples_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                call: 'get_cell_subtypes',
                cell_type: cell_type,
                csrfmiddlewaretoken: middleware_token
            },
            success: function (json) {
                var options = json.dropdown;
                var current_value = subtype.val();
                subtype.html(options);
                if (current_value && $('#id_cell_subtype option[value='+current_value+']')[0]) {
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

    // Change cell_image preview as necessary
    cell_image.change(function() {
        IMAGES.display_image(cell_image, image_display, current_display);
    });

    // Setup whittling
    type.change(function() {
        whittle_subtype(type.val());
    });

    // Initial whittle
    whittle_subtype(type.val());
});
