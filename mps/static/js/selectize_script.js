// Experiment with dropdown searching using selectize.js
$(document).ready(function () {
    $('select').each(function(i, obj){
        var current_select = $(obj);
        if (!current_select.parent().hasClass('no-selectize') && !current_select.hasClass('no-selectize')) {
            current_select.selectize({
                diacritics: true
            });
        }
    });

    // SLOPPY TRIGGERS FOR REFRESHING DROPDOWNS
    // DUMB, BAD
    // TESTING: Comment out for the moment
    // $('.selectize-input').click(function() {
    //     // Descendent selectors are bad
    //     var current_selectize_input = $(this).find('input');
    //     var current_id = current_selectize_input.attr('id').replace('-selectized', '');
    //     var current_input = $('#' + current_id);
    //     var current_selectize = current_input[0].selectize;
    //
    //     // Get the new dropdown
    //     // Start spinner
    //     window.spinner.spin(
    //         document.getElementById("spinner")
    //     );
    //     $.ajax({
    //         url: "/assays_ajax/",
    //         type: "POST",
    //         dataType: "json",
    //         data: {
    //             call: 'fetch_dropdown',
    //             csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken,
    //             app: current_input.attr('data-app'),
    //             model: current_input.attr('data-model'),
    //         },
    //     })
    //     .done(function (json) {
    //         // Stop spinner
    //         window.spinner.stop();
    //
    //         var options = json.dropdown;
    //         var current_value = current_input.val();
    //         current_selectize.clear();
    //         current_selectize.clearOptions();
    //
    //         current_selectize.addOption(options);
    //
    //         if (current_value) {
    //             current_selectize.setValue(current_value);
    //         }
    //
    //         current_selectize.blur();
    //         current_selectize.focus();
    //     })
    //     .fail(function (xhr, errmsg, err) {
    //         // Stop spinner
    //         window.spinner.stop();
    //
    //         console.log(xhr.status + ": " + xhr.responseText);
    //     });
    // });
});
