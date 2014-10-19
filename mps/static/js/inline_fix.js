$(document).ready(function () {
    var index = 0;

    for (i in $(".module")) {
        if ($(".module")[i].outerHTML.indexOf("<h2>Change Tracking</h2>") > -1){
            index = i;
            break;
        }
    }

    for (i in $(".module")) {
        if ($(".module")[i].outerHTML.indexOf("<h2>Reference Parameters</h2>") > -1){
            index = i;
            break;
        }
    }

    $( ".inline-group" ).insertBefore( $( ".module" )[index]);
});
