$(document).ready(function () {

    //Note that this requires certain class name, add name, inlines name

    var inlines = $('.inline');
    var next_id = inlines.length;
    var title = $('.inline')[0].id.split('-')[0];
    var add = $('.inline:first').html();

    $('#add_button').click(function() {
        var tag = '<div class="inline" id="' + title + '-' + next_id + '">';
        // Use a regular expression to replace all the places where ID is needed
        $(tag).appendTo($("div[name='inlines']")).html(add.replace(new RegExp('-0-', 'g'),'-'+next_id+'-'));
        next_id += 1;
        // Set the hidden TOTAL_FORMS to be incremented, otherwise won't bother reading other inline
        $("input[id*='TOTAL_FORMS']").val(""+next_id);
    });
});
