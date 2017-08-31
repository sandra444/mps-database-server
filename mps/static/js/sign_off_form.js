$(document).ready(function() {
    var sign_off_confirm = $("#sign_off_confirm");
    var study_submit = $('#study_submit').val();

    var sign_off_confirm_warning = $('#sign_off_confirm_warning');
    var mark_reviewed_label = $('#mark_reviewed_label');
    var mark_reviewed_check = $('#mark_reviewed_check');
    var mark_reviewed_button_group = $('#mark_reviewed_button_group');

    var signed_off_selector = $('#id_signed_off');

    var dialog_title = '';

    if (study_submit) {
        dialog_title = 'Study Sign Off';
        sign_off_confirm_warning.html('Signing off will prevent anyone from editing this Study and the data associated with it.<br><br>Are you sure you want to change the sign off status?');
    }
    else {
        dialog_title = 'Entry Validation';
        sign_off_confirm_warning.html('If this is checked, the entry will be marked as Validated.<br><br>Are you sure you want to change the validated status?');
    }

    function set_labels() {
        if (signed_off_selector.prop('checked')) {
            mark_reviewed_check.show();
            if (study_submit) {
                mark_reviewed_label.text('Click Here to Remove Sign Off');
            }
            else {
                mark_reviewed_label.text('Click Here to Remove Validated Mark');
            }
        }
        else {
            mark_reviewed_check.hide();
            if (study_submit) {
                mark_reviewed_label.text('Click Here to Sign Off on this Study');
            }
            else {
                mark_reviewed_label.text('Click Here to Mark this Entry as Validated');
            }
        }
    }

    sign_off_confirm.dialog({
        title: dialog_title,
        height:325,
        modal: true,
        closeOnEscape: true,
        autoOpen: false,
        buttons: {
        Yes: function() {
            signed_off_selector.prop('checked', !signed_off_selector.prop('checked'));
            set_labels();
            $(this).dialog("close");
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
    sign_off_confirm.removeProp('hidden');

    mark_reviewed_button_group.click(function() {
        sign_off_confirm.dialog('open');
    });

    // Set initial labels
    set_labels();
});
