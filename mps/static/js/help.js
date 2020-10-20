$(document).ready(function () {
    var offset = 110;
    var help_offset = 200;
    var global_true_if_all_are_open = false;

    var selector = "#realTimeContents";
    var searchTermRegEx = null;
    var searchTerm = null;
    var matches = null;
    var buttons = null;
    var match_case_flag = "ig";
    var match_index = 0;
    var help_buttons = null;

    //this will get the anchor, if one called
    var initial_hash = window.location.hash;
    //just for testing, use this hash
    initial_hash = '#help_download_button';
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

    $(".help-collapsible").click(function() {
        // console.log("help-collapsible")
        var content = this.nextElementSibling;
        var parent_id = '';
        try {
            parent_id = $(this).parent().attr('id');
        } catch {
            parent_id = '';
        }
        change_display(parent_id, content, 'toggle');
    });

    //https://api.jquery.com/click/
    $("#expand_all").click(function(){
        //https://stackoverflow.com/questions/24844566/click-all-buttons-on-page
        // Get all buttons with the name and store in a NodeList called 'buttons'
        var buttons = document.getElementsByName('help_button');
        // Loop through and change display of the content
        for (var i = 0; i <= buttons.length; i++) {
            try {
                var content = buttons[i].nextElementSibling;
                change_display('expand_all', content, 'expand');
            } catch {
            }
        }
        global_true_if_all_are_open = true;
    })
    $("#close_all").click(function(){
        var buttons = document.getElementsByName('help_button');
        // Loop through and change display of the content
        for (var i = 0; i <= buttons.length; i++) {
            try {
                var content = buttons[i].nextElementSibling;
                change_display('close_all', content, 'close');
            } catch {
            }
        }
        global_true_if_all_are_open = false;
    })

    function change_display(this_checker, content, what_doing) {
        if (what_doing === 'toggle') {
            if ($(content).css("display") != "none") {
                $(content).css("display", "none");
                global_true_if_all_are_open = false;
            } else {
                $(content).css("display", "block");
            }
        } else if (what_doing === 'expand') {
            $(content).css("display", "block");
        } else {
            $(content).css("display", "none");
        }
    }

    function change_search_ables(which) {
        if (which === 'search') {
            $('#search_next').attr('disabled', 'disabled');
            $('#search_prev').attr('disabled', 'disabled');
            $('#search_gooo').removeAttr('disabled');
        } else {
            $('#search_next').removeAttr('disabled');
            $('#search_prev').removeAttr('disabled');
            $('#search_gooo').attr('disabled', 'disabled');
        }
    }

    //make them disabled on load
    $('#search_next').attr('disabled', 'disabled');
    $('#search_prev').attr('disabled', 'disabled');

    $(document).on('click', '#match_case', function() {
        change_search_ables('search');
    });

    document.getElementById("search_term").onfocus = function() {myFunction()};
    function myFunction() {
        change_search_ables('search');
    }

    $(document).on('click', '#search_gooo', function() {
        searchTerm = $('#search_term').val();
        change_search_ables('xsearch');
         
        matches = null;
        //remove all the old matches, if any
        $(".highlighted").removeClass("highlighted").removeClass("match");
        //Remove old search highlights
        $('.highlighted').removeClass('highlighted');
        //Remove the previous matches
        $span = $('#realTimeContents span');
        $span.replaceWith($span.html());     
        
        if (searchTerm.length === 0) {
            alert("Search box is empty");
            change_search_ables('search');
        } else {
            if (!global_true_if_all_are_open) {
                help_buttons = document.getElementsByName('help_button');
                for (var i = 0; i <= help_buttons.length; i++) {
                    try {
                        var content = help_buttons[i].nextElementSibling;
                        change_display('expand_all', content, 'expand');
                    } catch {
                    }
                }
            }
            // find the matches array and go to and highlighted
            // this calls search 1 (not a call back)
            let match_found_true = searchAndHighlight_search_master();
            if (!match_found_true) {
                alert("No results found");
                animate_scroll_hash('#overview_section');
            }
        }
    });

    // https://www.aspforums.net/Threads/211834/How-to-search-text-on-web-page-similar-to-CTRL-F-using-jQuery/
    // http://jsfiddle.net/wjLmx/23/
    function searchAndHighlight_search_master() {
        var result = false;
        if ($('#match_case').prop('checked')){
            match_case_flag = "g";
        } else {
            match_case_flag = "ig";
        }
        if (searchTerm) {
            searchTermRegEx = new RegExp(searchTerm, match_case_flag);
            //call search 0 that has a call back
            var matches_length = findMatches_search0(afterFindMatches_search1);
            console.log("matches_length after callback "+matches_length)
            if (matches_length > 0) {
                result = true;
            }
        }
        return result;
    }

    function findMatches_search0(callback1) {
        console.log("searchTermRegEx "+searchTermRegEx)
        console.log("selector "+selector)
        matches = [];
        console.log("matches a1 "+matches)
        matches = $(selector).text().match(searchTermRegEx);
        for (var i = 0; i <= 10000; i++) {
            if (i === 0) {
                console.log("i matches "+ i + " " + matches)
            }
            if (i % 1000 === 0) {
                console.log("i matches "+ i + " " + matches)
            }
        }
        console.warn('done')
        console.log("matches a "+matches)
        console.log("matches b "+matches)
        console.log("b "+matches.length)
        callback1();
        return matches.length;
    }

    function afterFindMatches_search1() {
        var result = false;
        if (matches != null && matches.length > 0) {
            if (searchTerm === "&") {
                searchTerm = "&amp;";
                searchTermRegEx = new RegExp(searchTerm, match_case_flag);
            }
            //https://codeburst.io/javascript-what-the-heck-is-a-callback-aba4da2deced
            labelMatchSpan_search2(continueFunction_search3);
            result = true;
        }
        return result;
    }

    function labelMatchSpan_search2(callback2){
        // do some asynchronous work and when the asynchronous stuff is complete
        $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + searchTerm + "</span>"));
        callback2();
    }

    function continueFunction_search3() {
        // call first function and pass in a callback function which
        // first function runs when it has completed
        $('.match').each(function (index, currentElement) {
            currentElement.innerHTML = matches[index];
        });
        $('.match:first').addClass('highlighted');
        match_index = 0;
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

    //These seem to work fine
    $(document).on('click', '#search_next', function () {
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

});

    //just keep for now - original search but did not work like I wanted
    // $(document).on('click', '.searchButtonClickText_h', function (event) {
    //     searchCall_search1();
    // });
    //
    // function searchCall_search1() {
    //     console.log("g_counter1 "+g_counter1)
    //     g_counter1=g_counter1+1;
    //
    //     searchTerm = $('.textSearchvalue_h').val();
    //     selector = "#realTimeContents";
    //     console.log("searchTerm "+searchTerm)
    //
    //     if (!global_true_if_all_are_open) {
    //         buttons = document.getElementsByName('help_button');
    //         for (var i = 0; i <= buttons.length; i++) {
    //             try {
    //                 var content = buttons[i].nextElementSibling;
    //                 change_display('expand_all', content, 'expand');
    //             } catch {
    //             }
    //         }
    //     }
    //     $(".highlighted").removeClass("highlighted").removeClass("match");
    //
    //     if (searchTerm.length === 0) {
    //         alert("Search box is empty");
    //     } else
    //     if (!searchAndHighlight_search_master()) {
    //         alert("No results found");
    //         initial_hash = '#overview_section';
    //         if (initial_hash) {
    //             animate_scroll_hash(initial_hash);
    //         }
    //     }
    // }
    //
    // // https://www.aspforums.net/Threads/211834/How-to-search-text-on-web-page-similar-to-CTRL-F-using-jQuery/
    // // http://jsfiddle.net/wjLmx/23/
    // // function searchAndHighlight_search_master(searchTerm, selector) {
    // function searchAndHighlight_search_master() {
    //
    //     console.log("g_counter2 "+g_counter2)
    //     g_counter2=g_counter2+1;
    //
    //     if ($('#match_case').prop('checked')){
    //         match_case_flag = "g";
    //     } else {
    //         match_case_flag = "ig";
    //     }
    //
    //     if (searchTerm) {
    //         //var wholeWordOnly = new RegExp("\\g"+searchTerm+"\\g","ig"); //matches whole word only
    //         //var anyCharacter = new RegExp("\\g["+searchTerm+"]\\g","ig"); //matches any word with any of search chars characters
    //         // i = With this flag the search is case-insensitive: no difference between A and a (see the example below).
    //         // g = With this flag the search looks for all matches, without it – only the first match is returned.
    //         // selector = selector || "#realTimeContents"; //use body as selector if none provided
    //         searchTermRegEx = new RegExp(searchTerm, match_case_flag);
    //         matches = $(selector).text().match(searchTermRegEx);
    //         // the matches list is case insensitive
    //
    //         if (matches != null && matches.length > 0) {
    //             //Remove old search highlights
    //             $('.highlighted').removeClass('highlighted');
    //             //Remove the previous matches
    //             $span = $('#realTimeContents span');
    //             $span.replaceWith($span.html());
    //
    //             if (searchTerm === "&") {
    //                 searchTerm = "&amp;";
    //                 searchTermRegEx = new RegExp(searchTerm, match_case_flag);
    //             }
    //
    //             continueFunction_search3();
    //             return true;
    //         }
    //     }
    //     return false;
    // }
    //
    // function labelMatchSpan_search2(next){
    //     // do some asynchronous work and when the asynchronous stuff is complete
    //     $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + searchTerm + "</span>"));
    //     next();
    // }
    // function continueFunction_search3(){
    //     // call first function and pass in a callback function which
    //     // first function runs when it has completed
    //     labelMatchSpan_search2(function() {
    //         $('.match').each(function(index, currentElement) {
    //             // console.log(index)
    //             // console.log("currentElement "+currentElement)
    //             // console.log("currentElement.innerHTML "+currentElement.innerHTML)
    //             // console.log("matches[index] "+matches[index])
    //             currentElement.innerHTML= matches[index];
    //         });
    //
    //         // var allListElements = $(".match");
    //         // console.log("e "+allListElements)
    //         // m = 0;
    //         // allListElements.each(function() {
    //         //     console.log("m "+m)
    //         //     console.log(this)
    //         //     $(this).replace("<span class='match'>" + searchTerm + "</span>", "<span class='match'>" + match[m] + "</span>");
    //         //     m++;
    //         // });
    //
    //         // var unique_matches = matches.filter(function(itm, i, a) {
    //         //     return i == matches.indexOf(itm);
    //         // });
    //         //
    //         // for (var j = 0; j < unique_matches.length; j++) {
    //         //     if (j == 1) {
    //         //         console.log("j " + j)
    //         //         console.log("matches[j] " + unique_matches[j])
    //         //         searchTerm = unique_matches[j];
    //         //         if (searchTerm === "&") {
    //         //             searchTerm = "&amp;";
    //         //             searchTermRegEx = new RegExp(searchTerm, "g");
    //         //             console.log("searchTermRegEx " + searchTermRegEx)
    //         //         } else {
    //         //             searchTermRegEx = new RegExp(searchTerm, "g");
    //         //             console.log("searchTermRegEx " + searchTermRegEx)
    //         //         }
    //         //         $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + matches[j] + "</span>"));
    //         //
    //         //     }
    //         // }
    //
    //         // console.log("fire 5")
    //         $('.match:first').addClass('highlighted');
    //
    //         var i = 0;
    //
    //         $('.next_h').off('click').on('click', function () {
    //             // console.log("fire 6")
    //             i++;
    //             if (i >= $('.match').length) {
    //                 i = 0;
    //             }
    //             // **$('.match').removeAttr('id');
    //             $('.match').removeClass('highlighted');
    //             $('.match').eq(i).addClass('highlighted');
    //             // **$('.highlighted').attr('id', 'id_high');
    //
    //             // var idArray = [];
    //             // $('.highlighted').each(function () {
    //             //     HANDY to get the text back from a nodeValue
    //             //     console.log("i "+this.firstChild.nodeValue)
    //             //     idArray.push(?);
    //             // });
    //
    //             // **this works, but will need a lot of stop points to use it
    //             // **var id_parents = $('#id_high').parents('.stop-point').attr('id');
    //             // **var this_hash = '#' + id_parents;
    //             // **animate_scroll_hash(this_hash, 'search');
    //
    //             // console.log("animate next")
    //             $('html, body').animate({
    //                 scrollTop: $('.highlighted:visible:first').offset().top - help_offset
    //             }, 400);
    //
    //         });
    //
    //         $('.previous_h').off('click').on('click', function () {
    //             // console.log("fire 7")
    //             i--;
    //             if (i < 0) {
    //                 i = $('.match').length - 1;
    //             }
    //             $('.match').removeClass('highlighted');
    //             $('.match').eq(i).addClass('highlighted');
    //
    //             // console.log("animate previous")
    //             $('html, body').animate({
    //                 scrollTop: $('.highlighted:visible:first').offset().top - help_offset
    //             }, 400);
    //         });
    //
    //         // when the search is clicked - finds the first occurance
    //         if ($('.highlighted:first').length) {
    //             // console.log("animate search first")
    //             //if match found, scroll to where the first one appears
    //             // this did not work for study summary....do not know why
    //             // $(window).scrollTop($('.highlighted:first').position().top - help_offset);
    //             $('html, body').animate({
    //                 scrollTop: $('.highlighted:visible:first').offset().top - help_offset
    //             }, 400);
    //         }
    //     });
    // }


    // did this, still got a major race issue problem
    // function labelMatchSpan_search2(next){
    //     // do some asynchronous work and when the asynchronous stuff is complete
    //     console.log("matches3 "+matches)
    //     console.log("len3 "+$('.match').length)
    //
    //     $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + searchTerm + "</span>"));
    //     console.log("matches4 "+matches)
    //     console.log("len4 "+$('.match').length)
    //     next();
    // }
    //
    // function continueFunction_search3(){
    //     // call first function and pass in a callback function which
    //     // first function runs when it has completed
    //     labelMatchSpan_search2(function() {
    //         console.log("back from 3")
    //         $('.match').each(function(index, currentElement) {
    //             currentElement.innerHTML= matches[index];
    //         });
    //         $('.match:first').addClass('highlighted');
    //         match_index = 0;
    //         // when the search is clicked - finds the first occurrence
    //         if ($('.highlighted:first').length) {
    //             console.log("search first")
    //             //if match found, scroll to where the first one appears
    //             // this did not work for study summary....do not know why
    //             // $(window).scrollTop($('.highlighted:first').position().top - help_offset);
    //             $('html, body').animate({
    //                 scrollTop: $('.highlighted:visible:first').offset().top - help_offset
    //             }, 400);
    //         }
    //     });
    // }
