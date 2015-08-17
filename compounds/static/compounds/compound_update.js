// TODO This file really should not exist
// TODO This was made in the interest of time, but it makes more sense to modify inline_add to be general
// Perhaps there will not be any more models with multiple inlines, but perhaps not so it is something I should look in to
$(document).ready(function () {

    // Note that this requires certain class name, add name, inlines name
    // Note that the selector that selects TABLES (not divs) with the name inlines

    var inlines_property = $('#compoundproperty_set-group .inline');
    var next_id_property = inlines_property.length;
    var title_property = 'property';
    var add_property = $('#compoundproperty_set-group .inline:last').html();

    $('#add_button_property').click(function() {
        var tag = '<tr class="inline" id="' + title_property + '-' + next_id_property + '">';
        // Use a regular expression to replace all the places where ID is needed
        // In case the RegExp looks a little obfuscated, it means to replace any number of digits that fall between two hyphens
        $(tag).appendTo($("table[name='inlines_property']")).html(add_property.replace(/\-\d+\-/g,'-'+ next_id_property +'-'));
        next_id_property += 1;
        // Set the hidden TOTAL_FORMS to be incremented, otherwise won't bother reading other inline
        $("#id_compoundproperty_set-TOTAL_FORMS").val(""+next_id_property);
    });

    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on( "click", "#compoundproperty_set-group input[name*='DELETE']", function(event) {
        // Use a regex to get the desired ID number
        // var thenum = thestring.match(/\d+$/)[0];
        var id = parseInt(event.target.id.match(/\d+/)[0]);

        // Prevent user from removing ALL inlines (can cause unexpected behavior)
        if ($("#compoundproperty_set-group input[name*='DELETE']").length < 2) {
            // Uncheck
            $("input[name*='DELETE']").prop('checked', false);
            return;
        }

        // Exit the function if this is an update page (if it has an original, it already exists)
        if ($('#' + title_property + '-' + id + ' .original')[0]) {
            return;
        }

        // Remove the element
        $('#'+title_property+'-'+id).remove();

        // Need to find way to correctly decrement TOTAL_FORMS and next_id to avoid conflict
        // Rename all greater than deleted, next_id = inlines.length
        inlines_property = $('#compoundproperty_set-group .inline');
        next_id_property = inlines_property.length;

        // Decrease TOTAL_FORMS
        $("#id_compoundproperty_set-TOTAL_FORMS").val(""+inlines_property.length);

        var end = inlines_property.length;
        for (var i=id+1; i<=end; i++){
            var current = $('#'+title_property+'-'+i);

            // Need to update values before creating the replacement text
            // Add values to input
            $('#'+ title_property +'-'+ i + ' input').each(function () {
                $(this).attr("value", this.value);
            });
            // Add selected attribute to selected option of each select
            $('#'+ title_property +'-'+ i + ' select').each(function (){
                //console.log(this.id);
                $('#' + this.id + ' option[value="' + $(this).val() + '"]').attr("selected", true);
            });

            var replacement = current.html().replace(/\-\d+\-/g,'-'+ (i-1) +'-');
            //console.log(replacement);
            //console.log("Iter:" + i);
            var tag = '<tr class="inline" id="' + title_property + '-' + (i-1) + '">';
            $(tag).appendTo($("table[name='inlines_property']")).html(replacement);
            // Remove old
            current.remove();
        }
    });

    var inlines_summary = $('#compoundsummary_set-group .inline');
    var next_id_summary = inlines_summary.length;
    var title_summary = 'summary';
    var add_summary = $('#compoundsummary_set-group .inline:last').html();

    $('#add_button_summary').click(function() {
        var tag = '<tr class="inline" id="' + title_summary + '-' + next_id_summary + '">';
        // Use a regular expression to replace all the places where ID is needed
        // In case the RegExp looks a little obfuscated, it means to replace any number of digits that fall between two hyphens
        $(tag).appendTo($("table[name='inlines_summary']")).html(add_summary.replace(/\-\d+\-/g,'-'+ next_id_summary +'-'));
        next_id_summary += 1;
        // Set the hidden TOTAL_FORMS to be incremented, otherwise won't bother reading other inline
        $("#id_compoundsummary_set-TOTAL_FORMS").val(""+next_id_summary);
    });

    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on( "click", "#compoundsummary_set-group input[name*='DELETE']", function(event) {
        // Use a regex to get the desired ID number
        // var thenum = thestring.match(/\d+$/)[0];
        var id = parseInt(event.target.id.match(/\d+/)[0]);

        // Prevent user from removing ALL inlines (can cause unexpected behavior)
        if ($("#compoundsummary_set-group input[name*='DELETE']").length < 2) {
            // Uncheck
            $("input[name*='DELETE']").prop('checked', false);
            return;
        }

        // Exit the function if this is an update page (if it has an original, it already exists)
        if ($('#' + title_summary + '-' + id + ' .original')[0]) {
            return;
        }

        // Remove the element
        $('#'+title_summary+'-'+id).remove();

        // Need to find way to correctly decrement TOTAL_FORMS and next_id to avoid conflict
        // Rename all greater than deleted, next_id = inlines.length
        inlines_summary = $('#compoundsummary_set-group .inline');
        next_id_summary = inlines_summary.length;

        // Decrease TOTAL_FORMS
        $("#id_compoundsummary_set-TOTAL_FORMS").val(""+inlines_summary.length);

        var end = inlines_summary.length;
        for (var i=id+1; i<=end; i++){
            var current = $('#'+title_summary+'-'+i);

            // Need to update values before creating the replacement text
            // Add values to input
            $('#'+ title_summary +'-'+ i + ' textarea').each(function () {
                $(this).text(this.text());
            });
            // Add selected attribute to selected option of each select
            $('#'+ title_summary +'-'+ i + ' select').each(function (){
                //console.log(this.id);
                $('#' + this.id + ' option[value="' + $(this).val() + '"]').attr("selected", true);
            });

            var replacement = current.html().replace(/\-\d+\-/g,'-'+ (i-1) +'-');
            //console.log(replacement);
            //console.log("Iter:" + i);
            var tag = '<tr class="inline" id="' + title_summary + '-' + (i-1) + '">';
            $(tag).appendTo($("table[name='inlines_summary']")).html(replacement);
            // Remove old
            current.remove();
        }
    });
});
