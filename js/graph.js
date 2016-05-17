loader.addModule('graph',
'canvas', 'B',
function (canvas, B) {
	"use strict";

	/**
	 * Module to manage the game map
	 */

	var canvasContext = canvas.getContext();

	function generate (graph, nbNodes) {
		while (nbNodes > 0) {
			graph.nodes.push({
				x: Math.random() * 1000,
				y: Math.random() * 1000
			});
			nbNodes--;
		}
	}

	/**
	 * Map construct. Build the level, set the objects and the frame information
	 */
	function Graph (nbNodes, surfaceW, surfaceH) {
		var graph = {
			nodes: [],
			edges: []
		};

		generate(graph, nbNodes);

		graph.draw = function (camera) {
			canvasContext.beginPath();
			graph.nodes.forEach(function (node) {
				var coords = camera.adapt(node);
				canvasContext.moveTo(coords.x, coords.y);
				canvasContext.arc(coords.x, coords.y, 5, 0, 2 * Math.PI, false);
			});
			canvasContext.fill();
		};

		return graph;
	}

	return Graph;
});
