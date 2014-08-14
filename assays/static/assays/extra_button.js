$(document).ready(function () {

    var row_field_dom = $('#id_row_labels');
    var row_labels = document.getElementById('id_row_labels');

       row_field_dom.change( function() {

        if ( row_labels.value.split(" ").length == 1 ){

            var start = row_labels.value;
            var rows = document.getElementById('id_number_of_rows').value;
            var input = "";

            for ( var i = 1; i <= rows; i++) {
                input += start + " ";
                start++;
            }
            console.log(input);
            row_labels.value = input;

        }
        });

});
