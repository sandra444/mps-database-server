$(document).ready(function () {

    var row_field = document.getElementById('id_row_labels');
    console.log(row_field.value);
    console.log(row_field);

    //not working to change issue with assay device readouts

//    row_field.change( function() {

        if ( row_field.value.split().length == 1 ){
            var start = row_field.value;
            var rows = document.getElementById('id_number_of_rows').value;
            var input = "";

            for ( var i = start; i <= rows; i++) {
                input += i + " ";
            }
            console.log(input);
            row_field.value = input;

        }
//    });

});
