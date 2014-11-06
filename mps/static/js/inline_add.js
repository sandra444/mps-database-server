$(document).ready(function () {
    var inlines = $('.inline');
    var next_id = inlines.length;
    var title = $('.inline')[0].id.split('-')[0];
    var add = $('.inline:first').html();

    $('#add_button').click(function() {
        var tag = '<div class="inline" id="' + title + '-' + next_id + '">';
        $(tag).appendTo('#inlines').html(add);
        next_id += 1;
    });
});
