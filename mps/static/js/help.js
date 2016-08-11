$(document).ready(function () {
    // Resolve anchors going to the incorrect location
    var offset = 60;

    $('.navbar li a').click(function(event) {
        event.preventDefault();
    $('html, body').animate({
            scrollTop: $($(this).attr('href')).offset().top -offset
        }, 500);
    });

    var initial_hash = window.location.hash;
    if (initial_hash) {
        $('html, body').animate({
            scrollTop: $(initial_hash).offset().top - offset
        }, 500);
    }

    // Call datatables for glossary
    $('#glossary_table').DataTable({
        dom: 'B<"row">lfrtip',
        "iDisplayLength": 10
    });
});
