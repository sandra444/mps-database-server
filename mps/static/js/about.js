$(document).ready(function () {
    // Resolve anchors going to the incorrect location
    var offset = 60;


    // Activate carousel
    $("#myCarousel").carousel();

    // Enable carousel control
    $(".carousel-control-prev").click(function(){
        $("#myCarousel").carousel('prev');
    });
    $(".carousel-control-next").click(function(){
        $("#myCarousel").carousel('next');
    });

    // Enable carousel indicators
    $(".slide-one").click(function(){
        $("#myCarousel").carousel(0);
    });
    $(".slide-two").click(function(){
        $("#myCarousel").carousel(1);
    });
    $(".slide-three").click(function(){
        $("#myCarousel").carousel(2);
    });
    $(".slide-four").click(function(){
        $("#myCarousel").carousel(3);
    });
    $(".slide-five").click(function(){
        $("#myCarousel").carousel(4);
    });
    $(".slide-six").click(function(){
        $("#myCarousel").carousel(5);
    });


    $(".collapsible1, .collapsible2, .collapsible3").click(function() {
        var content = this.nextElementSibling;
        if ($(content).css("display") != "none") {
            $(content).css("display", "none");
        } else {
            $(content).css("display", "block");
        }
    });

    $('a').not("[href*='/']").click(function(event) {
        event.preventDefault();
        if ($($(this).attr('href'))[0]) {
            $('html, body').animate({
                scrollTop: $($(this).attr('href')).offset().top -offset
            }, 500);
            $($(this).attr('href')).find('button').next().first().css("display", "block");
        }
    });

    var initial_hash = window.location.hash;
    if (initial_hash) {
        $('html, body').animate({
            scrollTop: $(initial_hash).offset().top - offset
        }, 500);
        $(initial_hash).find('button').next().first().css("display", "block");
    }

    // Call datatables for glossary
    var about_studies_for_release_table = $('#about_studies_for_release_table').DataTable({
        dom: 'B<"row">lfrtip',
        "iDisplayLength": 10,
        responsive: true
    });
});
