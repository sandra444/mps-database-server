$(function() {
    var compounds = [];

    function better_search(req, responseFn) {
        var re = $.ui.autocomplete.escapeRegex(req.term);
        var pattern1 = new RegExp("^"+re, "i");
        var a = $.grep(compounds, function(item, index){return pattern1.test(item);}); //build array item begins with input string
        var b = $.grep(compounds, function(item, index){return ((item.toLowerCase()).indexOf(re.toLowerCase())>0);}); //build array items with input string somewhere
        responseFn(a.concat(b));
    }

    function get_compounds() {
        $.ajax({
            url: "/compounds_ajax/",
            type: "POST",
            dataType: "json",
            data: {
                call: 'fetch_compound_list',
                csrfmiddlewaretoken: window.COOKIES.csrfmiddlewaretoken
            },
            success: function (json) {
                compounds = json;
                // Apply autocomplete after getting JSON
                $("#id_compound").autocomplete({
                    source: better_search
                });
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }

    // Make the AJAX call
    get_compounds();
});
