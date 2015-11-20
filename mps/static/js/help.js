// Code for handling help dialog boxes
$(document).ready(function() {
    // Make the dialog box
    var dialog = $('#help_dialog');
    dialog.dialog({
        width: 900,
        height: 500,
        closeOnEscape: true,
        autoOpen: false
    });
    // Remove hidden attribute
    dialog.removeProp('hidden');

    // Clicking the help button will spawn the help dialog
    $('#help_button').click(function() {
        dialog.dialog('open');
        // Remove focus
        $('.ui-dialog :button').blur();
    });
});
