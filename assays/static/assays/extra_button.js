$(document).ready(function () {

    var row_field = $('#id_row_labels');

       row_field.change( function() {

        if ( row_field[0].value.split(" ").length == 1 ){

            var start = row_field[0].value;
            var rows = document.getElementById('id_number_of_rows').value;
            var input = "";

            for ( var i = 1; i <= rows; i++) {
                input += start + " ";
                start++;
            }
            console.log(input);
            row_field[0].value = input;

        }
        });

});
