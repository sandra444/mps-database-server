//Get token
var middleware_token = getCookie('csrftoken');

function whittle(master,master_id,subject,next_model,next_filter) {
    $.ajax({
        url: "/assays_ajax",
        type: "POST",
        dataType: "json",
        data: {
            call: 'fetch_context',

            master: master,
            master_id: master_id,
            subject: subject,
            next_model: next_model,
            next_filter: next_filter,

            csrfmiddlewaretoken: middleware_token
        },
        success: function (json) {
            console.log(json.context);
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
