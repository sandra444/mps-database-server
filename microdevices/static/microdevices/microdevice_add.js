// This script adds previews for images
$(document).ready(function () {
    var device_image = $('#id_device_image');
    var device_image_display = $('#device_image_display');
    var device_image_current_display = $('#device_current_display');

    var cross_section_image = $('#id_device_cross_section_image');
    var cross_section_image_display = $('#cross_section_image_display');
    var cross_section_current_display = $('#cross_section_current_display');

    // Change device preview as necessary
    device_image.change(function() {
        IMAGES.display_image(device_image, device_image_display, device_image_current_display);
    });

    // Change cross section preview as necessary
    cross_section_image.change(function() {
        IMAGES.display_image(cross_section_image, cross_section_image_display, cross_section_current_display);
    });
});
