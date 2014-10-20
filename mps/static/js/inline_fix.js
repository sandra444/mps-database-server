$(document).ready(function () {
    var index = 0;

    // If sufficient number of modules
    if ($(".module")[1]) {

        // Check each module. If it is, desired stop and add inline before that module
        for (i in $(".module")) {
            if ($(".module")[i].outerHTML.indexOf("<h2>Change Tracking</h2>") > -1 ||
                $(".module")[i].outerHTML.indexOf("<h2>Reference Parameters</h2>") > -1) {
                index = i;
                break;
            }
        }
        $(".inline-group").insertBefore($(".module")[index]);

    }
});

