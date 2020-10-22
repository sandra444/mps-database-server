$(document).ready(function () {

    //make them disabled on load
    $('#search_next').attr('disabled', 'disabled');
    $('#search_prev').attr('disabled', 'disabled');

    var offset = 110;
    var help_offset = 200;
    var if_all_are_open_true = false;

    var selector = "#realTimeContents";
    var searchTermRegEx = null;
    var searchTerm = null;
    var matches = null;
    var buttons = null;
    var match_case_flag = "ig";
    var match_index = 0;
    var help_buttons = null;
    var matches_length = 0;

    //this will get the anchor, if one called
    var initial_hash = window.location.hash;
    //just for testing, use this hash
    // initial_hash = '#help_download_button';
    if (initial_hash) {
        animate_scroll_hash(initial_hash);
    }

    function animate_scroll_hash(this_hash) {
        // if the anchor is NOT on the page, do not cause and error in the console
        // this error causes the glossary NOT to display!!!
        if ($(initial_hash).length)
        {
            $('html, body').animate({
                scrollTop: $(this_hash).offset().top - offset
            }, 500);
            $(this_hash).find('button').next().first().css("display", "block");
        }
    }

    // need a listener click for after the search....
    //https://api.jquery.com/click/
    $(document).on('click', '#expand_all', function() {
    // $("#expand_all").click(function(){
        expand_or_close_all(selector, 'e');
        if_all_are_open_true = true;
    })
    $(document).on('click', '#close_all', function() {
    // $("#close_all").click(function(){
        expand_or_close_all(selector, 'c');
    })

    function expand_or_close_all(selector, what_doing) {
        //https://stackoverflow.com/questions/24844566/click-all-buttons-on-page
        // Get all buttons with the name and store in a NodeList called 'buttons'
        // console.log("selector "+selector)
        // console.log("what_doing "+what_doing)
        var buttons = document.getElementsByName('help_button');
        // Loop through and change display of the content
        for (var i = 0; i <= buttons.length; i++) {
            try {
                var content = buttons[i].nextElementSibling;
                change_display(content, what_doing);
            } catch {
            }
        }
    }

    $(document).on('click', '.help-collapsible', function() {
    // $(".help-collapsible").click(function() {
        change_display(this.nextElementSibling, 't');
    });

    $(document).on('click', '.video-collapsible', function() {
    // $(".help-collapsible").click(function() {
        change_display(this.nextElementSibling, 't');
    });

    function change_display(content, what_doing) {
        // console.log("content "+content)
        // console.log("what_doing "+what_doing)
        if (what_doing === 't') {
            if ($(content).css("display") != "none") {
                $(content).css("display", "none");
                if_all_are_open_true = false;
            } else {
                $(content).css("display", "block");
            }
        } else if (what_doing === 'e') {
            $(content).css("display", "block");
        } else {
            $(content).css("display", "none");
            if_all_are_open_true = false;
        }
    }

    // START SEARCH SECTION
    function change_search_ables_to_search(which) {
        if (which) {
            $('#search_next').attr('disabled', 'disabled');
            $('#search_prev').attr('disabled', 'disabled');
            $('#search_gooo').removeAttr('disabled');
        } else {
            $('#search_next').removeAttr('disabled');
            $('#search_prev').removeAttr('disabled');
            $('#search_gooo').attr('disabled', 'disabled');
        }
    }

    $(document).on('click', '#match_case', function() {
    // $("#match_case").click(function() {
        change_search_ables_to_search(true);
    });
    
    // consider on input
    document.getElementById("search_term").onfocus = function() {
        myFunction()
    };
    
    function myFunction() {
        change_search_ables_to_search(true);
    }

    $(document).on('click', '#search_gooo', function() {
    // $("#search_gooo").click(function() {
        change_search_ables_to_search(false);
         
        //Remove old search highlights
        $('.highlighted').removeClass('highlighted');
        //Remove the spans and old matches
        $span = $('#realTimeContents .match');
        // NO NO NO - this does not iterate as expected, it just pulls one - $span.replaceWith($span.html());
        // the following makes sure to iterate through
        $span.each(function() {
            $(this).replaceWith($(this).html());
        });

        if ($('#match_case').prop('checked')){
            match_case_flag = "g";
        } else {
            match_case_flag = "ig";
        }

        searchTerm = $('#search_term').val();
        if (searchTerm.length === 0) {
            alert("Search box is empty");
            change_search_ables_to_search(true);
        } else {
            // open all the collapsibles if they are not already open
            // console.log("if_all_are_open_true ", if_all_are_open_true)
            if (!if_all_are_open_true) {
                expand_or_close_all(selector, 'e');
            }
            // find the matches array and go to and highlighted
            // this calls search master outer (not a call back)
            let match_found_true = searchAndHighlight_search_master();
            if (!match_found_true) {
                alert("No results found");
                animate_scroll_hash('#overview_section');
            }
        }
    });

    // https://www.aspforums.net/Threads/211834/How-to-search-text-on-web-page-similar-to-CTRL-F-using-jQuery/
    // http://jsfiddle.net/wjLmx/23/
    //https://codeburst.io/javascript-what-the-heck-is-a-callback-aba4da2deced
    function searchAndHighlight_search_master() {
        var result = false;
        if (searchTerm) {
            searchTermRegEx = new RegExp(searchTerm, match_case_flag);

            // console.log("matches (previous call) "+matches)
            // console.log("step 1 searchTermRegEx "+searchTermRegEx)
            // console.log("step 1 selector "+selector)

            matches = null;

            findMatches_search0(afterFindMatches_search1);

            // console.log("End - Number of matches after back from everything = "+matches_length)

            if (matches_length > 0) {
                result = true;
            }
        }
        return result;
    }

    function findMatches_search0(callback1) {
        matches = $(selector).text().match(searchTermRegEx);
        callback1();
    }

    function afterFindMatches_search1() {
        if (!matches) {
            matches = [];
        }
        matches_length = matches.length;
        // console.log("step 1 matches "+matches)
        // console.log("step 1 number matches = "+matches_length)

        if (matches != null && matches_length > 0) {
            // unique_matches = matches.filter(function(itm, i, a) {
            //     return i == matches.indexOf(itm);
            // });
            if (searchTerm === "&") {
                searchTerm = "&amp;";
                searchTermRegEx = new RegExp(searchTerm, match_case_flag);
            }
            // console.log("searchTerm ",searchTerm)
            labelMatchSpan_search2(continueFunction_search3);
        }
    }

    function labelMatchSpan_search2(callback2){
        $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + searchTerm + "</span>"));
        callback2();
    }

    function continueFunction_search3() {
        // console.log("in search 3")
        // console.log("$('.match').length = "+$('.match').length)
        // console.log("matches_length = " + matches_length)
        // the previous function replaced with the search term, fix to match the original case
        if ($('.match').length != matches_length) {
            alert("there is a mismatch in the counting....")
        }
        // console.log("step right above matches "+matches)
        $('.match').each(function (index, currentElement) {
            // console.log("~~~index = "+index)
            // console.log("~~~matches[index] = "+matches[index])
            // console.log("~~~currentElement.innerHTML = "+currentElement.innerHTML)
            // console.log("~~~$(this).html() = "+$(this).html())
            // currentElement.innerHTML = matches[index];
            $(this).html(matches[index]);
        });
        $('.match:first').addClass('highlighted');
        match_index = 0;
        // console.log("in search 3 - getting ready to highlight")
        // when the search is clicked - finds the first occurrence
        if ($('.highlighted:first').length) {
            //if match found, scroll to where the first one appears
            // this did not work for study summary....do not know why
            // $(window).scrollTop($('.highlighted:first').position().top - help_offset);
            $('html, body').animate({
                scrollTop: $('.highlighted:visible:first').offset().top - help_offset
            }, 400);
        }
    }

    $(document).on('click', '#search_next', function () {
    // $("#search_next").click(function() {
        // $('.next_h').off('click').on('click', function () {
        match_index =  match_index + 1;
        if (match_index >= $('.match').length) {
            match_index = 0;
        }
        $('.match').removeClass('highlighted');
        $('.match').eq(match_index).addClass('highlighted');
        $('html, body').animate({
            scrollTop: $('.highlighted:visible:first').offset().top - help_offset
        }, 400);
    });

    $(document).on('click', '#search_prev', function () {
    // $("#search_prev").click(function() {
        // $('.previous_h').off('click').on('click', function () {
        match_index = match_index - 1;
        if (match_index < 0) {
            match_index = $('.match').length - 1;
        }
        $('.match').removeClass('highlighted');
        $('.match').eq(match_index).addClass('highlighted');
        $('html, body').animate({
            scrollTop: $('.highlighted:visible:first').offset().top - help_offset
        }, 400);
    });
    // END SEARCH SECTION

    // START GLOSSARY SECTION
    $('a').not("[href*='/']").click(function(event) {
        event.preventDefault();
        if ($($(this).attr('href'))[0]) {
            $('html, body').animate({
                scrollTop: $($(this).attr('href')).offset().top - offset
            }, 500);
            $($(this).attr('href')).find('button').next().first().css("display", "block");
        }
    });

    var _alphabetSearch = '';

    $.fn.dataTable.ext.search.push(function(settings, searchData ) {
        // fires when click a letter
        if (!_alphabetSearch) {
            return true;
        }

        else if (searchData[0].charAt(0) === _alphabetSearch) {
            return true;
        }

        else if (searchData[0].charAt(0).toUpperCase() === _alphabetSearch) {
            return true;
        }

        return false;
    });

    // Call datatables for glossary
    var glossary_table = $('#glossary_table').DataTable({
        dom: '<Bl<"row">frptip>',
        "iDisplayLength": 10,
        responsive: true
    });

    var alphabet = $('<div class="alphabet"/>').append('Search: ');

    // Add none
    $('<a/>')
        .attr('data-letter', '')
        .attr('role', 'button')
        .html('None')
        .addClass('btn btn-sm')
        .appendTo(alphabet);

    for(var i=0; i<26; i++) {
        var letter = String.fromCharCode(65 + i);
        $('<a/>')
            .attr('data-letter', letter)
            .attr('role', 'button')
            .html(letter)
            .addClass('btn btn-sm')
            .appendTo(alphabet);
    }

    alphabet.insertBefore(glossary_table.table().container());

    alphabet.on('click', 'a', function() {
        // fires when click a letter (for each glossary term)
        alphabet.find('.active').removeClass('active');
        $(this).addClass('active');
        _alphabetSearch = $(this).attr('data-letter');
        glossary_table.draw();
    });
    // END GLOSSARY SECTION
});

