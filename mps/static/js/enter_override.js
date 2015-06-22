// Adding this script will override enter such that it will display a modal confirmation
// This script will additionally help prevent the multiple submission issue
$(document).ready(function () {
    // On submit, disable all submit buttons
    // This only really matters on add pages and causes a bug on update pages when 'cancel' is selected
    // if 'Edit ' in h1 is a crude test to determine whether update or not
    if (!($('h1').first().text().indexOf('Edit ') > -1)) {
        $('form').submit(function () {
            $(':submit').attr('disabled', 'disabled');
            return true;
        });
    }

    // Add the dialog box
    $("#content").append('<div hidden id="dialog-confirm" title="Submit this form?"><p><span class="glyphicon glyphicon-exclamation-sign text-danger" aria-hidden="true" style="float:left; margin:0 7px 20px 0;"></span>Are you sure you want to submit the form?</p></div>');

    var dialogConfirm = $("#dialog-confirm");

    dialogConfirm.dialog({
        height:200,
        modal: true,
        buttons: {
        Submit: function() {
            $("#submit").trigger("click");
            },
        Cancel: function() {
            $(this).dialog("close");
            }
        }
    });

    dialogConfirm.dialog('close');
    dialogConfirm.removeProp('hidden');

    $(window).keydown(function(event){
        if(event.keyCode == 13) {
            // Only perform the override if an input is focused
            if($('input:focus')[0]) {
                event.preventDefault();
                dialogConfirm.dialog('open');
                return false;
            }
        }
    });
});
