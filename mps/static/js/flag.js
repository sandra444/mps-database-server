// This script will deal with flagging records for review
$(document).ready(function () {

    var flag = $('#flag');
    var check = $("#id_flagged");
    var notes = $('#notes_for_flag');

    $('[data-toggle="popover"]').popover({html : true});

    flag.click( function() {
        var current_check = check.prop('checked');
        check.prop('checked',!current_check);
        notes.toggle('slow');
        if (check.prop('checked')) {
            flag.addClass('btn-danger');
        }
        else {
            flag.removeClass('btn-danger')
        }
    });
});
