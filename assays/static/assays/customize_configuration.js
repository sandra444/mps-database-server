// This script will show a graphical representation of a study configuration
$(document).ready(function () {

    // Find out if user is using IE
    var ms_ie = false;
    var ua = window.navigator.userAgent;
    var old_ie = ua.indexOf('MSIE ');
    var new_ie = ua.indexOf('Trident/');

    if ((old_ie > -1) || (new_ie > -1)) {
        ms_ie = true;
    }

    var data = getValues();

    function changeOccurred(new_data) {

        if (new_data.length != data.length) {
           return true;
        }

        for (var i in data) {
            for (var j in new_data[i]) {
                if (new_data[i][j] != data[i][j]) {
                    return true;
                }
            }
        }

        return false;

    }

    function getValues() {
        // Selector for all inline rows
        var inlines = $("tr[id*='studymodel_set']");
        // Returned array of nodes
        var data = [];

        // For every inline (i is the index)
        for (var i in inlines) {
            // Get the label
            var label = $('#id_studymodel_set-'+ i +'-label').val();
            // Get the organ
            var organ = $('#id_studymodel_set-'+ i +'-organ').val();
            var organ_name = $( '#id_studymodel_set-'+ i +'-organ option:selected').text();
            // Get the sequence #
            var sequence = $('#id_studymodel_set-'+ i +'-sequence_number').val();
            // Get the outputs
            var output = $('#id_studymodel_set-'+ i +'-output').val();
            // Get the integration mode (1 for connected and 0 for not connected)
            var connection = Math.floor($('#id_studymodel_set-'+ i +'-integration_mode').val());

            // Only add complete nodes
            if (label && organ && sequence) {
                data.push({'label': label, 'organ': organ, 'sequence': sequence, 'connection': connection, 'organ_name': organ_name, 'output': output});
            }
        }

        // Sort the data by sequence
        _.sortBy(data, function(o) { return o.sequence; });

        return data;
    }

    function makeGraph() {

        var nodes = $(data).slice();
        var links = [];
        var bilinks = [];

        // Get links
        for (var i=0; i < data.length; i++) {

            var source = data[i];

            var outputs = source.output.split('-');

            for (var j=0; j < data.length; j++) {

                if (i == j) {
                    continue;
                }

                var target = data[j];
                var label = target.label;
                var connection = target.connection;

                var intermediate = {};

                if (outputs.indexOf(label) > -1) {
                    links.push({'source':source, 'target':intermediate }, {'source':intermediate, 'target':target });
                    bilinks.push([source,intermediate,target,connection]);
                    nodes.push(intermediate);
                }
            }
        }

        // Purge old graph if it exists
        if ($('svg')[0]) {
            $('svg').remove();
        }
        //Subject to change
        var width = $('#content').width(),
            height = 500;

        var color = d3.scale.category20();

        var force = d3.layout.force()
            .charge(-800)
            //.linkDistance(30)
            .size([width, height]);

        var drag = force.drag()
            .on("dragstart", dragstart);

        var svg = d3.select("#graph").append("svg")
            .attr("width", width)
            .attr("height", height);

        force
            .nodes(nodes)
            .links(links)
            .start();

        var link = svg.selectAll(".link")
            .data(bilinks)
            .enter().append("path")
            .attr("class", "link")
            .style("stroke-width", 3)
            .style('stroke', function(d) { return d[3] ? '#00FF00':'#FF0000' })
            .style("marker-end", function(d) { return ms_ie ? "":'url(#arrow)' });

        var gnodes = svg.selectAll('g.gnode')
            .data(data)
            .enter()
            .append('g')
            .classed('gnode', true)
            .on("dblclick", dblclick)
            .call(drag);

        var node = gnodes.append("circle")
            .attr("class", "node")
            .attr("r", 18)
            .style("fill", '#FDF5E6')
            .style("stroke", function(d) { return color(d.organ); })
            .style("stroke-width", 3);

        //Titles for hovering
        gnodes.append("title")
            .text(function (d) {
            return d.label + ' : ' + d.organ_name;
        });

        var labels = gnodes.append("text")
            .attr("x", 0)
            // This attribute is necessary to "bump" the text down
            // otherwise the bottom of the text is centered, not the text itself
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .attr("font-size", 20)
            .text(function(d) { return d.label; });

        force.on("tick", function() {
            link.attr("d", function(d) {
              return "M" + d[0].x + "," + d[0].y
                  + "S" + d[1].x + "," + d[1].y
                  + " " + d[2].x + "," + d[2].y;
            });

            gnodes.attr("transform", function(d) {
                return 'translate(' + [d.x, d.y] + ')';
            });
        });

        //---Insert for markers-------
        // Just call url('#arrow') when you want this marker
        svg.append("defs").selectAll("marker")
            .data(["arrow"])
          .enter().append("marker")
            .attr("id", function(d) { return d; })
            // It is possible that the negative value in this viewBox breaks IE
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 10)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
          .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .style("stroke", "#0000FF")
            .style("fill", "#0000FF")
            .style("opacity", "1");
        //---End Insert---

        function dblclick(d) {
          d3.select(this).classed("fixed", d.fixed = false);
        }

        function dragstart(d) {
          d3.select(this).classed("fixed", d.fixed = true);
        }
    }

    function refresh() {
        var new_data = getValues();

        if(changeOccurred(new_data)) {
            data = new_data;
            makeGraph();
        }
    }

    makeGraph();

    // Whenever one of the inputs change
    $("body").on("change", "tr [id*='studymodel_set']", function(event) {
        refresh();
    });

    // This selector will check all items with DELETE in the name, including newly created ones
    $("body").on("click", "input[name*='DELETE']", function(event) {
        refresh();
    });

    $('#reset').click( function(event) {
        data = getValues();
        makeGraph();
    });
});
