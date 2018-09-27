// Experiment with dropdown searching using selectize.js
$(document).ready(function () {
    $("select").each(function(i, obj){
        if(!$(obj).parent().hasClass('no-selectize') && !$(obj).hasClass('no-selectize')) {
            $(obj).selectize({
                diacritics: true
            });
        }
    });
});
