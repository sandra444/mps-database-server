// This file contains functions for displaying images
var IMAGES = {};

$(document).ready(function () {
    IMAGES.display_image = function(image, image_display, current_display) {
        var file = image[0].files[0];

        if (file) {
            current_display.hide();
            var image_type = /image.*/;

            if (file.type.match(image_type)) {
                var reader = new FileReader();

                reader.onload = function (e) {
                    image_display.html('');

                    var img = new Image();
                    img.src = reader.result;
                    img.id = 'preview_' + image.attr('id');

                    image_display.append(img);
                    $('#'+img.id).addClass(
                        'img-responsive center-block padded-bottom'
                    );
                }

                reader.readAsDataURL(file);
            }

            else {
                image_display.html('File not supported!');
            }
        }
        else {
            current_display.show();
        }
    }
});
