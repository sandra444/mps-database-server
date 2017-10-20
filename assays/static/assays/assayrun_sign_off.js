$(document).ready(function() {
    // Prevent CSS conflict with Bootstrap
    // $.fn.button.noConflict();

    var sign_off_confirm = $("#sign_off_confirm");

    var sign_off_confirm_warning = $('#sign_off_confirm_warning');

    var mark_reviewed_buttons = $('.mark_reviewed_button_group');

    var signed_off_selector = null;
    var mark_reviewed_label = null;
    var mark_reviewed_check = null;

    var dialog_title = 'Study Sign Off';

    function set_labels(owner) {
        if (signed_off_selector.prop('checked')) {
            mark_reviewed_check.show();
            if (owner) {
                mark_reviewed_label.text('Click Here to Remove Sign Off');
                sign_off_confirm_warning.html(
                    'Removing the Sign Off will allow permitted users to continue editing the Study\'s data.' +
                    '<br><br>It will also keep the data hidden from external users.' +
                    '<br><br>Are you sure you want to change the Sign Off status?'
                );

            }
            else {
                mark_reviewed_label.text('Click Here to Remove Sign Off');
                sign_off_confirm_warning.html(
                    'Removing the Sign Off will prevent consortium viewers from viewing this Study\'s data.' +
                    '<br><br>Are you sure you want to change the Sign Off status?'
                );
            }
        }
        else {
            mark_reviewed_check.hide();
            if (owner) {
                mark_reviewed_label.text('Click Here to Sign Off on this Study');
                sign_off_confirm_warning.html(
                    'Signing Off will prevent anyone, including you, from editing this Study and the data associated with it.' +
                    '<br><br>Signing Off will also allow consortium viewers to view this Study\'s data (granted all Stakeholders Sign Off as well)' +
                    '<br><br>Are you sure you want to change the Sign Off status?'
                );

            }
            else {
                mark_reviewed_label.text('Click Here to Sign Off on this Study');
                sign_off_confirm_warning.html(
                    'Signing Off will allow consortium viewers to view this Study\'s data (granted all other Stakeholders Sign Off as well)' +
                    '<br><br>Are you sure you want to change the Sign Off status?'
                );
            }
        }
    }

    sign_off_confirm.dialog({
        title: dialog_title,
        height:450,
        width:450,
        modal: true,
        closeOnEscape: true,
        autoOpen: false,
        // buttons: {
        // Yes: function() {
        //     signed_off_selector.prop('checked', !signed_off_selector.prop('checked'));
        //     set_labels();
        //     $(this).dialog("close");
        //     },
        // Cancel: function() {
        //     $(this).dialog("close");
        //     }
        // },
        buttons: [
        {
            text: 'Yes',
            id: 'sign_off_confirm_submit_button',
            click: function() {
                signed_off_selector.prop('checked', !signed_off_selector.prop('checked'));
                set_labels();
                $(this).dialog('close');
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
            var dialog_submit_button = $('#sign_off_confirm_submit_button');
            $('body').addClass('stop-scrolling');
            dialog_submit_button.button('disable');

            setTimeout(function() {
                dialog_submit_button.button('enable');
                dialog_submit_button.focus();
            }, 1500);
        }
    });
    sign_off_confirm.removeProp('hidden');

    mark_reviewed_buttons.click(function() {
        signed_off_selector = $(this).parent().parent().find('input');
        mark_reviewed_label = $(this).parent().parent().find('.mark_reviewed_label');
        mark_reviewed_check = $(this).parent().parent().find('.mark_reviewed_check');
        sign_off_confirm.dialog('open');

        // Set initial labels
        set_labels($(this).hasClass('owner'));
    });

    // Contrived, hide all checks:
    $('.mark_reviewed_check').hide();
});
