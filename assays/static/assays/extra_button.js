$(document).ready(function () {

    var row_field = document.getElementById('id_row_labels');
    var array = [row_field];
    console.log(array);

    row_field.change(function() {
        if ( row_field.value.split().length == 1 ){
            var start = row_field.value;
            var rows = document.getElementById('id_number_of_rows').value;

            if ( rows == undefined ){
            }
            else {

                var input = "";
                for ( var i = start; i <= rows; i++){
                    input += i + " ";
                }
                row_field.value(input);

            }
        }
    }, false);

});
