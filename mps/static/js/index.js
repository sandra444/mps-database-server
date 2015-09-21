$(function() {
    var initial = $('#id_app').val();

    if (initial == 'Bioactivities') {
        $("#bioactivities_search").show();
        $("#search_bar").hide();
    }

    $('#search_options li').click(function(e){
        $("#bioactivities_search").show("slow");
        $("#search_bar").hide("slow");
        $("#id_app").val("Bioactivities");
    });

    $('#back').click(function(){
        $("#bioactivities_search").hide("slow");
        $("#search_bar").show("slow");
        $("#id_app").val("Global");
    })
});
