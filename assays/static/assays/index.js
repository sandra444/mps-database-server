$(document).ready(function() {
    $('#studies').DataTable( {
        "iDisplayLength": 50,
        // Initially sort on start date (descending), not ID
        "order": [ 2, "desc" ]
    });
});
