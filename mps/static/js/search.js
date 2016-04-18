// This script adds additional functionality to the global search
$(document).ready(function () {
    var filter = [];
    var at_least_one_checked = $("#filter [type=checkbox]").is(':checked');
    var middleware_token = getCookie('csrftoken');

    function filter_results() {
        // Default to showing everything (ie, only run if filters selected)
        if (filter.length > 0) {
            $('.result-group').hide();
            for(var x in filter) {
                $(filter[x]).show();
            }
        }
        else {
            $('.result-group').show();
        }
    }

    function init_checkbox(box) {
        // Must remove period for ID
        var id = '#' + box.value.replace('.','');
        // Add if newly checked
        if (box.checked) {
            filter.push(id);
        }
        // Mark if it was not part of the search
        else {
            if (at_least_one_checked) {
                $(box).parent().parent().addClass('bg-danger');
            }
        }
    }

    function examine_checkbox(box) {
        // Must remove period for ID
        var id = '#' + box.value.replace('.','');
        // Add if newly checked
        if (box.checked) {
            filter.push(id);
        }
        // Remove if unchecked
        else {
            filter = _.without(filter, id);
        }
    }

// This was used to remove empty sections when front-end group filtering was performed
// Group filtering is now done on the backend
//    $('.result-group').each(function() {
//         if(!$(this)[0].children[1].children[0]) {
//             $(this).remove();
//         }
//    });

   // Initial values
   $("#filter [type=checkbox]").each(function() {
       init_checkbox(this);
   });
   filter_results();

    // Listener for change
    $("#filter [type=checkbox]").change(function() {
        //console.log(this.value);
        examine_checkbox(this);
        filter_results();
    });

    $("#clear_filters").click(function() {
        $("[type=checkbox]").prop('checked',false).trigger('change');
    });

    $("#id_q").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/search_ajax",
                type: "POST",
                dataType: "json",
                data: {
                    call: 'fetch_global_search_suggestions',
                    text: request.term,
                    csrfmiddlewaretoken: middleware_token
                },
                success: function (json) {
                    response(json);
                },
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        },
        minLength: 2
    });
});
