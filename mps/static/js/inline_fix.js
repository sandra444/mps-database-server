$(document).ready(function () {
    var index = 0;

    for (i in $(".module")) {
        if ($(".module")[i].outerHTML.indexOf("<h2>Change Tracking</h2>") > -1) {
            index = i;
            break;
        }
    }
    $( ".inline-group" ).insertBefore( $( ".module" )[index]);

# The following will move the inline in front of the Reference Parameters.
# Note that the following will generate an error if "Reference Parameters" does
# exist.  This is true in most cases and should be fixed at some point.

    for (i in $(".module")) {
        if ($(".module")[i].outerHTML.indexOf("<h2>Reference Parameters</h2>") > -1) {
            index = i;
            break;
        }
    }
    $( ".inline-group" ).insertBefore( $( ".module" )[index]);
});
