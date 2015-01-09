$(document).ready(function () {

    function cluster(cluster_data_json, bioactivities, compounds) {

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
        var query = "<div style='width: 100%;height: 600px !important;overflow: scroll;'><table class='table table-striped'><thead><tr><td><b>Target</b></td><td><b>Bioactivity</b></td></tr></thead>";

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
//        $http(
//                {
//                    url: '/bioactivities/gen_cluster/',
//                    method: 'POST',
//                    data: {
//                        'bioactivities_filter': get_bioactivities_filter,
//                        'targets_filter': get_targets_filter,
//                        'compounds_filter': get_compounds_filter,
//                        'target_types_filter': target_types_filter,
//                        'organisms_filter': organisms_filter,
//                        'normalize_bioactivities': normalize_bioactivities,
//                        'metric': get_metric,
//                        'method': get_method,
//                        'chemical_properties': get_chemical_properties
//                    },
//                    headers: {
//                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
//                    }
//                }
//            ).success(
//                function (data) {
//                    window.spinner.stop();
//                    if (data["data_json"] != undefined) {
//                        $scope.cluster_data_json = data["data_json"];
//                        $scope.bioactivities = data["bioactivities"];
//                        $scope.compounds = data["compounds"];
//                        window.d3_cluster_render($scope.cluster_data_json,$scope.bioactivities,$scope.compounds);
//
//                    } else {
//                        $scope.error_message_visible = true;
//                        window.spinner.stop();
//                    }
//                }
//            ).error(
//                function () {
//                    window.spinner.stop();
//                    $scope.error_message_visible = true;
//                }
//            );
    }

    function refresh() {
//        promise: function() {
//                return $http({
//                    method: 'GET',
//                    params: {
//                        'target_types': JSON.stringify(target_types),
//                        'organisms': JSON.stringify(organisms)
//                    },
//                    url: '/bioactivities/all_data'
//                })
//                .then(function(response) {
//                    min_feat_count = $rootScope.min_feat_count ? $rootScope.min_feat_count : 10;
//                    if (typeof response.data === 'object') {
//                        targets = get_list(response.data.targets);
//                        compounds = get_list(response.data.compounds);
//                        bioactivities = get_list(response.data.bioactivities);
//                        return response.data
//                    } else {
//                        return $q.reject(response.data);
//                    }
//                }, function(response) {
//                    return $q.reject(response.data);
//                });
//            }

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
                    var row = "<tr>";
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
                    var row = "<tr>";
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
                    var row = "<tr>";
                    row += "<td>" + "<input type='checkbox' value='" + bioactivities[i].name + "'></td>";
                    row += "<td>" + bioactivities[i].name + "</td>";
                    $('#bioactivities').append(row);
                }

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

    // Currently testing, should grab these with a function in refresh (KEEP THIS FORMAT)
    var target_types = [{"name":"Cell-Line","is_selected":false},{"name":"Organism","is_selected":false},{"name":"Single Protein","is_selected":true},{"name":"Tissue","is_selected":false}];
    var organisms = [{"name":"Homo Sapiens","is_selected":true},{"name":"Rattus Norvegicus","is_selected":true},{"name":"Canis Lupus Familiaris","is_selected":false}];

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

    // Initial min_feature count
    var min_feat_count = $('#minimum_feature_count').val();
    // Listen min feature count
    $('#apply_minimum_feature_count').click(function(evt) {
        min_feat_count = $('#minimum_feature_count').val();
        refresh();
    });

    // Initial truth normalize
    var normalize_bioactivities = $('#normalize_bioactivities').val();
    // Listen normalize
    $('#normalize_bioactivities').change(function(evt) {
        normalize_bioactivities = $('#normalize_bioactivities').val();
    });

    // Initial truth chem properties
    var chemical_properties = $('#chemical_properties').val();
    // Listen chemical properties
    $('#chemical_properties').change(function(evt) {
        chemical_properties = $('#chemical_properties').val();
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

    refresh();
});
