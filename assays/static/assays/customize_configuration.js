// This script will show a graphical representation of a study configuration
$(document).ready(function () {

    function getValues() {
        // Selector for all inline rows
        var inlines = $("tr[id*='studymodel_set']");
        // Returned array of nodes
        var data = [];

        // For every inline (i is the index)
        for (var i in inlines) {
            // Get the organ
            var organ = $('#id_studymodel_set-'+ i +'-organ').val();
            // Get the sequence #
            var sequence = $('#id_studymodel_set-'+ i +'-sequence_number').val();
            // Get the integration mode (1 for connected and 0 for not connected)
            var connection = $('#id_studymodel_set-'+ i +'-integration_mode').val();

            // Only add complete nodes
            if (organ && sequence && connection) {
                data.push({'organ': organ, 'sequence': sequence, 'connection': connection});
            }
        }

        // Sort the data by sequence
        _.sortBy(data, function(o) { return o.sequence; });

        return data;
    }

    function makeGraph() {

        var nodes = getValues();
        var links = [];

        // Get links
        for (var i=0; i < nodes.length-1; i++) {
            // Current model
            var current = nodes[i];
            // Next model
            var next = nodes[i+1];

            // If the next model is in parallel
            if (current.sequence == next.sequence) {
                links.push({'source':i, 'target':i+1, 'connection':1});
            }

            // If next is not in parallel and is connection
            else if (next.connection == 1) {
                links.push({'source':i, 'target':i+1, 'connection':1});
            }

            // If next is not in parallel and not connection
            else {
                links.push({'source':i, 'target':i+1, 'connection':0});
            }

            // Check to find any more models in parallel
            for (var j=i+2; j < nodes.length; j++) {
                var further_node = nodes[j];
                // If the next model is in parallel
                if (current.sequence == further_node.sequence) {
                    links.push({'source':i, 'target':i+1, 'connection':1});
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
            .charge(-120)
            .linkDistance(30)
            .size([width, height]);

        var svg = d3.select("#content").append("svg")
            .attr("width", width)
            .attr("height", height);

        force
            .nodes(nodes)
            .links(links)
            .start();

        var link = svg.selectAll(".link")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .style('stroke', function(d) { return d.connection ? '#00FF00':'#FF0000' });
            //.style("stroke-width", function(d) { return Math.sqrt(d.value); });

        var gnodes = svg.selectAll('g.gnode')
            .data(nodes)
            .enter()
            .append('g')
            .classed('gnode', true);

        var node = gnodes.append("circle")
            .attr("class", "node")
            .attr("r", 5)
            .style("fill", function(d) { return color(d.organ); });
            //.call(force.drag);

        var labels = gnodes.append("text")
            .text(function(d) { return d.sequence; });

        force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            gnodes.attr("transform", function(d) {
                return 'translate(' + [d.x, d.y] + ')';
            });
        });
    }

    makeGraph();
});
