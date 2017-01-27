// This file adds datepickers to date fields
// It currently is only used in Chip Setups, but will be added elsewhere soon
// TODO to be refactored
$(document).ready(function() {
    // Function to apply the datepickers
    function apply_date_pickers() {
        // Only iterate through elements with datepicker class
        $.each($('.datepicker-input'), function() {
            // Only apply the datepicker if necessary
            // Will ignore those with 'hasDatepicker'
            if(!$(this).hasClass('hasDatepicker')) {
                var curr_date = $(this).val();
                //Add datepicker to assay and readout start time
                $(this).datepicker();
                $(this).datepicker("option", "dateFormat", "yy-mm-dd");
                $(this).datepicker("setDate", curr_date);
            }
        });
    }

    // NOTE Considering datetime fields only appear as an inline in chip setup:
    // perhaps this file should be trimmed
    // NAIVE: Just checks the datepickers literally every click
    $(document).on('click', function() {
        apply_date_pickers();
    });

    // Initial apply
    apply_date_pickers();
});
