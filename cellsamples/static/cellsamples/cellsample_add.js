$(function() {
    var date = $("#id_receipt_date");
    var curr_date = date.val();
    //Add datepicker to receipt date
    date.datepicker();
    date.datepicker("option", "dateFormat", "yy-mm-dd");
    date.datepicker("setDate", curr_date);

    var isolation = $("#id_isolation_datetime");
    var curr_isolation = isolation.val();
    //Add datepicker to isolation
    isolation.datepicker();
    isolation.datepicker("option", "dateFormat", "yy-mm-dd");
    isolation.datepicker("setDate", curr_isolation);
});
