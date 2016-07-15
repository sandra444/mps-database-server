// This script adds previews for images
$(document).ready(function () {
    var model_image = $('#id_model_image');
    var image_display = $('#image_display');
    var current_display = $('#current_display');

    // Change cell_image preview as necessary
    model_image.change(function() {
        IMAGES.display_image(model_image, image_display, current_display);
    });
});
