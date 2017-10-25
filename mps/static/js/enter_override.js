// Adding this script will override enter such that it will display a modal confirmation
// This script will additionally help prevent the multiple submission issue

// This global variable checks whether there is an exception to the override
window.OVERRIDE = {
    'exceptions': []
};

$(document).ready(function () {
    // On submit, disable all submit buttons
    $('form').submit(function () {
        $(':submit').attr('disabled', 'disabled');
        return true;
    });

    // Prevent CSS conflict with Bootstrap
    $.fn.button.noConflict();

    // Add the dialog box
    // $("#content").append('<div hidden id="enter_dialog_confirm" title="Submit this form?"><p><span class="glyphicon glyphicon-exclamation-sign text-danger" aria-hidden="true" style="float:left; margin:0 7px 20px 0;"></span>Are you sure you want to submit the form?</p></div>');

    var dialogConfirm = $("#enter_dialog_confirm");

    dialogConfirm.dialog({
        height:250,
        modal: true,
        closeOnEscape: true,
        autoOpen: false,
        buttons: [
        {
            text: 'Submit',
            // id: 'enter_dialog_confirm_submit_button',
            click: function() {
                $("#submit").trigger("click");
            }
        },
        {
            text: 'Cancel',
            click: function() {
               $(this).dialog("close");
            }
        }],
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            // var dialog_submit_button = $('#enter_dialog_confirm_submit_button');
            $('body').addClass('stop-scrolling');
            // dialog_submit_button.button('disable');
            //
            // setTimeout(function() {
            //     dialog_submit_button.button('enable');
            //     dialog_submit_button.focus();
            // }, 1500);
            // Blur to prevent double enter inadvertant accepts
            $('.ui-dialog :button').blur();
        }
    });
    dialogConfirm.removeProp('hidden');

    $(window).keydown(function(event) {
        if(event.keyCode == 13) {
            // Make sure this isn't the exception
            var exception_focused = false;
            if(window.OVERRIDE.exceptions) {
                $.each(window.OVERRIDE.exceptions, function(index, exception_selector) {
                    if(exception_selector.is(':focus')) {
                        exception_focused = true;
                    }
                });
            }

            // If this is an exception
            if(exception_focused) {
                // Just prevent default if this is an exception
                event.preventDefault();
                return false;
            }
            // Only perform the override if an input is focused
            else if($('input:focus')[0]) {
                event.preventDefault();
                dialogConfirm.dialog('open');
                return false;
            }
        }
    });

    // Increase the height of the footer to ensure it is not obscured
    $('#footer').height("+=150")
});
