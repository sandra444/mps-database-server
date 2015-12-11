// Code for handling help dialog boxes
$(document).ready(function() {
    // Make the dialog box
    var dialog = $('#help_dialog');
    dialog.dialog({
        width: 1025,
        height: 500,
        closeOnEscape: true,
        autoOpen: false,
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            $('body').addClass('stop-scrolling');
        }
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
