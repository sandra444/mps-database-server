$(document).ready(function () {
    var group_selector = $('#id_group');
    var center_name_selector = $('#center_name');
    var image_selector = $('#id_image');
    var image_display_selector = $('#image_display');
    var current_image_display_selector = $('#current_display');

    function get_center_id() {
        if (group_selector.val()) {
            $.ajax({
                url: "/assays_ajax/",
                type: "POST",
                dataType: "json",
                data: {
                    call: 'fetch_center_id',
                    id: group_selector.val(),
                    csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
                },
                success: function (json) {
                    center_name_selector.html(json.center_name);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
        else {
            center_name_selector.html('');
        }
    }

    // Need to have condition for adding vs. changing data
    get_center_id();

    // Needs an AJAX call to get centerID
    group_selector.change(function (evt) {
        get_center_id();
    });

    // Change image preview as necessary
    image_selector.change(function() {
        IMAGES.display_image(image_selector, image_display_selector, current_image_display_selector);
    });
});
