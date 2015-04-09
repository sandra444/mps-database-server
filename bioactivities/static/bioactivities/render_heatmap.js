$(document).ready(function () {

    function heatmap(heatmap_data_csv, row_order, col_order) {

        //console.log(row_order);
        //console.log(col_order);

        // Show graphic
        $('#graphic').prop('hidden',false);
        // Hide error
        $('#error_message').prop('hidden',true);

        // Clear old (if present)
        $('#heatmap').html('');
        $('#heatmap_legend').html('');

        // Add href to download link
        $("#download").attr("href", heatmap_data_csv);

        var margin = { top: 650, right: 50, bottom: 50, left: 125 };
        var cell_size = 10;
        var legend_element_width = cell_size * 3;
        var legend_element_height = cell_size;

        var colors = [
            '#008000', '#1A8C00', '#339800', '#4DA400', '#66B000',
            '#80BC00',
            '#99C800', '#B3D400', '#CCE000', '#E6EC00', '#FFFF00',
            '#F3E600',
            '#E7CC00', '#DBB300', '#CF9900', '#C38000', '#B76600',
            '#AB4D00',
            '#9F3300', '#931A00', '#870000'
        ];

        d3.csv(
            heatmap_data_csv,
            function (d) {
                return {
                    compound: d.compound,
                    bioactivity: d.bioactivity,
                    value: +d.value  /* + converts string to number */
                };
            },
            function (error, data) {

                var i;
                var cols_list = [];
                var cols_list_original;
                var rows_list = [];
                var rows_list_original;
                var max_row_name_length = 0;
                var max_col_name_length = 0;
                var min_value = 0;
                var max_value = 0;
                var median;
                var list_of_all_values = [];

                function sort_rows_on_columns(col_name) {
                    var i;
                    var j;
                    var new_row_order = [];

                    for(j = 0; j < rows_list.length; j += 1) {
                        for (i = 0; i < data.length; i += 1) {
                            if (data[i]["bioactivity"] === col_name
                                && data[i]["compound"] === rows_list[j]) {
                                new_row_order.push(
                                    [
                                        data[i]["value"],
                                        data[i]["compound"]
                                    ]
                                );
                            }
                        }
                    }

                    new_row_order.sort(
                        function(first, next) {

                            // note: sorting direction greatest to smallest this way
                            if (first[0] < next[0]) {
                                return 1;
                            }
                            if (first[0] > next[0]) {
                                return -1;
                            }
                            return 0;
                        }
                    );

                    // now we begin to build the final array
                    var temp_rows_list = [];

                    // left to right add columns in order of value from greatest to least

                    for (i = 0; i < new_row_order.length; i += 1) {
                        temp_rows_list.push(new_row_order[i][1]);
                    }

                    // left to right add columns in alphabetical order
                    // for elements where there is no data
                    rows_list.sort();

                    // whatever isn't in the first part goes to the back of the array
                    // where we don't care about the order of the undefined elements
                    for (i = 0; i <= rows_list.length; i += 1) {
                        if (temp_rows_list.indexOf(rows_list[i]) === -1) {
                            temp_rows_list.push(rows_list[i]);
                        }
                    }

                    rows_list = temp_rows_list;

                }

                function sort_columns_on_row(row_name) {
                    var i;
                    var j;
                    var new_column_order = [];

                    for(j = 0; j < cols_list.length; j += 1) {
                        for (i = 0; i < data.length; i += 1) {
                            if (data[i]["compound"] === row_name
                                && data[i]["bioactivity"] === cols_list[j]) {
                                new_column_order.push(
                                    [
                                        data[i]["value"],
                                        data[i]["bioactivity"]
                                    ]
                                );
                            }
                        }
                    }

                    new_column_order.sort(
                        function(first, next) {

                            // note: sorting direction greatest to smallest this way
                            if (first[0] < next[0]) {
                                return 1;
                            }
                            if (first[0] > next[0]) {
                                return -1;
                            }
                            return 0;
                        }
                    );

                    // now we begin to build the final array
                    var temp_cols_list = [];

                    // left to right add columns in order of value from greatest to least

                    for (i = 0; i < new_column_order.length; i += 1) {
                        temp_cols_list.push(new_column_order[i][1]);
                    }

                    // left to right add columns in alphabetical order
                    // for elements where there is no data
                    cols_list.sort();

                    // whatever isn't in the first part goes to the back of the array
                    // where we don't care about the order of the undefined elements
                    for (i = 0; i <= cols_list.length; i += 1) {
                        if (temp_cols_list.indexOf(cols_list[i]) === -1) {
                            temp_cols_list.push(cols_list[i]);
                        }
                    }

                    cols_list = temp_cols_list;

                }

                function update_all() {
                    render_main_svg();
                    render_row_labels();
                    render_col_labels();
                    render_heatmap();
                }

                for (i = 0; i < data.length; i += 1) {
                    var current_bioactivity = data[i]["bioactivity"];
                    var current_compound = data[i]["compound"];
                    if (cols_list.indexOf(current_bioactivity) === -1) {
                        cols_list.push(current_bioactivity);
                        if (current_bioactivity.length >= max_col_name_length) {
                            max_col_name_length = current_bioactivity.length;
                        }
                    }
                    if (rows_list.indexOf(current_compound) === -1) {
                        rows_list.push(current_compound);
                        if (current_compound.length >= max_row_name_length) {
                            max_row_name_length = current_compound.length;
                        }
                    }
                    if (min_value > data[i]["value"]) {
                        min_value = data[i]["value"];
                    }
                    if (max_value < data[i]["value"]) {
                        max_value = data[i]["value"];
                    }
                    list_of_all_values.push(data[i]["value"]);
                }

                // Old sorting just on name
                // alphabetically sort row and column labels
                //rows_list = rows_list.sort();
                //cols_list = cols_list.sort();

                rows_list = row_order;
                cols_list = col_order;

    //            console.log(rows_list);
    //            console.log(cols_list);

                // archive the original arrays in their respective copy of '_original'
                rows_list_original = rows_list.slice(0);
                cols_list_original = cols_list.slice(0);

                min_value -= min_value * 0.1;
                max_value += max_value * 0.1;
                median = d3.median(list_of_all_values);

                var char_pixels_width = 8;
                margin.top = char_pixels_width * max_col_name_length;
                margin.left = char_pixels_width * max_row_name_length;

                var width = cell_size * cols_list.length;
                var height = cell_size * rows_list.length;

                var color_scale = d3.scale.quantile()
                    .domain([min_value , median, max_value])
                    .range(colors);

                var svg;

                var render_main_svg = function () {

                    // remove old svg canvas rendering
                    d3.select("svg").remove();

                    svg = d3.select("#heatmap").append("svg")
                        .attr(
                        "width", width + margin.left + margin.right
                    )
                        .attr(
                        "height", height + margin.top + margin.bottom
                    )
                        .append("g")
                        .attr(
                        "transform",
                        "translate(" +
                        margin.left + "," + margin.top
                            + ")"
                    );
                };

                render_main_svg();

                var render_row_labels = function () {

                    svg.append("g")
                        .selectAll(".row_labelg")
                        .data(rows_list)
                        .enter()
                        .append("text")
                        .text(
                        function (d) {
                            return d;
                        }
                    )
                        .attr("x", 0)
                        .attr(
                        "y", function (d, i) {
                            return (rows_list.indexOf(d) + 1) * cell_size;
                        }
                    )
                        .style("text-anchor", "end")
                        .attr(
                        "transform",
                        "translate(-6," + cell_size / 1.5 + ")"
                    )
                        .attr(
                        "class", function (d, i) {
                            return "row_label mono r" + i;
                        }
                    )
                        .on(
                        "mouseover", function (d) {
                            d3.select(this).classed("text-hover", true);
                        }
                    )
                        .on(
                        "mouseout", function (d) {
                            d3.select(this).classed(
                                "text-hover", false
                            );
                        }
                    )
                        .on(
                        "click", function (d, i) {

                            sort_columns_on_row(d);
                            update_all(d);

                        }
                    );
                };

                render_row_labels();

                var render_col_labels = function () {
                    svg.append("g")
                        .selectAll(".col_labelg")
                        .data(cols_list)
                        .enter()
                        .append("text")
                        .text(
                        function (d) {
                            return d;
                        }
                    )
                        .attr("x", 0)
                        .attr("y", function (d, i) {
                                  return (cols_list.indexOf(d) + 1) * cell_size;
                              }
                    )
                        .style("text-anchor", "left")
                        .attr(
                        "transform", "translate(" + cell_size / 2 + ",-6) rotate (-90)"
                    )
                        .attr(
                        "class", function (d, i) {
                            return "col_label mono c" + i;
                        }
                    )
                        .on(
                        "mouseover", function (d) {
                            d3.select(this).classed("text-hover", true);
                        }
                    )
                        .on(
                        "mouseout", function (d) {
                            d3.select(this).classed("text-hover", false);
                        }
                    )
                        .on(
                        "click", function (d, i) {

                            sort_rows_on_columns(d);
                            update_all(d);

                        }
                    );
                };

                render_col_labels();

                var render_heatmap = function () {
                    svg.append("g").attr("class", "g3")
                        .selectAll(".cellg")
                        .data(
                        data, function (d) {
                            return d["compound"] + ": " + d["bioactivity"];
                        }
                    )
                        .enter()
                        .append("rect")
                        .attr(
                        "x", function (d) {
                            return (cols_list.indexOf(d["bioactivity"]) + 1) * cell_size;
                        }
                    )
                        .attr(
                        "y", function (d) {
                            return (rows_list.indexOf(d["compound"]) + 1) * cell_size;
                        }
                    )
                        .attr(
                        "class", function (d) {
                            return "cell cell-border cr" + (
                                rows_list.indexOf(d["compound"]) - 1 ) + " cc" + (  cols_list.indexOf(d["bioactivity"]) - 1);
                        }
                    )
                        .attr("width", cell_size)
                        .attr("height", cell_size)
                        .style(
                        "fill", function (d) {
                            return color_scale(d.value);
                        }
                    )
                        .on(
                        "click", function (d) {
                            alert(d.value);
                        }
                    )
                        .on(
                        "mouseover", function (d) {
                            //highlight text
                            d3.select(this).classed("cell-hover", true);
                            d3.selectAll(".row_label").classed(
                                "text-highlight", function (r, ri) {
                                    return ri == (
                                        rows_list.indexOf(d["compound"])
                                        );
                                }
                            );
                            d3.selectAll(".col_label").classed(
                                "text-highlight", function (c, ci) {
                                    return ci == (
                                        cols_list.indexOf(d["bioactivity"])
                                        );
                                }
                            );

                        }
                    )
                        .on(
                        "mouseout", function () {
                            d3.select(this).classed(
                                "cell-hover", false
                            );
                            d3.selectAll(".row_label").classed(
                                "text-highlight", false
                            );
                            d3.selectAll(".col_label").classed(
                                "text-highlight", false
                            );
                        }
                    );
                };

                render_heatmap();

                var svg_legend = d3.select("#heatmap_legend").append("svg")
                    .attr(
                    "width", legend_element_width * 21
                )
                    .attr(
                    "height", cell_size * 4
                )
                    .append("g");

                var legend = svg_legend.selectAll(".legend")
                    .data(
                    [
                        "Low", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "", "", "", "", "", "High"
                    ]
                )
                    .enter().append("g")
                    .attr("class", "legend");

                legend.append("rect")
                    .attr(
                    "x", function (d, i) {
                        return legend_element_width * i;
                    }
                )
                    .attr(
                    "y", 0
                )
                    .attr("width", legend_element_width)
                    .attr("height", legend_element_height)
                    .style(
                    "fill", function (d, i) {
                        return colors[i];
                    }
                );

                legend.append("text")
                    .attr("class", "mono")
                    .text(
                    function (d) {
                        return d;
                    }
                )
                    .attr("width", legend_element_width)
                    .attr(
                    "x", function (d, i) {
                        return legend_element_width * i;
                    }
                )
                    .attr(
                    "y", legend_element_height * 2
                );

            }
        );
    }

    function submit() {

        // Clear all filters
        bioactivities_filter = [];
        targets_filter = [];
        compounds_filter = [];
        drugtrials_filter = [];

        // Get bioactivities
        $("#bioactivities input[type='checkbox']:checked").each( function() {
            bioactivities_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Get targets
        $("#targets input[type='checkbox']:checked").each( function() {
            targets_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Get compounds
        $("#compounds input[type='checkbox']:checked").each( function() {
            compounds_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Get drugtrials
        $("#drugtrials input[type='checkbox']:checked").each( function() {
            drugtrials_filter.push({"name":this.value, "is_selected":this.checked});
        });

        // Hide Selection html
        $('#selection').prop('hidden',true);
        // Hide error
        $('#error_message').prop('hidden',true);

        // Show spinner
        window.spinner.spin(
            document.getElementById("spinner")
        );

        $.ajax({
            url:  '/bioactivities/gen_heatmap/',
            type: 'POST',
            contentType: 'application/json',
            // Remember to convert to string
            data: JSON.stringify({
                'bioactivities_filter': bioactivities_filter,
                'targets_filter': targets_filter,
                'compounds_filter': compounds_filter,
                'drugtrials_filter': drugtrials_filter,
                'target_types_filter': target_types,
                'organisms_filter': organisms,
                'log_scale': log_scale,
                'normalize_bioactivities': normalize_bioactivities,
                'metric': metric,
                'method': method
            }),
            success: function (json) {
                // Stop spinner
                window.spinner.stop();
                //console.log(json);

                if (json.data_csv) {
                    //console.log(json);
                    heatmap(json.data_csv, json.row_order, json.col_order);
//                    document.location.hash = "display";
                }
                else {
                    if (json.error) {
                        $('#error').html(json.error);
                    }
                    // Show error
                    $('#error_message').prop('hidden',false);
                    // Show Selection
                    $('#selection').prop('hidden',false);
                }

            },
            error: function (xhr, errmsg, err) {
                // Stop spinner
                window.spinner.stop();

                console.log(xhr.status + ": " + xhr.responseText);

                // Show error
                $('#error_message').prop('hidden',false);
                // Show Selection
                $('#selection').prop('hidden',false);
            }
        });
    }

    // Get a list for checkboxes from returned AJAX data
    // Min is a boolean value to see if data should be restricted on min_feat_count
    function get_list(data, min) {
        if (!data || data.length == 0) {
            return [];
        }

        var result = [];
        var i;
        for (i = 0; i < data.length; i += 1) {
            // Consider refactor for min_feat_count restriction
            if (!min || data[i][1] >= min_feat_count) {
                result.push({
                    name: data[i][0],
                    is_selected: false
                });
            }
        }

        // Case insensitive sort
        result = _.sortBy(result, function (i) { return i.name.toLowerCase(); });

        return result;
    }

    // Function to reset the rows after refresh
    // PLEASE BE CERTAIN TO ESCAPE CHARACTERS LIKE ' (for prime)
    function reset_rows(name,list,add) {
        // Clear current
        $('#' + name).html('');
        // Add from list
        for (var i in list) {
            // Note added 'c' to avoid confusion with graphic
            var row = "<tr id='" + add + list[i].name.replace(/ /g,"_").replace(/'/g,"&#39;") + "'>";
            row += "<td>" + "<input type='checkbox' value='" + list[i].name.replace(/'/g,"&#39;") + "'></td>";
            row += "<td>" + list[i].name + "</td>";
            $('#' + name).append( row );
        }

        // Reset select all box
        $("#all_" + name).prop('checked',false);
    }

    function refresh() {

        // Disable everything
        $(":input").prop("disabled",true);

        $.ajax({
            url:  '/bioactivities/all_data',
            type: "GET",
            dataType: "json",
            data: {
                target_types: JSON.stringify(target_types),
                organisms: JSON.stringify(organisms)
            },
            success: function (json) {
                //console.log(json);
                targets = get_list(json.targets, true);
                compounds = get_list(json.compounds, true);
                bioactivities = get_list(json.bioactivities, true);
                drugtrials = get_list(json.drugtrials, false);
                //console.log(targets);
                //console.log(compounds);
                //console.log(bioactivities);
                //console.log(drugtrials);

                // Clear bioactivities
                reset_rows('bioactivities',bioactivities,'');

                // Clear targets
                reset_rows('targets',targets,'');

                // Clear compounds
                reset_rows('compounds',compounds,'c');

                // Clear drugtrials
                reset_rows('drugtrials',drugtrials,'');

                // Enable everything
                $(":input").prop("disabled",false);
            },
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);

                // Enable everything
                $(":input").prop("disabled",false);
            }
        });
    }

//    // Initial hash change
//    document.location.hash = "";

    // Currently testing, should grab these with a function in refresh (KEEP THIS FORMAT)
    var target_types = [];
    var organisms = [];
    $("#control_target_types input[type='checkbox']:checked").each( function() {
        target_types.push({"name":this.value, "is_selected":this.checked});
    });
    $("#control_organisms input[type='checkbox']:checked").each( function() {
        organisms.push({"name":this.value, "is_selected":this.checked});
    });

    // Functions to acquire new lists for target_types
    var control_target_types = $("#control_target_types input[type='checkbox']");
    control_target_types.change(function(evt) {
        target_types = [];
        if ($("#control_target_types input[type='checkbox']:checked").length == control_target_types.length) {
            $('#all_target_types').prop('checked', true);
        }
        else {
            $('#all_target_types').prop('checked', false);
        }

        control_target_types.each(function() {
            //console.log(this.value);
            target_types.push({"name":this.value, "is_selected":this.checked});
        });

        refresh();
    });
    //Change all target_types
    $('#all_target_types').change(function(evt) {
        if (this.checked) {
            control_target_types.prop('checked', true);
        }
        else {
            control_target_types.prop('checked', false);
        }
        // Please note the use of first to prevent redundant calls
        control_target_types.first().trigger('change');
    });

    // Functions to acquire new lists for organisms
    var control_organisms = $("#control_organisms input[type='checkbox']");
    control_organisms.change(function(evt) {
        organisms = [];
        if ($("#control_organisms input[type='checkbox']:checked").length == control_organisms.length) {
            $('#all_organisms').prop('checked', true);
        }
        else {
            $('#all_organisms').prop('checked', false);
        }

        control_organisms.each(function() {
            //console.log(this.value);
            organisms.push({"name":this.value, "is_selected":this.checked});
        });

        refresh();
    });
    //Change all organisms
    $('#all_organisms').change(function(evt) {
        if (this.checked) {
            control_organisms.prop('checked', true);
        }
        else {
            control_organisms.prop('checked', false);
        }
        // Please note the use of first to prevent redundant calls
        control_organisms.first().trigger('change');
    });

    // Function to refactor redundant code
    // Name is the general selector without #
    function track_selections(name) {
        // Check to see if the "select all" button has been clicked
        $('#all_' + name).change(function(evt) {
            // If the "all" box is checked, select all visible checkboxes
            if (this.checked) {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', true);
            }
            // Otherwise deselect all checkboxes
            else {
                $("#" + name + " input[type='checkbox']:visible").prop('checked', false);
            }
        });

        // Track when any row checkbox is clicked and discern whether all visible check boxes are checked, if so then check the "all" box
        $("body").on( "change", "#" + name + " input[type='checkbox']", function(event) {
            if ($("#" + name + " input[type='checkbox']:checked:visible").length == $("#" + name + " input[type='checkbox']:visible").length) {
                $('#all_' + name).prop('checked', true);
            }
            else {
                $('#all_' + name).prop('checked', false);
            }
        });
    }

    // Change all bioactivities
    track_selections('bioactivities');

    // Change all targets
    track_selections('targets');

    // Change all compounds
    track_selections('compounds');

    // Change all drugtrials
    track_selections('drugtrials');

    // Initial min_feature count
    var min_feat_count = $('#minimum_feature_count').val();
    // Listen min feature count
    $('#apply_minimum_feature_count').click(function(evt) {
        min_feat_count = $('#minimum_feature_count').val();
        refresh();
    });

    // Initial truth log scale
    var log_scale = $('#log_scale').prop('checked');
    // Listen log_scale
    $('#log_scale').change(function(evt) {
        log_scale = $('#log_scale').prop('checked');
    });

    // Initial truth normalize
    var normalize_bioactivities = $('#normalize_bioactivities').prop('checked');
    // Listen normalize
    $('#normalize_bioactivities').change(function(evt) {
        normalize_bioactivities = $('#normalize_bioactivities').prop('checked');
    });

    // Initial metric
    var metric = $('#metric').val();
    // Listen metric
    $('#metric').change(function(evt) {
        metric = $('#metric').val();
    });

    // Initial method
    var method = $('#method').val();
    // Listen method
    $('#method').change(function(evt) {
        method = $('#method').val();
    });

    var targets = [];
    var compounds = [];
    var bioactivities = [];
    var drugtrials = [];

    var targets_filter = [];
    var compounds_filter = [];
    var bioactivities_filter = [];
    var drugtrials_filter = [];

    refresh();

    $('#submit').click(function(evt) {
        submit();
    });

    // Return to selection
    $('#back').click(function(evt) {
        $('#graphic').prop('hidden',true);
        $('#selection').prop('hidden',false);
//        document.location.hash = "";
//        //Why does microsoft want me to suffer?
//        if (browser.isIE && browser.verIE >= 11) {
//            $('#graphic').prop('hidden',true);
//            $('#selection').prop('hidden',false)
//        }
    });

    var bioactivity_search = $('#bioactivity_filter');
    var target_search = $('#target_filter');
    var compound_search = $('#compound_filter');
    var drugtrial_search = $('#drugtrial_filter');

    var bioactivity_string = bioactivity_search.val().toLowerCase().replace(/ /g,"_");
    var target_string = target_search.val().toLowerCase().replace(/ /g,"_");
    // Note added 'c' to compound string
    var compound_string = 'c' + compound_search.val().toLowerCase().replace(/ /g,"_");
    var drugtrial_string = drugtrial_search.val().toLowerCase().replace(/ /g,"_");

    // Function to reduce code
    // search = selector for search filter
    // string = the string typed into the input box
    // selector = the string (no #) to identify what is being acted on
    // add = string to add to the search values (used for compounds)
    function search_filter(search,string,selector,add) {
        search.on('input',function() {
        // Note the added 'c' to avoid confusion in compounds
        string = add + search.val().toLowerCase().replace(/ /g,"_");

        // For every row in the given table
        $("#" + selector + " tr").each(function() {
                // If the row contains the requested string, do not hide it
                if (this.id.toLowerCase().indexOf(string) > -1) {
                    this.hidden = false;
                }
                // If it does not contain the string hide it
                else {
                    this.hidden = true;
                }
            });

            // Check or uncheck all as necessary
            if ($("#" + selector + " input[type='checkbox']:checked:visible").length == $("#" + selector + " input[type='checkbox']:visible").length) {
                $('#all_' + selector).prop('checked', true);
            }
            else {
                $('#all_' + selector).prop('checked', false);
            }
        }).trigger('input');
    }

    // When the bioactivity search changes
    search_filter(bioactivity_search,bioactivity_string,'bioactivities','');

    // When the target search changes
    search_filter(target_search,target_string,'targets','');

    // When the compound search changes
    search_filter(compound_search,compound_string,'compounds','c');

    // When the drugtrial search changes
    search_filter(drugtrial_search,drugtrial_string,'drugtrials','');

//    function hashChange() {
//
//        if (document.location.hash == "") {
//            $('#graphic').prop('hidden',true);
//            $('#selection').prop('hidden',false)
//        }
//
//        else {
//            $('#graphic').prop('hidden',false);
//            $('#selection').prop('hidden',true)
//        }
//    }
//
//    //This will call the hashchange function whenever the hashchanges (does not work on outdated versions of IE)
//    window.onhashchange = hashChange;
});

