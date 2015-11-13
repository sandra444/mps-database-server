$(document).ready(function () {
    // Open and then close dialog so it doesn't get placed in window itself
    var dialog = $('#dialog');
    dialog.dialog();
    dialog.dialog('close');
    dialog.removeProp('hidden');

    // Clicking the help button will spawn the help dialog
    $('#help_button').click(function() {
        $("#dialog").dialog({
            width: 900,
            height: 500
        });
    });
});
