// Global functions for cookies
// TODO CHANGE FILES TO USE THESE
window.COOKIES = {};

$(document).ready(function() {
    window.COOKIES.get_cookie = function (name) {
        var cookie_value = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookie_value;
    };

    window.COOKIES.csrfmiddlewaretoken = window.COOKIES.get_cookie('csrftoken');
});
