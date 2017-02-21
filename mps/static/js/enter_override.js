// Adding this script will override enter such that it will display a modal confirmation
// This script will additionally help prevent the multiple submission issue

// This global variable checks whether there is an exception to the override
window.OVERRIDE = {
    'exceptions': []
};

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

    // Prevent CSS conflict with Bootstrap
    $.fn.button.noConflict();

    // Add the dialog box
    $("#content").append('<div hidden id="dialog-confirm" title="Submit this form?"><p><span class="glyphicon glyphicon-exclamation-sign text-danger" aria-hidden="true" style="float:left; margin:0 7px 20px 0;"></span>Are you sure you want to submit the form?</p></div>');

    var dialogConfirm = $("#dialog-confirm");

    dialogConfirm.dialog({
        height:200,
        modal: true,
        closeOnEscape: true,
        autoOpen: false,
        buttons: {
        Submit: function() {
            $("#submit").trigger("click");
            },
        Cancel: function() {
            $(this).dialog("close");
            }
        },
        close: function() {
            $('body').removeClass('stop-scrolling');
        },
        open: function() {
            $('body').addClass('stop-scrolling');
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
