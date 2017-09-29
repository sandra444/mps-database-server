$(document).ready(function () {
    // Prevent CSS conflict with Bootstrap
    // $.fn.button.noConflict();

    var overwrite_confirm = $("#overwrite_confirm");
    var overwrite_was_confirmed = false;

    overwrite_confirm.dialog({
        height:250,
        modal: true,
        closeOnEscape: true,
        autoOpen: false,
        // buttons: {
        // Submit: function() {
        //     // Submit the form if so
        //     overwrite_was_confirmed = true;
        //     $('#submit').trigger('click');
        //     $('form').disable();
        //     },
        // Cancel: function() {
        //     $(this).dialog("close");
        //     }
        // },
        buttons: [
        {
            text: 'Overwrite',
            disabled: true,
            id: 'overwrite_confirm_submit_button',
            click: function() {
                overwrite_was_confirmed = true;
                $('#submit').trigger('click');
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
            $('body').addClass('stop-scrolling');

            setTimeout(function() {
                $('#overwrite_confirm_submit_button').button('enable');
            }, 1500);
        }
    });
    overwrite_confirm.removeProp('hidden');

    // TODO MAKE SURE THIS DOES NOT INTERRUPT OTHER TRIGGERS
    $('form').submit(function(event) {
        if (!overwrite_was_confirmed) {
            // Stop propagation
            event.preventDefault();
            overwrite_confirm.dialog('open');
        }
    });
});
