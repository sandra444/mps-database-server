$(document).ready(function () {
    var offset = 0;
    var help_offset = 0;
    var global_true_if_all_are_open = false;

    var initial_hash = window.location.hash;
    initial_hash = '#video_demo_w1';
    if (initial_hash) {
        animate_scroll_hash(initial_hash);
    }

    function animate_scroll_hash(this_hash) {
        // if the anchor is NOT on the page, do not cause and error in the console
        // this error causes the glossary NOT to display!!!
        if ($(initial_hash).length)
        {
            $('html, body').animate({
                scrollTop: $(this_hash).offset().top - help_offset
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
        console.log("dis "+what_doing)
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

    $(document).on('click', '.searchButtonClickText_h', function (event) {
        if (!global_true_if_all_are_open) {
            var buttons = document.getElementsByName('help_button');
            for (var i = 0; i <= buttons.length; i++) {
                try {
                    var content = buttons[i].nextElementSibling;
                    change_display('expand_all', content, 'expand');
                } catch {
                }
            }
        }
        $(".highlighted").removeClass("highlighted").removeClass("match");
        if (!searchAndHighlight($('.textSearchvalue_h').val())) {
            alert("No results found (or search box is empty)");
        }

    });

    // https://www.aspforums.net/Threads/211834/How-to-search-text-on-web-page-similar-to-CTRL-F-using-jQuery/
    // http://jsfiddle.net/wjLmx/23/
    function searchAndHighlight(searchTerm, selector) {
        if (searchTerm) {
            //var wholeWordOnly = new RegExp("\\g"+searchTerm+"\\g","ig"); //matches whole word only
            //var anyCharacter = new RegExp("\\g["+searchTerm+"]\\g","ig"); //matches any word with any of search chars characters
            // i = With this flag the search is case-insensitive: no difference between A and a (see the example below).
            // g = With this flag the search looks for all matches, without it – only the first match is returned.
            var selector = selector || "#realTimeContents"; //use body as selector if none provided
            var searchTermRegEx = new RegExp(searchTerm, "ig");
            var matches = $(selector).text().match(searchTermRegEx);
            // the matches list is case insensitive

            if (matches != null && matches.length > 0) {
                //Remove old search highlights
                $('.highlighted').removeClass('highlighted');
                //Remove the previous matches
                $span = $('#realTimeContents span');
                $span.replaceWith($span.html());

                if (searchTerm === "&") {
                    searchTerm = "&amp;";
                    searchTermRegEx = new RegExp(searchTerm, "ig");
                }
                $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + searchTerm + "</span>"));

                console.log("here")
                $('.match').each(function(index, currentElement) {

                    console.log(index)
                    console.log("currentElement "+currentElement)
                    console.log("currentElement.innerHTML "+currentElement.innerHTML)
                    console.log("matches[index] "+matches[index])
                    //currentElement.replace(currentElement.innerHTML, "<span class='match'>" + matches[index] + "</span>"));
                });
                console.log("here2")


                // var allListElements = $(".match");
                // console.log("e "+allListElements)
                // m = 0;
                // allListElements.each(function() {
                //     console.log("m "+m)
                //     console.log(this)
                //     $(this).replace("<span class='match'>" + searchTerm + "</span>", "<span class='match'>" + match[m] + "</span>");
                //     m++;
                // });

                // var unique_matches = matches.filter(function(itm, i, a) {
                //     return i == matches.indexOf(itm);
                // });
                //
                // for (var j = 0; j < unique_matches.length; j++) {
                //     if (j == 1) {
                //         console.log("j " + j)
                //         console.log("matches[j] " + unique_matches[j])
                //         searchTerm = unique_matches[j];
                //         if (searchTerm === "&") {
                //             searchTerm = "&amp;";
                //             searchTermRegEx = new RegExp(searchTerm, "g");
                //             console.log("searchTermRegEx " + searchTermRegEx)
                //         } else {
                //             searchTermRegEx = new RegExp(searchTerm, "g");
                //             console.log("searchTermRegEx " + searchTermRegEx)
                //         }
                //         $(selector).html($(selector).html().replace(searchTermRegEx, "<span class='match'>" + matches[j] + "</span>"));
                //
                //     }
                // }

                // console.log("fire 5")
                $('.match:first').addClass('highlighted');

                var i = 0;

                $('.next_h').off('click').on('click', function () {
                    // console.log("fire 6")
                    i++;
                    if (i >= $('.match').length) {
                        i = 0;
                    }
                    // **$('.match').removeAttr('id');
                    $('.match').removeClass('highlighted');
                    $('.match').eq(i).addClass('highlighted');
                    // **$('.highlighted').attr('id', 'id_high');

                    // var idArray = [];
                    // $('.highlighted').each(function () {
                    //     HANDY to get the text back from a nodeValue
                    //     console.log("i "+this.firstChild.nodeValue)
                    //     idArray.push(?);
                    // });

                    // **this works, but will need a lot of stop points to use it
                    // **var id_parents = $('#id_high').parents('.stop-point').attr('id');
                    // **var this_hash = '#' + id_parents;
                    // **animate_scroll_hash(this_hash, 'search');

                    // console.log("animate next")
                    $('html, body').animate({
                        scrollTop: $('.highlighted:visible:first').offset().top - (help_offset)
                    }, 400);

                });

                $('.previous_h').off('click').on('click', function () {
                    // console.log("fire 7")
                    i--;
                    if (i < 0) {
                        i = $('.match').length - 1;
                    }
                    $('.match').removeClass('highlighted');
                    $('.match').eq(i).addClass('highlighted');

                    // console.log("animate previous")
                    $('html, body').animate({
                        scrollTop: $('.highlighted:visible:first').offset().top - (help_offset)
                    }, 400);
                });

                // when the search is clicked - finds the first occurance
                if ($('.highlighted:first').length) {
                    // console.log("animate search first")
                    //if match found, scroll to where the first one appears
                    $(window).scrollTop($('.highlighted:first').position().top - (help_offset));
                }
                return true;
            }
        }
        return false;
    }

    $('a').not("[href*='/']").click(function(event) {
        event.preventDefault();
        // console.log("animate a")
        if ($($(this).attr('href'))[0]) {
            $('html, body').animate({
                scrollTop: $($(this).attr('href')).offset().top - help_offset
            }, 500);
            $($(this).attr('href')).find('button').next().first().css("display", "block");
        }
    });

    var _alphabetSearch = '';

    $.fn.dataTable.ext.search.push(function(settings, searchData ) {
        if (!_alphabetSearch) {
            return true;
        }

        else if (searchData[0].charAt(0) === _alphabetSearch) {
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
        alphabet.find('.active').removeClass('active');
        $(this).addClass('active');

        _alphabetSearch = $(this).attr('data-letter');
        glossary_table.draw();
    });

});
