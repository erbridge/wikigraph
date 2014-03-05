(function() {
    "use strict";

    $(document).ready(function() {
        var width = $(document).width() * 0.98;
        var height = $(document).height() * 0.97;

        var force = d3.layout.force()
            .charge(-120)
            .linkDistance(30)
            .size([width, height]);

        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

        d3.json("data/data.json", function(error, graph) {
            var hash_lookup = {};

            _.each(graph.nodes, function(node, i) {
                hash_lookup[node.name] = i;
            });

            _.each(graph.links, function(link, i) {
                link.source = hash_lookup[link.source_name];
                link.target = hash_lookup[link.target_name];
            });

            force.nodes(graph.nodes)
                .links(graph.links)
                .start();

            var link = svg.selectAll(".link")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke-width", 2)
                .style("stroke", "#757575")
                .style("stroke-opacity", "0.7");

            var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 3)
                .style("fill", "#242424")
                .style("stroke", "#ffffff")
                .style("stroke-width", 2)
                .call(force.drag);

            node.append("title")
                .text(function(node) { return node.name; });

            force.on("tick", function() {
                link.attr("x1", function(link) { return link.source.x; })
                    .attr("y1", function(link) { return link.source.y; })
                    .attr("x2", function(link) { return link.target.x; })
                    .attr("y2", function(link) { return link.target.y; });

                node.attr("cx", function(node) { return node.x; })
                    .attr("cy", function(node) { return node.y; });
            });
        });
    });
})();

