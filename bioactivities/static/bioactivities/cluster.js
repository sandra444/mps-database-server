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
                if (i >= 9){
                    break;
                }
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
        var query = "<div style='width:" + queryWidth + "px; height: "+ queryHeight + "px;!important;overflow: scroll;'><table class='table table-striped'><thead><tr><td><b>Target</b></td><td><b>Bioactivity</b></td></tr></thead>";

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

                document.location.hash = "display";

                if (json.data_json) {
                    //console.log(json);
                    cluster(json.data_json, json.bioactivities, json.compounds);
                }
                else {
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
                targets = get_list(json.targets);
                compounds = get_list(json.compounds);
                bioactivities = get_list(json.bioactivities);
                //console.log(targets);
                //console.log(compounds);
                //console.log(bioactivities);

                // Case INSENSITIVE sort
                targets = _.sortBy(targets, function (i) { return i.name.toLowerCase(); });

                // Clear targets
                $('#targets').html('');
                // Add targets
                for (var i in targets) {
                    var row = "<tr id='" + targets[i].name.replace(/ /g,"_") + "'>";
                    row += "<td>" + "<input type='checkbox' value='" + targets[i].name + "'></td>";
                    row += "<td>" + targets[i].name + "</td>";
                    $('#targets').append( row );
                }

                // Case INSENSITIVE sort
                compounds = _.sortBy(compounds, function (i) { return i.name.toLowerCase(); });

                // Clear compounds
                $('#compounds').html('');
                // Add compounds
                for (var i in compounds) {
                    // Note added 'c' to avoid confusion with graphic
                    var row = "<tr id='c" + compounds[i].name.replace(/ /g,"_") + "'>";
                    row += "<td>" + "<input type='checkbox' value='" + compounds[i].name + "'></td>";
                    row += "<td>" + compounds[i].name + "</td>";
                    $('#compounds').append( row );
                }

                // Case INSENSITIVE sort
                bioactivities = _.sortBy(bioactivities, function (i) { return i.name.toLowerCase(); });

                // Clear targets
                $('#bioactivities').html('');
                // Add targets
                for (var i in bioactivities) {
                    var row = "<tr id='" + bioactivities[i].name.replace(/ /g,"_") + "'>";
                    row += "<td>" + "<input type='checkbox' value='" + bioactivities[i].name + "'></td>";
                    row += "<td>" + bioactivities[i].name + "</td>";
                    $('#bioactivities').append(row);
                }

                // Reset select all boxes
                $("#all_bioactivities").prop('checked',false);
                $("#all_targets").prop('checked',false);
                $("#all_compounds").prop('checked',false);

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

    function get_list(data) {
        if (!data || data.length == 0){
            return [];
        }

        var result = [];
        var i;
        for (i = 0; i < data.length; i += 1) {
            if (data[i][1] >= min_feat_count) {
                result.push({
                    name: data[i][0],
                    is_selected: false
                });
            }
        }
        return result;
    }

    document.location.hash = "";

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

    // Change all bioactivities
    $('#all_bioactivities').change(function(evt) {
        if (this.checked) {
            $("#bioactivities input[type='checkbox']:visible").prop('checked', true);
        }
        else {
            $("#bioactivities input[type='checkbox']:visible").prop('checked', false);
        }
    });

    $("body").on( "change", "#bioactivities input[type='checkbox']", function(event) {
        if ($("#bioactivities input[type='checkbox']:checked:visible").length == $("#bioactivities input[type='checkbox']:visible").length) {
            $('#all_bioactivities').prop('checked', true);
        }
        else {
            $('#all_bioactivities').prop('checked', false);
        }
    });

    // Change all targets
    $('#all_targets').change(function(evt) {
        if (this.checked) {
            $("#targets input[type='checkbox']:visible").prop('checked', true);
        }
        else {
            $("#targets input[type='checkbox']:visible").prop('checked', false);
        }
    });

    $("body").on( "change", "#targets input[type='checkbox']", function(event) {
        if ($("#targets input[type='checkbox']:checked:visible").length == $("#targets input[type='checkbox']:visible").length) {
            $('#all_targets').prop('checked', true);
        }
        else {
            $('#all_targets').prop('checked', false);
        }
    });

    // Change all compounds
    $('#all_compounds').change(function(evt) {
        if (this.checked) {
            $("#compounds input[type='checkbox']:visible").prop('checked', true);
        }
        else {
            $("#compounds input[type='checkbox']:visible").prop('checked', false);
        }
    });

    $("body").on( "change", "#compounds input[type='checkbox']", function(event) {
        if ($("#compounds input[type='checkbox']:checked:visible").length == $("#compounds input[type='checkbox']:visible").length) {
            $('#all_compounds').prop('checked', true);
        }
        else {
            $('#all_compounds').prop('checked', false);
        }
    });

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

    var targets_filter = [];
    var compounds_filter = [];
    var bioactivities_filter = [];

    refresh();

    $('#submit').click(function(evt) {
        submit();
    });

    // Return to selection
    $('#back').click(function(evt) {
        document.location.hash = "";
        $('#graphic').prop('hidden',true);
        $('#selection').prop('hidden',false)
    });

    var bioactivity_search = $('#bioactivity_filter');
    var target_search = $('#target_filter');
    var compound_search = $('#compound_filter');

    var bioactivity_string = bioactivity_search.val().toLowerCase().replace(/ /g,"_");
    var target_string = target_search.val().toLowerCase().replace(/ /g,"_");
    var compound_string = 'c' + compound_search.val().toLowerCase().replace(/ /g,"_");

    // When the bioactivity search changes
    bioactivity_search.on('input',function() {
        bioactivity_string = bioactivity_search.val().toLowerCase().replace(/ /g,"_");

        $("#bioactivities tr").each(function() {
            if (this.id.toLowerCase().indexOf(bioactivity_string) > -1) {
                this.hidden = false;
            }
            else {
                this.hidden = true;
            }
        });

        // Check or uncheck all as necessary
        if ($("#bioactivities input[type='checkbox']:checked:visible").length == $("#bioactivities input[type='checkbox']:visible").length) {
            $('#all_bioactivities').prop('checked', true);
        }
        else {
            $('#all_bioactivities').prop('checked', false);
        }
    }).trigger('input');

    // When the target search changes
    target_search.on('input',function() {
        target_string = target_search.val().toLowerCase().replace(/ /g,"_");

        $("#targets tr").each(function() {
            if (this.id.toLowerCase().indexOf(target_string) > -1) {
                this.hidden = false;
            }
            else {
                this.hidden = true;
            }
        });

        // Check or uncheck all as necessary
        if ($("#targets input[type='checkbox']:checked:visible").length == $("#targets input[type='checkbox']:visible").length) {
            $('#all_targets').prop('checked', true);
        }
        else {
            $('#all_targets').prop('checked', false);
        }
    }).trigger('input');

    // When the compound search changes
    compound_search.on('input',function() {
        // Note the added 'c' to avoid confusion
        compound_string = 'c' + compound_search.val().toLowerCase().replace(/ /g,"_");

        $("#compounds tr").each(function() {
            if (this.id.toLowerCase().indexOf(compound_string) > -1) {
                this.hidden = false;
            }
            else {
                this.hidden = true;
            }
        });

        // Check or uncheck all as necessary
        if ($("#compounds input[type='checkbox']:checked:visible").length == $("#compounds input[type='checkbox']:visible").length) {
            $('#all_compounds').prop('checked', true);
        }
        else {
            $('#all_compounds').prop('checked', false);
        }
    }).trigger('input');

    var hashChange = function() {

        if (document.location.hash == "") {
            $('#graphic').prop('hidden',true);
            $('#selection').prop('hidden',false)
        }

        else {
            $('#graphic').prop('hidden',false);
            $('#selection').prop('hidden',true)
        }
    };

    //This will call the hashchange function whenever the hashchanges (does not work on outdated versions of IE)
    window.onhashchange = hashChange;
});
