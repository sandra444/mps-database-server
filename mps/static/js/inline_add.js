$(document).ready(function () {

    // Note that this requires certain class name, add name, inlines name
    // Note that the selector that selects TABLES (not divs) with the name inlines

    var inlines = $('.inline');
    var next_id = inlines.length;
    var title = $('.inline')[0].id.split('-')[0];
    var add = $('.inline:last').html();

    $('#add_button').click(function() {
        var tag = '<tr class="inline" id="' + title + '-' + next_id + '">';
        // Use a regular expression to replace all the places where ID is needed
        // In case the RegExp looks a little obfuscated, it means to replace any number of digits that fall between two hyphens
        $(tag).appendTo($("table[name='inlines']")).html(add.replace(/\-\d+\-/g,'-'+ next_id +'-'));
        next_id += 1;
        // Set the hidden TOTAL_FORMS to be incremented, otherwise won't bother reading other inline
        $("input[id*='TOTAL_FORMS']").val(""+next_id);
    });

    // This selector will check all items with DELETE in the name, including newly created ones
    $( "body" ).on( "click", "input[name*='DELETE']", function(event) {
        // Use a regex to get the desired ID number
        // var thenum = thestring.match(/\d+$/)[0];
        var id = parseInt(event.target.id.match(/\d+/)[0]);

        // Prevent user from removing ALL inlines (can cause unexpected behavior)
        if ($("input[name*='DELETE']").length < 2) {
            // Uncheck
            $("input[name*='DELETE']").prop('checked', false);
            return;
        }

        // Exit the function if this is an update page (known via hidden div)
        // Really should just check if original class exists for the given row
        // Continue only if original class does not exist in the row
        // TODO scrap odd update hidden div thing
        if ($('#' + title + '-' + id + ' .original')[0]) {
            return;
        }

        // Remove the element
        $('#'+title+'-'+id).remove();

        // Need to find way to correctly decrement TOTAL_FORMS and next_id to avoid conflict
        // Rename all greater than deleted, next_id = inlines.length
        inlines = $('.inline');
        //console.log(inlines.length + " " + id);
        next_id = inlines.length;

        // Decrease TOTAL_FORMS
        $("input[id*='TOTAL_FORMS']").val(""+inlines.length);

        var end = inlines.length;
        for (var i=id+1; i<=end; i++){
            var current = $('#'+title+'-'+i);

            // Need to update values before creating the replacement text
            $('#'+ title +'-'+ i + ' input').each(function () {
                $(this).attr("value", this.value);
            });
            $('#'+ title +'-'+ i + ' select').each(function (){
                //console.log(this.id);
                $('#' + this.id + ' option[value="' + $(this).val() + '"]').attr("selected", true);
            });

            var replacement = current.html().replace(/\-\d+\-/g,'-'+ (i-1) +'-');
            //console.log(replacement);
            //console.log("Iter:" + i);
            var tag = '<tr class="inline" id="' + title + '-' + (i-1) + '">';
            $(tag).appendTo($("table[name='inlines']")).html(replacement);
            // Remove old
            current.remove();
        }
    });
});
