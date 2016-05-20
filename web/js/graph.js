loader.addModule('graph',
'canvas', 'B',
function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var canvasContext = canvas.getContext();

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Graph (nodes, edges) {
		var graph = {
			nodes: nodes,
			edges: edges
		};

		graph.draw = function (camera) {
			canvasContext.beginPath();
			graph.nodes.forEach(function (node) {
				var coords = camera.adapt(node);
				canvasContext.moveTo(coords.x, coords.y);
				canvasContext.arc(coords.x, coords.y, 5, 0, 2 * Math.PI, false);
			});
			graph.edges.forEach(function (edge) {
				var coordsStart = camera.adapt(edge[0]),
					coordsEnd = camera.adapt(edge[1]);
				canvasContext.moveTo(coordsStart.x, coordsStart.y);
				canvasContext.lineTo(coordsEnd.x, coordsEnd.y);
			});
			canvasContext.stroke();
			canvasContext.fill();
		};

		return graph;
	}

	return Graph;
});
