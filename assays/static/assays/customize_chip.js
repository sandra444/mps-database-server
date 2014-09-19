$(document).ready(function () {
    $('<div id="csv_table" align="center" style="margin-top: 10px;margin-bottom: 10px;">').appendTo('body').html("<table class='layout-table' style='width: 99%;'><tbody><tr><th>Time</th><th>Field</th><th>Raw Data</th></tr><tr><th><br><br></th><th><br><br></th><th><br><br></th></tr><tr><th><br><br></th><th><br><br></th><th><br><br></th></tr></tbody></table>");
    $( "#csv_table" ).insertBefore( $( ".module" )[3]);
    
    $('#id_file').change(function(evt) {
        console.log("A change has been registered");
        console.log($('#id_file')[0].files[0]);
        
        var file = $('#id_file')[0].files[0];
        getText(file);
    });
    
    var getText = function (readFile) {
        var reader = new FileReader();
        reader.readAsText(readFile, "UTF-8");
        reader.onload = loaded;
    }
    
    var loaded = function (evt) {
        var fileString = evt.target.result;
        console.log(fileString);
    }
    
    var parseAndReplace = function (csv) {
        
    }   
    
});