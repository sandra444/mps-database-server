$(document).ready(function () {

    function cluster(cluster_data_json, bioactivities, compounds) {

        // Show graphic
        $('#graphic').prop('hidden',false);
        // Hide error
        $('#error_message').prop('hidden',true);

        // Clear old (if present)
        $('#cluster').html('');
        $('#query').html('');
        $('#compound').html('');


        var height = null;
        var find = Object.keys(compounds).length;

        if (find < 11) {
            height = 600;
        }
        else if (find < 20) {
            height = 800;
        }
        else if (find < 50) {
            height = 1000;
        }
        else if (find < 80) {
            height = 1600;
        }
        else {
            height = 2000;
        }

        var width = $("#cluster").width();

        var cluster = d3.layout.cluster()
            .size([height, width - 160]);

        var diagonal = d3.svg.diagonal()
            .projection(function (d) {
                return [d.y, d.x];
            });

        var svg = d3.select("#cluster").append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(40,0)");

        var root = cluster_data_json;

        var nodes = cluster.nodes(root),
            links = cluster.links(nodes);

        var link = svg.selectAll(".link")
            .data(links)
            .enter().append("path")
            .attr("class", "link")
            .attr("d", diagonal);

        var node = svg.selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", "node")
            .attr("id", function (d) {
                return d.name.replace(/\s/g, "");
            })
            .attr("transform", function (d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        node.append("circle")
            .attr("r", 4.5);

        node.on("mouseover", function (d) {
            var recurse = function(node) {
                // Change the class to selected node
                $('#'+node.name.replace(/\s/g, "")).attr('class', 'node-s');

                // Stop at leaves
                if (!node.children) {
                    return;
                }
                // For nodes with children
                else {
                    for (var child in node.children) {
                        recurse(node.children[child]);
                    }
                }
            };
            recurse(d);
        });

        node.on("mouseout", function (d) {
            node.attr("class", "node");
        });

        node.on("click", function (d) {
            $('#compound').html("");
            var names = d.name.split('\n');
            var box = "";
            for (var i  in names){
                if (compounds[names[i]]){
                    var com = compounds[names[i]];
                    var box = box = "<div id='com" + i + "' class='thumbnail text-center'>";
                    box += '<button id="X' + i + '" type="button" class="btn-xs btn-danger">X</button>';
                    box += "<img src='https://www.ebi.ac.uk/chembldb/compound/displayimage/"+ com.CHEMBL + "' class='img-polaroid'>";
                    box += "<strong>" + com.name + "</strong><br>";
                    box += "Known Drug: ";
                    box += com.knownDrug ? "<span class='glyphicon glyphicon-ok'></span><br>" : "<span class='glyphicon glyphicon-remove'></span><br>";
                    box += "Passes Rule of 3: ";
                    box += com.ro3 ? "<span class='glyphicon glyphicon-ok'></span><br>" : "<span class='glyphicon glyphicon-remove'></span><br>";
                    box += "Rule of 5 Violations: " + com.ro5 + "<br>";
                    box += "Species: " + com.species;
                    box += "</div>";
                    $('#compound').prepend(box);
                }
                // Break at 10
//                if (i >= 9){
//                    break;
//                }
            }
        });

        //Titles for hovering
        node.append("title")
            .text(function (d) {
                return d.name.indexOf("\n") > -1 ? "" : d.name;
        });

        node.append("text")
            .attr("dx", function (d) {
                return d.children ? -8 : 8;
            })
            .attr("dy", 3)
            .style("text-anchor", function (d) {
                return d.children ? "end" : "start";
            })
            .text(function (d) {
                return d.name.indexOf("\n") > -1 ? "" : d.name;
            });

        d3.select(self.frameElement).style("height", height + "px");

        // Display the original query in terms of what bioactivity-target pairs were used
        var queryHeight = 600;
        var queryWidth = $('#query_box').width();
        var query = "<div style='width:" + queryWidth + "px; height: "+ queryHeight + "px;!important;overflow: scroll;'><table class='table table-striped table-hover'><thead><tr><td><b>Target</b></td><td><b>Bioactivity</b></td></tr></thead>";

        for (var i in bioactivities){
            bioactivity = bioactivities[i].split('_');
            query += "<tr><td>"+bioactivity[0]+"</td><td>"+bioactivity[1]+"</td></tr>";
        }

        query += "</table></div>";

        $('#query').html(query);

        $('#compound').html('<div id="com" class="thumbnail text-center">Click a node or compound name to view additional information</div>');

        $(function () {
            $(document).on("click", function (e) {
                if (e.target.id.indexOf("X") > -1) {
                    var num = e.target.id.replace( /^\D+/g, '');
                    $("#com" + num).remove();
                    e.stopPropagation();
                    return false;
                }
            });
        });
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
            url:  '/bioactivities/gen_cluster/',
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
                'method': method,
                'chemical_properties': chemical_properties
            }),
            success: function (json) {
                // Stop spinner
                window.spinner.stop();
                //console.log(json);

                if (json.data_json) {
                    //console.log(json);
                    cluster(json.data_json, json.bioactivities, json.compounds);
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
    function reset_rows(name,list,add) {
        // Clear current
        $('#' + name).html('');
        // Add from list
        for (var i in list) {
            // Note added 'c' to avoid confusion with graphic
            var row = "<tr id='" + add + list[i].name.replace(/ /g,"_") + "'>";
            row += "<td>" + "<input type='checkbox' value='" + list[i].name + "'></td>";
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

    // Initial truth chem properties
    var chemical_properties = $('#chemical_properties').prop('checked');
    // Listen chemical properties
    $('#chemical_properties').change(function(evt) {
        chemical_properties = $('#chemical_properties').prop('checked');
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
