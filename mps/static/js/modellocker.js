$(document).ready(function() {
    // Effects ADD/CHANGE object pages
    // Locks entries for editing
    if ($('#id_locked').prop('checked')) {
        $('input[type=text]').prop('disabled', true);
        $('input[type=radio]').prop('disabled', true);
        $('input[type=password]').prop('disabled', true);
        $('input[type=checkbox]:not(#id_locked)').prop('disabled', true);
        $('select').prop('disabled', true);
        $('textarea').prop('disabled', true);
        $('input[type=button]').prop('disabled', true);
        
        // fields need to be enabled before submitting to avoid Django save errors
        $('input[type=submit]').click(function() {
            $('input[type=text]').prop('disabled', false);
            $('input[type=radio]').prop('disabled', false);
            $('input[type=password]').prop('disabled', false);
            $('input[type=checkbox]:not(#id_locked)').prop('disabled', false);
            $('select').prop('disabled', false);
            $('textarea').prop('disabled', false);
            $('input[type=button]').prop('disabled', false);  
        });
    }
});
