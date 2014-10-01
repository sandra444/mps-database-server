$(document).ready(function () {

    var data = [[],[],[]];
    var id = $('#id_assay_run_id');

    //Needs an AJAX call to get centerID
    $('#id_center_id').change(function(evt) {
        data[0] = $('#id_center_id').val();
        id.html(data.join('-'));
    });

    //Need to find a way to handle people clicking the widgets (today's date, etc)
    $('#id_start_date_0').on('input', function() {
        data[1] = $('#id_start_date_0').val();
        id.html(data.join('-'));
    }).trigger('input');

    $('#id_name').on('input', function() {
        data[2] = $('#id_name').val();
        id.html(data.join('-'));
    }).trigger('input');
});
